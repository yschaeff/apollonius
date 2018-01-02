import numpy as np
import bisect, math
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

    l = len(candidates)
    for ci, candidate in enumerate(candidates):
        for i, winner in enumerate(winners):
            candidate.shrink(winner, E)
            if candidate.radius != math.inf: break
        candidate.wi = i+1 # monkey patch
        print("initializing candidates: {}/{})\r".format(ci, l), end="")
    print("")

    candidates.sort()
    print(len(candidates), len(winners))
    while candidates:
        print("candidates: {}/{})\r".format(len(winners), len(candidates)), end="")
        candidate = candidates.pop()
        if candidate.dead:
            break
        ##apply rest of winners
        for i, winner in enumerate(winners[candidate.wi:]):
            candidate.shrink(winner, E)
            if candidate.dead:
                break
            if candidates and candidate < candidates[-1]:
                #reinsert
                candidate.wi += i+1
                bisect.insort_left(candidates, candidate)
                break
        else:
            winners.append(candidate)
    print("")
    return winners
