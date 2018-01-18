import stl, sys
import numpy as np
from collections import defaultdict

"""
This model takes an stl mesh as input and outputs a simplified mesh
"""

def insort(array, item, key):
    """
    Insert item in sorted array. Implemented because bisect does not
    support key function.
    """
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
    """
    The weight of vertex uH given its neighbour vertices.
    Simplified curvature.
    """
    u = np.array(uH)
    V = [np.array(v) for v in VH]
    return max(abs(np.sum([v-u for v in V], 0)))

def traverse_collapses(uH, collapses):
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
    queue = sorted(weights.keys(), key = lambda x: weights[x])
    print("FILTERING")
    collapses = dict()
    while len(queue) > N:
        uH = queue.pop(0)
        VH = neighbours[uH]
        VH.discard(uH)

        ## neighbours might or might not already be collapsed, we dont care
        W = [traverse_collapses(v, collapses) for v in VH]
        W = [v for v in W if (v != uH)]
        W = sorted(W, key = lambda x: np.linalg.norm(np.array(x) - np.array(uH))) #lightest first
        vH = W[0]
        collapses[uH] = vH
        UH = neighbours[vH]
        UH.update(VH)
        UH.discard(uH)
        if vH in queue:
            weights[vH] = weight(vH, UH)
            queue.remove(vH)
            insort(queue, vH, key = lambda x: weights[x])

    ## now write faces, translate all vertices if any two match ->delete
    data = mesh.data.copy()
    face_count = 0
    for face in mesh.vectors:
        UH = [traverse_collapses(tuple(u), collapses) for u in face]
        ## if vertices colinear the face is collapsed
        if UH[0] == UH[1] or UH[0] == UH[2] or UH[1] == UH[2]: continue
        data['vectors'][face_count] = np.stack([np.array(uH) for uH in UH])
        face_count += 1
    reduced_mesh = stl.mesh.Mesh(data[:face_count])
    return reduced_mesh

if False:
    mesh = stl.mesh.Mesh.from_file(sys.argv[1])
    reduced_mesh = reduce(mesh, int(sys.argv[2]))
    reduced_mesh.save("out.stl", mode=stl.Mode.ASCII)  # save as ASCII
