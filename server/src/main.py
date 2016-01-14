import os
import cherrypy
from cherrypy.lib.static import serve_file

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
        print STATIC_DIR_ROOT
        indexPagePath = os.path.join(STATIC_DIR_ROOT, 'index.html')
        return serve_file(indexPagePath)
        
         

@cherrypy.popargs('projectOwner', 'projectName', 'pullRequestId')
class PullRequestResource(object):
    def __init__(self):
        self.partitions = PartitionResource()

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
    '''    
    @cherrypy.expose
    @cherrypy.tools.accept(media='application/json')
    @cherrypy.tools.json_out()
    def index(self, projectOwner, projectName, pullRequestId):
        projectId = '/'.join((projectOwner, projectName))
        self.partitionController.downloadPullRequestFromGitHub(projectId, pullRequestId)
        #self.partitionController.partitionPullRequest(projectId, pullRequestId)
        #partitionsJSON = self.partitionController.parsePartitions()
        #return partitionsJSON;
        return 'JSON of partitions from pull %s from %s/%s' % (pullRequestId, projectOwner, projectName)


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
    