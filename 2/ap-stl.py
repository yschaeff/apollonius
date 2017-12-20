from numpy import array, dot, matrix, ravel, arange, mgrid
from numpy.linalg import norm, det
from collections import namedtuple
from stl import mesh, Dimension
from math import ceil

BB = namedtuple('BoundingBox', "minx miny minz maxx maxy maxz")

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
    # Remove all inpossible candidates
    while candidate_spheres:
        if candidate_spheres[0].valid(): break
        candidate_spheres.pop(0)

def obj2boundingspheres(obj, bb): # -> list of spheres
    #TODO
    return []

def obj2spherecloud(obj, bb): # -> list of spheres
    return []

def initialize_candidates(candidates, winners): # -> None
    pass

obj = mesh.Mesh.from_file('cube.stl')
bb = bounding_box(obj)
bounding_spheres = obj2boundingspheres(obj, bb)
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

