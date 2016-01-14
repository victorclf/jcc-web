import cherrypy
from cherrypy.test import helper

import main

class Test(helper.CPWebCase):
    @staticmethod
    def setup_server():
        cherrypy.tree.mount(main.MainResource(), '/')
    
#     def test_pull_request_index(self):
#         self.getPage("/pulls/tesla/coil/1/")
#         self.assertStatus('200 OK')
#         self.assertBody('Pull Request 1 from tesla/coil')

    def test_web_app_index(self):
        self.getPage("/")
        self.assertStatus('200 OK')
        
# TODO: Fix this test case that checks if static files are being served     
#     def test_web_app_static_js(self):
#         self.getPage("/js/main.js")
#         self.assertStatus('200 OK')
                        
    # TODO Update this test
#     def test_pull_request_partitions(self):
#         self.getPage("/pulls/tesla/coil/1/partitions/")
#         self.assertStatus('200 OK')
#         self.assertBody('JSON of partitions from pull 1 from tesla/coil')


