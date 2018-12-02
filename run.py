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

import shelves.shelvesf as shelvesf

import numpy as np


def main():

    sampler = SynthGen(GLOBAL_CONF)

    sampler.globalSetup()
    sampler.setupEnv()


    places = shelvesf.loadShelf(sampler.objloader)

    # mat = bpy.data.materials.new(name="DebugMat")
    # mat.diffuse_color = (1, 0, 0)
    #
    # for pt1, pt2 in places:
    #     bpy.ops.mesh.primitive_ico_sphere_add(location=pt1, size=0.02)
    #     sph1 = bpy.context.active_object
    #     sph1.data.materials.append(mat)
    #     bpy.ops.mesh.primitive_ico_sphere_add(location=pt2, size=0.02)
    #     sph2 = bpy.context.active_object
    #     sph2.data.materials.append(mat)




    objlist = []
    with open("objlist.txt") as f:
        for line in f:
            objlist.append(line.split()[0])


    NUM_OBJ = 3

    for obj_i in range(NUM_OBJ):
        obj_idx = np.random.randint(len(objlist))
        obj = sampler.objloader.load(objlist[obj_idx])

        stage_idx = np.random.randint(len(places))
        pt1, pt2 = places[stage_idx]

        random_loc_x = np.random.uniform(pt1[0], pt2[0])
        random_loc_y = np.random.uniform(pt1[1], pt2[1])
        random_loc_z = np.random.uniform(pt1[2], pt2[2])

        obj = utils.moveObj(obj, (random_loc_x, random_loc_y, random_loc_z))

        obj.pass_index = obj_idx

        scene = bpy.data.scenes['Scene']
        scene.render.layers["RenderLayer"].use_pass_object_index = True
        scene.use_nodes = True
        renderlayers_node = scene.node_tree.nodes["Render Layers"]

        idmask_node = scene.node_tree.nodes.new("CompositorNodeIDMask")
        idmask_node.name = "idmask_{}".format(str(obj_idx))
        idmask_node.index = obj_idx
        scene.node_tree.links.new(renderlayers_node.outputs["IndexOB"], idmask_node.inputs["ID value"])

        file_output_node = scene.node_tree.nodes.new("CompositorNodeOutputFile")
        file_output_node.name = "fileout_{}".format(str(obj_idx))
        file_output_node.base_path = os.path.join(GLOBAL_CONF["render_folder"], 'cam_{}_obj_{}'.format(0, obj_idx))
        scene.node_tree.links.new(idmask_node.outputs["Alpha"], file_output_node.inputs["Image"])



    #file_output_node.location.y += file_output_node.height

    #exit(0)

    sampler.setupRenderOptions()
    sampler.renderScene()

    utils.postprocessResult(GLOBAL_CONF)


    bpy.ops.wm.save_as_mainfile(filepath=GLOBAL_CONF["scene_save_path"])




if __name__ == '__main__':
    main()