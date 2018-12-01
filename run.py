import bpy

# Check if script is opened in Blender program
import os, sys
if(bpy.context.space_data == None):
    cwd = os.path.dirname(os.path.abspath(__file__))
else:
    cwd = os.path.dirname(bpy.context.space_data.text.filepath)

sys.path.append(cwd)
import package.utils as utils
import package.sample as sample

from math import pi
from mathutils import Euler
tau = 2*pi

import numpy as np

assets_blend_path = "./assets/model_assets.blend"
object_dir = "/Object/"


def main():

    # Specify folder to save rendering
    render_folder = os.path.join(cwd, 'result')
    if(not os.path.exists(render_folder)):
        os.mkdir(render_folder)




    np.random.seed(0)

    # Remove all elements
    utils.removeAll()

    # Create camera
    bpy.ops.object.add(type='CAMERA', location=(0, -3.5, 1))
    cam = bpy.context.object
    cam.rotation_euler = Euler((pi/2, 0, 0), 'XYZ')
    # Make this the current camera
    bpy.context.scene.camera = cam


    objloader = utils.ObjectLoader(assets_blend_path, object_dir)
    
    places = sample.loadShelf(objloader)

    mat = bpy.data.materials.new(name="DebugMat")
    mat.diffuse_color = (1, 0, 0)

    for pt1, pt2 in places:
        bpy.ops.mesh.primitive_ico_sphere_add(location=pt1, size=0.02)
        sph1 = bpy.context.active_object
        sph1.data.materials.append(mat)
        bpy.ops.mesh.primitive_ico_sphere_add(location=pt2, size=0.02)
        sph2 = bpy.context.active_object
        sph2.data.materials.append(mat)

    objlist = []
    with open("objlist.txt") as f:
        for line in f:
            objlist.append(line.split()[0])


    NUM_OBJ = 3

    for obj_i in range(NUM_OBJ):
        obj_idx = np.random.randint(len(objlist))
        obj = objloader.load(objlist[obj_idx])

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
        file_output_node.base_path = os.path.join(render_folder, 'res_cam_{}_obj_{}'.format(0, obj_idx))
        scene.node_tree.links.new(idmask_node.outputs["Alpha"], file_output_node.inputs["Image"])



    # for i in scene.node_tree.nodes:
    #    print(i.name)


    


    #file_output_node.location.y += file_output_node.height

    #exit(0)






    # Render image
    # for scene in bpy.data.scenes:
    #     scene.cycles.device = 'GPU'
    #     scene.cycles.samples = 16
    scene = bpy.data.scenes['Scene']
    rnd = scene.render


    rnd.resolution_x = 1080
    rnd.resolution_y = 1920
    rnd.resolution_percentage = 15

    cam_list = []
    for ob in scene.objects:
        if ob.type == 'CAMERA':
            #ob.angle = 4.10
            #ob.sensor_width = 4.5
            cam_list.append(ob)


    for i, cam in enumerate(cam_list):
        scene.camera = cam
        rnd.filepath = os.path.join(render_folder, 'res_cam_{}.png'.format(i))
        bpy.ops.render.render(write_still=True)


    

    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)




if __name__ == '__main__':
    main()