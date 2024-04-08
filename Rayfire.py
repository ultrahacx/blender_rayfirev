import bpy

bl_info = {
    "name": "Rayfire Creator",
    "author": "ultrahacx",
    "version": (1, 1),
    "blender": (3, 6, 0),
    "location": "View3D > N",
    "description": "Create GTAV Rayfire Sollumz drawable in a single click",
    "category": "",
}


def add_bone_flags(armature):
    for pBone in armature.pose.bones:
        new_flag = pBone.bone.bone_properties.flags.add()
        new_flag.name = "RotX"
        new_flag = pBone.bone.bone_properties.flags.add()
        new_flag.name = "RotY"
        new_flag = pBone.bone.bone_properties.flags.add()
        new_flag.name = "RotZ"
        new_flag = pBone.bone.bone_properties.flags.add()
        new_flag.name = "TransX"
        new_flag = pBone.bone.bone_properties.flags.add()
        new_flag.name = "TransY"
        new_flag = pBone.bone.bone_properties.flags.add()
        new_flag.name = "TransZ"


def join_objects(active_object, objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        if obj.animation_data is not None:
            obj.animation_data_clear()

        vg = obj.vertex_groups.new(name=obj.name)
        vg.add(range(len(obj.data.vertices)), 1.0, 'REPLACE')
        obj.select_set(True)
    bpy.context.view_layer.objects.active = active_object
    bpy.ops.object.join()
    return bpy.context.view_layer.objects.active


def create_armature_from_objects(armature, objs):
    #togle to edit mode to add bones to armature
    bpy.ops.object.editmode_toggle()

    parent_bone = None
    for obj in objs:
            obj.name = obj.name.replace(".","_")
            if parent_bone is None:
                current_bone = armature.edit_bones.new("root")
            
                current_bone.head = [0, 0, 0]
                current_bone.tail = [0, 0.1, 0]
                parent_bone = current_bone
            
            current_bone = armature.edit_bones.new(obj.name)
            
            current_bone.head = [0, 0, 0]
            current_bone.tail = [0, 0.1, 0]
            
            current_bone.translate(obj.location)
            
            current_bone.parent = parent_bone
            current_bone.use_connect = False

    bpy.ops.object.editmode_toggle()


class ULTRAHACX_OT_rayfire_create(bpy.types.Operator):
    bl_idname = "ultrahacx.rayfire_create"
    bl_label = "Create rayfire drawable"
    bl_action = "Create sollumz rayfire drawable"

    def execute(self, context):
        selected_objects = context.selected_objects
        if len(selected_objects) <= 0:
            self.report({'ERROR'}, 'No objects selected')
            return {'FINISHED'}

        armature = bpy.data.armatures.new("rayfire_armature")
        rig = bpy.data.objects.new("rayfire_armature", armature)
        bpy.data.collections[selected_objects[0].users_collection[0].name].objects.link(rig)

        context.view_layer.objects.active = rig
        rig.sollum_type = 'sollumz_drawable'

        #set the currect frame to 0
        bpy.context.scene.frame_set(0)

        #togle to edit mode to add bones to armature
        bpy.ops.object.editmode_toggle()

        parent_bone = None

        for obj in selected_objects:
            obj.name = obj.name.replace(".","_")
            if parent_bone is None:
                current_bone = armature.edit_bones.new("root")
            
                current_bone.head = [0, 0, 0]
                current_bone.tail = [0, 0.1, 0]
                parent_bone = current_bone
            
            current_bone = armature.edit_bones.new(obj.name)
            
            current_bone.head = [0, 0, 0]
            current_bone.tail = [0, 0.1, 0]
            
            current_bone.translate(obj.location)
            
            current_bone.parent = parent_bone
            current_bone.use_connect = False

                
        bpy.ops.object.editmode_toggle()

        add_bone_flags(rig)

        for bone in rig.pose.bones:
            if bpy.data.objects.get(bone.name):
                crc = bone.constraints.new('COPY_TRANSFORMS')
                crc.target = bpy.data.objects[bone.name]
                crc.target_space = 'WORLD'
                crc.owner_space = 'POSE'

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = rig
        rig.select_set(True)
        bpy.ops.nla.bake(frame_start=context.scene.rayfire_start_frame, frame_end=context.scene.rayfire_end_frame, only_selected=False, visual_keying=True, clear_constraints=True, use_current_action=False, bake_types={'POSE'})


        for obj in selected_objects:
            if obj.animation_data is not None:
                obj.animation_data_clear()
            
            matrix = obj.matrix_world.copy()
            for vert in obj.data.vertices:
                vert.co = matrix @ vert.co
            obj.matrix_world.identity()
            
            obj.parent = rig
            obj.sollum_type = 'sollumz_drawable_model'
            obj.sollumz_lods.add_empty_lods()
            obj.sollumz_lods.set_lod_mesh("sollumz_high", obj.data)
            obj.sollumz_lods.set_active_lod("sollumz_high")
            
            crc = obj.constraints.new('CHILD_OF')
            crc.target = rig
            crc.subtarget = obj.name
            crc.set_inverse_pending = True

        self.report({'INFO'}, f'Created new drawable {rig.name} successfully')

        return {'FINISHED'}
    

class ULTRAHACX_OT_rayfire_skinned_create(bpy.types.Operator):
    bl_idname = "ultrahacx.rayfire_skinned_create"
    bl_label = "Create skinned rayfire drawable"
    bl_action = "Create sollumz skinned rayfire drawable"

    def execute(self, context):
        selected_objects = context.selected_objects
        if len(selected_objects) <= 0:
            self.report({'ERROR'}, 'No objects selected')
            return {'FINISHED'}

        joined_objects = []
        split_objects_list = [selected_objects[x:x+context.scene.rayfire_split_count] for x in range(0, len(selected_objects), context.scene.rayfire_split_count)]
        
        armature_index = 0

        for objects_list in split_objects_list:
            name = f"rayfire_armature_{armature_index}"
            armature = bpy.data.armatures.new(name)
            rig = bpy.data.objects.new(name, armature)
            bpy.data.collections[objects_list[0].users_collection[0].name].objects.link(rig)

            context.view_layer.objects.active = rig
            rig.sollum_type = 'sollumz_drawable'

            #set the currect frame to 0
            bpy.context.scene.frame_set(0)
            
            create_armature_from_objects(armature, objects_list)

            add_bone_flags(rig)

            for bone in rig.pose.bones:
                if bpy.data.objects.get(bone.name):
                    crc = bone.constraints.new('COPY_TRANSFORMS')
                    crc.target = bpy.data.objects[bone.name]
                    crc.target_space = 'WORLD'
                    crc.owner_space = 'POSE'

            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = rig
            rig.select_set(True)
            bpy.ops.nla.bake(frame_start=context.scene.rayfire_start_frame, frame_end=context.scene.rayfire_end_frame, only_selected=False, visual_keying=True, clear_constraints=True, use_current_action=False, bake_types={'POSE'})
            rig.select_set(False)

            joined_object_returned = join_objects(objects_list[0], objects_list)

            # Remove rigid body physics if any
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = joined_object_returned
            joined_object_returned.select_set(True)

            if joined_object_returned.rigid_body:
                bpy.ops.rigidbody.object_remove()

            bpy.ops.object.select_all(action='DESELECT')


            print("Adding modifier to joined mesh:", joined_object_returned.name)
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = joined_object_returned

            matrix = joined_object_returned.matrix_world.copy()
            for vert in joined_object_returned.data.vertices:
                vert.co = matrix @ vert.co
            joined_object_returned.matrix_world.identity()
            
            joined_object_returned.parent = rig
            joined_object_returned.sollum_type = 'sollumz_drawable_model'
            joined_object_returned.sollumz_lods.add_empty_lods()
            joined_object_returned.sollumz_lods.set_lod_mesh("sollumz_high", joined_object_returned.data)
            joined_object_returned.sollumz_lods.set_active_lod("sollumz_high")

            armature_mod = joined_object_returned.modifiers.new("skel", "ARMATURE")
            armature_mod.object = rig

            rig.skinned_model_properties.high.unknown_1 = len(rig.data.bones)
            rig.skinned_model_properties.high.flags = 1
            armature_index+=1


        self.report({'INFO'}, f'Created new skinned drawable {rig.name} successfully')

        return {'FINISHED'}


class ULTRAHACX_OT_rayfire_create_joined_vertmesh(bpy.types.Operator):
    bl_idname = "ultrahacx.rayfire_create_joined_vertmesh"
    bl_label = "Join mesh as vertex groups"
    bl_action = "Join mesh as vertex groups"

    def execute(self, context):
        selected_objects = context.selected_objects
        if len(selected_objects) <= 0:
            self.report({'ERROR'}, 'No objects selected')
            return {'FINISHED'}
        
        joined_objects = []
        joined_objects.append(join_objects(selected_objects[0], selected_objects))

        return {'FINISHED'}
        

class ULTRAHACX_PT_VIEW_PANEL(bpy.types.Panel):
    bl_label = "Rayfire Creator"
    bl_idname = "ULTRAHACX_PT_VIEW_PANEL"
    bl_category = "Rayfire"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 0

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.scene, "rayfire_start_frame")
        row = layout.row()
        row.prop(context.scene, "rayfire_end_frame")
        row = layout.row()
        row.operator("ultrahacx.rayfire_create")
        row = layout.row()
        row.prop(context.scene, "rayfire_split_count")
        row.operator("ultrahacx.rayfire_skinned_create")

        row = layout.row()
        row.operator("ultrahacx.rayfire_create_joined_vertmesh")

        row = layout.row()
        row.label(text="Liked the addon? Consider supporting me")
        row = layout.row()
        url_btn = row.operator('wm.url_open',
                     text='Github',
                     icon='URL')
        url_btn.url = 'https://github.com/ultrahacx'
        row = layout.row()
        url_btn = row.operator('wm.url_open',
                     text='Donate',
                     icon='URL')
        url_btn.url = 'https://ko-fi.com/ultrahacx'

def register():
    bpy.types.Scene.rayfire_start_frame = bpy.props.IntProperty(
        name="Start frame", default=0)
    bpy.types.Scene.rayfire_end_frame = bpy.props.IntProperty(
        name="End frame", default=250)
    bpy.types.Scene.rayfire_split_count = bpy.props.IntProperty(
        name="Split count", default=128, description="Maximum number of bones per geometry")
    bpy.utils.register_class(ULTRAHACX_OT_rayfire_create)
    bpy.utils.register_class(ULTRAHACX_OT_rayfire_skinned_create)
    bpy.utils.register_class(ULTRAHACX_OT_rayfire_create_joined_vertmesh)
    bpy.utils.register_class(ULTRAHACX_PT_VIEW_PANEL)
    
def unregister():
    del bpy.types.Scene.rayfire_start_frame
    del bpy.types.Scene.rayfire_end_frame
    bpy.utils.unregister_class(ULTRAHACX_OT_rayfire_create)
    bpy.utils.unregister_class(ULTRAHACX_OT_rayfire_skinned_create)
    bpy.utils.unregister_class(ULTRAHACX_OT_rayfire_create_joined_vertmesh)
    bpy.utils.unregister_class(ULTRAHACX_PT_VIEW_PANEL)