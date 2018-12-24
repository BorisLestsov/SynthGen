import sys, os

GLOBAL_CONF = {
    "num_samples": 5,
    "seed": 0,

    "scene_save_path": "./scenes/main.blend",
    "assets_blend_path" : "./assets/model_assets.blend",
    "object_dir" : "/Object/",
    "render_folder": os.path.join('.', 'result'),
    "output_folder": os.path.join('.', 'output'),
    "output_format": 'render_{}',

    "objlist_file": "./objlist.txt",
    "texlist_file": "./texlist.txt",
    "tex_prefix": "./tex/",

    "scene_name" : "Scene",
    "resolution_x" : 1080,
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


def init_conf(conf):
    if not conf["is_inited"]:
        conf['result_resolution_x'] = int(conf['resolution_x'] * conf['resolution_percentage'])/100
        conf['result_resolution_y'] = int(conf['resolution_y'] * conf['resolution_percentage'])/100

        conf["num_raw_classes"] = 0
        with open(conf["objlist_file"]) as f:
            for line in f:
                if len(line.split()) != 0:
                    conf["num_raw_classes"] += 1
        conf["is_inited"] = True


init_conf(GLOBAL_CONF)
