import sys, os
import json

GLOBAL_CONF = {
    "num_samples": 100,
    "seed": 0,

    "scene_save_path": "./result/main.blend",
    "assets_blend_path" : "./assets/model_assets.blend",
    "object_dir" : "/Object/",
    "render_folder": os.path.join('.', 'result'),
    "output_folder": os.path.join('.', 'output'),
    "output_format": 'render_{}',

    "objlist_file": "./objlist.txt",
    "texlist_file": "./texlist.txt",
    "tex_prefix": "./tex/",
    "logger_name": "logger", 

    "scene_name" : "Scene",
    "scene_name_masks" : "SceneMasks",
    "resolution_x" : 1920,
    "resolution_y" : 1920,
    "result_resolution_x" : None,
    "result_resolution_y" : None,
    "resolution_percentage" : 15, 
    "samples" : 32,
    "use_gpu": False,

    "num_raw_classes": None,
    #"total_classes": None,

    "is_inited": False
}


def init_conf(cfg):
    if not cfg["is_inited"]:
        cfg['result_resolution_x'] = int(cfg['resolution_x'] * cfg['resolution_percentage']/100)
        cfg['result_resolution_y'] = int(cfg['resolution_y'] * cfg['resolution_percentage']/100)

        with open(cfg["objlist_file"]) as f:
            cfg["num_raw_classes"] = len(json.load(f))+1
        
        cfg["is_inited"] = True


init_conf(GLOBAL_CONF)
