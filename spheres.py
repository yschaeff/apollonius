import math
import numpy as np

class Sphere:

    def __init__(self, center, radius=math.inf, face=None):
        self.center = center
        self.radius = radius
        self.face = face
        self.dead = False

    def bounding(self):
        return self.face is not None

    def shrink_bounding(self, others):
        for other in others:
            distance = np.linalg.norm(self.center - other.center) - other.radius
            if distance >= self.radius: continue
            Tin = np.vstack([other.face, self.center])
            Tin = np.hstack([Tin, np.ones([4, 1])])
            if np.linalg.det(Tin) < 0: continue
            if distance <= 0:
                self.dead = True
                return
            elif self.radius > distance:
                self.radius = distance

    def shrink(self, other, E):
        if self.dead: return
        distance = np.linalg.norm(self.center - other.center) - other.radius
        if distance >= self.radius: return
        if distance < E/2:
            self.dead = True
            return
        if self.radius > distance:
            self.radius = distance

    def __repr__(self):
        return "{SPHERE: " + str((self.center, self.radius, self.face, self.dead)) +"}"

    def __lt__(self, other):
        if self.dead: return True
        return self.radius < other.radius
