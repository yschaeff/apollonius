import numpy as np
import math
import spheres

def coefficients(Tin, tv, i):
    S = Tin.copy()
    S[:,i] = tv
    return np.linalg.det(S)

def face2sphere(face, normal, epsilon):
    ## from: http://www.ambrsoft.com/TrigoCalc/Sphere/Spher3D_.htm
    v_epsilon = (normal/np.linalg.norm(normal)) * epsilon
    vector4 = sum(face)/3 - v_epsilon
    vectors = np.vstack([face, vector4])
    tv =  [-sum(vector**2) for vector in vectors]
    Tin = np.hstack([vectors, np.ones([4, 1])])
    T = np.linalg.det(Tin)
    D, E, F, G = [coefficients(Tin, tv, i)/T for i in range(4)]
    x, y, z, r = -D/2, -E/2, -F/2, math.sqrt(D**2+E**2+F**2-4*G)/2
    return spheres.Sphere(np.array([x, y, z]), r, face)

def solid2spheres(solid, epsilon): # -> list of spheres
    return [face2sphere(face, normal, epsilon) for normal, face, _ in solid.data]

def apolloniate(solid, points, E):
    winners = solid2spheres(solid.solid, E/100)
    candidates = [spheres.Sphere(point) for point in points]

    n = len(candidates)
    w = len(winners)
    print(n, w)
    
    for candidate in candidates:
        candidate.shrink_bounding(winners)
    while candidates:
        candidates.sort()
        c = candidates.pop()
        if c.dead:
            continue
        if c.radius < E:
            break
        for loser in candidates:
            loser.shrink(c)
        winners.append(c)


    return winners
