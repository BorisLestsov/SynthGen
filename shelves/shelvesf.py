import bpy
import package.utils as utils


def loadShelf(loader, heights=[2,1.5,1,1], scale_d=[2,1.5,1,1,1], scale_l=0.7):
    shelf_bot_name = "cgaxis_models_32_10_15.003" 
    shelf_mid_name = "cgaxis_models_32_10_15.006" 
    shelf_top_name = "cgaxis_models_32_10_15.010" 

    places = []

    i = 0
    base = loader.load(shelf_bot_name)
    utils.resizeObj(base, (scale_l,scale_d[i],1))
    i += 1

    prev_obj_top = None
    for h_coef in heights:   
        obj = loader.load(shelf_mid_name)
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

        obj = loader.load(shelf_top_name)
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
