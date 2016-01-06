import cherrypy
from cherrypy.test import helper

import main

class Test(helper.CPWebCase):
    @staticmethod
    def setup_server():
        cherrypy.tree.mount(main.PullRequest(), '/pull/')
    
#     def test_pull_request_index(self):
#         self.getPage("/pull/tesla/coil/1/")
#         self.assertStatus('200 OK')
#         self.assertBody('Pull Request 1 from tesla/coil')
        
    def test_pull_request_partitions(self):
        self.getPage("/pull/tesla/coil/1/partitions/")
        self.assertStatus('200 OK')
        self.assertBody('JSON of partitions from pull 1 from tesla/coil')

