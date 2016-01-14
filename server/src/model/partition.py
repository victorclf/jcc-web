class Partition(object):
    def __init__(self, id_, isTrivial):
        self.id = id_
        self.isTrivial = isTrivial
        self.diffRegions = {}
        
    def __str__(self):
        return 'partition #%d isTrivial:%s diffRegions:%d' % (self.id, self.isTrivial, len(self.diffRegions))

