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
            scene.use_nodes = True # Ensure compositor runs
        else:
            scene.use_nodes = True
            tree = scene.node_tree
            
        links = tree.links
        
        for n in tree.nodes:
            tree.nodes.remove(n)
            
        render_layers = tree.nodes.new('CompositorNodeRLayers')
        
        # Depth via Viewer Node to ensure it gets generated as a standard OPEN_EXR
        # (avoiding CompositorNodeOutputFile multilayer restrictions)
        viewer_node = tree.nodes.new('CompositorNodeViewer')
        links.new(render_layers.outputs['Depth'], viewer_node.inputs[0])
        
        # In Blender 5.1, when executing in background mode, the compositor might not evaluate 
        # file output nodes if the node group is not the active scene node tree.
        # But EEVEE/CYCLES might still fail if there's no actual output. 
        # Using CYCLES and saving explicitly via save_render as fallback.
        
        # Render Frame
        scene.frame_set(1)
        
        # Explicitly set the main render path for RGB (bypassing compositor quirks in background mode)
        scene.render.image_settings.file_format = 'PNG'
        scene.render.filepath = os.path.join(output_dir, "rgb.png")
        
        # Execute render (write_still=True forces the main composite/scene to save to filepath)
        bpy.ops.render.render(write_still=True)
        
        # After render, save the depth explicitly from the Viewer Node as a standard EXR
        scene.render.image_settings.file_format = 'OPEN_EXR'
        scene.render.image_settings.color_depth = '32'
        if 'Viewer Node' in bpy.data.images:
            depth_img = bpy.data.images['Viewer Node']
            depth_img.save_render(filepath=os.path.join(output_dir, "depth.exr"))
        else:
            raise RuntimeError("Viewer Node did not generate an image for depth!")
        
        # Pointcloud export (pure code fixture)
        # We select all visible mesh objects and export them as a .ply
        bpy.ops.object.select_all(action='DESELECT')
        for obj in scene.objects:
            if obj.type == 'MESH' and not obj.hide_render:
                obj.select_set(True)
                
        ply_path = os.path.join(output_dir, "pointcloud.ply")
        # Export PLY
        bpy.ops.wm.ply_export(filepath=ply_path, export_selected_objects=True, ascii_format=True)

        
        if not os.path.exists(os.path.join(output_dir, "depth.exr")):
            raise FileNotFoundError(f"CRITICAL FAILURE: Depth pass was not generated for {output_dir}")
