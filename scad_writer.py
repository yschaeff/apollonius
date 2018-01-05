
def sphere_to_scad_color(sphere, E, r, g, b):
    extra = E/10
    s = "translate([%f, %f, %f]) color([%f, %f, %f, 1]) sphere(r=%f);" % (*sphere.center, r, g, b, sphere.radius+extra)
    if sphere.bounding:
        return "//" + s
    return s

def sphere_to_scad(sphere, E):
    extra = E/10
    s = "translate([%f, %f, %f]) sphere(r=%f);" % (*sphere.center, sphere.radius+extra)
    if sphere.bounding:
        return "//" + s
    return s

def write(mmspheres, outfile, infile, E):
    with open(outfile, "w") as f:
        print("$fs=.1;", file=f)
        print("$fa=10;", file=f)
        
        print("% import(\"" + infile + "\");", file=f)

        if len(mmspheres) == 1:
            for sphere in mmspheres[0]:
                print(sphere_to_scad(sphere, E), file=f)
        else:
            for i, spheres in enumerate(reversed(mmspheres)):
                r = i/len(mmspheres)
                g = ((i+1)%len(mmspheres))/len(mmspheres)
                b = ((i+2)%len(mmspheres))/len(mmspheres)
                for sphere in spheres:
                    print(sphere_to_scad_color(sphere, E, r, g, b), file=f)

