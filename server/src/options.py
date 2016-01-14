import os

# GitHub
GITHUB_CREDENTIALS_FILE_PATH = os.path.join(os.path.expanduser("~"), '.pullRequestMinerrc') 

# Paths
PULL_REQUESTS_PATH = os.path.abspath(os.path.join(os.getcwd(), './pulls'))
PULL_CACHE_INFO_FILENAME = '.pull-cache-info'
JCC_PATH = os.path.abspath(os.path.join(os.getcwd(), '../../../ccjava/ccjava-plugin/build/eclipse/eclipse'))
PARTITION_RESULTS_FOLDER_NAME = 'ccjava-results'
PARTITION_RESULTS_FILENAME = 'partitions.csv'

# Misc
MAX_DOWNLOAD_RETRIES = 3



def loadOptionsFromDisk():
    pass