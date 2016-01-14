import os
import traceback

class Object(object):
    pass

class RichException(Exception):
    def __init__(self, msg="", cause=None):
        super(RichException, self).__init__(msg)
        self.msg = msg
        self.cause = cause
        if cause:
            self.traceback = traceback.format_exc()
            
    def __str__(self):
        txt = self.msg
        if self.cause:
            txt += '\n\n--->Caused by another exception:\n%s' % self.traceback
        return txt

def makedirsIfNotExists(path):
    pathExisted = os.path.exists(path)
    if not pathExisted:
        os.makedirs(path)
    pathCreated = not pathExisted 
    return pathCreated