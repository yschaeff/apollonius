from numpy import array, dot, matrix, ravel, arange
from numpy.linalg import norm

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
    return U, r

def boundingbox(vertices):
    BB = [[v[i] for v in vertices] for i in range(DIM)]
    BB = [(min(c), max(c)) for c in BB]
    return BB

def inside(p, U):
    return norm(U[0]-p) <= U[1]

def inside_any(p, Us):
    return any(map(lambda U: inside(p, U), Us))

def distance(p, U):
    return norm(U[0]-p) - U[1]

def min_distance(p, Us):
    return min(map(lambda U: distance(p, U), Us))

def export(U):
    c = U[0]
    x, y = c
    r = U[1]
    print("translate([%f, %f, %f]) sphere(r=%f);"%(x, y, 0, r+EPSILON/2))

EPSILON = .1
DIM = 2
vertices = [array([0,0]), array([10,0]), array([0, 10])]
faces = [(0, 1), (1, 2), (2, 0)] #right hand rule

BB = boundingbox(vertices)
obj = []
initial_spheres = []

for face in faces:
    p0 = vertices[face[0]]
    p1 = vertices[face[1]]
    p2 = find_3rth(p0, p1, EPSILON)
    C = find_inscribed(p0, p1, p2)
    initial_spheres.append(C)

cand = []
for x in arange(BB[0][0], BB[0][1], EPSILON):
    for y in arange(BB[1][0], BB[1][1], EPSILON):
        cand.append(array([x, y]))

print("$fs=.1;")
print("$fa=1;")

cand = list(filter(lambda p: not inside_any(p, initial_spheres), cand))
obj.extend(initial_spheres)
while cand:
    d = list(map(lambda p: (p, min_distance(p, obj)), cand))
    new_obj = max(d, key=lambda x: x[1])
    if new_obj[1] < EPSILON: break
    ### optionally wiggle winner until touching 3 winners within e
    cand = list(filter(lambda p: not inside_any(p, [new_obj]), cand))
    obj.append(new_obj)
    export(new_obj)

