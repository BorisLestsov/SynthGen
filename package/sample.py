import bpy
import bmesh
import colorsys
import os

import package.utils as utils

from math import pi
tau = 2*pi
import numpy as np




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


class ObjectSampler:
    def __init__(self, objlist_f, loader, modifier, augmenter, obj_cache=None):
        self.objlist = []
        self.loader = loader
        self.modifier = modifier
        self.augmenter = augmenter

        #self.obj_cache = obj_cache if not obj_cache is None else {}
        with open(objlist_f) as f:
            for line in f:
                self.objlist.append(line.split()[0])

    # def buildObjCache(self):
    #     for i, model_name in enumerate(objlist):
    #         obj = self.loader.load(objlist[obj_idx])
    #         self.obj_cache[model_name] = {}
    #         self.obj_cache[model_name]


    def sampleObjects(self, possible_locations):
        NUM_TRIES = 100
        BREAK_TOL = 20

        num_placed = {i:np.random.randint(5, 10) for i in range(len(possible_locations))}

        time_since = 0
        for try_i in range(NUM_TRIES):
            if time_since > BREAK_TOL:
                break

            obj_idx = np.random.randint(1, len(self.objlist))
            orig_obj = self.loader.load(self.objlist[obj_idx])

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
            times_h = 1 if not stackable else min(times_h, 3)

            for i_w in range(int(times_w*coef_w)):
                for i_h in range(int(times_h)):
                    for i_d in range(int(times_d)):
                        obj = orig_obj.copy()

                        self.augmenter.runtime_augment_rot(orig_obj)

                        self.modifier.scene.objects.link(obj)
                        obj = utils.moveObj(obj, (marg_w+i_w*w*1.1, marg_d+d*i_d*1.1, marg_h+h*i_h))
                        if i_d == 0:
                            self.modifier.addObjectMaskOutput(obj, obj_idx)

                pt1[0] += w*1.1

            bpy.data.objects.remove(orig_obj, True)




class SynthGen:

    def __init__(self, cfg):
        self.cfg = cfg
        self.loader = ObjectLoader(cfg["assets_blend_path"], cfg["object_dir"])
        self.modifier = ObjectModifier(cfg)
        self.augmenter = ObjectAugmenter(cfg)
        self.sampler = ObjectSampler(cfg["objlist_file"], self.loader, self.modifier, self.augmenter)
        self.scene = bpy.data.scenes[self.cfg['scene_name']]

    def globalSetup(self, seed=None):
        np.random.seed(self.cfg["seed"] if seed is None else seed)



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





class ObjectModifier:
    def __init__(self, cfg):
        self.cfg = cfg
        self.scene = bpy.data.scenes[self.cfg['scene_name']]
        self.cur_pass = 1
        self.dest_dir = self.cfg['render_folder']
        self.outf = open(os.path.join(self.dest_dir, 'objects.txt'), 'w')

        self.scene.render.layers["RenderLayer"].use_pass_object_index = True
        self.scene.use_nodes = True
        self.renderlayers_node = self.scene.node_tree.nodes["Render Layers"]

    def addObjectMaskOutput(self, obj, class_id):

        obj.pass_index = self.cur_pass

        idmask_node = self.scene.node_tree.nodes.new("CompositorNodeIDMask")
        idmask_node.name = "idmask_{}_{}".format(str(class_id), str(obj.pass_index))
        idmask_node.index = obj.pass_index
        self.scene.node_tree.links.new(self.renderlayers_node.outputs["IndexOB"], idmask_node.inputs["ID value"])

        file_output_node = self.scene.node_tree.nodes.new("CompositorNodeOutputFile")
        file_output_node.name = "fileout_{}_{}".format(str(class_id), obj.pass_index)
        outpath = os.path.join(self.dest_dir, 'cam_{}_obj_{}_{}'.format(0, class_id, obj.pass_index))
        file_output_node.base_path = outpath
        self.scene.node_tree.links.new(idmask_node.outputs["Alpha"], file_output_node.inputs["Image"])

        self.outf.write('{} {} {}\n'.format(outpath, class_id, obj.pass_index))
        self.outf.flush()

        self.cur_pass += 1

    def __del__(self):
        self.outf.close()



class ObjectAugmenter:
    def __init__(self, cfg):
        self.cfg = cfg

    def runtime_augment_rot(self, obj):
        rot_x = 0
        rot_y = 0
        rot_z = np.random.uniform(-pi/12, pi/12)
        utils.rotateObj(obj, (rot_x, rot_y, rot_z))
        return obj



