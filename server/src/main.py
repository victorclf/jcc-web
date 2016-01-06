import cherrypy

@cherrypy.popargs('projectOwner', 'projectName', 'pullRequestId')
class PullRequest(object):
    def __init__(self):
        self.partitions = Partition()

    '''
    ./pull/<projectOwner>/<projectName>/<pullId>/
    '''
#     @cherrypy.expose
#     def index(self, projectOwner, projectName, pullRequestId):
#         return 'Pull Request %s from %s/%s' % (pullRequestId, projectOwner, projectName)
    

class Partition(object):
    '''
    ./pull/<projectOwner>/<projectName>/<pullId>/partitions/
    '''    
    @cherrypy.expose
    def index(self, projectOwner, projectName, pullRequestId):
        return 'JSON of partitions from pull %s from %s/%s' % (pullRequestId, projectOwner, projectName)


if __name__ == '__main__':
    # TODO share static files
    cherrypy.quickstart(PullRequest(), '/pull/')