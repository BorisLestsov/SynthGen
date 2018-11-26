import bpy

# Check if script is opened in Blender program
import os, sys
if(bpy.context.space_data == None):
    cwd = os.path.dirname(os.path.abspath(__file__))
else:
    cwd = os.path.dirname(bpy.context.space_data.text.filepath)

sys.path.append(cwd)
import utils

from math import pi
from mathutils import Euler
tau = 2*pi



assets_blend_path = "./assets/model_assets.blend"
object_dir = "/Object/"


def main():
    # Remove all elements
    utils.removeAll()

    # Create camera
    bpy.ops.object.add(type='CAMERA', location=(0, -3.5, 1))
    cam = bpy.context.object
    cam.rotation_euler = Euler((pi/2, 0, 0), 'XYZ')
    # Make this the current camera
    bpy.context.scene.camera = cam


    objloader = utils.ObjectLoader(assets_blend_path, object_dir)
    
    places = loadShelf(objloader)

    mat = bpy.data.materials.new(name="DegugMat")
    mat.diffuse_color = (1, 0, 0)

    for pt1, pt2 in places:
        bpy.ops.mesh.primitive_ico_sphere_add(location=pt1, size=0.02)
        sph1 = bpy.context.active_object
        sph1.data.materials.append(mat)
        bpy.ops.mesh.primitive_ico_sphere_add(location=pt2, size=0.02)
        sph2 = bpy.context.active_object
        sph2.data.materials.append(mat)

    #obj = objloader.load("cgaxis_models_32_10_05.010")
    #obj = utils.moveObj(obj, (0.5, 0, 0))
    
    #obj2 = objloader.load("cgaxis_models_32_10_05.010")


    






    # Specify folder to save rendering
    render_folder = os.path.join(cwd, 'result')
    if(not os.path.exists(render_folder)):
        os.mkdir(render_folder)

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




def loadShelf(loader, heights=[2,1,1,1], scale=(0.4,0.5)):
    shelf_bot_name = "cgaxis_models_32_10_15.003" 
    shelf_mid_name = "cgaxis_models_32_10_15.006" 
    shelf_top_name = "cgaxis_models_32_10_15.010" 

    scale_l, scale_d = scale

    places = []

    base = loader.load(shelf_bot_name)
    utils.resizeObj(base, (scale_l,scale_d,1))

    prev_obj = None
    for h_coef in heights:   
        obj = loader.load(shelf_mid_name)
        utils.resizeObj(obj, (scale_l,scale_d,h_coef))
        back_offset = obj.dimensions.z
        if not prev_obj is None:
            obj.location.z += prev_obj.location.z
        else:
            obj.location.z += base.dimensions.y
            
            right_pt = (-base.dimensions.z/2*0.93, -back_offset, base.dimensions.y)
            left_pt = (base.dimensions.z/2*0.93, -base.dimensions.x*0.9, base.dimensions.y)
            places.append([right_pt, left_pt])

        prev_obj = obj

        obj = loader.load(shelf_top_name)
        utils.resizeObj(obj, (scale_l,scale_d,1))
        obj.location.z += prev_obj.location.z+prev_obj.dimensions.y
        prev_obj = obj

        right_pt = (-obj.dimensions.z/2, -back_offset, obj.location.z)
        left_pt = (obj.dimensions.z/2, -obj.dimensions.x, obj.location.z)

        places.append([right_pt, left_pt])

    return places


if __name__ == '__main__':
    main()