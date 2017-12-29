import stl3d, spheres, scad_writer, stl_writer
import sys

stl_path = sys.argv[1]
E = float(sys.argv[2])
scad_path = sys.argv[3]

print("importing")
solid = stl3d.Solid(stl_path)
#print(solid.boundingbox())
print("dicing")
points = solid.discretize(E)
print("sphering")
cspheres = [spheres.Sphere(point, radius=E/2) for point in points]
print("writing")
scad_writer.write(cspheres, scad_path, stl_path, E)
sprite = sys.argv[4]
stl_writer.write(cspheres, scad_path, stl_path, sprite, E)
