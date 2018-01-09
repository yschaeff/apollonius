
def sphere_to_scad_color(sphere, E, r, g, b):
    extra = E/10
    s = "translate([%g, %g, %g]) color([%g, %g, %g, 1]) sphere(r=%g);" % (*sphere.center, r, g, b, sphere.radius+extra)
    if sphere.bounding:
        return "//" + s
    return s

def sphere_to_scad(sphere, E):
    extra = E/10
    s = "translate([%g, %g, %g]) sphere(r=%g);" % (*sphere.center, sphere.radius+extra)
    if sphere.bounding:
        return "//" + s
    return s

def write(mmspheres, outfile, infile, E):
    with open(outfile, "w") as f:
        print("$fs=.01;", file=f)
        #print("$fa=10;", file=f)
        
        print("% import(\"" + infile + "\");", file=f)

        if len(mmspheres) == 1:
            for sphere in reversed(mmspheres[0]):
                print(sphere_to_scad(sphere, E), file=f)
        else:
            for i, spheres in enumerate(mmspheres):
                r = i/len(mmspheres)
                g = ((i+1)%len(mmspheres))/len(mmspheres)
                b = ((i+2)%len(mmspheres))/len(mmspheres)
                for sphere in reversed(spheres):
                    print(sphere_to_scad_color(sphere, E, r, g, b), file=f)

