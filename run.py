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



def main():

    loader = ObjectLoader(GLOBAL_CONF["assets_blend_path"], GLOBAL_CONF["object_dir"])

    print("Creating cache scene")
    tmp_scene = bpy.context.screen.scene
    bpy.ops.scene.new(type="EMPTY")     
    bpy.context.scene.name = "scene_cache"

    cache = ObjCache(GLOBAL_CONF["objlist_file"], loader)
    cache.buildCache()
    bpy.context.screen.scene = tmp_scene



    print("Creating new scene")
    old_scene = bpy.context.screen.scene
    bpy.ops.scene.new(type="EMPTY")     
    bpy.context.scene.name = GLOBAL_CONF["scene_name_masks"]
    bpy.context.screen.scene = old_scene

    new_scene = bpy.data.scenes[GLOBAL_CONF["scene_name_masks"]]


    for i in range(GLOBAL_CONF['num_samples']):
        bpy.context.screen.scene = old_scene

        print("Clearing render folder")
        utils.clearRenderFolder(GLOBAL_CONF)

        print("Creating sampler")
        sampler = SynthGen(GLOBAL_CONF, cache, loader)
        sampler.globalSetup(seed=i+GLOBAL_CONF["seed"])
        shelvesf = ShelvesFuncs(GLOBAL_CONF, sampler)

        print("Clearing Scenes")
        # Remove all elements
        bpy.context.screen.scene = old_scene
        utils.removeAllNew(old_scene)
        bpy.context.screen.scene = new_scene
        utils.removeAllNew(new_scene)
        bpy.context.screen.scene = old_scene


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
        #sampler.sampler.printStats()


        print("Rendering scene")
        sampler.setupRenderOptions()



        old_scene.render.filepath = os.path.join(GLOBAL_CONF["render_folder"], 'res_cam_{}.png'.format(0))
        sampler.renderScene()



        old_scene = bpy.context.screen.scene
        bpy.context.screen.scene = bpy.data.scenes[GLOBAL_CONF["scene_name_masks"]]
        for obj in sampler.modifier.objects:
            new_scene.objects.link(obj)
        #new_scene.objects.link(old_scene.camera)
        new_scene.camera=old_scene.camera

        clownmat = sampler.text.getClownMat()
        new_scene.render.layers["RenderLayer"].material_override = clownmat
    

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


        print("Postprocessing result")
        utils.postprocessResultNew(GLOBAL_CONF)
        print("Saving blend file")
        bpy.ops.wm.save_as_mainfile(filepath=GLOBAL_CONF["scene_save_path"])
        print("Copying result to output folder")
        utils.copyResultToOutputFolder(GLOBAL_CONF, GLOBAL_CONF["output_format"].format(i))

    #utils.clearRenderFolder(GLOBAL_CONF)



if __name__ == '__main__':
    main()
