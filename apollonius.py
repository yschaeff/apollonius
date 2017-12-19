#!/usr/bin/env python3
import math
import matplotlib.pyplot as plt
import matplotlib
from numpy import array, dot
from numpy.linalg import norm

DIM = 3
MAX_OBJECTS = 500
MAX_ERROR = 0.00001
MAX_TRIES = 1000 #per object

class Obj:
    def __init__(self, vector, scalar):
        self.vector = vector
        self.scalar = scalar
    def origin(self):
        return self.vector
    #def intersect(s, circle):
        #return s.distance(circle.o) + circle.o
    def __repr__(self):
        return "vector={0}, scalar={1}".format(self.vector, self.scalar)

class Circle(Obj):
    def distance(self, p): ## returns vector with direction and amplitude
        radius = self.scalar
        f = self.vector - p
        n = norm(f)
        if n == 0: return self.vector*0
        direction = 1
        if n < radius:
            direction = -0.5
        return direction * f * (1 - radius/n)

    def is_inverted(self, p):
        """ true if p is in the circle"""
        return norm(self.vector - p) <= self.scalar

    def plt(self, ax):
        radius = self.scalar
        ax.add_patch(plt.Circle(self.vector, radius))

    def overlaps(self, c):
        return norm(self.vector-c.vector)+10000*MAX_ERROR < self.scalar + c.scalar

class Line2(Obj):
    def distance(self, p):
        n = self.vector/norm(self.vector)
        v = n * self.scalar
        return n * dot( (v - p), n)

    def is_inverted(self, p):
        """ true if p is on wrong side of line"""
        ##TODO, this can be a lot simpler. I think.
        d = self.distance(p)
        d = d/norm(d)
        n = self.vector/norm(self.vector)
        return  norm(d+n) > norm(d)

    def f(self, x):
        a,b = self.vector
        c,d = self.vector/norm(self.vector) * self.scalar
        return (-a/float(b))*(x-c) + d

    def plt(self, ax):
        xmin, xmax = ax.get_xbound()
        ax.add_line(matplotlib.lines.Line2D([xmin,xmax], [self.f(xmin), self.f(xmax)], linewidth=2, color='blue'))

def err_vect(v, n):
    """give the error vector given vector v and len l"""
    if norm(v) == 0: return v*0
    return  v - (v/norm(v) * n)

def error_vectors(v):
    n = avg([norm(f) for f in v])
    return [err_vect(f, n) for f in v]

def avg(summable):
    return sum(summable)/len(summable)

def starting_point(objects):
    circles = [o.origin() for o in objects if type(o) is Circle]
    if not circles:
        return  0 * objects[0].origin()
    return avg(circles)

def sign(p, objects): #only circles! DIM
    obj = list(map(lambda o: p-o.vector, objects))
    first = obj[0]
    obj = map(lambda o: dot(first, o), obj[1:])
    return sum(obj)

def in_volume(p, objects): #
    """ This works when object are DIM+1 circles
        sadly most of these cases happen at the edge. """
    signs = None
    for i in range(len(objects)):
        O = objects[:i] + objects[i+1:]
        s = sign(p, O) > 0
        if signs == None:
            signs = s
        if signs != s:
            return False
    return True



def find_inscribed(objects):
    P = starting_point(objects)
    for i in range(MAX_TRIES): #just an upper bound, real condition is e
        f = [obj.distance(P) for obj in objects]   # Distance between P and objects
        ev = error_vectors(f)                  # Error rel to average
        P = P + avg(ev)                     # new P
        n = [norm(v)**2 for v in ev]
        e = sum(n)
        if e < MAX_ERROR:
            break
    r = avg([norm(fi) for fi in  f])
    #success = all(map(lambda c: not c.is_inverted(P), objects))
    circles = [o for o in objects if type(o) is Circle]
    success = 1
    success &= all(map(lambda c: c.scalar > r, circles))
    #also P must be inside polygon spanned by objects
    #if len(circles) == len(objects):
    #if len(circles) == DIM+1:
        #success &= in_volume(P, circles)
    return P, r, success

if DIM == 2:
    print("$fn=40;")
    L1 = Line2(array([-5,  4]), 0)
    L2 = Line2(array([ 9,  1]), 9)
    L3 = Line2(array([ 0, -9]), 9)
    queue = [[L1, L2, L3]]
    fig = plt.figure(1)
    plt.axis([-10, 20, -10, 10])
    ax = fig.add_subplot(1,1,1)
    [obj.plt(ax) for obj in queue[0]]
elif DIM == 3:
    print("$fn=20;")
    L1 = Line2(array([-1,  1,  1]), 1)
    L2 = Line2(array([ 1,  1,  1]), 1)
    L3 = Line2(array([ 0, -1,  1]), 1)
    L4 = Line2(array([ 0,  0, -1]), 10)
    queue = [[L1, L2, L3, L4]]
else:
    print("unsupported DIM")
    import sys
    sys.exit(1)

vol = 0
db = []
for i in range(MAX_OBJECTS):
    if not queue: break
    objects = queue.pop(0)

    P, r, success = find_inscribed(objects)
    if not success:
        #print("result in other circle, aborting")
        if DIM == 2:
            p = plt.Circle(P, r, fill=False, color="red")
            ax.add_patch(p)
        continue
    # TODO find intersectionpoints between P and all objects and add to cache

    ## 1) minimize radius
    #ic = filter(lambda o: o.overlaps(Circle(P, r)), db)
    #m = map(lambda o: abs(norm(o.vector - P)-o.scalar), ic)
    #m = list(m)
    #if m:
        #r = min(m)
    ##1a) minimize less
    ic = filter(lambda o: o.overlaps(Circle(P, r)), db)
    for c in ic:
        if c.overlaps(Circle(P, r)):
            #TODO, this fails if we are IN c
            if not c.is_inverted(P):
                d = c.distance(P)
                e = r - norm(d)
                P = P - (d/norm(d))*(e/2)
                r = r - (e/2)
            else:
                d = c.distance(P)
                d = d/norm(d) * (norm(d)+r)
                e = norm(d) - r
                P = P + (d/norm(d))*(e/2)
                r = r + (e/2)

    # 2) skip
    #if any(map(lambda o: o.overlaps(Circle(P, r)), db)):
        #continue
    ## 3) reiterate
    #ic = list(filter(lambda o: o.overlaps(Circle(P, r*.9)), db))
    #if ic:
        #objects+=ic
        #queue.insert(0, objects)
        #continue
        #print("fail")
        #continue
    #print("succ")

    C = Circle(P, r)
    db.append(C)
    if DIM == 2:
        print("translate([%f, %f, 0]) circle(%f);" %(P[0], P[1], r*1.01))
    elif DIM == 3:
        print("translate([%f, %f, %f]) sphere(%f);" %(P[0], P[1], P[2], r*1.00))
    for idx, o in enumerate(objects[:DIM+1]):
        obj = objects[:DIM+1]
        obj[idx] = C
        queue.append(obj)
    if DIM == 2:
        p = plt.Circle(P, r, fill=False, color=".6")
        ax.add_patch(p)
    vol += math.pi * r**2
    #if i%100 == 0:
        #print(i)
#print(i)

#print(vol)
#plt.show()
