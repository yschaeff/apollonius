import stl, sys
import numpy as np
from collections import defaultdict
import bisect

def face2edges(face):
    l = len(face)
    for i, v in enumerate(face):
        yield v, face[(i+1)%l]

def reduce(mesh, N):

    v2vi = {} # numpy arrays to index in vs
    vs = []   # numpy arrays
    VI = 0    # next index number
    vi2fis = defaultdict(set)  # faces for vertex index
    fi2vis = defaultdict(list)  # vertices for face index
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
                Tu = [mesh.units[fi] for fi in v1fis]
                Tuv = [mesh.units[fi] for fi in v12fis]
                return np.linalg.norm(u-v) * \
                    (1-min([max([np.dot(f, n) for n in Tuv]) for f in Tu]))/2

            Fedge = (v1, v2)
            if Fedge not in edges:
                edges[Fedge] = calc_cost(v1, v2)
            Redge = (v2, v1)
            if Redge not in edges:
                edges[Redge] = calc_cost(v2, v1)
    #print("edges,faces,vertices", len(edges), len(fi2vis), len(vs))

    sorted_edges = list(edges.keys())
    sorted_edges.sort(key = lambda x: edges[x])
    #for edge in sorted_edges[:10]:
        #print(edge, edges[edge])

    deleted_edges = set()
    deleted_vertices = set()
    deleted_faces = set()
    while len(fi2vis) - len(deleted_faces) > N:
        edge = sorted_edges.pop(0)
        print("collapsing", edge, vs[edge[0]], vs[edge[1]])
        if edge in deleted_edges:
            print("nvm")
            continue
        ui, vi = edge
        if ui in deleted_vertices:
            print("u deleted, skip, todo add new edge")
            continue
        if vi in deleted_vertices:
            print("v deleted, skip, todo add new edge")
            continue
        else:
            deleted_vertices.add(ui)
        deleted_edges.add((vi, ui)) # reverse
        u_fis = vi2fis[ui]
        v_fis = vi2fis[vi]
        uv_fis = u_fis.intersection(v_fis)
        #changed_vertices = set()
        #changed_faces = set()
        
        ## remove collapsed faces from any vertices
        for fi in uv_fis:
            vis = fi2vis[fi]
            for v in vis:
                vi2fis[v].remove(fi)
            #changed_vertices.update(vis)
        deleted_faces.update(uv_fis)
        #changed_faces.update(u_fis)

        ## all leftover faces in add to v AND update face[u]=v
        v_fis.update(u_fis)
        for fi in u_fis:
            face = fi2vis[fi]
            for i, v in enumerate(face):
                if v==ui: face[i] = vi
        #for fi in u_fis.difference(uv_fis):
            #vis = fi2vis[fi]
        vs[ui] = vs[vi]

        ## add all faces from u to v
        ## delete common faces from all vs

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



#def reduce(mesh, N):
    #Nfaces = len(mesh.data)
    #Nvertices = len(mesh.vectors)
    #print(Nfaces, Nvertices)

    ##for every point find all neighbours and faces
    #neighbours = defaultdict(set)
    #faces = defaultdict(set)
    #edges = {} # both forward and reverse edges
    #for i_face, face in enumerate(mesh.vectors):
        #for i, v in enumerate(face):
            #faces[tuple(v)].add((i_face, i))
        #for v1, v2 in face2edges(face):
            #v1t, v2t = tuple(v1), tuple(v2)
            #neighbours[v1t].add(v2t)
            #neighbours[v2t].add(v1t)
            ##faces[v1t].add(i_face)
            ##faces[v2t].add(i_face)
            #edges[(v1t, v2t)] = (v1, v2)
            #edges[(v2t, v1t)] = (v2, v1)

    #def faces2unitnormals(i_faces):
        #normals = []
        #for i_face in i_faces:
            #if i_face in removed_faces: continue
            #if i_face not in changed_faces:
                #normals.append(mesh.units[i_face])
            #else:
                #face = mesh.vectors[i_face]
                #v0, v1, v2 = face
                #while tuple(v0) in edge_translate: v0 = edge_translate[tuple(v0)]
                #while tuple(v1) in edge_translate: v1 = edge_translate[tuple(v1)]
                #while tuple(v2) in edge_translate: v2 = edge_translate[tuple(v2)]
                #u = v0-v2
                #v = v1-v2
                #normal = np.cross(u, v)
                #normal /= np.linalg.norm(normal)
                #normals.append(normal)
        #return normals


    #def edgecost(edge, u, v):
        #ut, vt = edge
        #u_faces = [f[0] for f in faces[ut]]
        #v_faces = [f[0] for f in faces[vt]]
        #uv_faces = set.intersection(u_faces, v_faces)
        ##Tu  = [mesh.units[i_face] for i_face in u_faces]
        ##Tuv = [mesh.units[i_face] for i_face in uv_faces]
        #Tu = faces2unitnormals(u_faces)
        #Tuv = faces2unitnormals(uv_faces)
        #cost = np.linalg.norm(u-v) * (1-min([max([np.dot(f, n) for n in Tuv]) for f in Tu]))/2
        #return cost

    #removed_edges = set()
    #removed_vertices = set()
    #removed_faces = set()
    #changed_faces = set()

    ### calculate cost
    #costs = []
    #for edge, (u, v) in edges.items():
        #cost, uv_faces = edgecost(edge, u, v)
        #costs.append((cost, edge, uv_faces))

    #costs.sort(key = lambda x: x[0])
    #edge_translate = {}
    #while Nfaces - len(removed_faces) > N:
        ##print(costs[0])
        #cost, edge, uv_faces = costs.pop(0)
        #ut, vt = edge
        #u, v = edges[edge]

        #Redge = vt, ut
        #if Redge in removed_edges:
            #continue
        #removed_edges.add(edge)

        #u_faces = faces[ut]
        #v_faces = faces[vt]
        #uv_faces = set.intersection(u_faces, v_faces)
        #for i_face, i in uv_faces:
            #removed_faces.add(i_face)
        #for i_face in u_faces.difference(v_faces):
            #u_faces.add(i_face)
            

        #for neight in neighbours[ut]:
            #neighbours[neight].remove(ut)


        #while ut in edge_translate:
            #f = faces[ut]
            #u = edge_translate[ut]
            #ut = tuple(u)
            #faces[ut].update(f)
        #while vt in edge_translate:
            #f = faces[vt]
            #v = edge_translate[vt]
            #vt = tuple(v)
            #faces[vt].update(f)
        ## TODO if any of the faces changed update cost
        ## TODO: afected faces might not be accurate
        ## ALSO: normals are no longer accurate!
        #if vt in removed_vertices:
            #assert()
        #if ut in removed_vertices:
            #assert()
        #try:
            ##newcost, uv_faces = edgecost(edge, u, v)
            #newcost, uv_faces = edgecost((ut, vt), u, v)
        #except:
            #continue
        #if newcost > cost:
            #bisect.insort_left(costs, (newcost, edge, uv_faces))
            #continue

        #if Redge in removed_edges:
            ##print("removed reverse")
            #continue
        #removed_edges.add((ut, vt))
        #for i_face in uv_faces:
            ##print("removed face")
            #removed_faces.add(i_face)

        #if ut == vt:
            #continue
            #assert()
            ##TODO: WHY?!

        ##print("u,v:", u, v)
        ## collapse u to v
        #edge_translate[ut] = v
        #u_faces = faces[ut]
        #v_faces = faces[vt]
        #for i_face in u_faces:
            #if i_face in removed_faces:
                ##print("face already removed")
                #continue
            #changed_faces.add(i_face)
            #v_faces.add(i_face)
        #removed_vertices.add(ut)

    #for i_face in changed_faces:
        ##print("changed: ", mesh.vectors[i_face])
        #face = mesh.vectors[i_face].copy()
        #for i in range(3):
            #while tuple(face[i]) in edge_translate:
                #face[i] = edge_translate[tuple(face[i])]
        #mesh.data[i_face][1] = face

    #data = np.delete(mesh.data, list(removed_faces), 0)
    #reduced_mesh = stl.mesh.Mesh(data)
    #Nfaces = len(reduced_mesh .data)
    #print(Nfaces, len(removed_faces))
    #return reduced_mesh

#mesh = stl.mesh.Mesh.from_file("models/marvin.stl")
#mesh = stl.mesh.Mesh.from_file("models/falcon.stl")
#mesh = stl.mesh.Mesh.from_file("models/unit_cube.stl")
#mesh = stl.mesh.Mesh.from_file("models/unit_sphere.stl")
mesh = stl.mesh.Mesh.from_file(sys.argv[1])
reduced_mesh = reduce(mesh, int(sys.argv[2]))
reduced_mesh.save("out.stl", mode=stl.Mode.ASCII)  # save as ASCII
