import bpy
import bmesh
import colorsys
import os

from math import pi
from math import radians
from math import sin, cos, pi
tau = 2*pi

import mathutils
from mathutils import Euler


import cv2
import numpy as np


def removeObject(obj):
    if obj.type == 'MESH':
        if obj.data.name in bpy.data.meshes:
            bpy.data.meshes.remove(obj.data)
        if obj.name in bpy.context.scene.objects:
            bpy.context.scene.objects.unlink(obj)
        bpy.data.objects.remove(obj)
    else:
        raise NotImplementedError('Other types not implemented yet besides \'MESH\'')


def trackToConstraint(obj, target):
    constraint = obj.constraints.new('TRACK_TO')
    constraint.target = target
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    #constraint.track_axis = 'TRACK_Z'
    constraint.up_axis = 'UP_Y'
    #constraint.owner_space = 'LOCAL'
    #constraint.target_space = 'LOCAL'

    return constraint


def target(origin=(0,0,0)):
    tar = bpy.data.objects.new('Target', None)
    bpy.context.scene.objects.link(tar)
    tar.location = origin

    return tar


def camera(origin, target=None, lens=35, clip_start=0.1, clip_end=200, type='PERSP', ortho_scale=6):
    # Create object and camera
    camera = bpy.data.cameras.new("Camera")
    camera.lens = lens
    camera.clip_start = clip_start
    camera.clip_end = clip_end
    camera.type = type # 'PERSP', 'ORTHO', 'PANO'
    if type == 'ORTHO':
        camera.ortho_scale = ortho_scale

    # Link object to scene
    obj = bpy.data.objects.new("CameraObj", camera)
    obj.location = origin
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.camera = obj # Make this the current camera

    if target: trackToConstraint(obj, target)
    return obj


def lamp(origin, type='POINT', energy=1, color=(1,1,1), target=None):
    # Lamp types: 'POINT', 'SUN', 'SPOT', 'HEMI', 'AREA'
    print('createLamp called')
    bpy.ops.object.add(type='LAMP', location=origin)
    obj = bpy.context.object
    obj.data.type = type
    obj.data.energy = energy
    obj.data.color = color

    if target: trackToConstraint(obj, target)
    return obj


def simpleScene(targetCoord, cameraCoord, sunCoord, lens=35):
    print('createSimpleScene called')

    tar = target(targetCoord)
    cam = camera(cameraCoord, tar, lens)
    sun = lamp(sunCoord, 'SUN', target=tar)

    return tar, cam, sun


def setAmbientOcclusion(ambient_occulusion=True, samples=5, blend_type='ADD'):
    # blend_type options: 'ADD', 'MULTIPLY'
    bpy.context.scene.world.light_settings.use_ambient_occlusion = ambient_occulusion
    bpy.context.scene.world.light_settings.ao_blend_type = blend_type
    bpy.context.scene.world.light_settings.samples = samples


def setSmooth(obj, level=None, smooth=True):
    if level:
        # Add subsurf modifier
        modifier = obj.modifiers.new('Subsurf', 'SUBSURF')
        modifier.levels = level
        modifier.render_levels = level

    # Smooth surface
    mesh = obj.data
    for p in mesh.polygons:
        p.use_smooth = smooth


def rainbowLights(r=5, n=100, freq=2, energy=0.1):
    for i in range(n):
        t = float(i)/float(n)
        pos = (r*sin(tau*t), r*cos(tau*t), r*sin(freq*tau*t))

        # Create lamp
        bpy.ops.object.add(type='LAMP', location=pos)
        obj = bpy.context.object
        obj.data.type = 'POINT'

        # Apply gamma correction for Blender
        color = tuple(pow(c, 2.2) for c in colorsys.hsv_to_rgb(t, 0.6, 1))

        # Set HSV color and lamp energy
        obj.data.color = color
        obj.data.energy = energy


def removeAll(scene, type=None):
    # Possible type: ‘MESH’, ‘CURVE’, ‘SURFACE’, ‘META’, ‘FONT’, ‘ARMATURE’, ‘LATTICE’, ‘EMPTY’, ‘CAMERA’, ‘LAMP’
    if type:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_by_type(type=type)
        bpy.ops.object.delete()
    else:
        # Remove all elements in scene
        bpy.ops.object.select_by_layer()
        bpy.ops.object.delete(use_global=False)

    scene.node_tree
    scene.use_nodes=True
    nodes = scene.node_tree.nodes
    for node in nodes:
        if not node.name in ["Render Layers", "Composite"]:
            nodes.remove(node)
    


def simpleMaterial(diffuse_color):
    mat = bpy.data.materials.new('Material')

    # Diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 0.9
    mat.diffuse_color = diffuse_color

    # Specular
    mat.specular_intensity = 0

    return mat


def falloffMaterial(diffuse_color):
    mat = bpy.data.materials.new('FalloffMaterial')

    # Diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.use_diffuse_ramp = True
    mat.diffuse_ramp_input = 'NORMAL'
    mat.diffuse_ramp_blend = 'ADD'
    mat.diffuse_ramp.elements[0].color = (1, 1, 1, 1)
    mat.diffuse_ramp.elements[1].color = (1, 1, 1, 0)
    mat.diffuse_color = diffuse_color
    mat.diffuse_intensity = 1.0

    # Specular
    mat.specular_intensity = 0.0

    # Shading
    mat.emit = 0.05
    mat.translucency = 0.2

    return mat


def colorRGB_256(color):
    return tuple(pow(float(c)/255.0, 2.2) for c in color)


def renderToFolder(renderFolder='rendering', renderName='render', resX=800, resY=800, resPercentage=100, animation=False, frame_end=None):
    print('renderToFolder called')
    scn = bpy.context.scene
    scn.render.resolution_x = resX
    scn.render.resolution_y = resY
    scn.render.resolution_percentage = resPercentage
    if frame_end:
        scn.frame_end = frame_end

    print(bpy.context.space_data)

    # Check if script is executed inside Blender
    if bpy.context.space_data is None:
        # Specify folder to save rendering and check if it exists
        render_folder = os.path.join(os.getcwd(), renderFolder)
        if(not os.path.exists(render_folder)):
            os.mkdir(render_folder)

        if animation:
            # Render animation
            scn.render.filepath = os.path.join(
                render_folder,
                renderName)
            bpy.ops.render.render(animation=True)
        else:
            # Render still frame
            scn.render.filepath = os.path.join(
                render_folder,
                renderName + '.png')
            bpy.ops.render.render(write_still=True)


def bmeshToObject(bm, name='Object'):
    mesh = bpy.data.meshes.new(name+'Mesh')
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.update()

    return obj



################
# My own utils #
################


def shiftObj(obj, vec):
    obj.location += mathutils.Vector(vec)
    return obj

def moveObjAbs(obj, vec):
    obj.location = mathutils.Vector(vec)
    return obj

def setObjRot(obj, angles):
    obj.rotation_euler = Euler((angles[0], angles[1], angles[2]), 'XYZ')

def addObjRot(obj, angles):
    old_rot = obj.rotation_euler
    obj.rotation_euler = Euler((old_rot.x+angles[0], old_rot.y+angles[1], old_rot.z+angles[2]), 'XYZ')

def resizeObj(obj, vals):
    obj.select=True
    bpy.ops.transform.resize(value=vals)
    obj.select=False
    return obj

colors = None
def postprocessResult(cfg):

    def find_bound(mask, axis, f):
        nonzero_ind = mask.any(axis=axis).nonzero()[0]
        return f(nonzero_ind)

    def safe_min(arr):
        return min(arr) if len(arr)!=0 else 0

    def safe_max(arr):
        return max(arr) if len(arr)!=0 else 0

    objdict = {}
    with open(os.path.join(cfg["render_folder"], "objects.txt"), 'r') as f:
        for line in f:
            path, class_idx, obj_idx = line.split()
            objdict[path] = (int(class_idx), int(obj_idx))

    num_classes = cfg["num_raw_classes"]
    if colors is None:
        global colors
        np.random.seed(0)
        colors = np.random.uniform(0.25, 1., size=(num_classes, 3))

    result = cv2.imread(os.path.join(cfg["render_folder"], "res_cam_{}.png".format(0)))
    result = np.zeros(shape=(result.shape[0], result.shape[1], num_classes), dtype=np.uint8)

    boxes = []
    f = open(os.path.join(cfg["render_folder"], "box_coords.txt"), 'w')
    for path, (class_idx, obj_idx) in objdict.items():
        maskpath = os.path.join(path, "Image0001.png")
        print(maskpath)
        mask = cv2.imread(maskpath)[..., 0]
        if mask.any() != 0:
            bbox = (find_bound(mask, 0, min), find_bound(mask, 1, min), find_bound(mask, 0, max), find_bound(mask, 1, max))
            #if (bbox[2]-bbox[0]) < 5 or (bbox[3]-bbox[1]) < 5:
            #    continue
            result[bbox[1]:bbox[3], bbox[0]:bbox[2], class_idx] |= mask[bbox[1]:bbox[3], bbox[0]:bbox[2]]
            f.write('{} {} {} {} {} {}\n'.format(obj_idx, class_idx, *bbox))
            boxes.append(bbox)
    f.close()

    np.savez_compressed(os.path.join(cfg["render_folder"], "masks.npz"), result)

    dbg = np.zeros(shape=(result.shape[0], result.shape[1], result.shape[2], 3))
    dbg[..., :] = result[..., None]
    dbg *= colors[None, None, ...]
    dbg = dbg.max(axis=2)
    for i, bbox in enumerate(boxes):
        cv2.rectangle(dbg, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 255, 255), 1)

    cv2.imwrite(os.path.join(cfg["render_folder"], "mask_res.png"), dbg)


def postprocessResultNew(cfg):

    def find_bound(mask, axis, f):
        nonzero_ind = mask.any(axis=axis).nonzero()[0]
        return f(nonzero_ind)

    def safe_min(arr):
        return min(arr) if len(arr)!=0 else 0

    def safe_max(arr):
        return max(arr) if len(arr)!=0 else 0

    objdict = {}
    with open(os.path.join(cfg["render_folder"], "objects.txt"), 'r') as f:
        for line in f:
            path, class_idx, obj_idx = line.split()
            objdict[path] = (int(class_idx), int(obj_idx))

    num_classes = cfg["num_raw_classes"]
    if colors is None:
        global colors
        np.random.seed(0)
        colors = np.random.uniform(0.25, 1., size=(num_classes, 3))

    mask = cv2.imread(os.path.join(cfg["render_folder"], "res_cam_{}_mask.exr".format(0)), 
                      cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)[:,:,2]

    print(np.unique(mask))
    
    residual = np.modf(mask)[0]
    mask[(residual>(0+0.001)) & (residual < (1-0.001))]=0
    mask = np.round(mask)
    mask = mask.astype(np.int32)

    result = np.zeros(shape=(mask.shape[0], mask.shape[1], num_classes), dtype=np.int32)

    boxes = []
    f = open(os.path.join(cfg["render_folder"], "box_coords.txt"), 'w')
    for path, (class_idx, obj_idx) in objdict.items():
        tmp_mask = mask==obj_idx
        if tmp_mask.any() != 0:
            #cv2.imwrite("tmp/dbg{}.png".format(obj_idx), tmp_mask.astype(np.uint8)*255)
            bbox = (find_bound(tmp_mask, 0, min), find_bound(tmp_mask, 1, min), find_bound(tmp_mask, 0, max), find_bound(tmp_mask, 1, max))
            #if (bbox[2]-bbox[0]) < 5 or (bbox[3]-bbox[1]) < 5:
            #    continue
            result[bbox[1]:bbox[3], bbox[0]:bbox[2], class_idx] |= tmp_mask[bbox[1]:bbox[3], bbox[0]:bbox[2]]
            f.write('{} {} {} {} {} {}\n'.format(obj_idx, class_idx, *bbox))
            boxes.append(bbox)
    f.close()

    np.savez_compressed(os.path.join(cfg["render_folder"], "masks.npz"), result)

    dbg = np.zeros(shape=(result.shape[0], result.shape[1], result.shape[2], 3))
    dbg[..., :] = result[..., None]
    dbg *= colors[None, None, ...]*255
    dbg = dbg.max(axis=2)
    for i, bbox in enumerate(boxes):
        cv2.rectangle(dbg, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (255, 255, 255), 1)

    print(np.unique(dbg), dbg.dtype)
    cv2.imwrite(os.path.join(cfg["render_folder"], "mask_res.tiff"), dbg.astype(np.uint8))



def exec_command(command, need_print=True):
    if need_print:
        print(command)
    os.system(command)

def copyResultToOutputFolder(cfg, cur_out_dir):
    dest_dir = os.path.join(cfg["output_folder"], cur_out_dir)
    command = "mkdir -p {}".format(dest_dir)
    exec_command(command)

    command = 'cp {} {} {} {} {} {} -t {}'.format(os.path.join(cfg["render_folder"], "mask_res.tiff"),
                                         os.path.join(cfg["render_folder"], "masks.npz"),
                                         os.path.join(cfg["render_folder"], "box_coords.txt"),
                                         os.path.join(cfg["render_folder"], "objects.txt"),
                                         os.path.join(cfg["render_folder"], "res_cam_{}_mask.exr".format(0)),
                                         os.path.join(cfg["render_folder"], "res_cam_{}.png".format(0)), 
                                         dest_dir)
    exec_command(command)



def clearRenderFolder(cfg):
    command = 'rm -rf {}/*'.format(cfg["render_folder"])
    exec_command(command)
