import os
import sys

# GitHub
GITHUB_CREDENTIALS_FILE_PATH = os.path.join(os.path.expanduser("~"), '.pullRequestMinerrc') 

# Paths
PULL_REQUESTS_PATH = os.path.abspath(os.path.join(os.getcwd(), './pulls'))
PULL_CACHE_INFO_FILENAME = '.pull-cache-info'
JCC_PATH = os.path.abspath(os.path.join(os.getcwd(), '../../../ccjava/ccjava-plugin/build/eclipse/eclipse'))
JCC_ARGS = '-consoleLog -nosplash --launcher.suppressErrors -vmargs -Xms40m -Xmx1024m'
JCC_LOG_STDOUT = 'jcc-stdout.log'
JCC_LOG_STDERR = 'jcc-stderr.log'
PARTITION_RESULTS_FOLDER_NAME = 'ccjava-results'
PARTITION_RESULTS_FILENAME = 'partitions.csv'

# Misc
SERVER_PORT = 8080
MAX_DOWNLOAD_RETRIES = 3
DROP_PRIVILEGES_GID = 1000
DROP_PRIVILEGES_UID = 1000


def readOptionsFromFile(filePath):
	optVars = {}
	with open(filePath) as fin:
		for l in fin.readlines():
			l = l.strip()
			if l.startswith('#'):
				continue
			splitL = l.split('=', 1)
			if len(splitL) != 2:
				continue
			name, val = [s.strip(' "\'') for s in splitL]
			try: 
				val = int(val) #if it is an integer, convert to int
			except ValueError:
				pass 
			optVars[name] = val
	return optVars

def loadOptionsFromDisk():
	OPTIONS_LOCAL_PATH = 'options.local'
	if os.path.exists(OPTIONS_LOCAL_PATH):
		optVars = readOptionsFromFile(OPTIONS_LOCAL_PATH)
		module = sys.modules[__name__]
		for optName, optVal in optVars.iteritems():
			setattr(module, optName, optVal)

loadOptionsFromDisk()
