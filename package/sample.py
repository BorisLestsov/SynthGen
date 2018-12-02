import bpy
import bmesh
import colorsys
import os

import package.utils as utils

from math import pi
from mathutils import Euler
tau = 2*pi
import numpy as np



class SynthGen:

    def __init__(self, cfg):
        self.cfg = cfg
        self.objloader = utils.ObjectLoader(cfg["assets_blend_path"], cfg["object_dir"])


    def globalSetup(self):
        np.random.seed(0)





    def setupEnv(self):

        # Remove all elements
        utils.removeAll()

        # Create camera
        bpy.ops.object.add(type='CAMERA', location=(0, -3.5, 1))
        self.cam = bpy.context.object
        self.cam.rotation_euler = Euler((pi/2, 0, 0), 'XYZ')
        # Make this the current camera
        bpy.context.scene.camera = self.cam


        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.active_object
        utils.resizeObj(cube, (5, 5, 2.5))
        utils.moveObj(cube, (0, 0, cube.dimensions.z/2-0.001))


        bpy.ops.mesh.primitive_plane_add()
        plane = bpy.context.active_object
        utils.resizeObj(plane, (0.1, 2, 1))
        utils.moveObj(plane, (0, 0, 4))

        mat = bpy.data.materials.new(name="LampMat")
        mat.use_nodes=True
        nodes = mat.node_tree.nodes
        for node in nodes:
            nodes.remove(node)

        # create emission node
        node_emission = nodes.new(type='ShaderNodeEmission')
        node_emission.inputs[0].default_value = (1,1,1,1)  # green RGBA
        node_emission.inputs[1].default_value = 10.0 # strength
        node_emission.location = 0,0

        # create output node
        node_output = nodes.new(type='ShaderNodeOutputMaterial')   
        node_output.location = 400,0

        links = mat.node_tree.links
        link = links.new(node_emission.outputs[0], node_output.inputs[0])

        plane.data.materials.append(mat)



    def loadEnvObjects(self):
        pass


    def setupRenderOptions(self):
        if(not os.path.exists(self.cfg["render_folder"])):
            os.mkdir(render_folder)

        # Render image
        # for scene in bpy.data.scenes:
        #     scene.cycles.device = 'GPU'
        #     scene.cycles.samples = 16


        self.scene = bpy.data.scenes[self.cfg['scene_name']]

        self.scene.cycles.samples = self.cfg["samples"]
        self.scene.cycles.use_denoising = True
        self.scene.render.layers[0].cycles.use_denoising = True
        self.scene.render.resolution_x = self.cfg["resolution_x"]
        self.scene.render.resolution_y = self.cfg["resolution_y"]
        self.scene.render.resolution_percentage = self.cfg["resolution_percentage"]

        # self.cam_list = []
        # for ob in self.scene.objects:
        #     if ob.type == 'CAMERA':
        #         #ob.angle = 4.10
        #         #ob.sensor_width = 4.5
        #         self.cam_list.append(ob)


    def renderScene(self):
        self.scene.render.filepath = os.path.join(self.cfg["render_folder"], 'res_cam_{}.png'.format(0))
        bpy.ops.render.render(write_still=True)
        # for i, cam in enumerate(self.cam_list):
        #     self.scene.camera = cam
        #     self.rnd.filepath = os.path.join(self.cfg["render_folder"], 'res_cam_{}.png'.format(i))
        #     bpy.ops.render.render(write_still=True)

