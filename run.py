import bpy

# Check if script is opened in Blender program
import os, sys
if(bpy.context.space_data == None):
    cwd = os.path.dirname(os.path.abspath(__file__))
else:
    cwd = os.path.dirname(bpy.context.space_data.text.filepath)
sys.path.append(cwd)


from config import GLOBAL_CONF


import package.utils as utils
from package.sample import SynthGen

from shelves.shelvesf import ShelvesFuncs

import numpy as np


def main():

    for i in range(GLOBAL_CONF['num_samples']):
        print("Clearing render folder")
        utils.clearRenderFolder(GLOBAL_CONF)

        print("Creating sampler")
        sampler = SynthGen(GLOBAL_CONF)
        sampler.globalSetup(seed=i+GLOBAL_CONF["seed"])
        shelvesf = ShelvesFuncs(GLOBAL_CONF, sampler)

        print("Creating environment")
        shelvesf.setupEnv()
        print("Creating camera")
        shelvesf.setupCamera()
        print("Creating lighting")
        shelvesf.setupLighting()

        print("Creating shelves")
        steps = np.random.randint(4, 7)
        heights=[np.random.uniform(1, 2) for i in range(steps)]
        scale_d = [np.random.uniform(1, 1.5)]
        for _ in range(steps):
            scale_d.append(np.random.uniform(0.3, scale_d[-1]))
        scale_l = np.random.uniform(2.5, 3.5)
        places = shelvesf.loadShelf(sampler.loader, heights=heights, scale_d=scale_d, scale_l=scale_l)

        print("Sampling objects")
        sampler.sampler.sampleObjects(places)


        print("Rendering scene")
        sampler.setupRenderOptions()
        sampler.renderScene()

        print("Postprocessing result")
        utils.postprocessResult(GLOBAL_CONF)
        print("Copying result to output folder")
        utils.copyResultToOutputFolder(GLOBAL_CONF, GLOBAL_CONF["output_format"].format(i))

        print("Saving blend file")
        bpy.ops.wm.save_as_mainfile(filepath=GLOBAL_CONF["scene_save_path"])

    utils.clearRenderFolder(GLOBAL_CONF)



if __name__ == '__main__':
    main()