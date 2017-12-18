from numpy import array, dot, matrix, ravel, arange
from numpy.linalg import norm, det

EPSILON = 1
DIM = 2
RADIUS_EXTRA = EPSILON/2
DIFFERENCE = False
#triangle
#vertices = [array([0,0]), array([10,0]), array([0, 10])]
#faces = [(0, 1), (1, 2), (2, 0)] #right hand rule
#hook
vertices = [array([0,0]), array([10,0]), array([2,2]), array([0, 10])]
faces = [(0, 1), (1, 2), (2, 3), (3, 0)] #right hand rule

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

    def update_radius_init(self, C):
        for c, p0, p1 in C:
            if self.r and self.r < 0: break
            M = array([[p0[0], p0[1], 1], [p1[0], p1[1], 1], [self.p[0], self.p[1], 1]]).transpose()
            if det(M) < 0: continue
            r = norm(self.p - c.p) - c.r
            if  self.r == None or r < self.r:
                self.r = r

    def export(self):
        print("translate([%f, %f, %f]) sphere(r=%f);"%(self.p[0], self.p[1], 0, self.r+RADIUS_EXTRA))

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

def intersections(p0, p1, epsilon):
    p = p1-p0
    if p[0]:
        dydx = p[1]/p[0]
        if p[1] < 0:
            ys = arange(p[1], step=-epsilon)
        else:
            ys = arange(p[1], step=epsilon)
        return [array((y/dydx, y))+p0 for y in ys]
    else:
        if p[1] < 0:
            ys = arange(p[1], step=-epsilon)
        else:
            ys = arange(p[1], step=epsilon)
        return [array((0, y))+p0 for y in ys]

def initial_probes(BB, initial_spheres, epsilon):
    for x in arange(BB[0][0], BB[0][1], epsilon):
        for y in arange(BB[1][0], BB[1][1], epsilon):
            c = Circle(array([x, y]), None)
            c.update_radius_init(initial_spheres)
            if c.r <= 0: continue
            yield c

def face2sphere(face):
    p0 = vertices[face[0]]
    p1 = vertices[face[1]]
    p2 = find_3rth(p0, p1, EPSILON/1000)
    C = find_inscribed(p0, p1, p2)
    return C, p0, p1

for face in faces:
    p0 = vertices[face[0]]
    p1 = vertices[face[1]]
    i = intersections(p0, p1, EPSILON)
    print(p0, p1, p1-p0, i)

print("$fs=.1;")
print("$fa=1;")
if not DIFFERENCE:
    print("//", end="")
print("difference()\n{")
a = "linear_extrude({}) polygon(points = [".format(EPSILON/2) + ",".join(["[{},{}]".format(x, y) for x,y in vertices]) + "]);"
print(a)

initial_spheres = [face2sphere(face) for face in faces]

for U, p0, p1 in initial_spheres:
    U.export()

BB = boundingbox(vertices)
init = initial_probes(BB, initial_spheres, EPSILON)

cand = list(init)
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

print("} //difference()")
