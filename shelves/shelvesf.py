import bpy
import package.utils as utils
from math import pi
tau = 2*pi
import numpy as np


class ShelvesFuncs:
    def __init__(self, cfg, sampler):
        self.cfg = cfg
        self.sampler = sampler
        self.loader = sampler.loader
        self.scene = bpy.data.scenes[self.cfg['scene_name']]


    def setupLighting(self):

        mat = bpy.data.materials.new(name="LampMat")
        mat.use_nodes=True
        nodes = mat.node_tree.nodes
        for node in nodes:
            nodes.remove(node)

        # create emission node
        node_emission = nodes.new(type='ShaderNodeEmission')
        node_emission.inputs[0].default_value = (1,1,1,1)  # green RGBA
        node_emission.inputs[1].default_value = 15.0 # strength
        node_emission.location = 0,0

        # create output node
        node_output = nodes.new(type='ShaderNodeOutputMaterial')   
        node_output.location = 400,0

        links = mat.node_tree.links
        link = links.new(node_emission.outputs[0], node_output.inputs[0])


        bpy.ops.mesh.primitive_plane_add()
        plane = bpy.context.active_object
        utils.resizeObj(plane, (0.1, 2, 1))
        utils.moveObj(plane, (0, 0, 4))

        plane.data.materials.append(mat)

        for i in range(3):
            obj = plane.copy()
            self.scene.objects.link(obj)
            utils.moveObj(obj, ( plane.dimensions.x*i*5, 0, 0))
            obj = plane.copy()
            self.scene.objects.link(obj)
            utils.moveObj(obj, (-plane.dimensions.x*i*5, 0, 0))




    def setupCamera(self):
        camera_loc_x = np.random.uniform(-0.5, 0.5)
        camera_loc_y = np.random.uniform(-3.5, -2)
        camera_loc_z = np.random.uniform(0.5, 2)

        camera_rot_x = np.random.uniform(pi/2-pi/12, pi/2+pi/36)
        #camera_rot_x = pi/2
        camera_rot_y = np.random.uniform(0   -pi/36, 0   +pi/36)
        camera_rot_z = np.random.uniform(0   -pi/6 , 0   +pi/6)

        # Create camera
        bpy.ops.object.add(type='CAMERA', location=(camera_loc_x, camera_loc_y, camera_loc_z))
        self.cam = bpy.context.object
        utils.rotateObj(self.cam, (camera_rot_x, camera_rot_y, camera_rot_z))
        # Make this the current camera
        bpy.context.scene.camera = self.cam


    def getTextMat(self, img_path):
        mat_name = img_path
        
        mat = bpy.data.materials.new(mat_name)        
        mat.use_nodes = True
        nt = mat.node_tree
        nodes = nt.nodes
        links = nt.links

        # clear
        while(nodes): nodes.remove(nodes[0])

        output  = nodes.new("ShaderNodeOutputMaterial")
        diffuse = nodes.new("ShaderNodeBsdfDiffuse")
        texture = nodes.new("ShaderNodeTexImage")

        texture.image = bpy.data.images.load(img_path)

        links.new( output.inputs['Surface'], diffuse.outputs['BSDF'])
        links.new(diffuse.inputs['Color'],   texture.outputs['Color'])
        return mat

    def applyTexToImage(self, obj, mat):
        obj.data.materials.append(mat)
        bpy.context.scene.objects.active = obj
        obj.select = True
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action= 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.uv.smart_project()
        return obj


    def setupEnv(self):

        # Remove all elements
        utils.removeAll(self.scene)

        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.active_object
        utils.resizeObj(cube, (5, 5, 2.5))
        utils.moveObj(cube, (0, 0, cube.dimensions.z/2-0.001))

        bpy.ops.mesh.primitive_plane_add()
        plane = bpy.context.active_object
        utils.resizeObj(plane, (5, 5, 1))

        path = "./tex/floor{}.jpg".format(np.random.randint(1, 6))
        print(path)
        mat = self.getTextMat(path)
        self.applyTexToImage(plane, mat)
        
        path = "./tex/wall{}.jpg".format(np.random.randint(1, 5))
        print(path)
        mat = self.getTextMat(path)
        self.applyTexToImage(cube, mat)



    def loadShelf(self, loader, heights=[2,1.5,1,1], scale_d=[2,1.5,1,1,1], scale_l=0.7):
        shelf_bot_name = "cgaxis_models_32_10_15.003" 
        shelf_mid_name = "cgaxis_models_32_10_15.006" 
        shelf_top_name = "cgaxis_models_32_10_15.010" 

        places = []

        i = 0
        base = loader.load(shelf_bot_name, link=False)
        utils.resizeObj(base, (scale_l,scale_d[i],1))
        i += 1

        prev_obj_top = None
        for h_coef in heights:   
            obj = loader.load(shelf_mid_name, link=False)
            utils.resizeObj(obj, (scale_l, scale_d[i], h_coef))
            back_offset = obj.dimensions.z
            if not prev_obj_top is None:
                obj.location.z += prev_obj_top.location.z
            else:
                obj.location.z += base.dimensions.y
                
                left_pt = [-base.dimensions.z/2*0.93, -back_offset, base.dimensions.y]
                right_pt = [base.dimensions.z/2*0.93, -base.dimensions.x*0.9, base.dimensions.y]
                places.append([left_pt, right_pt])

            prev_obj_mid = obj

            obj = loader.load(shelf_top_name, link=False)
            utils.resizeObj(obj, (scale_l,scale_d[i],1))
            obj.location.z += prev_obj_mid.location.z+prev_obj_mid.dimensions.y
            prev_obj_top = obj

            left_pt = [-obj.dimensions.z/2, -back_offset, obj.location.z]
            right_pt = [obj.dimensions.z/2, -obj.dimensions.x, obj.location.z]

            places[-1][1][2] += prev_obj_mid.dimensions[1]*0.7
            places.append([left_pt, right_pt])
            i += 1

        places[-1][1][2] += prev_obj_mid.dimensions[1]*1.5

        # mat = bpy.data.materials.new(name="DebugMat")
        # mat.diffuse_color = (1, 0, 0)
        
        # for pt1, pt2 in places:
        #     bpy.ops.mesh.primitive_ico_sphere_add(location=pt1, size=0.02)
        #     sph1 = bpy.context.active_object
        #     sph1.data.materials.append(mat)
        #     bpy.ops.mesh.primitive_ico_sphere_add(location=pt2, size=0.02)
        #     sph2 = bpy.context.active_object
        #     sph2.data.materials.append(mat)

        return places


