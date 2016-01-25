import os
import cherrypy
from cherrypy.lib.static import serve_file

import options
from controller.partition import PartitionController

STATIC_DIR_ROOT = os.path.abspath(os.path.join(os.getcwd(), '../../client/'))

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
#     @cherrypy.expose
#     def index(self, projectOwner, projectName, pullRequestId):
#         return 'Pull Request %s from %s/%s' % (pullRequestId, projectOwner, projectName)
    

class PartitionResource(object):
    def __init__(self):
        self.partitionController = PartitionController()
    
    '''
    ./pulls/<projectOwner>/<projectName>/<pullId>/partitions/
    Returns: pull request partitions (JSON)
    '''    
    @cherrypy.expose
    @cherrypy.tools.accept(media='application/json')
    def index(self, projectOwner, projectName, pullRequestId):
        projectId = '/'.join((projectOwner, projectName))
        pullRequestId = int(pullRequestId)
        pullRequestDownloaded = self.partitionController.downloadPullRequestFromGitHub(projectId, pullRequestId)
        if pullRequestDownloaded:
            self.partitionController.partitionPullRequest(projectId, pullRequestId)
        partitionsJSON = self.partitionController.getPartitionJSON(projectId, pullRequestId)
        return partitionsJSON;


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
        pullRequestId = int(pullRequestId)
        path = self.partitionController.getPullRequestFilePath(projectId, pullRequestId, relativeFilePath)
        return serve_file(path)


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
        '/test' : {
             'tools.staticdir.on': True,
             'tools.staticdir.dir': 'test'
         },
    }
    cherrypy.quickstart(MainResource(), '/', conf)


if __name__ == '__main__':
    main()
    