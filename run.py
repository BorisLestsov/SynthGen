import bpy

# Check if script is opened in Blender program
import os, sys
if(bpy.context.space_data == None):
    cwd = os.path.dirname(os.path.abspath(__file__))
else:
    cwd = os.path.dirname(bpy.context.space_data.text.filepath)
sys.path.append(cwd)


from config import GLOBAL_CONF

import sys

import package.utils as utils
from package.sample import SynthGen, ObjCache, ObjectLoader

from shelves.shelvesf import ShelvesFuncs


import numpy as np
import cv2
import argparse


def main():
    argv = sys.argv
    script_args = argv[argv.index("--") + 1:]
    print(script_args)

    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", help="seed", default=GLOBAL_CONF["seed"], type=int)
    args = parser.parse_args(script_args)
    seed = args.seed

    logger = utils.setup_custom_logger(GLOBAL_CONF["logger_name"], GLOBAL_CONF["logger_file"]+"_"+str(seed)+".txt")
    logger.info('Creating object loader')

    loader = ObjectLoader(GLOBAL_CONF["assets_blend_path"], GLOBAL_CONF["object_dir"])

    logger.info("Creating cache scene")
    tmp_scene = bpy.context.screen.scene
    bpy.ops.scene.new(type="EMPTY")     
    bpy.context.scene.name = "scene_cache"

    cache = ObjCache(GLOBAL_CONF["objlist_file"], loader)
    cache.buildCache()
    bpy.context.screen.scene = tmp_scene

    logger.info("Creating mask scene")
    old_scene = bpy.context.screen.scene
    bpy.ops.scene.new(type="EMPTY")     
    bpy.context.scene.name = GLOBAL_CONF["scene_name_masks"]
    bpy.context.screen.scene = old_scene

    logger.info("Creating clownmat")
    new_scene = bpy.data.scenes[GLOBAL_CONF["scene_name_masks"]]
    clownmat = None


    for i in range(GLOBAL_CONF['num_samples']):
        bpy.context.screen.scene = old_scene

        logger.info("Clearing render folder")
        utils.clearRenderFolder(GLOBAL_CONF)

        logger.info("Creating sampler")
        sampler = SynthGen(GLOBAL_CONF, cache, loader)
        sampler.globalSetup(seed=i+seed)
        shelvesf = ShelvesFuncs(GLOBAL_CONF, sampler)

        logger.info("Clearing Scenes")
        # Remove all elements
        bpy.context.screen.scene = old_scene
        utils.removeAllNew(old_scene)
        bpy.context.screen.scene = new_scene
        utils.removeAllNew(new_scene)
        bpy.context.screen.scene = old_scene


        logger.info("Creating environment")
        shelvesf.setupEnv()
        logger.info("Creating camera")
        shelvesf.setupCamera()
        logger.info("Creating lighting")
        shelvesf.setupLighting()

        logger.info("Creating shelves")
        steps = np.random.randint(4, 7)
        heights=[np.random.uniform(1, 2) for i in range(steps)]
        scale_d = [np.random.uniform(1, 1.5)]
        for _ in range(steps):
            scale_d.append(np.random.uniform(0.3, scale_d[-1]))
        scale_l = np.random.uniform(2.5, 3.5)
        places = shelvesf.loadShelf(sampler.loader, heights=heights, scale_d=scale_d, scale_l=scale_l)

        logger.info("Sampling objects")
        sampler.sampler.sampleObjects(places)
        ####sampler.sampler.logger.infoStats()


        logger.info("Rendering main scene")
        sampler.setupRenderOptions()



        old_scene.render.filepath = os.path.join(GLOBAL_CONF["render_folder"], 'res_cam_{}.png'.format(0))
        sampler.renderScene()



        logger.info("Linking objects to mask scene")
        old_scene = bpy.context.screen.scene
        bpy.context.screen.scene = bpy.data.scenes[GLOBAL_CONF["scene_name_masks"]]
        for obj in sampler.modifier.objects:
            new_scene.objects.link(obj)
        #new_scene.objects.link(old_scene.camera)
        new_scene.camera=old_scene.camera
        if clownmat is None:
            clownmat = sampler.text.getClownMat()
            new_scene.render.layers["RenderLayer"].material_override = clownmat


        logger.info("Rendering mask scene")
        sampler.setupRenderOptions(new_scene)
        new_scene.cycles.pixel_filter_type = "GAUSSIAN"
        new_scene.cycles.filter_width = 0.01
        new_scene.cycles.use_denoising = False
        new_scene.render.layers[0].cycles.use_denoising = False
        new_scene.view_settings.view_transform = "Raw"

        new_scene.render.image_settings.file_format = "OPEN_EXR"
        new_scene.render.filepath = os.path.join(GLOBAL_CONF["render_folder"], 'res_cam_{}_mask.exr'.format(0))
        
        new_scene.cycles.samples = 1

        sampler.renderScene(new_scene)
        
        bpy.context.screen.scene = old_scene

        if (i+seed) % 5 == 0:
            logger.info("Postprocessing result")
            utils.postprocessResultNew(GLOBAL_CONF)
        
        #logger.info("Saving blend file")
        #bpy.ops.wm.save_as_mainfile(filepath=GLOBAL_CONF["scene_save_path"])
        logger.info("Copying result to output folder")
        utils.copyResultToOutputFolder(GLOBAL_CONF, GLOBAL_CONF["output_format"].format(i+seed))

    #utils.clearRenderFolder(GLOBAL_CONF)



if __name__ == '__main__':
    main()
