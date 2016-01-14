class Partition(object):
    def __init__(self, id_, isTrivial):
        self.id = id_
        self.isTrivial = isTrivial
        self.diffRegions = {}

