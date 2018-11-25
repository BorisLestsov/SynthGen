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
    bpy.ops.object.add(type='CAMERA', location=(0, -3.5, 0))
    cam = bpy.context.object
    cam.rotation_euler = Euler((pi/2, 0, 0), 'XYZ')
    # Make this the current camera
    bpy.context.scene.camera = cam


    objloader = utils.ObjectLoader(assets_blend_path, object_dir)
    
    loadShelf(objloader)

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




def loadShelf(loader, heights=[2,1,1], scale=0.5):
    shelf_bot_name = "cgaxis_models_32_10_15.003" 
    shelf_mid_name = "cgaxis_models_32_10_15.006" 
    shelf_top_name = "cgaxis_models_32_10_15.010" 

    base = loader.load(shelf_bot_name)
    utils.resizeObj(base, (scale,1,1))

    heights = []

    prev_obj = None
    for h_coef in heights:   
        obj = loader.load(shelf_mid_name)
        #obj.location.z += (obj.dimensions.y)/4
        utils.resizeObj(obj, (scale,1,h_coef))
        if not prev_obj is None:
            obj.location.z += prev_obj.location.z
        else:
            obj.location.z += base.dimensions.y
        prev_obj = obj

        obj = loader.load(shelf_top_name)
        utils.resizeObj(obj, (scale,1,1))
        obj.location.z += prev_obj.location.z+prev_obj.dimensions.y
        prev_obj = obj

        heights.append(obj.location.z)


    return heights


if __name__ == '__main__':
    main()