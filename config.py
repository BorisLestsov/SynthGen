import sys, os

GLOBAL_CONF = {
	"num_samples": 10,

	"scene_save_path": "./scenes/main.blend",
	"assets_blend_path" : "./assets/model_assets.blend",
	"object_dir" : "/Object/",
	"render_folder": os.path.join('.', 'result'),
	"output_folder": os.path.join('.', 'output'),
	"output_format": 'render_{}',

	"objlist_file": "objlist.txt",

	"scene_name" : "Scene",
	"resolution_x" : 1080,
	"resolution_y" : 1920,
	"resolution_percentage" : 50, 
	"samples" : 32,

}