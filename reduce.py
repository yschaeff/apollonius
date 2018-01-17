import stl, sys
import numpy as np
from collections import defaultdict
import bisect

def normal(face, vs):
    ui, vi, wi = face
    u = vs[ui]
    v = vs[ui]
    w = vs[ui]
    n = np.cross(u-v, w-v)
    return n/np.linalg.norm(n)

def get_normals(mesh, normals, fis):
    for fi in fis:
        if fi in normals:
            yield normals[fi]
        else:
            yield mesh.units[fi]

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

def reduce(mesh, N):
    ## Index all vertices and faces
    v2vi = {} # numpy arrays to index in vs
    vs = []   # numpy arrays
    VI = 0    # next index number
    vi2fis = defaultdict(set)  # faces for vertex index
    fi2vis = defaultdict(list)  # vertices for face index
    normals = {} ## overlay
    for fi, face in enumerate(mesh.vectors):
        vis = fi2vis[fi] #vertices for this face
        for v in face:
            if tuple(v) not in v2vi:
                v2vi[tuple(v)] = VI
                vs.append(v)
                vi = VI
                VI += 1
            else:
                vi = v2vi[tuple(v)]
            vis.append(vi)
            vi2fis[vi].add(fi)

    edges = {}
    for fi, vis in fi2vis.items():
        #construct edges
        for i, v1 in enumerate(vis):
            v2 = vis[(i+1)%3]
            def calc_cost(v1, v2):
                u = vs[v1]
                v = vs[v2]
                v1fis = vi2fis[v1]
                v2fis = vi2fis[v2]
                v12fis = v1fis.intersection(v2fis)
                Tu = list(get_normals(mesh, normals, v1fis))
                Tuv = list(get_normals(mesh, normals, v12fis))
                #return (1-min([min([np.dot(f, n) for n in Tuv]) for f in Tu]))/2
                return np.linalg.norm(u-v) * \
                    (1-min([max([np.dot(f, n) for n in Tuv]) for f in Tu]))/2

            Fedge = (v1, v2)
            if Fedge not in edges:
                edges[Fedge] = calc_cost(v1, v2)
            Redge = (v2, v1)
            if Redge not in edges:
                edges[Redge] = calc_cost(v2, v1)

    sorted_edges = list(edges.keys())
    sorted_edges.sort(key = lambda x: edges[x])

    deleted_edges = set()
    deleted_vertices = set()
    deleted_faces = set()
    while len(fi2vis) - len(deleted_faces) > N and sorted_edges:
        #print(len(fi2vis), len(deleted_faces), N, l)
        #sorted_edges.sort(key = lambda x: edges[x]) ## TMP
        edge = sorted_edges.pop(0)
        #print("collapsing", edge, vs[edge[0]], vs[edge[1]])
        if edge in deleted_edges:
            #print("nvm")
            continue
        ui, vi = edge
        assert(ui != vi)
        if ui in deleted_vertices:
            #print("u deleted, skip, todo add new edge")
            continue
        if vi in deleted_vertices:
            #print("v deleted, skip, todo add new edge")
            continue
        else:
            deleted_vertices.add(ui)
        deleted_edges.add((vi, ui)) # reverse
        deleted_edges.add((ui, vi)) # forward
        u_fis = vi2fis[ui]
        v_fis = vi2fis[vi]
        uv_fis = u_fis.intersection(v_fis)
        
        ## remove collapsed faces from any vertices
        for fi in uv_fis:
            vis = fi2vis[fi]
            for v in vis:
                vi2fis[v].remove(fi)
        deleted_faces.update(uv_fis)

        edges_to_update = []
        ## all leftover faces in add to v AND update face[u]=v
        v_fis.update(u_fis)
        for fi in u_fis:
            face = fi2vis[fi]
            for i, v in enumerate(face):
                if v==ui: face[i] = vi
            normals[fi] = normal(face, vs)
            for i, v in enumerate(face):
                v2 = face[(i+1)%3]
                edges_to_update.append((v, v2))
                edges_to_update.append((v2, v))


        #TODO: find all edges with ui. update to vi. recalc cost
        if False:
            for edge in sorted_edges:
                if any([v==ui for v in edge]):
                    edges_to_update.append(edge)
            #print(len(edges_to_update))
            #print(edges_to_update)
            for (v1, v2) in edges_to_update:
                #print((v1, v2))
                if (v2, v1) in deleted_edges:
                    continue
                #print("whelp", v1, v2, ui, vi, vi2fis[v1], vi2fis[v2])
                if v1 == ui:
                    deleted_edges.add((v1, v2))
                    deleted_edges.add((v2, v1))
                    v1 = vi
                elif v2 == ui:
                    deleted_edges.add((v1, v2))
                    deleted_edges.add((v2, v1))
                    v2 = vi
                else:
                    print("just to recalc")
                    pass

                edge = v1, v2
                #print("new: ", edge)
                cost = calc_cost(v1, v2)
                edges[edge] = cost
                #sorted_edges.insert(0, edge)
                insort(sorted_edges, edge, lambda x: edges[x])


    print(len(deleted_faces), len(sorted_edges))
    data = np.zeros(len(fi2vis) - len(deleted_faces), dtype = stl.mesh.Mesh.dtype)
    i = 0
    for fi, vis in fi2vis.items():
        if fi in deleted_faces: continue
        V = [vs[vi] for vi in vis]
        data['vectors'][i] = np.stack(V)
        #print(data['vectors'][i],  np.stack(V))
        i += 1
    reduced_mesh = stl.mesh.Mesh(data)
    return reduced_mesh

mesh = stl.mesh.Mesh.from_file(sys.argv[1])
reduced_mesh = reduce(mesh, int(sys.argv[2]))
reduced_mesh.save("out.stl", mode=stl.Mode.ASCII)  # save as ASCII
