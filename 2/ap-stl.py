import numpy as np
from numpy import array, dot, matrix, ravel, arange, mgrid
from numpy.linalg import norm, det
from collections import namedtuple
from stl import mesh, Dimension
from math import ceil, sqrt
import sys

BB = namedtuple('BoundingBox', "minx miny minz maxx maxy maxz")
START_EPSILON = .5
END_EPSILON = .5

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
    def update_all(self, others):
        if self.radius and self.radius <= 0: return
        for other in others:
            distance = norm(self.center - other.center) - other.radius
            if self.radius == None or self.radius > distance:
                self.radius = distance
                if self.radius <= 0: break;
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

def bounding_box_epsilon(point, epsilon):
    minx = point[0] - epsilon
    miny = point[1] - epsilon
    minz = point[2] - epsilon
    maxx = point[0] + epsilon
    maxy = point[1] + epsilon
    maxz = point[2] + epsilon
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
    #print("creating {} points".format((bb.maxx-bb.minx) * (bb.maxy-bb.miny) * (bb.maxz-bb.minz)/(epsilon**3)), file=sys.stderr)
    for x in arange(bb.minx, bb.maxx, epsilon):
        for y in arange(bb.miny, bb.maxy, epsilon):
            for z in arange(bb.minz, bb.maxz, epsilon):
                cloud.append(Sphere(array([x,y,z]), None))
    return cloud

def initialize_candidates(candidates, winners): # -> None
    for candidate in candidates:
        candidate.update_all(winners)
    ## TODO this now only works for convex shapes

print("$fs=.01;")
print("$fa=10;")

print("Importing solid", file=sys.stderr)
#obj = mesh.Mesh.from_file('/home/yuri/repo/3d-models/stl/theepot_deksel2_smooth.stl')
obj = mesh.Mesh.from_file('cube.stl')
#obj = mesh.Mesh.from_file('sphere.stl')
#obj = mesh.Mesh.from_file('trapeziod.stl')
print("Calculating BB", file=sys.stderr)
bb = bounding_box(obj)
print(bb, file=sys.stderr)
print("Calculating Bounding Spheres", file=sys.stderr)
bounding_spheres = obj2boundingspheres(obj, bb, END_EPSILON)
winner_spheres = []

epsilon = START_EPSILON
while epsilon >= END_EPSILON:
    print("Generating Candidates", file=sys.stderr)
    candidate_spheres = obj2spherecloud(obj, bb, epsilon)
    print("Initializing Candidates", file=sys.stderr)
    initialize_candidates(candidate_spheres, bounding_spheres)
    initialize_candidates(candidate_spheres, winner_spheres)
    print("Sorting Candidates", file=sys.stderr)
    candidate_spheres.sort(reverse = True)
    print("running...", file=sys.stderr)
    while candidate_spheres:
        winner = candidate_spheres.pop(0)
        if winner.radius < epsilon: break

        ## Don't stop move it baby. Wiggle! Wiggle!
        e = epsilon
        while e >= END_EPSILON:
            bb_winner_center = bounding_box_epsilon(winner.center, e)
            candidate_winners = obj2spherecloud(obj, bb_winner_center, e/4)
            initialize_candidates(candidate_winners, bounding_spheres)
            initialize_candidates(candidate_winners, winner_spheres)
            winner = max(candidate_winners)
            e /= 2
        ## Don't stop move it baby. Wiggle! Wiggle!

        winner_spheres.append(winner)
        update_spheres(candidate_spheres, winner)
        print(winner)
    epsilon /= 2

scad = "\n".join([str(sphere) for sphere in winner_spheres])
#print(scad)
#for bbs in bounding_spheres:
    #print(bbs)
#print("winners")
#for bbs in winner_spheres:
    #print(bbs)
