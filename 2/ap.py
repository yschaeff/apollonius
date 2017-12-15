from numpy import array, dot, matrix, ravel, arange
from numpy.linalg import norm

class Circle:
    def __init__(self, p, r):
        self.p = p
        self.r = r

    def __lt__(self, c):
        return self.r < c.r

    def update_radius(self, C):
        for c in C:
            if self.r and self.r < 0: break
            #self.r = norm(self.p - c.p) - c.r
            r = norm(self.p - c.p) - c.r
            if  self.r == None or r < self.r:
                self.r = r

    def export(self):
        print("translate([%f, %f, %f]) sphere(r=%f);"%(self.p[0], self.p[1], 0, self.r+EPSILON/2))

    def __repr__(self):
        return "({}, {})".format(self.p, self.r)

def find_3rth(v1, v2, epsilon):
    a = v2-v1
    l = norm(a)
    R = matrix([[0, 1], [-1, 0]])
    b = ravel(a*R)
    return (b/norm(b))*epsilon + v1 + a/2

def find_inscribed(A, B, C):
    BB = B-A
    CC = C-A

    DD = 2*(BB[0]*CC[1] - BB[1]*CC[0])
    x = (CC[1]*(BB[0]**2 + BB[1]**2) - BB[1]*(CC[0]**2 + CC[1]**2)) / DD
    y = (BB[0]*(CC[0]**2 + CC[1]**2) - CC[0]*(BB[0]**2 + BB[1]**2)) / DD

    UU = array([x, y])
    U = UU + A
    r = norm(UU)
    return Circle(U, r)

def boundingbox(vertices):
    BB = [[v[i] for v in vertices] for i in range(DIM)]
    BB = [(min(c), max(c)) for c in BB]
    return BB

EPSILON = .01
DIM = 2
vertices = [array([0,0]), array([10,0]), array([0, 10])]
faces = [(0, 1), (1, 2), (2, 0)] #right hand rule

initial_spheres = []

for face in faces:
    p0 = vertices[face[0]]
    p1 = vertices[face[1]]
    p2 = find_3rth(p0, p1, EPSILON)
    C = find_inscribed(p0, p1, p2)
    initial_spheres.append(C)

cand = []
BB = boundingbox(vertices)
for x in arange(BB[0][0], BB[0][1], EPSILON):
    for y in arange(BB[1][0], BB[1][1], EPSILON):
        cand.append(Circle(array([x, y]), None))

print("$fs=.1;")
print("$fa=1;")

[c.update_radius(initial_spheres) for c in cand]
cand.sort(reverse=True)
while len(cand) > 0:
    w = cand.pop(0)
    if w.r < EPSILON: break
    for i, c in enumerate(cand):
        if c.r <= 0: break
        c.update_radius([w])
    cand = cand[:i]
    cand.sort(reverse=True)
    w.export()

