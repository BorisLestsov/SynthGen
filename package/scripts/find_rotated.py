import bpy
import mathutils
from math import pi
import numpy as np

def transform_obj(obj):
    try:
        bpy.context.scene.objects.active = obj
        bpy.ops.object.mode_set(mode = 'EDIT') 
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

        rot_vec = np.array((obj.rotation_euler.x, 
                            obj.rotation_euler.y, 
                            obj.rotation_euler.z))
        if not np.any(rot_vec>pi/4):
            obj.select = False
    except Exception as e:
        print(e)


    
selected = bpy.context.selected_objects
for obj in selected:
    print(obj)
    transform_obj(obj)
