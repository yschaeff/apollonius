import numpy as np

class Octree:
    def __init__(self, bb):
        self.bb = bb
        self.objs = []
        self.children = []
    def insert(self, obj, bb):
        smin, smax = self.bb
        omin, omax = bb
        if any(omin < smin) or any(omax > smax):
            return False
        ## so it is fully contained in this node.
        ## is it maybe fully contained in one of the children?
        if not self.children:
            self.create_children()
        for child in self.children:
            if child.insert(obj, bb):
                ## yes it is!
                return True
        ## no it isn't. Store at this level
        self.objs.append((obj, bb))
        return True
    def create_children(self):
        smin, smax = self.bb
        savg = (smax-smin)/2
        for x in range(2):
            for y in range(2):
                for z in range(2):
                    cmin = smin + savg * np.array([x, y, z])
                    cmax = cmin + savg
                    self.children.append(Octree((cmin, cmax)))

