#!/usr/bin/env python3

import stl3d, spheres, scad_writer, stl_writer, apolloniator
import sys, argparse, math, pickle
import numpy as np

def compute_epsilon(solid, epsilon):
    p0, p1 = solid.boundingbox()
    prod = np.prod(p1-p0)
    if not epsilon:
        epsilon = math.pow(prod, 1/3) / 10 ## about 1000 spheres
    samples = (math.pow(prod, 1/3) / epsilon)**3
    print("Using epsilon {} for maximum {} candidates".format(epsilon, int(samples)))
    return epsilon

def mm_split(colors, spheres, method):
    if colors == 1: return [spheres]
    sl = [[] for i in range(colors)]
    if method == "roundrobin":
        for i, s in enumerate(spheres):
            sl[i%colors].append(s)
    return sl

parser = argparse.ArgumentParser()
parser.add_argument("input", help="Base STL file", action="store")
parser.add_argument("output", help="file to write STL or SCAD", action="store")
parser.add_argument("-e", "--epsilon", help="resolution", action="store", type=float)
parser.add_argument("-m", "--max-radius", help="maximum radius of sprite", action="store", type=float)
parser.add_argument("-u", "--unit", help="voxel STL", action="store")
parser.add_argument("-r", "--raster", help="only rasterize", action="store_true")
parser.add_argument("-M", "--multi-material", help="Number of colors", action="store", type=int, default=1)
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
    outname = args.output
    with open(args.input, 'rb') as f:
        prev_args, cspheres = pickle.load(f)
        args.epsilon = prev_args.epsilon
        args.input = prev_args.input
else:
    print("unknown input file type")
    sys.exit(1)


out_ext = args.output.split(".")[-1].lower()
if out_ext == "stl":
    mmspheres = mm_split(args.multi_material, cspheres, "roundrobin")
    print("writing")
    stl_writer.write(mmspheres, args.output, args.input, args.unit, args.epsilon)
elif out_ext == "scad":
    mmspheres = mm_split(args.multi_material, cspheres, "roundrobin")
    print("writing")
    scad_writer.write(mmspheres, args.output, args.input, args.epsilon)
elif out_ext == "pickle":
    print("writing")
    ingredients = (args, cspheres)
    with open(args.output, 'wb') as f:
        pickle.dump(ingredients, f, pickle.HIGHEST_PROTOCOL)

