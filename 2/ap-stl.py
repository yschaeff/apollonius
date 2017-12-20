import numpy as np
from numpy import array, dot, matrix, ravel, arange, mgrid
from numpy.linalg import norm, det
from collections import namedtuple
from stl import mesh, Dimension
from math import ceil, sqrt

BB = namedtuple('BoundingBox', "minx miny minz maxx maxy maxz")
EPSILON = 1

class Sphere:
    def __init__(self, center, radius = None):
        self.center = center
        self.radius = radius
    def valid(self):
        return self.radius > 0
    def update(self, other):
        distance = norm(self.center - other.center) - other,center
        if self.radius == None or self.radius > distance:
            self.radius = distance


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

def obj2spherecloud(obj, bb): # -> list of spheres
    return []

def initialize_candidates(candidates, winners): # -> None
    pass

obj = mesh.Mesh.from_file('cube.stl')
bb = bounding_box(obj)
bounding_spheres = obj2boundingspheres(obj, bb, EPSILON)
candidate_spheres = obj2spherecloud(obj, bb)
initialize_candidates(candidate_spheres, bounding_spheres)
candidate_spheres.sort(reverse = True)
winner_spheres = []
while candidate_spheres:
    winner = candidate_spheres.pop(0)
    if winner.radius < ESPILON: break
    spheres.append(winner)
    update_spheres(candidate_spheres, winner)

scad = "\n".join([str(sphere) for sphere in winner_spheres])
print(scad)

