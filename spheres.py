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

    def shrink(self, others):
        for other in others:
            if self.dead: return
            if other.bounding():
                Tin = np.vstack([other.face, self.center])
                Tin = np.hstack([Tin, np.ones([4, 1])])
                if np.linalg.det(Tin) < 0: continue
            distance = np.linalg.norm(self.center - other.center) - other.radius
            if distance <= 0:
                self.dead = True
                break
            if self.radius > distance:
                self.radius = distance

    def __repr__(self):
        return "{SPHERE: " + str((self.center, self.radius, self.face, self.dead)) +"}"

    def __lt__(self, other):
        if self.dead: return True
        return self.radius < other.radius
