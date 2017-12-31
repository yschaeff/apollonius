#!/usr/bin/env python3

import stl3d, spheres, scad_writer, stl_writer, apolloniator
import sys, argparse, math
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("input", help="Base STL file", action="store")
parser.add_argument("output", help="file to write STL or SCAD", action="store")
parser.add_argument("-s", "--openscad", help="output OpenSCAD file instead of STL", action="store_true")
parser.add_argument("-e", "--epsilon", help="resolution", action="store", type=float)
parser.add_argument("-u", "--unit", help="voxel STL", action="store")
parser.add_argument("-r", "--raster", help="only rasterize", action="store_true")
args = parser.parse_args()

if not args.unit:
    args.unit = "models/unit_sphere.stl"

print("importing")
solid = stl3d.Solid(args.input)

if not args.epsilon:
    ## about 1000 spheres
    p0, p1 = solid.boundingbox()
    prod = np.prod(p1-p0)
    args.epsilon = math.pow(prod, 1/3) / 10
    print("Using epsilon {}".format(args.epsilon))

print("dicing")
points = solid.discretize(args.epsilon)

if args.raster:
    print("sphering")
    cspheres = [spheres.Sphere(point, radius=args.epsilon/2) for point in points]
else:
    cspheres = apolloniator.apolloniate(solid, points, args.epsilon)

print("writing")
if args.openscad:
    r = scad_writer.write(cspheres, args.output, args.input, args.epsilon)
else:
    r = stl_writer.write(cspheres, args.output, args.input, args.unit, args.epsilon)

sys.exit(r)
