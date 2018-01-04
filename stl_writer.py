import stl
import numpy as np

def sphere2mesh(sphere, sprite, E):
    copy = stl.mesh.Mesh(sprite.data.copy())
    ## first we scale to E
    extra = E/10
    ##scale
    copy.vectors *= sphere.radius*2 + extra
    ## translate
    copy.vectors += sphere.center
    return copy

def write_spheres(spheres, outfile, sprite, E):
    sprites = [sphere2mesh(sphere, sprite, E) for sphere in spheres if not sphere.bounding]
    if not sprites:
        print("No samples found")
    else:
        combined = stl.mesh.Mesh(np.concatenate([sprite.data for sprite in sprites]))
        combined.save(outfile, mode=stl.Mode.ASCII)  # save as ASCII

def write(mmspheres, outfile, infile, spritefile, E):
    sprite = stl.mesh.Mesh.from_file(spritefile)
    if len(mmspheres) == 1:
        write_spheres(mmspheres[0], outfile, sprite, E)
    else:
        fn = outfile.split(".")
        for i, spheres in enumerate(mmspheres):
            fni = fn[:]
            fni[-2] += "_MM{}".format(i)
            out = ".".join(fni)
            write_spheres(spheres, out, sprite, E)
