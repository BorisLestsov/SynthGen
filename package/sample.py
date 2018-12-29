import bpy
import bmesh
import colorsys
import os

import package.utils as utils

from math import pi
tau = 2*pi
import numpy as np

import json


# from line_profiler import LineProfiler  
# profile = LineProfiler()


class ObjectLoader:
    def __init__(self, lib_path, directory):
        self.lib_path = lib_path
        self.directory = directory
        self.obj_names_dict = {}
        self.uniq_counter = 1


    def load(self, object_name, link=True):
        filepath  = self.lib_path + self.directory + object_name
        directory = self.lib_path + self.directory
        filename  = object_name

        bpy.ops.wm.append(
            filepath=filepath,
            filename=filename,
            directory=directory, 
            link=link, 
            autoselect=True)

        obj = bpy.context.selected_objects[0]
        utils.moveObjAbs(obj, (0,0,0))

        if object_name in self.obj_names_dict:
            self.obj_names_dict[object_name] += 1
        else:
            self.obj_names_dict[object_name] = 0

        obj.name += "_"+str(self.obj_names_dict[object_name])

        return obj

    def giveUniqueCounter(self):
        self.uniq_counter += 1
        return self.uniq_counter


class ObjectSampler2D:
    """
        Samples objects on the planes from the list of possible_locations
    """

    def __init__(self, objlist_f, loader, modifier, augmenter, obj_cache=None):
        self.objlist = []
        self.loader = loader
        self.modifier = modifier
        self.augmenter = augmenter

        #self.obj_cache = obj_cache if not obj_cache is None else {}
        with open(objlist_f, 'r') as f:
            self.objlist = json.load(f)

    # def buildObjCache(self):
    #     for i, model_name in enumerate(objlist):
    #         obj = self.loader.load(objlist[obj_idx])
    #         self.obj_cache[model_name] = {}
    #         self.obj_cache[model_name]



    #@profile
    def sampleObjects(self, possible_locations):
        NUM_TRIES = 100
        BREAK_TOL = 20

        num_placed = {i:np.random.randint(5, 10) for i in range(len(possible_locations))}


        self.cached_objects = [None for _ in range(len(self.objlist))]
        for i, obj_prop in enumerate(self.objlist):
            self.cached_objects[i] = self.loader.load(obj_prop["name"])
            utils.moveObjAbs(self.cached_objects[i], (0, 0, -3))


        time_since = 0
        for try_i in range(NUM_TRIES):
            if time_since > BREAK_TOL:
                break

            obj_idx = np.random.randint(0, len(self.objlist))
            obj_prop = self.objlist[obj_idx]
            #orig_obj = self.loader.load(obj_prop["name"])
            orig_obj = self.cached_objects[obj_idx].copy()

            w, d, h = orig_obj.dimensions

            found = False
            randidx = np.random.permutation(len(possible_locations))
            for i in randidx:
                pt1, pt2 = possible_locations[i]
                place_h = pt2[2] - pt1[2]
                place_w = pt2[0] - pt1[0]
                place_d = pt1[1] - pt2[1]

                times_h = place_h / (h)
                times_w = place_w / (w*1.1)
                times_d = place_d / (d*1.1)

                if (times_h > 1) and (times_w > 1) and (times_d > 1):
                    found = True
                    break
            if not found:
                time_since += 1
                bpy.data.objects.remove(orig_obj, True)
                continue
            else:
                time_since = 0

            coef_w = np.random.uniform(1/(num_placed[i]+1), 1/num_placed[i])
            if int(times_w*coef_w) != 0 and num_placed[i] != 1: num_placed[i] -= 1

            marg_w = pt1[0] + w/2
            marg_d = pt2[1] + d/2
            marg_h = pt1[2]

            stackable = w > h/3 and d > h/3
            times_h = 1 if not obj_prop["stackable"] else min(times_h, 4)

            transforms = []
            #if obj_prop["rotatable_z"]:
            #    transforms.append(self.augmenter.runtime_augment_rotate_flip)
            transforms.append(self.augmenter.runtime_augment_rotate_small)
            transforms.append(self.augmenter.runtime_augment_jitter)

            #print(try_i, obj_idx)
            for i_w in range(int(times_w*coef_w)):
                for i_h in range(int(times_h)):
                    for i_d in range(int(times_d)):
                        obj = orig_obj.copy()

                        for tr in transforms:
                            obj = tr(obj)

                        self.modifier.scene.objects.link(obj)
                        obj = utils.moveObjAbs(obj, (marg_w+i_w*w*1.1, marg_d+d*i_d*1.1, marg_h+h*i_h))
                        if i_d == 0:
                            self.modifier.addObjectMaskOutputNew(obj, obj_prop["class"])

                pt1[0] += w*1.1

            bpy.data.objects.remove(orig_obj, True)

    # def printStats(self):
    #     print("STATS")
    #     profile.print_stats()  


class SynthGen:

    def __init__(self, cfg):
        self.cfg = cfg
        self.loader = ObjectLoader(cfg["assets_blend_path"], cfg["object_dir"])
        self.modifier = OutputRegistrator(cfg)
        self.augmenter = ObjectAugmenter(cfg)
        self.sampler = ObjectSampler2D(cfg["objlist_file"], self.loader, self.modifier, self.augmenter)
        self.text = TextureCreator(cfg)
        self.scene = bpy.data.scenes[self.cfg['scene_name']]

    def globalSetup(self, seed=None):
        np.random.seed(self.cfg["seed"] if seed is None else seed)



    def loadEnvObjects(self):
        pass


    def setupRenderOptions(self, scene=None):
        if scene is None:
            scene = self.scene

        if(not os.path.exists(self.cfg["render_folder"])):
            os.mkdir(render_folder)

        if self.cfg["use_gpu"]:
            scene.cycles.device = 'GPU'
            scene.render.tile_x = 256
            scene.render.tile_y = 256

            cycles_prefs = bpy.context.user_preferences.addons['cycles'].preferences

            scene.render.use_overwrite = False
            scene.render.use_placeholder = True
            cycles_prefs.compute_device_type = "CUDA"

            for device in cycles_prefs.devices:
                device.use = True



        scene.cycles.samples = self.cfg["samples"]
        scene.cycles.use_denoising = True
        scene.cycles.caustics_reflective = False
        scene.cycles.caustics_refractive = False


        scene.render.layers[0].cycles.use_denoising = True
        scene.render.resolution_x = self.cfg["resolution_x"]
        scene.render.resolution_y = self.cfg["resolution_y"]
        scene.render.resolution_percentage = self.cfg["resolution_percentage"]
        
        scene.view_settings.view_transform = "Filmic"
        scene.view_settings.look = "Filmic - High Contrast"



        # self.cam_list = []
        # for ob in self.scene.objects:
        #     if ob.type == 'CAMERA':
        #         #ob.angle = 4.10
        #         #ob.sensor_width = 4.5
        #         self.cam_list.append(ob)


    def renderScene(self, scene=None):
        if scene is None:
            scene = self.scene
        #scene.render.filepath = os.path.join(self.cfg["render_folder"], 'res_cam_{}.png'.format(0))
        bpy.ops.render.render(write_still=True)
        # for i, cam in enumerate(self.cam_list):
        #     self.scene.camera = cam
        #     self.rnd.filepath = os.path.join(self.cfg["render_folder"], 'res_cam_{}.png'.format(i))
        #     bpy.ops.render.render(write_still=True)

    def addNewScene(self, name, type):
        old_scene = bpy.context.screen.scene
        bpy.ops.scene.new(type=type)     
        bpy.context.scene.name = name
        bpy.context.screen.scene = old_scene

    def chooseScene(self, name):
        bpy.context.screen.scene = bpy.data.scenes[name]


class OutputRegistrator:
    def __init__(self, cfg):
        self.cfg = cfg
        self.scene = bpy.data.scenes[self.cfg['scene_name']]
        self.cur_pass = 1
        self.dest_dir = self.cfg['render_folder']
        self.outf = open(os.path.join(self.dest_dir, 'objects.txt'), 'w')

        self.scene.render.layers["RenderLayer"].use_pass_object_index = True
        self.scene.render.layers["RenderLayer"].use_pass_z = False
        self.scene.use_nodes = True
        self.renderlayers_node = self.scene.node_tree.nodes["Render Layers"]

        self.objects = []

    def addObjectMaskOutput(self, obj, class_id):

        obj.pass_index = self.cur_pass

        idmask_node = self.scene.node_tree.nodes.new("CompositorNodeIDMask")
        idmask_node.name = "idmask_{}_{}".format(str(class_id), str(obj.pass_index))
        idmask_node.index = obj.pass_index
        self.scene.node_tree.links.new(self.renderlayers_node.outputs["IndexOB"], idmask_node.inputs["ID value"])

        file_output_node = self.scene.node_tree.nodes.new("CompositorNodeOutputFile")
        file_output_node.name = "fileout_{}_{}".format(str(class_id), obj.pass_index)
        outpath = os.path.join(self.dest_dir, 'cam_{}_obj_{}_{}'.format(0, class_id, obj.pass_index))
        #outpath = './mnttmp/cam_{}_obj_{}_{}'.format(0, class_id, obj.pass_index)
        file_output_node.base_path = outpath
        self.scene.node_tree.links.new(idmask_node.outputs["Alpha"], file_output_node.inputs["Image"])

        self.outf.write('{} {} {}\n'.format(outpath, class_id, obj.pass_index))
        self.outf.flush()

        self.cur_pass += 1

    def addObjectMaskOutputNew(self, obj, class_id):
        
        obj.pass_index = self.cur_pass
        self.objects.append(obj)

        outpath = os.path.join(self.dest_dir, 'cam_{}_obj_{}_{}'.format(0, class_id, obj.pass_index))
        self.outf.write('{} {} {}\n'.format(outpath, class_id, obj.pass_index))
        self.outf.flush()

        self.cur_pass += 1



    def __del__(self):
        self.outf.close()



class ObjectAugmenter:
    def __init__(self, cfg):
        self.cfg = cfg

    def runtime_augment_rotate_small(self, obj):
        rot_x = 0
        rot_y = 0
        rot_z = np.random.uniform(-pi/12, pi/12)
        utils.addObjRot(obj, (rot_x, rot_y, rot_z))
        return obj

    def runtime_augment_rotate_flip(self, obj):
        rot_x = 0
        rot_y = 0
        rotations_z = [0, pi]
        rot_z = np.random.choice(rotations_z)
        utils.addObjRot(obj, (rot_x, rot_y, rot_z))
        return obj

    def runtime_augment_jitter(self, obj, coef=0.05):
            jit_x = np.random.uniform(-obj.dimensions.x*coef, obj.dimensions.x*coef)
            jit_y = np.random.uniform(-obj.dimensions.y*coef, obj.dimensions.y*coef)
            jit_z = 0
            utils.shiftObj(obj, (jit_x, jit_y, jit_z))
            return obj




class TextureCreator:
    def __init__(self, cfg):
        self.cfg = cfg
        self.texlist = []
        self.tex_prefix = self.cfg["tex_prefix"]
        self.counter = 0
        
        with open(self.cfg["texlist_file"], "r") as f:
            self.texlist = json.load(f)


    def getRandomTexWithProp(self, *args, **kwargs):
        randind = np.random.permutation(len(self.texlist))

        for prop, val in kwargs.items():
            for i in randind:
                if self.texlist[i][prop] == val:
                    path = os.path.join(self.tex_prefix, self.texlist[i]["path"])
                    return self.getTextMat(path)
        print("No texture found with such prop!")


    def getTextMat(self, img_path):
        mat_name = "{}_{}".format(img_path, self.counter)
        self.counter += 1
        
        mat = bpy.data.materials.new(mat_name)        
        mat.use_nodes = True
        nt = mat.node_tree
        nodes = nt.nodes
        links = nt.links

        # clear
        while(nodes): nodes.remove(nodes[0])

        texcoor = nodes.new("ShaderNodeTexCoord")
        mapping = nodes.new("ShaderNodeMapping")
        texture = nodes.new("ShaderNodeTexImage")
        diffuse = nodes.new("ShaderNodeBsdfDiffuse")
        output  = nodes.new("ShaderNodeOutputMaterial")

        img = bpy.data.images.load(img_path)
        texture.image = img
        texture.projection = "BOX"

        links.new(mapping.inputs['Vector'],  texcoor.outputs['Object'],)
        links.new(texture.inputs['Vector'],  mapping.outputs['Vector'])
        links.new(diffuse.inputs['Color'],   texture.outputs['Color'])
        links.new( output.inputs['Surface'], diffuse.outputs['BSDF'])
        return mat


    def applyMatToObjWithTex(self, obj, mat):
        obj.data.materials.append(mat)
        bpy.context.scene.objects.active = obj
        obj.select = True
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_all(action= 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bpy.ops.uv.smart_project()
        return obj

    def applyMatToObj(self, obj, mat):
        obj.data.materials[0] = mat


    def getLightingMat(self, strength=15.0, color=(1,1,1,1)):

        mat = bpy.data.materials.new(name="{}_{}".format("LampMat", self.counter))
        self.counter += 1
        mat.use_nodes=True
        nodes = mat.node_tree.nodes
        for node in nodes:
            nodes.remove(node)

        node_emission = nodes.new(type='ShaderNodeEmission')
        node_emission.inputs[0].default_value = color  # green RGBA
        node_emission.inputs[1].default_value = strength # strength

        node_output = nodes.new(type='ShaderNodeOutputMaterial')

        links = mat.node_tree.links
        link = links.new(node_emission.outputs[0], node_output.inputs[0])

        return mat

    def getDiffuseMat(self, color=(1,1,1,1)):
        mat = bpy.data.materials.new(name="{}_{}".format("Diffuse", self.counter))
        self.counter += 1
        mat.use_nodes=True
        nodes = mat.node_tree.nodes
        for node in nodes:
            nodes.remove(node)

        node_diffuse = nodes.new(type='ShaderNodeBsdfDiffuse')
        node_diffuse.inputs[0].default_value = color

        node_output = nodes.new(type='ShaderNodeOutputMaterial')

        links = mat.node_tree.links
        link = links.new(node_diffuse.outputs[0], node_output.inputs[0])

        return mat

    def getClownMat(self):

        mat_name = "clown"
        
        mat = bpy.data.materials.new(mat_name)        
        mat.use_nodes = True
        nt = mat.node_tree
        nodes = nt.nodes
        links = nt.links

        # clear
        while(nodes): nodes.remove(nodes[0])

        info = nodes.new("ShaderNodeObjectInfo")
        hue = nodes.new("ShaderNodeHueSaturation")
        emis = nodes.new("ShaderNodeEmission")
        output  = nodes.new("ShaderNodeOutputMaterial")

        hue.inputs[4].default_value = (1,0,0,1)

        links.new(hue.inputs['Value'],  info.outputs['Object Index'],)
        links.new(emis.inputs['Color'],  hue.outputs['Color'])
        links.new(output.inputs['Surface'],   emis.outputs['Emission'])

        return mat

