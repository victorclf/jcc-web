import os

import cherrypy
from cherrypy.test import helper

import main

class Test(helper.CPWebCase):
    TEST_DATA_PATH = os.path.join(os.getcwd(), 'testdata')
    
    @staticmethod
    def setup_server():
        cherrypy.tree.mount(main.MainResource(), '/')

    def test_web_app_index(self):
        self.getPage("/")
        self.assertStatus('200 OK')
                        
    def test_pull_request_partitions(self):
        self.getPage("/pulls/victorclf/jcc-web-persontest/1/partitions/")
        self.getPage("/pulls/victorclf/jcc-web-persontest/1/files/somecompany/someprogram/person/Person.java.old/")
        
        with open(os.path.join(self.TEST_DATA_PATH, 'victorclf/jcc-web-persontest/1/somecompany/someprogram/person/Person.java.old')) as fin:
            fileContents = fin.read()
        
        self.assertEqual(self.body, fileContents)
        self.assertStatus('200 OK')
        


