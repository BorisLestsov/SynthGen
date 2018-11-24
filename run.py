import bpy

# Check if script is opened in Blender program
import os, sys
if(bpy.context.space_data == None):
    cwd = os.path.dirname(os.path.abspath(__file__))
else:
    cwd = os.path.dirname(bpy.context.space_data.text.filepath)




if __name__ == '__main__':



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
    
    rnd.resolution_percentage = 15

    cam_list = []
    for ob in scene.objects:
        if ob.type == 'CAMERA':
            cam_list.append(ob)

    for i, cam in enumerate(cam_list):
        scene.camera = cam
        rnd.filepath = os.path.join(render_folder, 'res_cam_{}.png'.format(i))
        bpy.ops.render.render(write_still=True)

