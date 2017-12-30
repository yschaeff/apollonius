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

def write(spheres, outfile, infile, spritefile, E):
    sprite = stl.mesh.Mesh.from_file(spritefile)
    sprites = [sphere2mesh(sphere, sprite, E) for sphere in spheres]
    combined = stl.mesh.Mesh(np.concatenate([sprite.data for sprite in sprites]))
    combined.save(outfile, mode=stl.Mode.ASCII)  # save as ASCII
