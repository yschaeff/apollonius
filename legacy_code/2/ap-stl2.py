import numpy as np
from numpy import array, dot, matrix, ravel, arange, mgrid, vstack, hstack
from numpy.linalg import norm, det
from math import ceil
from collections import defaultdict, namedtuple
import sys

#def BB(v): return np.min(v, 0), np.max(v, 0)
def discrete_line_y(p1, p2, epsilon):
    miny = np.min(np.vstack([p1, p2]), 0)[1]
    maxy = np.max(np.vstack([p1, p2]), 0)[1]
    s = (miny//epsilon)*epsilon
    if s<miny: s+=epsilon
    e = (maxy//epsilon + 1)*epsilon
    return np.arange(s, e, epsilon)

def discrete_line_x(x1, x2, epsilon):
    s = (x1//epsilon)*epsilon
    if s<x1: s+=epsilon
    e = (x2//epsilon + 1)*epsilon
    return np.arange(s, e, epsilon)

def find_x(p1, p2, y):
    """Given line defined by points p1, p2 find x of given y"""
    (x1, y1), (x2, y2) = p1, p2
    Px = ((x1-x2)*(y) - (x1*y2-y1*x2)) / (y1-y2)
    return Px, y

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
            #if CHECK_CONVEXITY and type(other) == BoundingSphere:
            #if type(other) == BoundingSphere:
                ### on wrong side of face?: skip
                #Tin = np.vstack([other.face, self.center])
                #Tin = np.hstack([Tin, np.ones([3, 1])])
                #T = det(Tin)
                #if T<0: continue
            distance = norm(self.center - other.center) - other.radius
            if self.radius == None or self.radius > distance:
                self.radius = distance
                if self.radius <= 0: break;
    def __repr__(self):
        #return "translate([%f, %f, 0]) sphere(r=%f, $fn=5);" % (*self.center, self.radius)
        return "translate([%f, %f, 0]) sphere(r=%f);" % (*self.center, self.radius)
    def __lt__(self, other):
        return self.radius < other.radius

class BoundingSphere(Sphere):
    def __init__(self, center, radius, face):
            Sphere.__init__(self, center, radius)
            self.face = face
    def __repr__(self):
        return "//" + Sphere.__repr__(self)

def find_3rth(v1, v2, epsilon):
    a = v2-v1
    l = norm(a)
    R = matrix([[0, 1], [-1, 0]])
    b = ravel(a*R)
    return (b/norm(b))*epsilon + v1 + a/2

def find_inscribed_2D(A, B, C):
    BB = B-A
    CC = C-A

    DD = 2*(BB[0]*CC[1] - BB[1]*CC[0])
    x = (CC[1]*(BB[0]**2 + BB[1]**2) - BB[1]*(CC[0]**2 + CC[1]**2)) / DD
    y = (BB[0]*(CC[0]**2 + CC[1]**2) - CC[0]*(BB[0]**2 + BB[1]**2)) / DD

    UU = array([x, y])
    U = UU + A
    r = norm(UU)
    return BoundingSphere(U, r, (A, B))

def face2sphere_2D(face, epsilon):
    p0 = vertices[face[0]]
    p1 = vertices[face[1]]
    p2 = find_3rth(p0, p1, epsilon)
    return find_inscribed_2D(p0, p1, p2)

def obj2boundingspheres_2D(faces, epsilon): # -> list of spheres
    return [face2sphere_2D(face, epsilon) for face in faces]


def initial_points(faces, epsilon):
    lines = []
    for face in faces:
        p1, p2 = [vertices[v] for v in face]
        p3 = p1 + array([1, 0])
        determinant = det(np.hstack([np.vstack([p1, p2, p3]), np.ones([3, 1])]))
        if not determinant: ##colineair
            continue
        ## find multiples of e in y
        Y = discrete_line_y(p1, p2, epsilon)
        intersections = [find_x(p1, p2, y) for y in Y]
        l = Line(p1, p2, determinant, intersections)
        lines.append(l)

    intersections = defaultdict(list)
    for line in lines:
        for x,y in line.intersections:
            intersections[int(y//epsilon)].append((x, line))
    #print(intersections)

    #points = []
    for y, lines in sorted(intersections.items()):
        lines.sort(key=lambda l: l[0])

        s = 0
        e = -1
        while s < len(lines):
            if lines[s][1].determinant < 0 or s <= e:
                s += 1
                continue
            e = s+1
            while e < len(lines) and lines[e][1].determinant > 0:
                e += 1
                continue
            if e >= len(lines):
                break
            X = discrete_line_x(lines[s][0], lines[e][0], epsilon)
            for x in X:
                yield Sphere(np.array([x, y*epsilon]), None)
            #points += [np.array([x, y*epsilon]) for x in X]
            #print(X)
            s = e+1

#RADIUS_EXTRA = 0
#triangle
vertices = [array([0,0]), array([10,0]), array([0, 10])]
faces = [(0, 1), (1, 2), (2, 0)] #right hand rule
#boomrang
#vertices = [array([0,0]), array([10,0]), array([2,2]), array([0, 10])]
##vertices = [array([0,0]), array([10,0]), array([2,-2]), array([0, -10])]
#faces = [(0, 1), (1, 2), (2, 3), (3, 0)] #right hand rule


Line = namedtuple("Line", "p1, p2, determinant, intersections")
#winners = [face2sphere(face) for face in faces]
##print(winners)
#cand = [Sphere(p, None) for p in points]
#for c in cand:
    #c.update_radius_init(winners)
#cand.sort(reverse=True)


#while len(cand) > 0:
    #w = cand.pop(0)
    #if w.r == None or w.r < EPSILON: break
    #for i, c in enumerate(cand):
        #if c.r <= 0: break
        #c.update_radius([w])
    #cand = cand[:i]
    #cand.sort(reverse=True)
    #winners.append(w)

#for w in winners:
    #print(w)

##print("} //difference()")


def initialize_candidates(candidates, winners): # -> None
    for candidate in candidates:
        candidate.update_all(winners)
    ## TODO this now only works for convex shapes

def update_spheres(candidates, winner):
    [candidate.update(winner) for candidate in candidates]
    candidate_spheres.sort(reverse = True)
    # Remove all impossible candidates
    while candidate_spheres:
        if candidate_spheres[0].valid(): break
        candidate_spheres.pop(0)


START_EPSILON = 1
END_EPSILON = .01
FACE_EPSILON = END_EPSILON /1000


print("$fs=.01;")
print("$fa=10;")

#obj = mesh.Mesh.from_file(obj_path)
#print("Calculating Bounding Spheres", file=sys.stderr)
winner_spheres = obj2boundingspheres_2D(faces, FACE_EPSILON)

epsilon = START_EPSILON
while epsilon >= END_EPSILON:
    candidate_spheres  = list(initial_points(faces, epsilon))
    initialize_candidates(candidate_spheres, winner_spheres)
    #print(candidate_spheres)
    candidate_spheres.sort(reverse = True)
    print("running... epsilon:", epsilon, file=sys.stderr)
    while candidate_spheres:
        winner = candidate_spheres.pop(0)
        if winner.radius < epsilon: break

        ### Don't stop move it baby. Wiggle! Wiggle!
        #e = epsilon
        #while e >= END_EPSILON:
            #bb_winner_center = bounding_box_epsilon(winner.center, e)
            #candidate_winners = obj2spherecloud(obj, bb_winner_center, e/4)
            #initialize_candidates(candidate_winners, winner_spheres)
            ### TODO eliminate candidates not in solid
            #winner = max(candidate_winners)
            #e /= 2
        ### Don't stop move it baby. Wiggle! Wiggle!

        winner_spheres.append(winner)
        update_spheres(candidate_spheres, winner)
        #print(winner)
    epsilon /= 2

scad = "\n".join([str(sphere) for sphere in winner_spheres])
print(scad)
