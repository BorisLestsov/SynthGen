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
        self.text = sampler.text
        self.scene = bpy.data.scenes[self.cfg['scene_name']]


    def setupLighting(self):

        mat = self.text.getLightingMat(strength=np.random.randint(12, 30), 
                                       color=np.random.uniform(0.8, 1, size=(3,)).tolist()+[1])

        bpy.ops.mesh.primitive_plane_add()
        plane = bpy.context.active_object
        utils.resizeObj(plane, (0.1, 2, 1))
        utils.moveObjAbs(plane, (0, 0, 4))

        plane.data.materials.append(mat)

        for i in range(3):
            obj = plane.copy()
            self.scene.objects.link(obj)
            utils.shiftObj(obj, ( plane.dimensions.x*i*5, 0, 0))
            obj = plane.copy()
            self.scene.objects.link(obj)
            utils.shiftObj(obj, (-plane.dimensions.x*i*5, 0, 0))


    def lin_sol(self, x1, x2, y1, y2):
        a = (y1-y2)/(x1-x2)
        b = y2 - a*x2
        return a, b


    def setupCamera(self):
        camera_loc_x = np.random.uniform(-1.5, 1.5)
        camera_loc_y = np.random.uniform(-4.95, -2)
        camera_loc_z = np.random.uniform(0.8, 2)

        a, b = self.lin_sol(2, 5, pi/4, pi/18)
        adiff =  a*(-camera_loc_y)+b
        alpha = np.arctan(-camera_loc_y/camera_loc_x)
        if camera_loc_x > 0:
            alpha = pi/2 - alpha
        else:
            alpha = -pi/2 - alpha

        camera_rot_x = np.random.uniform(pi/2-pi/12, pi/2+pi/36)
        camera_rot_y = np.random.uniform(0   -pi/36, 0   +pi/36)
        camera_rot_z = np.random.uniform(alpha-adiff, alpha+adiff)


        # Create camera
        bpy.ops.object.add(type='CAMERA', location=(camera_loc_x, camera_loc_y, camera_loc_z))
        self.cam = bpy.context.object
        utils.setObjRot(self.cam, (camera_rot_x, camera_rot_y, camera_rot_z))
        # Make this the current camera
        bpy.context.scene.camera = self.cam


    def setupEnv(self):

        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.active_object
        utils.resizeObj(cube, (5, 5, 2.5))
        utils.moveObjAbs(cube, (0, 0, cube.dimensions.z/2-0.001))

        bpy.ops.mesh.primitive_plane_add()
        plane = bpy.context.active_object
        utils.resizeObj(plane, (5, 5, 1))

        
        mat = self.text.getRandomTexWithProp(object="floor")
        self.text.applyMatToObjWithTex(plane, mat)
        
        mat = self.text.getRandomTexWithProp(object="wall")
        self.text.applyMatToObjWithTex(cube, mat)



    def loadShelf(self, loader, heights=[2,1.5,1,1], scale_d=[2,1.5,1,1,1], scale_l=0.7):
        shelf_bot_name = "cgaxis_models_32_10_15.003" 
        shelf_mid_name = "cgaxis_models_32_10_15.006" 
        shelf_top_name = "cgaxis_models_32_10_15.010" 

        places = []
        
        mat = self.text.getDiffuseMat(np.random.uniform(0.25, 1, size=4).tolist())

        i = 0
        base = loader.load(shelf_bot_name, link=False)
        self.text.applyMatToObj(base, mat)
        utils.resizeObj(base, (scale_l,scale_d[i],1))
        i += 1

        prev_obj_top = None
        for h_coef in heights:   
            obj = loader.load(shelf_mid_name, link=False)
            self.text.applyMatToObj(obj, mat)
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
            self.text.applyMatToObj(obj, mat)
            utils.resizeObj(obj, (scale_l,scale_d[i],1))
            obj.location.z += prev_obj_mid.location.z+prev_obj_mid.dimensions.y
            prev_obj_top = obj

            left_pt = [-obj.dimensions.z/2, -back_offset, obj.location.z]
            right_pt = [obj.dimensions.z/2, -obj.dimensions.x*0.9, obj.location.z]

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


