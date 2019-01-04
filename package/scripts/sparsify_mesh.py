import bpy
import mathutils
import numpy as np

def transform_obj(obj):
    try:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = obj
        obj.select = True
        bpy.ops.object.mode_set(mode = 'EDIT') 
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all()
        #bpy.ops.object.mode_set(mode = 'OBJECT')

        bpy.ops.mesh.decimate(ratio=2000/len(obj.data.vertices))
        
        #bpy.ops.object.modifier_add(type='DECIMATE')
        #obj.modifiers["Decimate"].ratio = 3000/len(obj.data.edges)
        #obj.modifier_apply(apply_as="DATA", modifier="Decimate")
        #bpy.ops.object.modifier_remove(modifier='Decimate')
        
        bpy.ops.object.mode_set(mode = 'OBJECT')
        obj.select = False
    except Exception as e:
        print(e)


    
selected = bpy.context.selected_objects
print(len(selected))
for obj in selected:
    if len(obj.data.vertices) <= 2000: continue
    transform_obj(obj)
