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
            return -f * (s.r/n)
        else:
            return f * (1 - s.r/n)

    def plt(s, ax):
        ax.add_patch(plt.Circle(s.p, s.r))

class Line(Obj):
    def __init__(s, a, c, n):
        s.a = a
        s.c = c
        #s.x = array([x1, x2])
        #s.y = array([y1, y2])
        s.n = n

    def force(s, p):
        """Find the force circle C with radius r applies to point P """
        x = (p[0] + s.a*p[1] - s.a*s.c) / (s.a**2 + 1)
        y = (s.a*(p[0]+s.a*p[1]) + s.c) / (s.a**2 + 1)
        d = array([x, y])

        return d - p

        y = s.b * p[0] + s.c
        x = (p[1] - s.c)/s.b
        dx = p[0] - x
        dy = p[1] - y
        
        d = y - p[n]
        f = s.p - p
        n = norm(f)
        # if n==0 the force has no direction!
        if n == 0: return array([0,0])
        if n < s.r:
            return - f * (1 - s.r/n)
        else:
            return f * (1 - s.r/n)

    def plt(s, ax):
        xmin, xmax = ax.get_xbound()
        ax.add_line(matplotlib.lines.Line2D([xmin,xmax], [s.a*xmin+s.c, s.a*xmax+s.c], linewidth=2, color='blue'))

#def pull(C, r, P):
    #"""Find the force circle C with radius r applies to point P """
    #f = C - P
    #n = norm(f)
    ## if n==0 the force has no direction!
    #if n == 0: return array([0,0])
    #if n<r:
        #return - f * (1 - r/n)
    #else:
        #return f * (1 - r/n)

def ev(v, n):
    """give the error vector given vector v and len l"""
    if norm(v) == 0: return v*0
    return  v - (v/norm(v) * n)

def error_vectors(f1, f2, f3):
    n = (norm(f1) + norm(f2) + norm(f3))/3
    return ev(f1, n), ev(f2, n), ev(f3, n)

C1 = Circle( 0, 0, 2.0)
C2 = Circle(10, 0, 8.0)
C3 = Circle( 1, 8, 1.0)
L = Line(1, 0, 0)
P = array([10, 0])
r = 0

fig = plt.figure(1)
plt.axis([-10, 20, -10, 10])
ax = fig.add_subplot(1,1,1)
L.plt(ax)
C1.plt(ax)
C2.plt(ax)
C3.plt(ax)

p = plt.Circle(P, r, fill=False, color="%f"%(0/26.0))
ax.add_patch(p)

for i in range(1000):
    f1 = C1.force(P)
    f2 = C2.force(P)
    f3 = C3.force(P)
    #f3 = L.force(P)

    ef1, ef2, ef3 = error_vectors(f1, f2, f3)
    P = P + (ef1 + ef2 + ef3)/3
    r = (norm(f1) + norm(f2) + norm(f3))/3
    e = (norm(ef1) + norm(ef2) + norm(ef3))
    print(i, norm(ef1), norm(ef2), norm(ef3), P, e)
    #p = plt.Circle(P, r, fill=False)
    #ax.add_patch(p)
    if e < 0.01: break
    continue

print (P, r)

#plt.show()
