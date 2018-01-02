import math
import numpy as np

class Sphere:

    def __init__(self, center, radius=math.inf, face=None):
        self.center = center
        self.radius = radius
        self.face = face
        self.bounding = face is not None
        self.dead = False

    def shrink(self, other, E):
        distance = np.linalg.norm(self.center - other.center) - other.radius
        if distance >= self.radius: return
        if other.bounding:
            Tin = np.vstack([other.face, self.center])
            Tin = np.hstack([Tin, np.ones([4, 1])])
            dTin = np.linalg.det(Tin)
            if dTin < -0.001: #consider very tiny determinant as on the line
            #if dTin < 0:
                return
        if distance < E/2:
            self.dead = True
        elif self.radius > distance:
            self.radius = distance

    def __repr__(self):
        return "{SPHERE: " + str((self.center, self.radius, self.face, self.dead)) +"}"

    def __lt__(self, other):
        if self.dead:
            return True
        elif other.dead:
            return False
        else:
            return self.radius < other.radius
