import bpy
import os

class RenderPipeline:
    def __init__(self, config):
        self.config = config
        
    def render(self, output_dir):
        scene = bpy.context.scene
        
        # Ensure nodes are setup and Z pass is enabled
        scene.view_layers["ViewLayer"].use_pass_z = True
        
        # Support Blender 5.x Compositor API
        if hasattr(scene, 'compositing_node_group'):
            scene.compositing_node_group = bpy.data.node_groups.new('Compositor', 'CompositorNodeTree')
            tree = scene.compositing_node_group
        else:
            scene.use_nodes = True
            tree = scene.node_tree
            
        links = tree.links
        
        for n in tree.nodes:
            tree.nodes.remove(n)
            
        render_layers = tree.nodes.new('CompositorNodeRLayers')
        
        # RGB
        file_output_rgb = tree.nodes.new('CompositorNodeOutputFile')
        file_output_rgb.directory = output_dir
        if hasattr(file_output_rgb, 'file_slots'):
            file_output_rgb.file_slots[0].path = "rgb"
        links.new(render_layers.outputs['Image'], file_output_rgb.inputs[0])
        
        # Depth
        file_output_depth = tree.nodes.new('CompositorNodeOutputFile')
        file_output_depth.directory = output_dir
        if hasattr(file_output_depth, 'file_slots'):
            file_output_depth.file_slots[0].path = "depth"
        file_output_depth.format.file_format = 'OPEN_EXR_MULTILAYER'
        links.new(render_layers.outputs['Depth'], file_output_depth.inputs[0])
        
        # Render Frame
        scene.frame_set(1)
        
        # Explicitly set the main render path for RGB (bypassing compositor quirks in background mode)
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = os.path.join(output_dir, "rgb.png")
        
        # Execute render (write_still=True forces the main composite/scene to save to filepath)
        bpy.ops.render.render(write_still=True)
        
        # Pointcloud export (pure code fixture)
        # We select all visible mesh objects and export them as a .ply
        bpy.ops.object.select_all(action='DESELECT')
        for obj in scene.objects:
            if obj.type == 'MESH' and not obj.hide_render:
                obj.select_set(True)
                
        ply_path = os.path.join(output_dir, "pointcloud.ply")
        # Export PLY
        bpy.ops.wm.ply_export(filepath=ply_path, export_selected_objects=True)

        
        # Blender's CompositorNodeOutputFile adds frame numbers (e.g. depth0001.exr). 
        # We rename them to exactly match schemas.
        try:
            os.rename(os.path.join(output_dir, "depth0001.exr"), os.path.join(output_dir, "depth.exr"))
        except FileNotFoundError:
            pass # Depending on blender settings it might not append frame number
