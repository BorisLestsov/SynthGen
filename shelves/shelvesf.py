import package.utils as utils

def loadShelf(loader, heights=[1,1,1,1,1], scale=(0.7,0.5)):
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


