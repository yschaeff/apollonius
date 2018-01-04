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

def mesh2spheres(mesh, epsilon): # -> list of spheres
    return [face2sphere(face, normal, epsilon) for normal, face, _ in mesh.data]

def explode(p, E):
    dE = E/2
    for x in [-1, 0, 1]:
        for y in [-1, 0, 1]:
            for z in [-1, 0, 1]:
                if x==y==z==0: continue
                yield np.array([p[0]+x*dE, p[1]+y*dE,  p[2]+z*dE])

def wiggle(solid, winners, candidate, E, MAX_E, depth):
    for d in range(depth):
        E /= 2
        points = [p for p in explode(candidate.center, E) if solid.point_inside(p)]
        new_cand = [spheres.Sphere(point, radius=MAX_E) for point in points]
        best = new_cand[0]
        for nc in new_cand:
            for winner in winners:
                nc.shrink(winner, E)
                if nc.dead: break
            else:
                if nc > best:
                    best = nc
        if best > candidate:
            candidate = best
    return candidate

def apolloniate(solid, points, E, MAX_E, pack):
    if MAX_E is None: MAX_E = math.inf
    winners = mesh2spheres(solid.mesh, E/1000)
    candidates = [spheres.Sphere(point, radius=MAX_E) for point in points]

    l = len(candidates)
    for ci, candidate in enumerate(candidates):
        candidate.id = ci # monkey patch
        for i, winner in enumerate(winners):
            candidate.shrink(winner, E)
            if candidate.radius != MAX_E: break
        candidate.wi = i+1 # monkey patch
        print("initializing candidates: {}/{})\r".format(ci, l), end="")
    print("")

    candidates.sort()
    while candidates:
        print("spheres: {} candidates: {})\r".format(len(winners), len(candidates)), end="")
        candidate = candidates.pop()
        if candidate.dead: break
        ##apply rest of winners
        for i, winner in enumerate(winners[candidate.wi:]):
            candidate.shrink(winner, E)
            if candidate.dead: break
            if candidates and candidate < candidates[-1]:
                #reinsert
                candidate.wi += i+1
                bisect.insort_left(candidates, candidate)
                break
        else:
            candidate = wiggle(solid, winners, candidate, E, MAX_E, pack)
            winners.append(candidate)
            #print(candidate.id, candidate)
    print("")
    return winners
