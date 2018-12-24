import bpy
import mathutils
import numpy as np

def transform_obj(obj):
    try:
        bpy.context.scene.objects.active = obj
        bpy.ops.object.mode_set(mode = 'EDIT') 
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

        coord_arr = np.array([vert.co for vert in obj.data.vertices])
        min = np.min(coord_arr[:, 1])
        idx = ((coord_arr[:, 1] - min)<0.00001).nonzero()[0]
        print(idx)
        c = np.mean(coord_arr[idx], axis=0).tolist()
        c = obj.matrix_world*mathutils.Vector(c)

        saved_location = bpy.context.scene.cursor_location.copy()
        bpy.context.scene.cursor_location = c
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        #bpy.context.scene.cursor_location = saved_location
        obj.select = False
    except Exception as e:
        print(e)


    
selected = bpy.context.selected_objects
for obj in selected:
    print(obj)
    transform_obj(obj)
