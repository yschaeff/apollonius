#!/usr/bin/env python3
import math
import matplotlib.pyplot as plt
import matplotlib
from numpy import array, dot
from numpy.linalg import norm

class Obj:
    pass

class Circle(Obj):
    def __init__(s, x, y, r):
        s.p = array([x, y])
        s.r = r

    def force(s, p):
        """Find the force circle C with radius r applies to point P """
        f = s.p - p
        n = norm(f)
        # if n==0 the force has no direction!
        if n == 0: return array([0,0])
        if n < s.r:
            print("err");
            return -f * (1 - s.r/n)
        else:
            return f * (1 - s.r/n)

    def plt(s, ax):
        ax.add_patch(plt.Circle(s.p, s.r))

class Line(Obj):
    def __init__(s, a, c, n):
        s.a = a # f(x): a*x + c
        s.c = c
        s.n = array([a,-1])
        if n:
            s.n = array([-a, 1])
        #s.n = n # reverse normal?
        # This is a terrible way of describing a line, vertical line is impossible
        # If a is positive normal will point to +Y
        # If a is negative normal will point to -Y

    def force(s, p):
        """Find the force circle C with radius r applies to point P """
        x = (p[0] + s.a*p[1] - s.a*s.c) / (s.a**2 + 1)
        y = (s.a*(p[0]+s.a*p[1]) + s.c) / (s.a**2 + 1)
        d = array([x, y])
        result_v = d-p
        #TODO result_v must be in direction of normal, otherwise switch sign
        if norm(s.n + result_v) < norm(result_v):
            return -result_v
        return result_v

    def plt(s, ax):
        xmin, xmax = ax.get_xbound()
        ax.add_line(matplotlib.lines.Line2D([xmin,xmax], [s.a*xmin+s.c, s.a*xmax+s.c], linewidth=2, color='blue'))

def err_vect(v, n):
    """give the error vector given vector v and len l"""
    if norm(v) == 0: return v*0
    return  v - (v/norm(v) * n)

def error_vectors(v):
    n = sum([norm(f) for f in v])/3
    return [err_vect(f, n) for f in v]

def start_pos(C):
    return array(C.p), C.r

C1 = Circle( 0, 0, 2.0)
C2 = Circle(10, 0, 8.0)
C3 = Circle( 1, 8, 1.0)
L1 = Line(2, 10, 1)
L2 = Line(-1, 9, 1)
L3 = Line(0, -9, 0)
objects = (L1, L2, L3)

P, r = start_pos(C2)
P = array([0, 0])

fig = plt.figure(1)
plt.axis([-10, 20, -10, 10])
ax = fig.add_subplot(1,1,1)
[obj.plt(ax) for obj in objects]

p = plt.Circle(P, r, fill=False, color="%f"%(0/26.0))
ax.add_patch(p)

for i in range(1000):
    f = [obj.force(P) for obj in objects]   # Distance between P and objects
    ev = error_vectors(f)                  # Error rel to average
    P = P + (sum(ev))/3                     # new P

    n = [norm(v)**2 for v in ev]
    e = sum(n)
    print(i, n, P, e)
    r = sum([norm(fi) for fi in  f])/3
    p = plt.Circle(P, r, fill=False)
    ax.add_patch(p)
    if e < 0.001: break

print (P, r)
p = plt.Circle(P, r, fill=False, color=".6")
ax.add_patch(p)

plt.show()
