import stl3d, spheres, scad_writer, stl_writer
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input", help="Base STL file", action="store")
parser.add_argument("output", help="file to write STL or SCAD", action="store")
parser.add_argument("-s", "--openscad", help="output OpenSCAD file instead of STL", action="store_true")
parser.add_argument("-e", "--epsilon", help="resolution", action="store", type=float)
parser.add_argument("-u", "--unit", help="voxel STL", action="store")
args = parser.parse_args()

if not args.unit:
    args.unit = "unit_sphere.stl"

print("importing")
solid = stl3d.Solid(args.input)
#print(solid.boundingbox())

if not args.epsilon:
    ## todo base on solid volume/BB
    args.epsilon = 1

print("dicing")
points = solid.discretize(args.epsilon)

print("sphering")
cspheres = [spheres.Sphere(point, radius=args.epsilon/2) for point in points]

print("writing")
if args.openscad:
    scad_writer.write(cspheres, args.output, args.input, args.epsilon)
else:
    stl_writer.write(cspheres, args.output, args.input, args.unit, args.epsilon)

