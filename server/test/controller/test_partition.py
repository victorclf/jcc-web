import unittest
import os
import shutil
import filecmp

import pytest
import marks

import options
import util
from controller.partition import PartitionController

class PartitionControllerTest(unittest.TestCase):
    TEST_DATA_PATH = os.path.join(os.getcwd(), 'testdata')
    
    def setUp(self):
        self.controller = PartitionController()
        self.projectOwner = 'victorclf'
        self.projectName = 'jcc-web-persontest'
        self.projectId = '%s/%s' % (self.projectOwner, self.projectName)
        self.pullRequestId = 1
        self.pullPath = os.path.join(options.PULL_REQUESTS_PATH, self.projectOwner, self.projectName, str(self.pullRequestId))
        
        self.tearDown()
        
        util.makedirsIfNotExists(options.PULL_REQUESTS_PATH)
        shutil.copytree(os.path.join(self.TEST_DATA_PATH, self.projectOwner), 
                        os.path.join(options.PULL_REQUESTS_PATH, self.projectOwner),
                        ignore=lambda root,files: [f for f in files if f.endswith('.old')])
        
    def tearDown(self):
        shutil.rmtree(options.PULL_REQUESTS_PATH, True)
        shutil.rmtree(os.path.join(os.getcwd(), 'workspace'), True)

    @marks.slow    
    def testDownloadPullRequest(self):
        shutil.rmtree(options.PULL_REQUESTS_PATH, True)
        self.assertFalse(os.path.exists(os.path.join(self.pullPath)))
        self.controller.downloadPullRequestFromGitHub(self.projectId, self.pullRequestId)
        self.assertTrue(os.path.exists(os.path.join(self.pullPath)))
    
    @marks.slow
    def testPartitionPullRequest(self):
        self.controller.partitionPullRequest(self.projectId, self.pullRequestId)
        self.assertTrue(os.path.exists(os.path.join(self.pullPath, options.PARTITION_RESULTS_FOLDER_NAME)))
        self.assertTrue(os.path.exists(os.path.join(self.pullPath, options.PARTITION_RESULTS_FOLDER_NAME, 'partitions.csv')))
        for root, dirs, files in os.walk(self.pullPath):
            for f in files:
                if f.endswith('java'):
                    oldF = os.path.join(root, f) + '.old'
                    self.assertTrue(os.path.exists(oldF))
                    expectedOldF = os.path.join(self.TEST_DATA_PATH, '..', os.path.relpath(oldF))
                    self.assertTrue(filecmp.cmp(oldF, expectedOldF, False))
                    self.assertFalse(filecmp.cmp(oldF, os.path.join(root, f), False))
    
    def testGetPartitionJSON(self):
        self.controller.partitionPullRequest(self.projectId, self.pullRequestId)
        pJSON = self.controller.getPartitionJSON(self.projectId, self.pullRequestId)
        self.assertTrue(pJSON)
