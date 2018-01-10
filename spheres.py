import math
import numpy as np
from stl3d import line_triangle_intersection

class Sphere:

    def __init__(self, center, radius=math.inf, face=None, normal=None):
        self.center = center
        self.radius = radius
        self.face = face
        self.normal = normal
        self.bounding = face is not None
        self.dead = False

    def shrink(self, other, E):
        if other.bounding:
            #distance is min distance to vertices
            #if projection in polygon consider it as well.
            dd = [np.linalg.norm(self.center - v) for v in other.face]

            line = [self.center, self.center+other.normal]
            triangle = other.face
            normal = other.normal
            P, in_triangle, on_edge =  line_triangle_intersection(line, triangle, normal)
            if in_triangle:
                dd.append(np.linalg.norm(self.center - P))
            else:
                #calculate the distance to the line segments instead
                pass
            distance = min(dd)
        else:
            distance = np.linalg.norm(self.center - other.center) - other.radius
        if distance >= self.radius: return
        if distance < E/2:
            #print(other.center[0])
            self.dead = True
        elif self.radius > distance:
            self.radius = distance

    def bb(self):
        if not self.bounding:
            smin = self.center - self.radius
            smax = self.center + self.radius
        else:
            smin = np.min(self.face, 0)
            smax = np.max(self.face, 0)
        return smin, smax

    def __repr__(self):
        return "{SPHERE: " + str((self.center, self.radius, self.face, self.dead)) +"}"

    def __lt__(self, other):
        if self.dead:
            return True
        elif other.dead:
            return False
        else:
            return self.radius < other.radius
