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

def insort(array, item, key):
    ci = key(item)
    s = 0
    e = len(array)
    p = (s+e)//2
    while s < e:
        cp = key(array[p])
        if ci > cp:
            s = p+1
        elif ci < cp:
            e = p
        else:
            break
        p = (s+e)//2
    array.insert(p, item)

def weight(uH, VH):
    u = np.array(uH)
    V = [np.array(v) for v in VH]
    return max(abs(np.sum([v-u for v in V], 0)))

def toStrong(uH, collapses):
    #return collapses.get(uH, uH)
    while uH in collapses:
        uH = collapses[uH]
    return uH

def reduce(mesh, N):
    print("INDEXING")
    neighbours = defaultdict(set)
    for face in mesh.vectors:
        for ui, u in enumerate(face):
            v = face[(ui+1)%3]
            vH = tuple(v)
            uH = tuple(u)
            neighbours[vH].add(uH)
            neighbours[uH].add(vH)
    print("Found {} vertices. Reducing to {}.".format(len(neighbours), N))
    print("WEIGHING")
    weights = dict()
    for uH, VH in neighbours.items():
        weights[uH] = weight(uH, VH)
    print("SORTING")
    vertices = sorted(weights.keys(), key = lambda x: weights[x])
    #n = len(vertices) - 1
    #if N < n: n = N
    n = N
    #n = len(vertices) - n
    #u = vertices[n] ## first of the weak points
    print("FILTERING")
    #Sstrong = set(vertices[n:])
    collapses = dict()
    #queue = vertices[n:] ## strong
    #queue = vertices[:n] ##weak
    queue = vertices ##weak
    while queue:
        uH = queue.pop(0)
        #if uH in Sstrong: break
        if len(queue) < n:
            print(len(queue), n)
            break
        VH = neighbours[uH]
        VH.discard(uH)
        assert(uH not in VH)

        def WW(u):
            return weight(u, neighbours[u])
        
        ## neighbours might or might not already be collapsed, we dont care
        W = [toStrong(v, collapses) for v in VH]
        #W = [(v , w) for v, w, selfmap in W if not selfmap]
        W = [v for v in W if (v != uH)]
        #W = sorted(W, key = lambda x: x[1]) #lightest first
        W = sorted(W, key = lambda x: WW(x)) #lightest first
        W = sorted(W, key = lambda x: np.linalg.norm(np.array(x) - np.array(uH))) #lightest first
        #W = sorted(W, key = lambda x: weights[x]) #lightest first
        #vH = W[-1]
        vH = W[0]
        assert(vH != uH)
        collapses[uH] = vH
        N = neighbours[vH]
        N.update(VH)
        #N.remove(vH)
        N.discard(uH)
        if vH in queue:
            weights[vH] = weight(vH, N)
            #weights[vH] *= 2
            queue.remove(vH)
            insort(queue, vH, key = lambda x: weights[x])

    ## now write faces, translate all vertices if any two match ->delete
    data = np.zeros(50000, dtype = stl.mesh.Mesh.dtype)
    for i, face in enumerate(mesh.vectors):
        UH = [toStrong(tuple(u), collapses) for u in face]
        if UH[0] == UH[1] or UH[0] == UH[2] or UH[1] == UH[2]:
            #colinear
            continue
        data['vectors'][i] = np.stack([np.array(uH) for uH in UH])
    reduced_mesh = stl.mesh.Mesh(data)
    return reduced_mesh

mesh = stl.mesh.Mesh.from_file(sys.argv[1])
reduced_mesh = reduce(mesh, int(sys.argv[2]))
reduced_mesh.save("out.stl", mode=stl.Mode.ASCII)  # save as ASCII
