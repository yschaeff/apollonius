import math
import matplotlib.pyplot as plt
from numpy import array, dot
from numpy.linalg import norm

C1 = array([0,0])
r1 = 2.0
C2 = array([10,0])
r2 = 8.0
C3 = array([1,8])
r3 = 1.0

P = (C1+C2+C3)/3
r = (r1+r2+r3)/3

def pull(C, r, P):
    """Find the force circle C with radius r applies to point P """
    f = C - P
    n = norm(f)
    # if n==0 the force has no direction!
    if n == 0: return array([0,0])
    if n<r:
        return - f * (1 - r/n)
    else:
        return f * (1 - r/n)

def ev(v, n):
    """give the error vector given vector v and len l"""
    if norm(v) == 0: return v*0
    return  v - (v/norm(v) * n)

def error_vectors(f1, f2, f3):
    n = (norm(f1) + norm(f2) + norm(f3))/3
    return ev(f1, n), ev(f2, n), ev(f3, n)

fig = plt.figure(1)
plt.axis([-10, 20, -10, 10])
ax = fig.add_subplot(1,1,1)
c1 = plt.Circle((C1[0], C1[1]), r1)
c2 = plt.Circle((C2[0], C2[1]), r2)
c3 = plt.Circle((C3[0], C3[1]), r3)
ax.add_patch(c1)
ax.add_patch(c2)
ax.add_patch(c3)

p = plt.Circle(P, r, fill=False, color="%f"%(0/26.0))
ax.add_patch(p)

for i in range(1000):
    f1 = pull(C1, r1, P)
    f2 = pull(C2, r2, P)
    f3 = pull(C3, r3, P)

    ef1, ef2, ef3 = error_vectors(f1, f2, f3)
    P = P + (ef1 + ef2 + ef3)/3
    r = (norm(f1) + norm(f2) + norm(f3))/3
    e = (norm(ef1) + norm(ef2) + norm(ef3))
    #print i, norm(ef1), norm(ef2), norm(ef3), P, e
    p = plt.Circle(P, r, fill=False, color=(i/25.0, 0, 0))
    ax.add_patch(p)
    if e < 0.01: break
    continue

print P, r

plt.show()
