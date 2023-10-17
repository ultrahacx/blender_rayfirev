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


        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = selected_objects[0]
        for obj in selected_objects:
            if obj.animation_data is not None:
                obj.animation_data_clear()

            vg = obj.vertex_groups.new(name=obj.name)
            vg.add(range(len(obj.data.vertices)), 1.0, 'REPLACE')
            obj.select_set(True)
        
        bpy.ops.object.join()

        obj = bpy.context.view_layer.objects.active

        matrix = obj.matrix_world.copy()
        for vert in obj.data.vertices:
            vert.co = matrix @ vert.co
        obj.matrix_world.identity()
        
        obj.parent = rig
        obj.sollum_type = 'sollumz_drawable_model'
        obj.sollumz_lods.add_empty_lods()
        obj.sollumz_lods.set_lod_mesh("sollumz_high", obj.data)
        obj.sollumz_lods.set_active_lod("sollumz_high")
        
        rig.skinned_model_properties.high.unknown_1 = len(rig.data.bones)
        rig.skinned_model_properties.high.flags = 1
        
        armature_mod = obj.modifiers.new("skel", "ARMATURE")
        armature_mod.object = rig

        self.report({'INFO'}, f'Created new skinned drawable {rig.name} successfully')

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
        row.operator("ultrahacx.rayfire_skinned_create")

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
    bpy.utils.register_class(ULTRAHACX_OT_rayfire_create)
    bpy.utils.register_class(ULTRAHACX_OT_rayfire_skinned_create)
    bpy.utils.register_class(ULTRAHACX_PT_VIEW_PANEL)
    
def unregister():
    del bpy.types.Scene.rayfire_start_frame
    del bpy.types.Scene.rayfire_end_frame
    bpy.utils.unregister_class(ULTRAHACX_OT_rayfire_create)
    bpy.utils.unregister_class(ULTRAHACX_OT_rayfire_skinned_create)
    bpy.utils.unregister_class(ULTRAHACX_PT_VIEW_PANEL)