
def sphere_to_scad(sphere, E):
    extra = E/10
    s = "translate([%f, %f, %f]) sphere(r=%f);" % (*sphere.center, sphere.radius+extra)
    if sphere.bounding():
        return "//" + s
    return s

def write(spheres, outfile, infile, E):
    with open(outfile, "w") as f:
        print("$fs=.1;", file=f)
        print("$fa=10;", file=f)
        
        print("%import(\"" + infile + "\");", file=f)

        for sphere in spheres:
            print(sphere_to_scad(sphere, E), file=f)
