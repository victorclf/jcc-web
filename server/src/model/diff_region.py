class DiffRegion(object):
    def __init__(self, id_, sourceFilePath, lineSpan, charSpan, enclosingMethodDefId):
        self.id = id_
        self.sourceFilePath = sourceFilePath
        self.lineSpan = lineSpan
        self.charSpan = charSpan
        self.enclosingMethodDefId = self.enclosingMethodDefId