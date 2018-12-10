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
from package.sample import SynthGen, ObjectModifier

import shelves.shelvesf as shelvesf

import numpy as np


def main():


    for i in range(GLOBAL_CONF['num_samples']):
        utils.clearRenderFolder(GLOBAL_CONF)

        sampler = SynthGen(GLOBAL_CONF)

        sampler.globalSetup(seed=i)
        sampler.setupEnv()

        steps = np.random.randint(1, 5)
        heights=[np.random.uniform(0.7, 2) for i in range(steps)]
        scale_d = [np.random.uniform(0.5, 2)]
        for _ in range(steps):
            scale_d.append(np.random.uniform(0.5, scale_d[-1]))
        scale_l = np.random.uniform(0.3, 0.7)
        places = shelvesf.loadShelf(sampler.loader, heights=heights, scale_d=scale_d, scale_l=scale_l)

        sampler.sampler.sampleObjects(places)


        sampler.setupRenderOptions()
        sampler.renderScene()

        utils.postprocessResult(GLOBAL_CONF)
        utils.copyResultToOutputFolder(GLOBAL_CONF, GLOBAL_CONF["output_format"].format(i))

        bpy.ops.wm.save_as_mainfile(filepath=GLOBAL_CONF["scene_save_path"])

    utils.clearRenderFolder(GLOBAL_CONF)






if __name__ == '__main__':
    main()