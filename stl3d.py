"""
    Given an STL file generate all points in the volume
"""

import stl, sys, random
import numpy as np
from collections import namedtuple, defaultdict

""" Axis along te test for intersections """
AXIS = stl.Dimension.X

def intersection_line(point):
    """ given point p return line through p in dim AXIS """
    a = np.zeros(3)
    a[AXIS] = 1
    return point, point+a

def line_plane_parallel(line, plane_normal):
    """ True if plane and line never intersect """
    p0, p1 = line
    return np.dot(plane_normal, p1-p0) == 0

def line_triangle_intersection(line, triangle, normal):
    """ line and a triangle on an intersecting plane return intersection
        point on plane p and bool in_triangle if line intersects triangle
    """
    v0, v1, v2 = triangle
    p0, p1 = line
    n = normal / np.linalg.norm(normal)

    u = v1-v0
    v = v2-v0
    d = p1-p0
    w = p0 - v0 - d * np.dot(n, p0-v0) / np.dot(n, d)
    
    uv = np.dot(u, v)
    vv = np.dot(v, v)
    wv = np.dot(w, v)
    wu = np.dot(w, u)
    uu = np.dot(u, u)

    denominator = uv**2 - uu*vv
    s = (uv*wv - vv*wu) / denominator
    t = (uv*wu - uu*wv) / denominator

    in_triangle = ((s >= 0) and (t >= 0) and (s+t <= 1))
    on_edge = s==0 or t == 0 or s+t == 1
    p = v0 + s*u + t*v
    return p, in_triangle, on_edge

def bb(vertices):
    f_min = np.min(vertices, 0)
    f_max = np.max(vertices, 0)
    return f_min, f_max

def face_to_triangle(face):
    return face[:, 1:]

def erange(start, end, E):
    """ produce range from start to end with steps of E or -E
        start and end included iff exacttly on E
    """
    if start > end:
        start, end = end, start
    E = abs(E)
    N = start//E
    if start % E: N += 1
    while N*E <= end:
        yield N
        N += 1

def triangle_to_edges(triangle):
    for i, p0 in enumerate(triangle):
        p1 = triangle[(i+1)%3]
        yield p0, p1

def intersect_linesegment(p1, p2, y):
    """Given line defined by points p1, p2 find x of given y"""
    (x1, y1), (x2, y2) = p1, p2
    x = ((x1-x2)*(y) - (x1*y2-y1*x2)) / (y1-y2)
    return x

def discretize_triangle(triangle, E):
    slices = defaultdict(set)
    for edge in triangle_to_edges(triangle):
        p0, p1 = edge
        if p0[stl.Dimension.Y] == p1[stl.Dimension.Y]:
            continue
        Y = erange(p0[stl.Dimension.Y], p1[stl.Dimension.Y], E)
        for y in Y:
            x = intersect_linesegment(p0, p1, y*E)
            slices[y].add(x)
    for y, ex in slices.items():
        if len(ex) != 2: continue
        x0, x1 = ex
        X = erange(x0, x1, E)
        for x in X:
            yield x,y

def ranges(intersections):
    # two adjecent intersections with normal in same direction are merged
    # two adjecant intersections with opposite normals are removed
    # must start with left normal
    # must and with right normal
    #normal must flip
    s = []
    for i in intersections:
        out = i.normal[AXIS] < 0
        if not s:
            if out: s.append(i)
            continue
        sout = s[-1].normal[AXIS] < 0
        if s[-1].point[AXIS] == i.point[AXIS]:
            if out != sout:
                s.pop()
            continue
        else:
            if out != sout:
                s.append(i)
    if not s:
        return []
    if (s[-1].normal[AXIS] < 0):
        s.pop()
    starts = [item.point[AXIS] for i, item in enumerate(s) if not i%2]
    ends = [item.point[AXIS] for i, item in enumerate(s) if i%2]
    return zip(starts, ends)

class Solid:

    def __init__(self, stl_path, reduce_vertices = False):
        self.mesh = stl.mesh.Mesh.from_file(stl_path)
        print("Solid {} had {} faces".format(stl_path, len(self.mesh.data)))
        if reduce_vertices:
            self.mesh = self.reduce(reduce_vertices)
            print("Solid {} had {} faces".format(stl_path, len(self.mesh.data)))
        self.min = np.min(np.min(self.mesh.vectors, 0), 0)
        self.max = np.max(np.max(self.mesh.vectors, 0), 0)
        ##every face must have bounding box, then generete octree
        self.boxes = [bb(vertices) for vertices in self.mesh.vectors]

    def mass(self):
        return self.mesh.get_mass_properties()[0]

    def boundingbox(self):
        return self.min, self.max

    def inside_bounding_box(self, point):
        return all(point >= self.min) and all(point <= self.max)

    def find_intersections(self, line):
        ## optimization idea: early on delete all parallel planes
        p0, p1 = line
        Intersection = namedtuple("Intersection", "point, normal, on_edge")
        intersections = []
        for (normal, vertices, _), box in zip(self.mesh.data, self.boxes):
            if any((p0 < box[0])[1:]) and any((p0 > box[1])[1:]):
                continue

            if line_plane_parallel(line, normal):
                continue
            p, in_triangle, on_edge = line_triangle_intersection(line, vertices, normal)
            if not in_triangle:
                continue
            intersections.append(Intersection(p, normal, on_edge))
        return intersections


    def point_inside(self, point):
        if not self.inside_bounding_box(point): return False
        ## define intersection line
        line = intersection_line(point)

        intersections = self.find_intersections(line)
        intersections = [i for i in intersections if i.point[AXIS] <= point[AXIS]]
        intersections.sort(key = lambda i: i.point[AXIS])

        while intersections:
            i = intersections.pop()
            if intersections and intersections[-1].point[AXIS] == i.point[AXIS]:
                if intersections[-1].normal[AXIS] * i.normal[AXIS] < 0:
                    ## conflicting, ignore
                    _ = intersections.pop()
                    continue
            return i.normal[AXIS] < 0
        return False

    def range_on_line(self, line):
        intersections = self.find_intersections(line)
        intersections.sort(key = lambda i: i.point[AXIS])
        return ranges(intersections)


    def discretize(self, E):
        """ discretize solid. returns list of points. """
        Intersection = namedtuple("Intersection", "point, normal, on_edge")
        #For every face generate intersections
        slices = defaultdict(list)
        for normal, face, _ in self.mesh.data:
            if normal[AXIS] == 0:
                continue
            triangle = face_to_triangle(face)
            points2D = discretize_triangle(triangle, E) ## in 2D plane
            for y,z in points2D:
                line = intersection_line(np.array([0, y*E, z*E]))
                p, in_triangle, on_edge = line_triangle_intersection(line, face, normal)
                ## might indicate p is not in triangle. However it must be
                ## likely rounding errors
                slices[(y, z)].append(Intersection(p, normal, on_edge))
        for (y, z), I in slices.items():
            I.sort(key = lambda i: i.point[AXIS])
            R = ranges(I)
            R = ranges(I)
            for x0, x1 in R:
                X = erange(x0, x1, E)
                for x in X:
                    yield np.array([x*E, y*E, z*E])

    def discretize_linear(self, E):
        """ discretize solid. returns list of points. """
        #z = 0
        for y in np.arange(self.min[stl.Dimension.Y], self.max[stl.Dimension.Y], E):
            for z in np.arange(self.min[stl.Dimension.Z], self.max[stl.Dimension.Z], E):
                point = np.array([0, y, z])
                line = intersection_line(point)
                ranges = self.range_on_line(line)
                for s,e in ranges:
                    for x in np.arange(s, e+E, E):
                        point = np.array([x, y, z])
                        yield point

    def discretize_naive(self, E):
        """ discretize solid. returns list of points. **SLOW** """
        ## totaly naive approach
        for y in np.arange(self.min[stl.Dimension.Y], self.max[stl.Dimension.Y], E):
            for z in np.arange(self.min[stl.Dimension.Z], self.max[stl.Dimension.Z], E):
                for x in np.arange(self.min[stl.Dimension.X], self.max[stl.Dimension.X], E):
                    point = np.array([x, y, z])
                    if self.point_inside(point):
                        yield point



    def reduce(self, n):
        def sort_by_dull(vertices):
            norms = []
            for v, indices in vertices.items():
                normals = [self.mesh.normals[index] for index in indices]
                n = np.linalg.norm(np.sum(normals, 0)) / (len(normals)-1)
                norms.append((v, n))
            norms.sort(reverse=True, key=lambda x: x[1])
            return [v for v, n in  norms]

        #NOTE: recalculate dullness
        #NOTE: if two triangles share 3 vertices delete both
        #NOTE if 2 triangles connected have opposite norm. collapse

        mesh = self.mesh
        original = len(mesh)
        removed = 0
        vertices = defaultdict(list)
        # dict of faces for every vertex
        for i, vectors in enumerate(mesh.vectors):
            #normal, vectors, _ = data
            for vector in vectors:
                vertices[tuple(vector)].append(i)
        v_sort = sort_by_dull(vertices)
        ## step find the most dull points
        mask = set()
        ## now starting from dullest point remove
        for vr in v_sort:
        #for vr, face_indexes in vertices.items():
            face_indexes = vertices[vr]
            if not face_indexes: continue
            if n >= original - removed: break
            #for index in face_indexes:
                #if index in mask: continue
                #vc = None
            for v in mesh.vectors[face_indexes[0]]:
            #for v in mesh.vectors[index]:
                if all(v==vr): continue
                vc = v
                break
                #if vc is not None: break
            else:
                assert()
                    
            #vr is vector to remove
            #vc is vector to collapse to
            rem = []
            for face_index in face_indexes:
                if face_index in mask:
                    #print(face_index, "already deleted")
                    continue
                a, b = -1, -1
                #print("deleting:", vr, "from face", face_index)
                for i, v in enumerate(mesh.vectors[face_index]):
                    if all(v==vr):
                        a = i
                        continue
                    if all(v==vc):
                        b = i
                        continue
                if a == -1:
                    panick
                if b == -1:
                    #print("collapse it")
                    #collapse
                    face = mesh.vectors[face_index]
                    mesh.vectors[face_index][a] = vc
                    #mesh.vectors[face_index][a] = np.array([0, 0, 0])
                    #vertices[tuple(vr)].remove(face_index)
                    rem.append(face_index)
                    vertices[tuple(vc)].append(face_index)
                else:
                    #print("remove it")
                    removed += 1
                    mask.add(face_index)
                    for v in mesh.vectors[face_index]:
                        if all(v == vr):
                            rem.append(face_index)
                        else:
                            vertices[tuple(v)].remove(face_index)
            #print(vr, rem, )
            for face_index in rem:
                vertices[tuple(vr)].remove(face_index)
        data = np.delete(mesh.data, list(mask), 0)
        print(removed, len(data))
        mesh = stl.mesh.Mesh(data)
        return mesh
