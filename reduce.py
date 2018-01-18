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
    vertices = sorted(weights.items(), key = lambda x: x[1], reverse = False)
    n = len(vertices) - 1
    if N < n: n = N
    n = len(vertices) - n
    u, cutoff_weight = vertices[n] ## first of the weak points
    print("FILTERING")
    Sstrong = set([v[0] for v in vertices[n:]])
    collapses = dict()
    queue = vertices[n:] ## strong
    #queue = vertices[:n] ##weak
    for uH, cost in vertices:
        if uH in Sstrong: break
        VH = neighbours[uH]
        #VH.difference_update(collapses)
        #VV = [v for v in VH if toStrong(v, collapses)]
        #W = sorted(VH, key = lambda x: weights[x])

        W = sorted(VH, key = lambda x: weights[x] / np.linalg.norm(np.array(uH)- np.array(x)))
        W = map(lambda x: toStrong(x, collapses), W)
        W = list(filter(lambda x: x != uH, W))
        w = W[-1] ## The most expensive
        assert(w != uH)
        collapses[uH] = w
        N = neighbours[w]
        N.update(W)
        N.remove(w)
        ## recalculate w
        #if w not in Sstrong:
        #weights[w] -= cost
            #weights[w] += cost
            #weights[w] /= 4



    #queue = vertices
    #PASS = 0
    #while queue:
        #PASS+=1
        #v, cost = queue.pop(0)
        #if v in collapses: continue
        #if v in Sstrong:
            #vH = v
            #UH = neighbours[vH]
            #add = set()
            #sub = set([vH])
            #UH.difference_update(Sstrong)
            #UH.difference_update(collapses)
            #if UH:
                #uH = min(list(UH), key = lambda x: weights[x])
                #sub.add(uH)
                #collapses[uH] = vH
                #add.update(neighbours[uH])
                ##for uH in UH:
                    ##sub.add(uH)
                    ###if uH in Sstrong or uH in collapses:
                        ###pass
                    ###else:
                    ##collapses[uH] = vH
                    ##add.update(neighbours[uH])
                    ###break
                ##UH.clear()
                #UH.update(add)
                #UH.difference_update(sub)
                #if UH:
                    #print("trigger?", len(UH))
                    #queue.append((vH, cost))
        #else:
            #uH = v
            #if uH in collapses:
                #continue
            #VH = neighbours[uH]
            #VH.difference_update(collapses.keys())
            #VH.discard(uH)
            ##S = VH.intersection(Sstrong)
            #S = VH.copy()
            #if S: ## strong neighbours
                ### pick strong one to collapse to
                #vM = max(list(S), key = lambda x: weights[x])
                #vM = toStrong(vM, collapses)

                #collapses[uH] = vM
                ##neighbours[vM].update(VH.difference(Sstrong))
                #neighbours[vM].update(VH)
                ##neighbours[vM].remove(uH)
            #else:
                #if VH:
                    ##print(VH)
                    #queue.append((uH, cost))
    #print("PASSES", PASS)

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
