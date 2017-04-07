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

    def plt(s, ax):
        radius = norm(s.n)
        ax.add_patch(plt.Circle(s.p, radius))

class Line2(Obj):
    def distance(s, p):
        n = s.n/norm(s.n)
        return n * dot((s.o-p), n)

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
    return P, r

L1 = Line2(array([-5,  0]), array([ 2, -1]))
L2 = Line2(array([ 9,  0]), array([-1, -1]))
L3 = Line2(array([ 0, -9]), array([ 0,  1]))
stack = [[L1, L2, L3]]

fig = plt.figure(1)
plt.axis([-10, 20, -10, 10])
ax = fig.add_subplot(1,1,1)
[obj.plt(ax) for obj in stack[0]]
vol = 0
for i in range(2000):
    objects = stack.pop(0)
    #objects = stack.pop()

    P, r = find_inscribed(objects, ax)
    if any(map(lambda c: norm(c.o-P) < norm(c.n), filter(lambda o: type(o) is Circle, objects))):
        print(i, r, list(map(lambda c: norm(c.n) < r, filter(lambda o: type(o) is Circle, objects))))
        print(objects)
        print(P, r)
        print("result in other circle, aborting")
        p = plt.Circle(P, r, fill=False, color="red")
        ax.add_patch(p)
        break
    C = Circle(P, array([r, 0]))
    objects.sort(key=lambda o: norm(o.n), reverse=True)
    stack.append([objects[0], objects[1], C])
    stack.append([objects[0], objects[2], C])
    stack.append([objects[1], objects[2], C])
    #print (P, r)
    p = plt.Circle(P, r, fill=False, color=".6")
    ax.add_patch(p)
    vol += math.pi * r**2
    if i%100 == 0:
        print(i)
print(i)

print(vol)
plt.show()
