import numpy as np

class Octree:
    def __init__(self, bb):
        self.bb = bb
        self.objs = []
        self.children = []

    def contains(self, obj):
        smin, smax = self.bb
        omin, omax = obj.bb()
        return (all(omin < smax) and all(omin > smin)) or \
               (all(omax > smin) and all(omax < smax))

    def contained(self, obj):
        smin, smax = self.bb
        omin, omax = obj.bb()
        return all(omin > smin) and all(omax < smax)

    def insert(self, obj):
        ## so it is fully contained in this node.
        ## is it maybe fully contained in one of the children?
        if not self.children:
            self.create_children()
        for child in self.children:
            if child.contained(obj):
                child.insert(obj)
                return
        self.objs.append(obj)

    def apply(self, obj, action, test):
        for w in self.objs[obj.wi[self]:]:
            obj.wi[self] += 1
            action(w)
            if test(): return False
        for child in self.children:
            if not child.contains(obj): continue
            if not child.apply(obj, action, test):
                return False
        return True

    def insert_if(self, obj, action, test):
        for w in self.objs[obj.wi[self]:]:
            obj.wi[self] += 1
            action(w)
            if test(): return False
        ## so it is fully contained in this node.
        ## is it maybe fully contained in one of the children?
        if not self.children:
            self.create_children()
        for child in self.children:
            if child.contained(obj):
                return child.insert_if(obj, action, test)
        ## no it isn't. Store at this level
        for child in self.children:
            if not child.contains(obj): continue
            if not child.apply(obj, action, test):
                return False
        self.objs.append(obj)
        return True

    def create_children(self):
        #print("creating")
        smin, smax = self.bb
        mid = (smax-smin)/2
        for x in range(2):
            for y in range(2):
                for z in range(2):
                    cmin = smin + mid * np.array([x, y, z])
                    cmax = cmin + mid
                    self.children.append(Octree((cmin, cmax)))

    def print(self, l=0):
        if not self.children: return
        prefix = " "*l
        print("{}{} {}".format(prefix, len(self.objs), self.bb))
        for c in self.children:
            c.print(l+1)

    def __repr__(self):
        c = [repr(c) for c in self.children if c.objs or c.children]
        return repr(len(self.objs)) + " " + str(self.bb) + " " + repr(c) + "\n"
