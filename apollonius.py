#!/usr/bin/env python3

import stl3d, spheres, scad_writer, stl_writer, apolloniator
import sys, argparse, math
import numpy as np

def compute_epsilon(solid, epsilon):
    p0, p1 = solid.boundingbox()
    prod = np.prod(p1-p0)
    if not epsilon:
        epsilon = math.pow(prod, 1/3) / 10 ## about 1000 spheres
    samples = (math.pow(prod, 1/3) / epsilon)**3
    print("Using epsilon {} for maximum {} candidates".format(epsilon, int(samples)))
    return epsilon

parser = argparse.ArgumentParser()
parser.add_argument("input", help="Base STL file", action="store")
parser.add_argument("output", help="file to write STL or SCAD", action="store")
parser.add_argument("-e", "--epsilon", help="resolution", action="store", type=float)
parser.add_argument("-m", "--max-radius", help="maximum radius of sprite", action="store", type=float)
parser.add_argument("-u", "--unit", help="voxel STL", action="store")
parser.add_argument("-r", "--raster", help="only rasterize", action="store_true")
args = parser.parse_args()

if not args.unit:
    args.unit = "models/unit_sphere.stl"

out_ext = args.output.split(".")[-1].lower()
if not out_ext in "stl scad pickle".split():
    print("output file extension must be one of stl, scad, or pickle")
    sys.exit(1)

in_ext = args.input.split(".")[-1].lower()
if in_ext == "stl":
    print("importing")
    solid = stl3d.Solid(args.input)
    args.epsilon = compute_epsilon(solid, args.epsilon)

    print("dicing")
    points = solid.discretize(args.epsilon)

    print("sphering")
    if args.raster:
        cspheres = [spheres.Sphere(point, radius=args.epsilon/2) for point in points]
    else:
        cspheres = apolloniator.apolloniate(solid, points, args.epsilon, args.max_radius)
elif in_ext == "pickle":
    pass

else:
    print("unknown input file type")
    sys.exit(1)


out_ext = args.output.split(".")[-1].lower()
if out_ext == "stl":
    print("writing")
    r = stl_writer.write(cspheres, args.output, args.input, args.unit, args.epsilon)
elif out_ext == "scad":
    print("writing")
    r = scad_writer.write(cspheres, args.output, args.input, args.epsilon)
elif out_ext == "pickle":
    ingredients = (args, cspheres)
    r = 0

sys.exit(r)
