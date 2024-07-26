import maya.cmds as cmds
import os
import re
import shutil
import json
from FT_public import FT_skincluster as skn  # Import the skincluster module from FT_public
from PySide2.QtWidgets import QDialog,QPushButton, QButtonGroup, QRadioButton, QFileDialog, QListView, QTreeView, QAbstractItemView, QApplication, QVBoxLayout
import importlib
importlib.reload(skn)

# Use your FT Accessories directory and sourceimages path
SOURCEIMAGES_DIR = os.path.dirname(cmds.file(q=1, loc=1)) #should be the rig directory or whereever the user is placing the rig, as the only reliable way to get them to load is to put them in the same folder


def check_project_folder():
    """
       Does a check to determine if were in a character 
    """            
    project_folder = cmds.workspace(query=True, fullName=True)
    folder_name = os.path.basename(project_folder)
    print(f"Project folder: {folder_name}")  # Debug print
    pattern = r".*_[A-Za-z0-9\-]+$"
    if re.search(pattern, folder_name):
        print("Project folder is set correctly.")
        return True
    else:
        cmds.warning("Incorrect project folder. Expected format: FT_*_{FT_ID} (Set your project to A FIGURE-TEK character folder)")
        return False

def check_accessory_folder(accessory_folder_path):
    folder_name = os.path.basename(accessory_folder_path)
    #folder_name = "Jacket_EE3-HK6-WGP5"
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

def remove_existing_accessory_group(): 
    
    #This needs to be joint rez sensitive too!
    # Delete any accessory groups associated with the FT_ID
    pass
    '''
    accessory_groups = cmds.ls(type='transform')
    for group in accessory_groups:
        if cmds.attributeQuery('FT_ID', node=group, exists=True):
            if cmds.getAttr(f"{group}.FT_ID") == FT_ID:
                print('Removing old accessory group node:', group)
                cmds.delete(group)
    '''
    '''
    cmds.delete(group_name)
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
                        if cmds.objExists(file_node):
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
                '''
           
                
def import_obj(obj_file_path, FT_ID, joint_resolution):
    # Extract the base name of the file (e.g., Handwrap_001_L)
    if joint_resolution == "Lo":
        base_name = os.path.splitext(os.path.basename(obj_file_path))[0] + "Lo_"
    if joint_resolution == "Standard":
        base_name = os.path.splitext(os.path.basename(obj_file_path))[0]
    if joint_resolution == "Hi":
        base_name = os.path.splitext(os.path.basename(obj_file_path))[0] + "Hi_"
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

def setup_materials(materials_info, obj_materials, textures_folder, textures_subfolder, joint_resolution):
    shading_groups = {}
    
    for obj, materials in obj_materials.items():

        print ("setup_materials obj", obj)
        if joint_resolution == "Lo":
            obj+="Lo_"

        if joint_resolution == "Hi":
            obj+="Hi_"

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

                if not os.path.exists(dest_texture_path):  # Only copy if not already copied
                    print("Copying texture into the character sourceimages folder:", dest_texture_path)
                    shutil.copy(original_texture_path, dest_texture_path)
                  
                # Update the file node with the new texture path
                cmds.setAttr(f"{file_node}.fileTextureName", dest_texture_path, type="string")

def import_rig_weights(obj, weights_folder, joint_resolution):
    #export_joints = cmds.ls('out_C0_*_jnt')

    #joint_resolution = 'export' if export_joints else ''
    weights_file_path = os.path.join(weights_folder, joint_resolution, f"{obj}_skin.xml")

    print("Loading weights from", weights_file_path)
    if os.path.exists(weights_file_path):
        skn.import_skin_weights(obj, weights_file_path)
    else:
        cmds.warning(f"Weight file not found: {weights_file_path}")
        
def import_assets(asset_path, joint_resolution):
    print("asset_path ----->", asset_path)
    #asset_path = "D:\Working\dev\git\_accessories\staging\LeatherPants_FE6-DJ7-HAD5"
    #joint_resolution = "Lo"
    asset_name, FT_ID = os.path.basename(asset_path).split("_")
    asset_folder = asset_path
    if not os.path.exists(asset_folder):
        cmds.error(f"Asset folder {asset_folder} does not exist.")

    print("asset_folder:", asset_folder)
    objs_folder = os.path.join(asset_folder, "objs")
    weights_folder = os.path.join(asset_folder, "weights")
    material_folder = os.path.join(asset_folder, "material_networks")
    textures_folder = os.path.join(asset_folder, "texture_maps")
    json_data_file = os.path.join(asset_folder, f"{asset_name}_{FT_ID}_data.json")

    json_data = load_json_data(json_data_file)
    materials_info = json_data['materials']
    incoming_materials = list(materials_info.keys())
    print("incoming_materials:", incoming_materials)
    obj_materials = json_data['obj_materials']
    version = json_data.get('version', '0001')

    # Create a new group for the imported OBJs
    if joint_resolution == "Standard":
        group_name = f"{asset_name}_{FT_ID.replace('-','')}_AccessoryGroup"
    elif joint_resolution == "Lo":
        group_name = f"{asset_name}_{FT_ID.replace('-','')}_{joint_resolution}_AccessoryGroup"
    elif joint_resolution == "Hi":
        group_name = f"{asset_name}_{FT_ID.replace('-','')}_{joint_resolution}_AccessoryGroup"
    if cmds.objExists(group_name):
        cmds.delete(group_name)
    affected_objects = []

    existing_like_accessory_groups = cmds.ls(f"{asset_name}_{FT_ID.replace('-','')}*_AccessoryGroup")

    #old_materials_to_check = []

    for existing_like_accessory_group in existing_like_accessory_groups:
        print("existing_like_accessory_group:", existing_like_accessory_group)
        unfiltered_child_shapes = cmds.listRelatives(existing_like_accessory_group, allDescendents=True, ni=True, type="shape")
        child_shapes = [shape for shape in unfiltered_child_shapes if "Orig" not in shape]

        if child_shapes:
            print("child_shapes:", child_shapes)
            for child_shape in child_shapes:
                print("child_shape:", child_shape)
                shading_groups = cmds.listConnections(child_shape, type='shadingEngine')
                if shading_groups:
                    for shading_group in shading_groups:
                        materials = cmds.ls(cmds.listConnections(shading_group + ".surfaceShader"), materials=True)
                        for material in materials:
                            connected_shapes = cmds.sets(shading_group, query=True)
                            if connected_shapes:
                                affected_objects.append([material, connected_shapes])
    
    
    # 
    for material, _ in affected_objects:
        print(material)
        if cmds.objExists(material):
            if material in incoming_materials:
                
                file_nodes = cmds.listConnections(material, type='file')
                shading_group = cmds.listConnections(material, type="shadingEngine")
                if shading_group:
                    cmds.delete(shading_group)
                file_nodes = cmds.listConnections(material, type='file')
                if file_nodes:
                    for file_node in file_nodes:
                        if cmds.objExists(file_node):
                            cmds.delete(file_node)
                utility_nodes = cmds.listConnections(material, type='utility')
                if utility_nodes:
                    for utility_node in utility_nodes:
                        if cmds.objExists(utility_node):
                            cmds.delete(utility_node)
                cmds.delete(material)
            
            else:
                old_material_name = material + "_OLD"
                if not cmds.objExists(old_material_name):
                    cmds.rename(material, old_material_name)
                    #old_materials_to_check.append(old_material_name)
                    file_nodes = cmds.listConnections(old_material_name, type='file')
                    if file_nodes:
                        for file_node in file_nodes:
                            old_file_node_name = file_node + "_OLD"
                            if cmds.objExists(file_node):
                                cmds.rename(file_node, old_file_node_name)
                           

    print("affected_objects:", affected_objects)
    import_material_networks(material_folder)

    group_node = cmds.group(empty=True, name=group_name)
    cmds.addAttr(group_node, longName="FT_ID", dataType="string")
    cmds.setAttr(f"{group_node}.FT_ID", FT_ID, type="string")
    cmds.addAttr(group_node, longName="version", dataType="string")
    cmds.setAttr(f"{group_node}.version", version, type="string")

    if not cmds.objExists(joint_resolution):
        joint_resolution_grp = cmds.group(empty=True, name=joint_resolution)
    else:
        joint_resolution_grp = joint_resolution
    cmds.parent(group_node, joint_resolution)

    all_imported_objs = []
    for obj_file in os.listdir(objs_folder):
        if obj_file.endswith(".obj"):
            obj_file_path = os.path.join(objs_folder, obj_file)
            imported_obj = import_obj(obj_file_path, FT_ID, joint_resolution)
            all_imported_objs.append(imported_obj)
            cmds.parent(imported_obj, group_node)

            import_rig_weights(imported_obj, weights_folder, joint_resolution)

    setup_materials(materials_info, obj_materials, textures_folder, SOURCEIMAGES_DIR, joint_resolution)

    for material,connected_shapes in affected_objects:
        if material in incoming_materials:        
            shading_groups = cmds.listConnections(material, type="shadingEngine")
            if shading_groups:
                cmds.sets(connected_shapes, edit=True, forceElement=shading_groups[0])
    
    for old_material in cmds.ls("*_OLD", materials=True):
        shading_group = cmds.listConnections(old_material, type="shadingEngine")
        connected_shapes = cmds.sets(shading_group, query=True)
        if connected_shapes == None or connected_shapes == []:
            print("Deleting old material:", old_material)
            
            if shading_group:
                if cmds.objExists(shading_group[0]):
                    cmds.delete(shading_group[0])
            file_nodes = cmds.listConnections(old_material, type='file')
            if file_nodes:
                for file_node in file_nodes:
                    if cmds.objExists(file_node):
                        cmds.delete(file_node)
            utility_nodes = cmds.listConnections(old_material, type='utility')
            if utility_nodes:
                for utility_node in utility_nodes:
                    if cmds.objExists(utility_node):
                        cmds.delete(utility_node)
            cmds.delete(old_material)

    for rez in ["Lo", "Standard", "Hi"]:
        if cmds.objExists(rez):
            cmds.hide(rez)
    cmds.showHidden(joint_resolution)
        
def import_asset_from_folder(asset_folder, joint_resolution):
    import_assets(asset_folder, joint_resolution)

# Global variable to remember the last selection
last_joint_resolution = "Standard"

def load_accessory_folders():
    global last_joint_resolution
    
    app = QApplication.instance()
    if not app:
        app = QApplication([])

    # Create a dialog for selecting the accessory folders
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

    # Create a dialog for selecting the joint density
    density_dialog = QDialog()
    density_dialog.setWindowTitle("Select Joint Density to load")
    layout = QVBoxLayout(density_dialog)

    radio_standard = QRadioButton("Standard")
    radio_lo = QRadioButton("Lo")
    radio_hi = QRadioButton("Hi")

    # Load last selection and set it as default
    if last_joint_resolution == "Standard":
        radio_standard.setChecked(True)
    elif last_joint_resolution == "Lo":
        radio_lo.setChecked(True)
    elif last_joint_resolution == "Hi":
        radio_hi.setChecked(True)

    button_group = QButtonGroup(density_dialog)
    button_group.addButton(radio_standard)
    button_group.addButton(radio_lo)
    button_group.addButton(radio_hi)

    layout.addWidget(radio_standard)
    layout.addWidget(radio_lo)
    layout.addWidget(radio_hi)

    button_ok = QPushButton("OK")
    button_ok.clicked.connect(density_dialog.accept)
    layout.addWidget(button_ok)

    density_dialog.setLayout(layout)

    if density_dialog.exec_():
        if radio_standard.isChecked():
            last_joint_resolution = "Standard"
        elif radio_lo.isChecked():
            last_joint_resolution = "Lo"
        elif radio_hi.isChecked():
            last_joint_resolution = "Hi"

        if file_dialog.exec():
            paths = file_dialog.selectedFiles()
            if not paths:
                return
            for accessory_folder_path in paths:
                print(accessory_folder_path)
                is_accessory_folder = check_accessory_folder(accessory_folder_path)
                if is_accessory_folder:
                    import_asset_from_folder(accessory_folder_path, last_joint_resolution)
                    print(f"Imported: {accessory_folder_path}")



load_accessory_folders()
