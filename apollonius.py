#!/usr/bin/env python3
import math
import matplotlib.pyplot as plt
import matplotlib
from numpy import array, dot
from numpy.linalg import norm

class Obj:
    def __init__(s, origin, normal):
        s.o = origin
        s.n = normal
    def origin(s):
        return s.o
    def __repr__(s):
        return "origin={0}, normal={1}".format(s.o, s.n)

class Circle(Obj):
    def distance(s, p): ## returns vector with direction and amplitude
        radius = norm(s.n)
        f = s.o - p
        n = norm(f)
        if n == 0: return s.o*0
        direction = 1
        if n < radius:
            direction = -0.5
        return direction * f * (1 - radius/n)

        #f = p-s.o
        #if norm(f) == 0: return s.o*0
        #m = s.o + (f*norm(s.n))/norm(f)
        #return p-m

    def is_inverted(s, p):
        """ true if p is in the circle"""
        return norm(s.o-p) <= norm(s.n)

    def plt(s, ax):
        radius = norm(s.n)
        ax.add_patch(plt.Circle(s.p, radius))

class Line2(Obj):
    def distance(s, p):
        n = s.n/norm(s.n)
        return n * dot((s.o-p), n)

    def is_inverted(s, p):
        """ true if p is on wrong side of line"""
        ##TODO, this can be a lot simpler. I think.
        d = s.distance(p)
        d = d/norm(d)
        n = s.n/norm(s.n)
        return  norm(d+n) > norm(d)

    def plt(s, ax):
        xmin, xmax = ax.get_xbound()
        ymin = s.o[1] - (s.n[0]/s.n[1])*(xmin-s.o[0])
        ymax = s.o[1] - (s.n[0]/s.n[1])*(xmax-s.o[0])
        ax.add_line(matplotlib.lines.Line2D([xmin,xmax], [ymin, ymax], linewidth=2, color='blue'))

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
    obj = list(map(lambda o: p-o.o, objects))
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



def find_inscribed(objects, ax):
    P = starting_point(objects)
    for i in range(1000): #just an upper bound, real condition is e
        f = [obj.distance(P) for obj in objects]   # Distance between P and objects
        ev = error_vectors(f)                  # Error rel to average
        P = P + avg(ev)                     # new P
        n = [norm(v)**2 for v in ev]
        e = sum(n)
        if e < 0.00001:
            break
    r = avg([norm(fi) for fi in  f])
    #success = all(map(lambda c: not c.is_inverted(P), objects))
    circles = [o for o in objects if type(o) is Circle]
    success = 1
    success &= all(map(lambda c: norm(c.n) > r, circles))
    #also P must be inside polygon spanned by objects
    if len(circles) == DIM+1:
        success &= in_volume(P, circles)
    return P, r, success

DIM = 3

if DIM == 2:
    print("$fn=40;")
    L1 = Line2(array([-5,  0]), array([ 2, -1]))
    L2 = Line2(array([ 9,  0]), array([-1, -1]))
    L3 = Line2(array([ 0, -9]), array([ 0,  1]))
    queue = [[L1, L2, L3]]
elif DIM == 3:
    print("$fn=40;")
    L1 = Line2(array([-5,  0, 0]), array([ 2, -1, 1]))
    L2 = Line2(array([ 9,  0, 0]), array([-1, -1, 1]))
    L3 = Line2(array([ 0, -9, 0]), array([ 0,  1, 1]))
    L4 = Line2(array([ 0, 0, 9]), array([ 0,  0, -1]))
    queue = [[L1, L2, L3, L4]]
else:
    print("unsupported DIM")
    import sys
    sys.exit(1)

fig = plt.figure(1)
plt.axis([-10, 20, -10, 10])
ax = fig.add_subplot(1,1,1)
[obj.plt(ax) for obj in queue[0]]
vol = 0
for i in range(80):
    if not queue: break
    objects = queue.pop(0)

    P, r, success = find_inscribed(objects, ax)
    if not success:
        #print("result in other circle, aborting")
        p = plt.Circle(P, r, fill=False, color="red")
        ax.add_patch(p)
        continue
    C = Circle(P, array([r, 0]))
    if DIM == 2:
        print("translate([%f, %f, 0]) circle(%f);" %(P[0], P[1], r*1.01))
    elif DIM == 3:
        print("translate([%f, %f, %f]) sphere(%f);" %(P[0], P[1], P[2], r*1.01))
    for idx, o in enumerate(objects):
        obj = objects[:]
        obj[idx] = C
        queue.append(obj)
    p = plt.Circle(P, r, fill=False, color=".6")
    ax.add_patch(p)
    vol += math.pi * r**2
    #if i%100 == 0:
        #print(i)
#print(i)

#print(vol)
#plt.show()
