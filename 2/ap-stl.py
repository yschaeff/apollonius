import numpy as np
from numpy import array, dot, matrix, ravel, arange, mgrid
from numpy.linalg import norm, det
from collections import namedtuple
from stl import mesh, Dimension
from math import ceil, sqrt

BB = namedtuple('BoundingBox', "minx miny minz maxx maxy maxz")
EPSILON = .5

class Sphere:
    def __init__(self, center, radius = None):
        self.center = center
        self.radius = radius
    def valid(self):
        return self.radius > 0
    def update(self, other):
        distance = norm(self.center - other.center) - other.radius
        if self.radius == None or self.radius > distance:
            self.radius = distance
    def __repr__(self):
        return "translate([%f, %f, %f]) sphere(r=%f);" % (*self.center, self.radius)
    def __lt__(self, other):
        return self.radius < other.radius

def bounding_box(obj):
    minx = min([min([vector[Dimension.X] for vector in face]) for face in obj.vectors])
    miny = min([min([vector[Dimension.Y] for vector in face]) for face in obj.vectors])
    minz = min([min([vector[Dimension.Z] for vector in face]) for face in obj.vectors])
    maxx = max([max([vector[Dimension.X] for vector in face]) for face in obj.vectors])
    maxy = max([max([vector[Dimension.Y] for vector in face]) for face in obj.vectors])
    maxz = max([max([vector[Dimension.Z] for vector in face]) for face in obj.vectors])
    return BB(minx, miny, minz, maxx, maxy, maxz)

def update_spheres(candidates, winner):
    [candidate.update(winner) for candidate in candidates]
    candidate_spheres.sort(reverse = True)
    # Remove all impossible candidates
    while candidate_spheres:
        if candidate_spheres[0].valid(): break
        candidate_spheres.pop(0)

def coefficients(Tin, tv, i):
    S = Tin.copy()
    S[:,i] = tv
    return det(S)

def face2sphere(face, normal, epsilon):
    ## from: http://www.ambrsoft.com/TrigoCalc/Sphere/Spher3D_.htm
    v_epsilon = (normal/norm(normal)) * epsilon
    vector4 = sum(face)/3 - v_epsilon
    vectors = np.vstack([face, vector4])
    tv =  [-sum(vector**2) for vector in vectors]
    Tin = np.hstack([vectors, np.ones([4, 1])])
    T = det(Tin)
    D, E, F, G = [coefficients(Tin, tv, i)/T for i in range(4)]
    x, y, z, r = -D/2, -E/2, -F/2, sqrt(D**2+E**2+F**2-4*G)/2
    return Sphere(array([x, y, z]), r)

def obj2boundingspheres(obj, bb, epsilon): # -> list of spheres
    faces = zip(obj.vectors, obj.normals)
    return [face2sphere(face, normal, epsilon) for face, normal in faces]

def obj2spherecloud(obj, bb, epsilon): # -> list of spheres
    # naive: bb, enly works because solid== BB
    cloud = []
    print("creating {} points".format((bb.maxx-bb.minx) * (bb.maxy-bb.miny) * (bb.maxz-bb.minz)/(epsilon**3)))
    for x in arange(bb.minx, bb.maxx, epsilon):
        for y in arange(bb.miny, bb.maxy, epsilon):
            for z in arange(bb.minz, bb.maxz, epsilon):
                cloud.append(Sphere(array([x,y,z]), None))
    return cloud

def initialize_candidates(candidates, winners): # -> None
    for i, candidate in enumerate(candidates):
        [candidate.update(winner) for winner in winners]
        #print(i)
    ## TODO this now only works for convex shapes

print("Importing solid")
obj = mesh.Mesh.from_file('cube.stl')
print("Calculating BB")
bb = bounding_box(obj)
print("Calculating Bounding Spheres")
bounding_spheres = obj2boundingspheres(obj, bb, EPSILON)
print("Generating Candidates")
candidate_spheres = obj2spherecloud(obj, bb, EPSILON)
print("Initializing Candidates")
initialize_candidates(candidate_spheres, bounding_spheres)
print("Sorting Candidates")
candidate_spheres.sort(reverse = True)
winner_spheres = []
print("running...")
while candidate_spheres:
    winner = candidate_spheres.pop(0)
    if winner.radius < EPSILON: break
    winner_spheres.append(winner)
    update_spheres(candidate_spheres, winner)
    print(winner)

scad = "\n".join([str(sphere) for sphere in winner_spheres])
#print(scad)
#for bbs in bounding_spheres:
    #print(bbs)
#print("winners")
#for bbs in winner_spheres:
    #print(bbs)
