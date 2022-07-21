import bpy
import math

import visualization.Blender.blender_utils as bu
import visualization.Blender.config as cfg

def create_instruction(name, location):
    bpy.ops.mesh.primitive_cube_add(size=cfg.BASE_SIZE, enter_editmode=False, align='WORLD', 
                                        location=location, scale=(1, 1, 1))
    cube = bpy.context.selected_objects[0]
    cube.name = name
    bu.assign_material(cube,"mat_instruction")
    bu.scale_object((cfg.CUBE_SIZE, cfg.CUBE_SIZE, cfg.CUBE_SIZE))
    return cube

def create_memory(name, location):
    bpy.ops.mesh.primitive_cube_add(size=cfg.BASE_SIZE, enter_editmode=False, align='WORLD', 
                                        location=location, scale=(1, 1, 1))
    cube = bpy.context.selected_objects[0]
    cube.name = name
    bu.assign_material(cube,"mat_memory")
    bu.scale_object((cfg.CUBE_SIZE, cfg.CUBE_SIZE, cfg.CUBE_SIZE))
    return cube


def create_ecall(name, location):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, 
                                            enter_editmode=False, align='WORLD', 
                                            location=location, 
                                            scale=(cfg.BASE_SIZE*0.75, cfg.BASE_SIZE*0.75, cfg.BASE_SIZE*0.75))
    sphere = bpy.context.selected_objects[0]
    sphere.name = name
    bu.assign_material(sphere,"mat_ecall")
    bu.scale_object((cfg.CUBE_SIZE, cfg.CUBE_SIZE, cfg.CUBE_SIZE))
    return sphere


def create_jump(name, location, jump_target, pc, depth,global_start):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=cfg.BASE_SIZE/2, 
                                            enter_editmode=False, align='WORLD', 
                                            location=location, 
                                            scale=(1, 1, 1))#TODO scale?
    jump = bpy.context.selected_objects[0]
    jump.name = name
    bu.assign_material(jump,"mat_jump")
    bu.scale_object((cfg.CUBE_SIZE, cfg.CUBE_SIZE, cfg.CUBE_SIZE))

    #create jump curve TODO: handle duplicate
    create_curve(radius=cfg.BASE_SIZE, location=location)
    curve = bpy.context.selected_objects[0]
    curve.name = name + "_branch"
    curve.data.bevel_depth = 0.02
    target_x = (((jump_target-global_start) - (pc-global_start))* cfg.INSTRUCTION_DISTANCE)+cfg.INSTRUCTION_DISTANCE/2
    target_point = (target_x,0, 0)#todo ignore depth for now
    bu.connect_points_with_curve(curve,(0,0,0),target_point)
    bu.assign_material(curve,"mat_jump_curve")
    return (jump,curve)

def create_curve(radius, location):
    curve = bpy.ops.curve.primitive_nurbs_path_add(radius=radius, enter_editmode=False, align='WORLD', 
                                                location=location, scale=(1, 1, 1))
    return curve

def create_timeline_branch(name, location, x_target_offset, y_target_offset):
    #create jump curve TODO: handle duplicate
    create_curve(radius=cfg.BASE_SIZE, location=location)
    curve = bpy.context.selected_objects[0]
    curve.name = name
    curve.data.bevel_depth = 0.02
    target_point = (x_target_offset,y_target_offset, 0)
    bu.connect_runs_with_curve(curve,(0,0,0),target_point)
    bu.assign_material(curve,"mat_timeline_curve")
    return (curve)



def create_branch(name, location, jump_target, pc, depth, branch_edge,global_start):
    "create and return a branch object. If branch_edge is true, also create and return a branch curve"
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=cfg.BASE_SIZE/2, 
                                            enter_editmode=False, align='WORLD', 
                                            location=location, 
                                            scale=(1, 1, 1))

    branch = bpy.context.selected_objects[0]
    branch.name = name
    bu.assign_material(branch,"mat_branch")
    bu.scale_object((cfg.CUBE_SIZE, cfg.CUBE_SIZE, cfg.CUBE_SIZE))

    curve = None; #TODO improve handling of false case
    if(branch_edge):
        #create branch curve TODO: handle duplicate
        create_curve(radius=cfg.BASE_SIZE, location=location)
        curve = bpy.context.selected_objects[0]
        curve.name = name + "_branch"
        target_x = (((jump_target-global_start) - (pc-global_start))* cfg.INSTRUCTION_DISTANCE)+cfg.INSTRUCTION_DISTANCE/2
        target_point = (target_x,0, 0)#todo set depth diff
        bu.connect_points_with_curve(curve,(0,0,0),target_point)
        curve.data.bevel_depth = 0.02
        bu.assign_material(curve,"mat_branch_curve")
    return (branch, curve)

def create_load(name, location):
    bpy.ops.mesh.primitive_cylinder_add(radius=cfg.BASE_SIZE/2, depth=cfg.BASE_SIZE, enter_editmode=False, align='WORLD', 
                                            location=location, scale=(1, 1, 1))
    cyl = bpy.context.selected_objects[0]
    cyl.name = name
    bu.assign_material(cyl,"mat_load")
    bu.scale_object((cfg.CUBE_SIZE, cfg.CUBE_SIZE, cfg.CUBE_SIZE))
    return cyl

def create_store(name, location):
    bpy.ops.mesh.primitive_cylinder_add(radius=cfg.BASE_SIZE/2, depth=cfg.BASE_SIZE, enter_editmode=False, align='WORLD', 
                                            location=location, scale=(1, 1, 1))
    cyl = bpy.context.selected_objects[0]
    cyl.name = name
    bu.assign_material(cyl,"mat_store")
    bu.scale_object((cfg.CUBE_SIZE, cfg.CUBE_SIZE, cfg.CUBE_SIZE))
    return cyl

def create_csr(name, location):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, 
                                            enter_editmode=False, align='WORLD', 
                                            location=location, 
                                            scale=(cfg.BASE_SIZE*0.75, cfg.BASE_SIZE*0.75, cfg.BASE_SIZE*0.75))
    sphere = bpy.context.selected_objects[0]
    sphere.name = name
    bu.assign_material(sphere,"mat_csr")
    bu.scale_object((cfg.CUBE_SIZE, cfg.CUBE_SIZE, cfg.CUBE_SIZE))
    return sphere

def create_active_marker(name, run):
    bpy.ops.mesh.primitive_cone_add(vertices=4, enter_editmode=False, align='WORLD', 
                                        location=(0, run*cfg.RUN_DISTANCE, cfg.DEPTH_MULT), 
                                        scale=(1, 1, 1))
    marker = bpy.context.selected_objects[0]
    marker.name = name
    bu.assign_material(marker,"mat_marker")
    bu.scale_object((cfg.CUBE_SIZE, cfg.CUBE_SIZE, cfg.CUBE_SIZE))
    marker.rotation_euler[1] = 3.14159
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    marker.rotation_euler[2] = 0
    marker.keyframe_insert(data_path="rotation_euler", frame=0, index=2)

    return marker

def create_camera(run):
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, run*cfg.RUN_DISTANCE, cfg.CAM_DISTANCE), 
                                rotation=(0, 0, math.radians(90)), scale=(1, 1, 1))
    bpy.context.selected_objects[0].name = f"cam_{run}"
    return bpy.context.selected_objects[0]


def create_block(cf_block, run, global_start):
    location = ((cf_block.block_start - global_start)*cfg.INSTRUCTION_DISTANCE, run*cfg.RUN_DISTANCE, cfg.BLOCK_Z)
    x_range = (cf_block.block_end-cf_block.block_start)*cfg.INSTRUCTION_DISTANCE
    y_range = cfg.RUN_DISTANCE - cfg.RUN_DISTANCE/8
    center_offset = -(global_start-cf_block.block_start)*cfg.INSTRUCTION_DISTANCE

    bpy.ops.mesh.primitive_cube_add(size=cfg.BASE_SIZE, enter_editmode=False, align='WORLD', 
                                        location=location, scale=(1, 1, 1))
    cube = bpy.context.selected_objects[0]
    cube.name = f"cf_block_{hex(cf_block.block_start)}_{hex(cf_block.block_end)}_{run}"
    bu.assign_material(cube,"mat_cf_block")
    bu.scale_object((max(x_range,0.2), y_range, cfg.CUBE_SIZE*2))
    
    bu.translate_object((x_range/2, 0, 0))
    #bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return cube

def create_function(name:str, function_start:int, function_end:int, global_start:int, text_scale:float=1):
    x_pos = (function_start - global_start)*cfg.INSTRUCTION_DISTANCE
    location = (x_pos, -8.5*cfg.CUBE_SIZE, cfg.BLOCK_Z)
    x_range = (function_end-function_start+1)*cfg.INSTRUCTION_DISTANCE - 0.1
    y_range = 8 * cfg.CUBE_SIZE
    function_name = f"function_{name}"
    location_text = (x_pos+x_range/2,#+len(name)*text_scale/2, #one letter uses about half as much space as a cube 
                    -12.5*cfg.CUBE_SIZE-y_range/2, 
                    cfg.BLOCK_Z+cfg.CUBE_SIZE*3)

    bpy.ops.mesh.primitive_cube_add(size=cfg.BASE_SIZE, enter_editmode=False, align='WORLD', 
                                        location=location, scale=(1, 1, 1))
    cube = bpy.context.selected_objects[0]
    cube.name = function_name
    bu.assign_material(cube,"mat_function")
    bu.scale_object((x_range, y_range, cfg.CUBE_SIZE*4))#'INDIVIDUAL_ORIGINS'
    bu.translate_object((x_range/2, 0, 0))
    #bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    text_obj = bu.create_text(location_text, f"text_function_{name}", name, 1, "mat_text")
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    bu.rotate_object(1.5708)
    scale = (math.sqrt(x_range)/(len(name)/4))*text_scale
    bu.scale_object((scale, scale, 1),'INDIVIDUAL_ORIGINS')

    return cube

def create_pc_text(global_start, min_pc, max_pc):
    print(f"Creating  pc text objects [START: {hex(global_start)}] | [RANGE:{hex(min_pc)} - {hex(max_pc)}]")
    for c_pc in range(int(min_pc/4),int(max_pc/4)+1):
        #create pc text object
        location=((c_pc*4-global_start)*cfg.INSTRUCTION_DISTANCE+cfg.INSTRUCTION_DISTANCE/2, 
                    0*cfg.RUN_DISTANCE, 
                    cfg.TEXT_HEIGHT)
        text_pc = bu.create_text(location, f"pc_{hex(c_pc*4)}", f"{hex(c_pc*4)[2:]}", 1, "mat_text")
