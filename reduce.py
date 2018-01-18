import stl, sys
import numpy as np
from collections import defaultdict
import bisect


#for each vertex find all neighbours
#for each vertex find cost (based on neighbours)
#sort by cost
#find cutoff cost
#For each choosen ones collapse all unchoosen ones
    #and cache that

def weight(uH, VH):
    u = np.array(uH)
    V = [np.array(v) for v in VH]
    return max(abs(np.sum([v-u for v in V], 0)))

def toStrong(uH, collapses):
    while uH in collapses:
        uH = collapses[uH]
    return uH

def reduce(mesh, N):
    neighbours = defaultdict(set)
    for face in mesh.vectors:
        for ui, u in enumerate(face):
            v = face[(ui+1)%3]
            vH = tuple(v)
            uH = tuple(u)
            neighbours[vH].add(uH)
            neighbours[uH].add(vH)
    weights = dict()
    for uH, VH in neighbours.items():
        weights[uH] = weight(uH, VH)
    vertices = sorted(weights.items(), key = lambda x: x[1], reverse = True)
    n = len(vertices) - 1
    if N < n: n = N
    u, cutoff_weight = vertices[n] ## first of the weak points
    #print(u, cutoff_weight)
    Sstrong = set([v[0] for v in vertices[:n]])
    print(len(vertices), len(Sstrong), n)
    collapses = dict()
    done = False
    while not done:
        done = True
        for vH in Sstrong:
            UH = neighbours[vH]
            UH.difference_update(Sstrong)
            N = set()
            for uH in UH:
                if uH in collapses: continue
                done = False
                collapses[uH] = vH
                N.update(neighbours[uH])
            N.difference_update(set([vH]))
            UH.update(N)

    ## now write faces, translate all vertices if any two match ->delete
    data = np.zeros(50000, dtype = stl.mesh.Mesh.dtype)
    for i, face in enumerate(mesh.vectors):
        UH = [toStrong(tuple(u), collapses) for u in face]
        if UH[0] == UH[1] or UH[0] == UH[2] or UH[1] == UH[2]:
            pass
        else:
            data['vectors'][i] = np.stack([np.array(uH) for uH in UH])
    reduced_mesh = stl.mesh.Mesh(data)
    return reduced_mesh

mesh = stl.mesh.Mesh.from_file(sys.argv[1])
reduced_mesh = reduce(mesh, int(sys.argv[2]))
reduced_mesh.save("out.stl", mode=stl.Mode.ASCII)  # save as ASCII
