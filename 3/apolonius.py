import stl3d, spheres, scad_writer
import sys

stl_path = sys.argv[1]
E = float(sys.argv[2])
scad_path = sys.argv[3]

print("importing")
solid = stl3d.Solid(stl_path)
#print(solid.boundingbox())
print("dicing")
points = solid.discretize2(E)
print("sphering")
cspheres = [spheres.Sphere(point, radius=E/2) for point in points]
#cspheres = []
#for i, point in enumerate(points):
    #sphere = spheres.Sphere(point, radius=E/2)
    #cspheres.append(sphere)
    #print(i)
print("writing")
scad_writer.write(cspheres, scad_path, stl_path, E)
