import os
import shutil
import urllib
import codecs
import csv

import cherrypy
import github
import simplejson

import options
import util
from model.diff_region import DiffRegion
from model.partition import Partition


class GitHubCredentialsFileNotFoundException(Exception): pass
class InvalidProjectIdException(Exception): pass
class InvalidPullRequestIdException(Exception): pass
class FailedToDownloadPullRequestException(util.RichException): pass
class FailedToPartitionPullRequestException(util.RichException): pass
class InvalidRelativeFilePathException(util.RichException): pass


class PartitionController(object):
    def __init__(self):
        self.__gitHubInterface = None
    
    @property
    def gh(self):
        return self.__gitHubInterface if self.__gitHubInterface else self._connectToGitHub()
    
    def getPullRequestFilePath(self, projectId, pullRequestId, relativeFilePath):
        path = os.path.abspath(os.path.join(options.PULL_REQUESTS_PATH, projectId, str(pullRequestId), relativeFilePath))
        # For security, make sure the requested files are inside the pull requests directory
        if not path.startswith(options.PULL_REQUESTS_PATH):
            raise InvalidRelativeFilePathException()
        return path
    
    '''
    returns False: pull request had been previously downloaded and local copy is up-to-date
    returns True: pull request was downloaded
    '''
    def downloadPullRequestFromGitHub(self, projectId, pullRequestId):
        assert isinstance(pullRequestId, (int, long)), pullRequestId
        try:
            repo = self.gh.get_repo(projectId)
        except github.UnknownObjectException:
            raise InvalidProjectIdException()
        try:
            pull = repo.get_pull(pullRequestId)
        except github.UnknownObjectException:
            raise InvalidPullRequestIdException()
        pullPath = self._getPullRequestPath(projectId, pullRequestId)
        
        if self._pullRequestCopyIsUpToDate(pull, pullPath):
            return False
        
        retries = 0
        while 1:
            shutil.rmtree(pullPath, True)
            util.makedirsIfNotExists(pullPath)
            try:
                self._downloadPullRequestData(pull, pullPath)
                break
            except Exception, e:
                if retries >= options.MAX_DOWNLOAD_RETRIES:
                    raise FailedToDownloadPullRequestException(cause=e)
                else:
                    cherrypy.log.error('Failed to download pull request %s #%d. Retrying...' % (projectId, pull.number))
                    retries += 1
        self._updatePullRequestCacheInfo(pull, pullPath)
        return True
        
    def partitionPullRequest(self, projectId, pullRequestId):
        assert isinstance(pullRequestId, (int, long)), pullRequestId
        pullPath = self._getPullRequestPath(projectId, pullRequestId)
        os.system('%s %s 1>tmp.out 2>tmp.err' % (options.JCC_PATH, pullPath))
        resultsPath = os.path.join(pullPath, options.PARTITION_RESULTS_FOLDER_NAME)
        if not os.path.exists(resultsPath):
            raise FailedToPartitionPullRequestException()
        
        for root, dirs, files in os.walk(pullPath):
            for f in files:
                if f.endswith('.java'):
                    fPath = os.path.join(root, f)
                    oldFPath = fPath + '.old'
                    patchPath = fPath + '.patch'
                    
                    shutil.copy(fPath, oldFPath)
                    previousPath = os.getcwd()
                    os.chdir(root)
                    try:
                        os.system('patch -R %s %s 1>tmp.out 2>tmp.err' % (oldFPath, patchPath))
                    finally:
                        os.chdir(previousPath)
        
    def getPartitionJSON(self, projectId, pullRequestId):
        assert isinstance(pullRequestId, (int, long)), pullRequestId
        pullPath = self._getPullRequestPath(projectId, pullRequestId)
        resultsPath = os.path.join(pullPath, options.PARTITION_RESULTS_FOLDER_NAME, options.PARTITION_RESULTS_FILENAME)
        partitions = self._partitionsFromCSV(resultsPath)
        return self._partitionsToMergelyJSON(projectId, pullRequestId, partitions)
    
    def _partitionsFromCSV(self, csvPath):
        partitions = {}
        with open(csvPath, 'rb') as fin:
            csvReader = csv.DictReader(fin)
            for row in csvReader:
                partitionId = int(row['partitionId'])
                isTrivial = True if row['isTrivial'].lower() == 'true' else False
                diffId = int(row['diffId'])
                diffSourceFile = row['diffSourceFile']
                diffLineSpanStart = int(row['diffLineSpanStart'])
                diffLineSpanEnd = int(row['diffLineSpanEnd'])
                diffCharSpanStart = int(row['diffCharacterSpanStart'])
                diffCharSpanEnd = int(row['diffCharacterSpanEnd'])
                enclosingMethodDefId = int(row['enclosingMethodDefId']) if row['enclosingMethodDefId'] != 'null' else None
                
                if partitionId not in partitions:
                    partitions[partitionId] = Partition(partitionId, isTrivial)
                    
                p = partitions.get(partitionId)
                p.diffRegions[diffId] = DiffRegion(diffId, diffSourceFile, 
                     (diffLineSpanStart, diffLineSpanEnd), (diffCharSpanStart, diffCharSpanEnd),
                     enclosingMethodDefId)
        return partitions
                
    def _partitionsToMergelyJSON(self, projectId, pullRequestId, partitions):
        rootNode = util.Object()
        rootNode.text = 'Partitions'
        rootNode.children = []
        
        partitionsSortedByTrivial = sorted(partitions.values(), key=lambda x : x.isTrivial)        
        for p in partitionsSortedByTrivial:
            pNode = util.Object()
            pNode.text = "%s Partition %d" % (("Trivial" if p.isTrivial else "Non-Trivial"), p.id)
            pNode.children = []
            
            diffsOfFile = {}
            for d in p.diffRegions.itervalues():
                if d.sourceFilePath not in diffsOfFile:
                    diffsOfFile[d.sourceFilePath] = []
                diffsOfFile[d.sourceFilePath].append(d)
            
            for (f, diffs) in diffsOfFile.iteritems():
                fNode = util.Object()
                fNode.text = os.path.basename(f)
                baseFilePath = './pulls/%s/%d/files' % (projectId, pullRequestId)
                fNode.before_file = os.path.join(baseFilePath, f + '.old')
                fNode.after_file = os.path.join(baseFilePath, f)
                fNode.children = []
                for d in diffs:
                    dNode = util.Object()
                    dNode.text = '[%d:%d]' % d.lineSpan
                    dNode.line_start = d.lineSpan[0]
                    dNode.line_end = d.lineSpan[1]
                    fNode.children.append(dNode)
                pNode.children.append(fNode)
                
            rootNode.children.append(pNode)
            
        return simplejson.dumps(rootNode, default=lambda x: x.__dict__)
         
    
    def _pullRequestCopyIsUpToDate(self, pull, pullPath):
        pullCacheInfoPath = os.path.join(pullPath, options.PULL_CACHE_INFO_FILENAME)
        if os.path.exists(pullCacheInfoPath):
            with open(pullCacheInfoPath) as fin:
                cacheUpdateDate = fin.readline().strip()
            return cacheUpdateDate == pull.updated_at.isoformat()
        return False
    
    def _updatePullRequestCacheInfo(self, pull, pullPath):
        pullCacheInfoPath = os.path.join(pullPath, options.PULL_CACHE_INFO_FILENAME)
        with open(pullCacheInfoPath, 'w') as fout:
            fout.write(pull.updated_at.isoformat())
            
    def _getPullRequestPath(self, projectId, pullRequestId):
        return os.path.join(options.PULL_REQUESTS_PATH, projectId, str(pullRequestId))
    
    def _connectToGitHub(self):
        try:
            username, password = self._getGitHubCredentials()
            gh = github.Github(username, password)
        except GitHubCredentialsFileNotFoundException:
            cherrypy.log.error(traceback=True)
            gh = github.Github()
        return gh
            
    def _getGitHubCredentials(self):
        if os.path.exists(options.GITHUB_CREDENTIALS_FILE_PATH):
            with open(options.GITHUB_CREDENTIALS_FILE_PATH) as fin:
                l = fin.readline()
                username, password = l.strip().split(':')
        else:
            raise GitHubCredentialsFileNotFoundException()
        return username, password
    
    def _downloadPullRequestData(self, pull, pullRequestPath):
        wholePatchPath = os.path.join(pullRequestPath, '%d.patch' % pull.number)
        urllib.urlretrieve(pull.patch_url, wholePatchPath)
    
        for f in pull.get_files():
            #Don't download files which were deleted.
            if (f.additions > 0 or f.changes > 0) and f.patch:
                filePath = os.path.join(pullRequestPath, f.filename)
                if not os.path.exists(os.path.dirname(filePath)):
                    os.makedirs(os.path.dirname(filePath))
    
                urllib.urlretrieve(f.raw_url, filePath)
                patchPath = filePath + ".patch"
                with codecs.open(patchPath, "w", encoding="UTF-8") as fout:
                    fout.write(f.patch)
                    fout.write('\n')
    