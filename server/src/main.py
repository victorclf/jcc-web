import os
import cherrypy
from cherrypy.lib.static import serve_file

import options
from controller.partition import *

STATIC_DIR_ROOT = os.path.abspath(os.path.join(os.getcwd(), '../../client/'))

WEB_EXCEPTION_MAP = {
    InvalidProjectIdException : cherrypy.HTTPError(400, "Invalid project owner and/or project name."), 
    InvalidPullRequestIdException : cherrypy.HTTPError(400, "Invalid pull request ID."),
    FailedToDownloadPullRequestException : cherrypy.HTTPError(500, "Server failed to download pull request from GitHub."),
    FailedToPartitionPullRequestException : cherrypy.HTTPError(500, "Server failed to partition the pull request."),
    InvalidRelativeFilePathException : cherrypy.HTTPError(404, "Invalid pull request file path.")
}

def mapToWebException(e):
    if type(e) in WEB_EXCEPTION_MAP:
        raise WEB_EXCEPTION_MAP[type(e)]
    else:
        raise

class MainResource(object):
    def __init__(self):
        self.pulls = PullRequestResource()

    '''
    ./
    '''
    @cherrypy.expose
    @cherrypy.tools.accept(media='text/html')
    def index(self):
        indexPagePath = os.path.join(STATIC_DIR_ROOT, 'index.html')
        return serve_file(indexPagePath)
         

@cherrypy.popargs('projectOwner', 'projectName', 'pullRequestId')
class PullRequestResource(object):
    def __init__(self):
        self.partitions = PartitionResource()
        self.files = PullRequestFilesResource()

    '''
    ./pulls/<projectOwner>/<projectName>/<pullId>/
    '''
    @cherrypy.expose
    @cherrypy.tools.accept(media='text/html')
    def index(self, projectOwner, projectName, pullRequestId):
        indexPagePath = os.path.join(STATIC_DIR_ROOT, 'index.html')
        return serve_file(indexPagePath)
    

class PartitionResource(object):
    def __init__(self):
        self.partitionController = PartitionController()
    
    '''
    ./pulls/<projectOwner>/<projectName>/<pullId>/partitions/
    Returns: pull request partitions (JSON)
    Errors: 
    - Invalid Pull Request URL: 
    '''    
    @cherrypy.expose
    @cherrypy.tools.accept(media='application/json')
    def index(self, projectOwner, projectName, pullRequestId):
        projectId = '/'.join((projectOwner, projectName))
        try:
            pullRequestDownloaded = self.partitionController.downloadPullRequestFromGitHub(projectId, pullRequestId)
            self.partitionController.partitionPullRequest(projectId, pullRequestId)
            partitionsJSON = self.partitionController.getPartitionJSON(projectId, pullRequestId)
            return partitionsJSON;
        except Exception as e:
            mapToWebException(e)


class PullRequestFilesResource(object):
    def __init__(self):
        self.partitionController = PartitionController()
    
    def _cp_dispatch(self, vpath):
        relativeFilePath = []
        while vpath:
            relativeFilePath.append(vpath.pop(0))
        cherrypy.request.params['relativeFilePath'] = '/'.join(relativeFilePath)
        return self
    
    '''
    ./pulls/<projectOwner>/<projectName>/<pullId>/files/<relativeFilePath...>
    '''    
    @cherrypy.expose
    def index(self, projectOwner, projectName, pullRequestId, relativeFilePath):
        projectId = '/'.join((projectOwner, projectName))
        try:
            path = self.partitionController.getPullRequestFilePath(projectId, pullRequestId, relativeFilePath)
            return serve_file(path)
        except Exception as e:
            mapToWebException(e)


def main():
    conf = {
         '/': {
             'tools.staticdir.root': STATIC_DIR_ROOT,
         },
        '/js' : {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': 'js'
         },
        '/lib' : {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': 'lib'
         },
        '/css' : {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': 'css'
         },
        '/images' : {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': 'images'
         },
        '/test' : {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': 'test'
         },
    }
    
    def error_page_default(status, message, traceback, version):
        return message
    cherrypy.config.update({'error_page.default': error_page_default})
    
    cherrypy.quickstart(MainResource(), '/', conf)


if __name__ == '__main__':
    main()
    