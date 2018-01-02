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
    winners = solid2spheres(solid.solid, E/1000)
    candidates = [spheres.Sphere(point) for point in points]

    m = n = len(candidates)
    w = len(winners)
    print("Faces: {}, Dices: {}".format(w, n))

    index = 0
    print("calculating inital size")
    for i, candidate in enumerate(candidates):
        print("candidate: {}/{} ({}%)\r".format(i, n, i*100//m), end="")
        candidate.shrink_bounding(winners)
        if candidates[index].dead or (candidate.radius > candidates[index].radius and not candidate.dead):
            index = i
    print("")

    print("eliminating")
    while candidates:
        print("queue size: {}\r".format(n), end="")
        c = candidates.pop(index)
        n -= 1
        if c.dead:
            break
            continue
        if c.radius < E/2:
            break
        index = 0
        #filtering the list seems to make it hardly any faster!
        #candidates = [candidate for candidate in candidates if not candidate.dead]
        for i, loser in enumerate(candidates):
            loser.shrink(c, E)
            #if loser > candidates[index] and not loser.dead:
            if candidates[index].dead or (loser.radius > candidates[index].radius and not loser.dead):
                index = i
        winners.append(c)
    print("")


    return winners
