class DiffRegion(object):
    def __init__(self, id_, sourceFilePath, lineSpan, charSpan, enclosingMethodDefId):
        self.id = id_
        self.sourceFilePath = sourceFilePath
        self.lineSpan = lineSpan
        self.charSpan = charSpan
        self.enclosingMethodDefId = enclosingMethodDefId
        
    def __str__(self):
        return 'diff #%d src:%s lines:%d,%d' % (self.id, self.sourceFilePath, self.lineSpan[0], self.lineSpan[1])