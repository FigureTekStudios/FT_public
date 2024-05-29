import maya.cmds as cmds
import os
import re
import shutil
import json
from FT_public import FT_skincluster as skn  # Import the skincluster module from FT_public
from PySide2.QtWidgets import QFileDialog, QListView, QTreeView, QAbstractItemView, QApplication
import importlib
importlib.reload(skn)


# Use your FT Accessories directory and sourceimages path

SOURCEIMAGES_DIR = cmds.workspace(query=True, fullName=True) + "/sourceimages/"

def check_project_folder():
    project_folder = cmds.workspace(query=True, fullName=True)
    folder_name = os.path.basename(project_folder)
    print(f"Project folder: {folder_name}")  # Debug print
    pattern = r"FT_.*_[A-Za-z0-9\-]+$"
    if re.search(pattern, folder_name):
        print("Project folder is set correctly.")
        return True
    else:
        cmds.warning("Incorrect project folder. Expected format: FT_*_{FT_ID} (Set your project to A FIGURE-TEK charachter folder)")
        return False

def check_accessory_folder(accessory_folder_path):
    folder_name = os.path.basename(accessory_folder_path)
    print(f"Accessory folder: {folder_name}")  # Debug print

    # The pattern ensures the folder name ends with an underscore followed by a 10-character alphanumeric string or hyphens
    pattern = r"[A-Za-z]+_[A-Za-z0-9]+-[A-Za-z0-9]+-[A-Za-z0-9]+"
    
    if re.match(pattern, folder_name):
        print(f"Accessory folder '{folder_name}' is set correctly.")
        return True
    else:
        print(f"Incorrect accessory folder '{folder_name}'. Expected format: <name>_<FT_ID> (FT_ID should be a 10-character alphanumeric string or containing hyphens)")
        return False
        
def load_json_data(json_file_path):
    with open(json_file_path, 'r') as file:
        return json.load(file)

def get_incremented_filename(file_path):
    base, ext = os.path.splitext(file_path)
    counter = 1
    new_file_path = f"{base}_OLD{counter:04d}{ext}"
    while os.path.exists(new_file_path):
        counter += 1
        new_file_path = f"{base}_OLD{counter:04d}{ext}"
    return new_file_path

def remove_existing_assets(FT_ID):
    # Delete any accessory groups associated with the FT_ID
    accessory_groups = cmds.ls(type='transform')
    for group in accessory_groups:
        if cmds.attributeQuery('FT_ID', node=group, exists=True):
            if cmds.getAttr(f"{group}.FT_ID") == FT_ID:
                print('Removing old accessory group node:', group)
                cmds.delete(group)
    
    # Delete any materials associated with the FT_ID
    materials = cmds.ls(mat=True)
    for material in materials:
        if cmds.attributeQuery('FT_ID', node=material, exists=True):
            if cmds.getAttr(f"{material}.FT_ID") == FT_ID:
                shading_group = cmds.listConnections(material, type='shadingEngine')
                if shading_group:
                    cmds.delete(shading_group)
                # Delete file nodes and texture files associated with the material
                file_nodes = cmds.listConnections(material, type='file')
                if file_nodes:
                    for file_node in file_nodes:
                        texture_path = cmds.getAttr(f"{file_node}.fileTextureName")
                        if FT_ID in texture_path:
                            new_texture_path = get_incremented_filename(texture_path)
                            print('Renaming out of date texture map:', new_texture_path)
                            if os.path.exists(texture_path):
                                os.rename(texture_path, new_texture_path)
                        print('Deleting out of date file node:', file_node)
                        cmds.delete(file_node)
                print('Deleting out of date material node network:', material)    
                cmds.delete(material)

def import_obj(obj_file_path, FT_ID):
    # Extract the base name of the file (e.g., Handwrap_001_L)
    base_name = os.path.splitext(os.path.basename(obj_file_path))[0]
    
    # Check for existing objects with the same name and delete them
    existing_objs = cmds.ls(base_name)
    if existing_objs:
        cmds.delete(existing_objs)
    
    # Import the OBJ file
    imported_objs = cmds.file(obj_file_path, i=True, type="OBJ", rnn=True)
    imported_obj = cmds.ls(imported_objs, assemblies=True)[0]  # Get the top-level transform node
    cmds.polyNormalPerVertex(imported_obj, ufn=True)
    cmds.polySoftEdge(imported_obj, ch=0)  # Smooth normals
    
    # Ensure the imported object has the correct name
    imported_obj = cmds.rename(imported_obj, base_name)
    
    # Add FT_ID attribute to the shape
    shapes = cmds.listRelatives(imported_obj, shapes=True, fullPath=True)
    if shapes:
        for shape in shapes:
            if not cmds.attributeQuery('FT_ID', node=shape, exists=True):
                cmds.addAttr(shape, longName='FT_ID', dataType='string')
            cmds.setAttr(f"{shape}.FT_ID", FT_ID, type='string')
    
    return imported_obj

def import_material_networks(material_folder):
    for material_file in os.listdir(material_folder):
        if material_file.endswith(".ma"):
            material_file_path = os.path.join(material_folder, material_file)
            cmds.file(material_file_path, i=True, type="mayaAscii", options="v=0", loadReferenceDepth="all")

def setup_materials(materials_info, obj_materials,textures_folder, textures_subfolder):
    shading_groups = {}
    for obj, materials in obj_materials.items():
        for material in materials:
            if material not in shading_groups:
                shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{material}SG")
                cmds.connectAttr(f"{material}.outColor", f"{shading_group}.surfaceShader")
                shading_groups[material] = shading_group
            else:
                shading_group = shading_groups[material]

            cmds.sets(obj, edit=True, forceElement=shading_group)

            file_nodes = materials_info.get(material, [])
            for file_node in file_nodes:
                new_texture_name = cmds.getAttr(f"{file_node}.newTextureName")
                original_texture_path = os.path.join(textures_folder, new_texture_name)
                dest_texture_path = os.path.join(textures_subfolder, new_texture_name)
                print 

                if not os.path.exists(dest_texture_path):  # Only copy if not already copied
                    print("copy texture into the charachter sourceimages folder:", dest_texture_path)
                    shutil.copy(original_texture_path, dest_texture_path)
                  
                # Update the file node with the new texture path
                cmds.setAttr(f"{file_node}.fileTextureName", dest_texture_path, type="string")

def import_rig_weights(obj, weights_folder):

    export_joints = cmds.ls('out_C0_*_jnt')

    weights_subfolder = 'export' if export_joints else ''
    weights_file_path = os.path.join(weights_folder, weights_subfolder, f"{obj}_skin.xml")

    print("Loading weights from", weights_file_path )
    if os.path.exists(weights_file_path):
        skn.import_skin_weights(obj, weights_file_path)
    else:
        cmds.warning(f"Weight file not found: {weights_file_path}")

def import_assets(asset_path):
    asset_name, FT_ID = os.path.basename(asset_path).split("_")
    print (asset_name)
    asset_folder = asset_path
    if not os.path.exists(asset_folder):
        cmds.error(f"Asset folder {asset_folder} does not exist.")
    
    # Remove existing assets with the same FT_ID
    remove_existing_assets(FT_ID)
    print (asset_folder)
    objs_folder = os.path.join(asset_folder, "objs")
    weights_folder = os.path.join(asset_folder, "weights")
    material_folder = os.path.join(asset_folder, "material_networks")
    textures_folder = os.path.join(asset_folder, "texture_maps")
    json_data_file = os.path.join(asset_folder, f"{asset_name}_{FT_ID}_data.json")

    json_data = load_json_data(json_data_file)
    materials_info = json_data['materials']
    obj_materials = json_data['obj_materials']
    version = json_data.get('version', '0001')
    
    # Create a new group for the imported OBJs
    group_name = f"{asset_name}_{FT_ID[0:3]}_accessoryGroup"
    group_node = cmds.group(empty=True, name=group_name)
    cmds.addAttr(group_node, longName="FT_ID", dataType="string")
    cmds.setAttr(f"{group_node}.FT_ID", FT_ID, type="string")
    cmds.addAttr(group_node, longName="version", dataType="string")
    cmds.setAttr(f"{group_node}.version", version, type="string")
        
    # Check if 'export_grp' exists, if not, create it
    if not cmds.objExists('export_grp'):
        export_grp = cmds.group(empty=True, name='export_grp')
    else:
        export_grp = 'export_grp'

    # Parent the new group node under 'export_grp'
    cmds.parent(group_node, export_grp)

    # Import material networks
    import_material_networks(material_folder)

    # Create a subfolder for textures in the sourceimages directory
    textures_subfolder = os.path.join(SOURCEIMAGES_DIR, f"accessory_maps/{asset_name}_{FT_ID}")
    if not os.path.exists(textures_subfolder):
        os.makedirs(textures_subfolder)

    # Import OBJ files
    all_imported_objs = []
    for obj_file in os.listdir(objs_folder):
        if obj_file.endswith(".obj"):
            obj_file_path = os.path.join(objs_folder, obj_file)
            imported_obj = import_obj(obj_file_path, FT_ID)
            all_imported_objs.append(imported_obj)
            # Parent the imported obj to the group
            cmds.parent(imported_obj, group_node)

            import_rig_weights(imported_obj, weights_folder)
    
    # Setup materials and apply them to imported OBJs
    setup_materials(materials_info, obj_materials, textures_folder, textures_subfolder)

def import_asset_from_folder(asset_folder):
    import_assets(asset_folder)

def load_accessory_folders():
    project_folder_is_set_correctly = check_project_folder()
    #Only proceed if the project is set to a FT Character folder.
    if project_folder_is_set_correctly:
        
        app = QApplication.instance()
        if not app:
            app = QApplication([])

        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        file_dialog.setWindowTitle("Select downloaded and unzipped FT accessory folders, name format should be-- AccessoryName_@@#-@@#-@@@#")
        file_view = file_dialog.findChild(QListView, 'listView')
        
        # Make it possible to select multiple directories
        if file_view:
            file_view.setSelectionMode(QAbstractItemView.MultiSelection)
        f_tree_view = file_dialog.findChild(QTreeView)
        if f_tree_view:
            f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)
    
        if file_dialog.exec():
            paths = file_dialog.selectedFiles()
            if not paths:
                return
            
            for accessory_folder_path in paths:
                print (accessory_folder_path)
                is_accessory_folder =  check_accessory_folder(accessory_folder_path)
                if is_accessory_folder:
                    import_asset_from_folder(accessory_folder_path)
                    print(f"Imported: {accessory_folder_path}")



#load_accessory_folders()



