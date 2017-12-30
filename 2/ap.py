from numpy import array, dot, matrix, ravel, arange, mgrid, vstack, hstack
from numpy.linalg import norm, det
from math import ceil
from collections import defaultdict

EPSILON = .05
DIM = 2
RADIUS_EXTRA = EPSILON/2
DIFFERENCE = False
#triangle
vertices = [array([0,0]), array([10,0]), array([0, 10])]
faces = [(0, 1), (1, 2), (2, 0)] #right hand rule
#boomrang
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
            if det(M) < 0:
                colin =  (c.p[0]*(p0[1]-p1[1]) + p0[0]*(p1[1]-c.p[1]) + p1[0]*(c.p[1]-p1[1]) == 0)
                if not colin:
                    continue
                #if not colin:
            #if det(M) < 0 and det(M) < -EPSILON:
                #print(det(M))
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

def ceilr(x, epsilon):
    return ceil(x/epsilon) * epsilon
def floorr(x, epsilon):
    return (x//epsilon) * epsilon

def yrange(start, end, epsilon):
    if start < end:
        s = ceilr(start, epsilon)
        if s == end: return [s]
        return mgrid[s:end:epsilon]
    elif start > end:
        s = floorr(start, epsilon)
        if s == end: return [s]
        return mgrid[s:end:-epsilon]
    else: ## == 
        if (start % epsilon) == 0: return [start]
        return []

def intersections(p0, p1, epsilon):
    ## these are the Y coords of all intersections
    r = yrange(p0[1], p1[1], epsilon)

    if p0[0] == p1[0]:
        #print("case 1")
        p = [array([p0[0], y]) for y in r]
    else:
        d = (p1[1] - p0[1]) / (p1[0] - p0[0])
        if d == 0:
            #print("case 2a")
            p = [array([p0[0], y]) for y in r]
        else:
            #print("case 2b", d, r)
            p = [array([(y - p0[1])/d + p0[0], y]) for y in r]
    return p

def face2sphere(face):
    p0 = vertices[face[0]]
    p1 = vertices[face[1]]
    p2 = find_3rth(p0, p1, EPSILON/1000)
    C = find_inscribed(p0, p1, p2)
    return C, p0, p1

#######################
def line_intersect(l1, l2):
    ## tuple of arrays per line
    (x1, y1), (x2, y2) = edge2line(l1)
    (x3, y3), (x4, y4) = edge2line(l2)
    denominator = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if denominator == 0:
        return False
    Px = ((x1*y2-y1*x2)*(x3-x4) - (x1-x2)*(x3*y4-y3*x4)) / denominator
    Py = ((x1*y2-y1*x2)*(y3-y4) - (y1-y2)*(x3*y4-y3*x4)) / denominator
    if Px <= min(x1, x2) or Px >= max(x1, x2): return False
    if Py <= min(y1, y2) or Py >= max(y1, y2): return False
    print("INTSCT AT", Px, Py)
    return True

def pair_permute(some_list):
    l = some_list[:]
    p = []
    while l:
        s = l.pop(0)
        p += [(s, e) for e in l]
    return p

def close_triangle(pair):
    p1, p2 = pair
    if p1[0] == p2[0] or p1[1] == p2[1]:
        return None
    if p1[0] == p2[1]:
        return p1[1], p2[0]
    else:
        return p2[1], p1[0]

def edge2line(edge):
    return [vertices[int(p)] for p in edge]

## find triangles
# for every point find all faces
points = defaultdict(list)
for face in faces:
    for P in face:
        points[P].append(face)

#print(points)
#print()

# loop over all vertices
for vertex in points.keys():
    edges = points[vertex]
    # loop over every pair of edges
    for pair in pair_permute(edges):
        # construct candidate edge OR CHECK EXISTENCE
        e = close_triangle(pair)
        if e == None: continue
        print(pair, e)
        if e[0] == e[1]: continue
        #er = e[1], e[0]
        #if e in faces or er in faces:
        if e in faces:
            continue
        #l1 = edge2line(e)
        available = True
        for face in faces:
            # if face has start of end in common with e, skip
            if any([p in e for p in face]): continue
            isect = line_intersect(e, face)
            if isect == False: continue
            available = False
            break
        if available:
            points[e[0]].append(e)
            points[e[1]].append(e)
            #points[e[0]].append(er)
            #points[e[1]].append(er)
            faces.append(e)
            #faces.append(er)
print(points)
## now find all triangles
#PROBLEM: in our croissant shape the points might be connected in the
#wrong direction.
# also doesn't cope with holes 


#ints = {}
#for face in faces:
    #p0 = vertices[face[0]]
    #p1 = vertices[face[1]]
    #i = intersections(p0, p1, EPSILON)
    #for p in i:
        #x,y = p
        #y = int(y/EPSILON)
        #if y in ints:
            #ints[y] += [x]
        #else:
            #ints[y] = [x]

##print(ints)

#print("$fs=.01;")
#print("$fa=10;")
#if not DIFFERENCE:
    #print("//", end="")
#print("difference()\n{")
#a = "linear_extrude({}) polygon(points = [".format(EPSILON/2) + ",".join(["[{},{}]".format(x, y) for x,y in vertices]) + "]);"
#print(a)

#initial_spheres = [face2sphere(face) for face in faces]

#for U, p0, p1 in initial_spheres:
    #print("//", end="")
    #U.export()

#BB = boundingbox(vertices)
#init = []
#for y, val in ints.items():
    #if len(val)%2: continue
    #val.sort()
    ##print("y", y, "val", val)
    #inside = False
    #x = BB[0][0]
    ##x = val[0]
    #while len(val):
        #if x >= val[0]:
            #val.pop(0)
            #inside = not inside
        #if inside:
            ###print(x, end=", ")
            #c = Circle(array([x, y*EPSILON]), None)
            #c.update_radius_init(initial_spheres)
            #if c.r > 0:
                #init.append(c)
        #x += EPSILON
    ##print("")
##print(init)

#cand = list(init)
#cand.sort(reverse=True)
#while len(cand) > 0:
    #w = cand.pop(0)
    #if w.r < EPSILON: break
    #for i, c in enumerate(cand):
        #if c.r <= 0: break
        #c.update_radius([w])
    #cand = cand[:i]
    #cand.sort(reverse=True)
    #w.export()

#print("} //difference()")
