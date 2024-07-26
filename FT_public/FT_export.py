import maya.cmds as cmds
import FT_public.FT_bake as bake
import FT_public.ml_worldBake as ml_worldBake
import os

#import importlib 
#importlib.reload(ml_worldBake)
#importlib.reload(bake)

def get_namespace_from_reference(reference_node):
    # Check if the given node is a reference node
    if not cmds.nodeType(reference_node) == "reference":
        cmds.error(f"{reference_node} is not a reference node.")
        return None

    # Get the namespace of the reference node
    namespace = cmds.referenceQuery(reference_node, namespace=True).split(":")[-1]
    
    return namespace
    
def create_reference(file_path, namespace=None):
    """
    Creates a reference to the specified file in the current Maya scene.

    Args:
    file_path (str): The path to the file to be referenced.
    namespace (str, optional): The namespace for the referenced content. If None, Maya generates a default namespace.

    Returns:
    str: The name of the top-level reference node created.
    """
    if namespace is None:
        reference_node = cmds.file(file_path, reference=True)
    else:
        reference_node = cmds.file(file_path, reference=True, namespace=namespace)

    return reference_node


def decompose_out_joints(out_joints):
    """
    Figure-Tek Rigs make use of matricies to speed up the many joints that drive the surface of the mesh. These matricies need to be decomposed to get the info onto the standard tx,ty,tz,rx,ry,rz channels
    """
    i = 0
    for joint in out_joints:
            
        print (f"decomposing matricies:{i}/{len(out_joints)}")
        multMatrix_node_catch = cmds.listConnections(joint + ".offsetParentMatrix")
        if multMatrix_node_catch:
            multMatrix_node = multMatrix_node_catch[0]
            decomposeMatrix_node =  cmds.createNode('decomposeMatrix', n = multMatrix_node.replace("mM","dM"))
            cmds.connectAttr(f'{multMatrix_node}.matrixSum',f'{decomposeMatrix_node}.inputMatrix', f = True)
        
            cmds.connectAttr(f'{decomposeMatrix_node}.outputTranslateX',f'{joint}.translateX', f = True)
            cmds.connectAttr(f'{decomposeMatrix_node}.outputTranslateY',f'{joint}.translateY', f = True)
            cmds.connectAttr(f'{decomposeMatrix_node}.outputTranslateZ',f'{joint}.translateZ', f = True)
            cmds.connectAttr(f'{decomposeMatrix_node}.outputRotateX',f'{joint}.rotateX', f = True)
            cmds.connectAttr(f'{decomposeMatrix_node}.outputRotateY',f'{joint}.rotateY', f = True)
            cmds.connectAttr(f'{decomposeMatrix_node}.outputRotateZ',f'{joint}.rotateZ', f = True)
            cmds.disconnectAttr(f'{multMatrix_node}.matrixSum',f'{joint}.offsetParentMatrix')
            #zero out matrix
            zeroOrigin = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
            #joint = 'FTF_Variant0001_REF:out_C0_47390_jnt'
            cmds.setAttr(f'{joint}.offsetParentMatrix', *zeroOrigin, type='matrix') 
            
        i+=1

def disconnect_incoming_shear(transform_node):
    shear_attrs = ['shearXY', 'shearXZ', 'shearYZ', "shear"]
    
    for attr in shear_attrs:
        full_attr = f"{transform_node}.{attr}"
        
        # Check if the attribute is connected
        if cmds.listConnections(full_attr, plugs=True):
            # Disconnect all incoming connections
            incoming_connections = cmds.listConnections(full_attr, source=True, destination=False, plugs=True)
            if incoming_connections:
                for inc in incoming_connections:
                    cmds.disconnectAttr(inc, full_attr)

# Function to get the file path of a reference node
def get_reference_file_path(reference_node):
    if not cmds.referenceQuery(reference_node, isLoaded=True):
        print(f"Reference {reference_node} is not loaded.")
        return None
    try:
        file_path = cmds.referenceQuery(reference_node, filename=True)
        return file_path
    except:
        print(f"Could not get file path for reference {reference_node}.")
        return None

# Function to check if the path is within a Figure-Tek project folder
'''
def is_figure_tek_project(path):
    # Split the path into components
    path_components = os.path.normpath(path).split(os.sep)
    # Look for a project folder pattern and '_rig' folder in the path
    for component in path_components:
        if component.startswith("FT_") and component.count('_') == 3:
            project_index = path_components.index(component)
            if '_rig' in path_components[project_index:]:
                return True
    return False
'''

def generate_fbx_animations(base_fbx_destination_folder = None, 
                            model_container_wo_namespace="export_grp", 
                            bypass_selection_export_all=False,
                            Lo_Mid_Hi = "Hi"):
    """
    runs in a scene with any number of rigs in it. cmds.select any <> reference nodes you want exported,
    if nothing or nothing in the selection in the  you want to export or itll generate one for every available rig
    if destination_folder == None:
        a folder will be created wherever the original rig files are
    
    """
    all_references = []
    user_sel = cmds.ls(sl=True)
    for sel in user_sel:
        print(sel)
        if cmds.nodeType(sel) == "reference":
            all_references.append(sel)
    if all_references == []:
        cmds.warning("No <> reference nodes were selected, theyre the diamond icons in the outliner, set bypass_selection_export_all = True if you just want all refernces")
    
    if bypass_selection_export_all:
        all_references = cmds.ls(type='reference')
    
    for reference_node in all_references:
        print (reference_node)
        # Skipping special reference nodes
        if reference_node in ["sharedReferenceNode", "UNKNOWN_REF_NODE"]:
            continue
        # Retrieve file path and namespace of the reference
        rig_file_path = get_reference_file_path(reference_node)
        rig_folder_path = os.path.dirname(rig_file_path)

        namespace = cmds.referenceQuery(reference_node, namespace=True, shortName=True)
        if rig_file_path:
            print(f"Reference Node: {reference_node}, File Path: {rig_file_path}, Namespace: {namespace}")
            #determine if an export rig exists


            #if is_figure_tek_project(file_path):
                #print(f"The file {file_path} is inside a Figure-Tek project folder.")
            '''
            if "_export" not in rig_file_path:  # We're dealing with an anim rig
                # Construct the path to the export rig
                name, extension = os.path.basename(rig_file_path).split(".")
                export_rig_file_path = rig_folder_path + f"/{name}_export.{extension}"
                # Check if the export rig exists and replace the reference
                if os.path.exists(export_rig_file_path):
                    # Swap in the animation.
                    cmds.file(export_rig, loadReference=reference_node)
                    print(f"Replaced with export rig: {export_rig}")
            '''
            if base_fbx_destination_folder == None:
                base_fbx_destination_folder = os.path.dirname(cmds.file(q=1, loc=1))


            generate_fbx_animation(reference_node, base_fbx_destination_folder, model_container_wo_namespace=model_container_wo_namespace, Lo_Mid_Hi = "Lo")
     

            #else:
            #    print(f"The file {file_path} is NOT inside a Figure-Tek project folder.")    

def generate_fbx_animation(reference_node, 
                            base_fbx_destination_folder, 
                            model_container_wo_namespace="export_grp", 
                            delete_model_containers = True,
                             Lo_Mid_Hi = "Hi"):
    '''
    imports the reference, bakes all joints, deletes everything but the baked skeleton, creates a folder and exports an fbx file.
    '''
    
    #current_project_path = cmds.workspace(q=True, rd=True) # -rootDirectory
    #print(current_project_path)
    
    #export_rig = current_project_path + "_rig/PG4_export.mb" #should do a list to determine what file needs to be pulled 

    namespace = get_namespace_from_reference(reference_node)
    cmds.file(importReference=True, referenceNode=reference_node)
    
    #gather joints perhaps - per reference or namespace
    
    #gather joints
    #namespace = "aperature_REF"
    joints = cmds.listRelatives (f"{namespace}:global_C0_0_jnt", ad = True, type = "joint") + cmds.ls(f"{namespace}:global_C0_0_jnt", type = "joint") #the decendents and the root joint
    #cmds.select(joints)
    
    #Set all joints to keyable for later baking
    for joint in joints:
        for attr in ["tx","ty","tz","rx","ry","rz","sx","sy","sz"]:
            cmds.setAttr(joint+"."+attr, k = True)
    
    out_joints = cmds.ls(f"{namespace}:out_C0_*_jnt")
    
    #if matricies need to be decomposed:
    if out_joints:
        decompose_out_joints(out_joints)
    resulting_joints_set = set(joints) - set(out_joints)
    
    # Convert back to a list
    base_joints = list(resulting_joints_set)
    
    print("using ml bake to the main joints")
    cmds.select(base_joints)
    ml_worldBake.matchBakeLocators(parent=None, bakeOnOnes=True, constrainSource=False)
    
    #BAKE!
    
    #import bake
    #smart = True
    #if smart:
    #    print("smart bake is on, calculation this will take several minutes.")
    
    #using a the standard maya bake command -
    print('baking down the out joints')
    if out_joints:
        bake.bake_transform_animation(out_joints, bakeSRT = False)
        print("out bake completed.")
    
    
    matrix_nodes = cmds.ls(type = "mgear_matrixConstraint") + cmds.ls(type = "multMatrix") + cmds.ls( "*:*_rigUParCon")
    print(len(matrix_nodes))
    #matrix_nodes = cmds.ls( "*:*_rigUParCon")
    #len(matrix_nodes)
    #deleting matrix constraints any other matrix in the scene
    for matrix_node in matrix_nodes:
        try:
            cmds.delete(matrix_node)
        except:
            pass
    
    #reparent the mesh group and the joint hierearchy to the world
    model_container = f"{namespace}:{model_container_wo_namespace}"
    global_joint = f"{namespace}:global_C0_0_jnt"

    # grabbing everything under jnt_org
    children_of_jnt_org = cmds.listRelatives(cmds.listRelatives(global_joint,p=True), c= True)
    
    cmds.parent(model_container,children_of_jnt_org, w =True)
    
    
    
    rig_nodes = cmds.ls(f"{namespace}:rig_*") #the rig and sets should be returned
    for rig_node in rig_nodes :
        if cmds.objExists(rig_node):
            cmds.delete(rig_node)

    cmds.select(cmds.ls( "worldBake_*",type = "transform"))
    
    ml_worldBake.fromLocators(bakeOnOnes=True)
    #process animCurves?

    scene_name, _ = os.path.basename(cmds.file(q=1, loc=1)).split(".")
    # Get the parent directory
    #character_project_directory = os.path.abspath(os.path.join(export_rig, '..', '..'))
    cmds.delete(model_container)            
    
    cmds.select(global_joint) 
    #fbx_export_path = os.path.join(base_fbx_destination_folder,"fbx_animations", f"{namespace}_{scene_name}.fbx")

    fbx_export_path = base_fbx_destination_folder + f"/{namespace}_fbx_animations/{Lo_Mid_Hi}/{namespace}_{scene_name}.fbx"
    
    print (fbx_export_path)
    if not os.path.exists(os.path.dirname(fbx_export_path)):
        # Create the folder
        os.makedirs(os.path.dirname(fbx_export_path))
    print ("fbx_export_path=", fbx_export_path)
    print ("""cmds.FBXExportBakeComplexAnimation("-v", "true")""")
    # Export the fbx file

    print ("""cmds.FBXExport("-file", fbx_export_path, "-s")""")
    # Include animations
    cmds.FBXExportBakeComplexAnimation("-v", "true")
    # Export the fbx file
    
    cmds.FBXExport("-file", fbx_export_path, "-s")


def generate_fbx_model(base_fbx_destination_folder=None, model_container_wo_namespace="export_grp", Lo_Mid_Hi = "Hi"):
    
    '''
    This function should be run in the rig scene with a single character, once its rig is complete. 
    If this is a character file we should be in the export rig scene. Whatever scene this is run from 
    is what will be operated on. Warn the user if this is a character rig and what the consequences may be.
    We will grab the required files based on what we find based on the namespace 
    '''
    
    #current_project_path = cmds.workspace(q=True, rd=True) # -rootDirectory
    #print(current_project_path)
    
    #export_rig = current_project_path + "_rig/PG4_export.mb" #should do a list to determine what file needs to be pulled 

    # Example usage
    
    rig_file_path =cmds.file(q=1, loc=1)
    cmds.file(new=True, f = True)
    # generate the namespace
    namespace, _ = os.path.basename(rig_file_path).split(".")
    #export_rig_file_path = rig_folder_path + f"/{name}_export.{extension}"
    #namespace = 
    create_reference(rig_file_path, namespace)

    all_references = cmds.ls(type='reference')
    reference_node = None
    for ref_node in all_references:
        print(ref_node)
        if rig_file_path in cmds.referenceQuery(ref_node, filename=True):
            reference_node = ref_node
            break
    #cmds.referenceQuery(reference_node, filename=True)

    cmds.file(importReference=True, referenceNode=reference_node)
    
    #gather joints perhaps - per reference or namespace
    
    joints = cmds.listRelatives ("*:global_C0_0_jnt", ad = True, type = "joint") + cmds.ls("*:global_C0_0_jnt", type = "joint")
    
    out_joints = cmds.ls(f"{namespace}:out_C0_*_jnt")
    
    #if matricies need to be decomposed:
    if out_joints:    
        decompose_out_joints(out_joints)
        
    #get only the base joints
    resulting_joints_set = set(joints) - set(out_joints)
    base_joints = list(resulting_joints_set)
    
    matrix_nodes = cmds.ls(type = "mgear_matrixConstraint") + cmds.ls(type = "multMatrix") + cmds.ls( "*:*_rigUParCon")
    print(len(matrix_nodes))
    
    for matrix_node in matrix_nodes:
        try:
            cmds.delete(matrix_node)
        except:
            pass

    #reparent the mesh group and the joint hierearchy to the world
    model_container = f"{namespace}:{model_container_wo_namespace}"
    global_joint = f"{namespace}:global_C0_0_jnt"
    children_of_jnt_org = cmds.listRelatives(cmds.listRelatives(global_joint,p=True), c= True)
    
    cmds.parent(model_container,children_of_jnt_org, w =True)

    
    rig_nodes = cmds.ls(f"{namespace}:rig_*") #the rig and sets should be returned
    for rig_node in rig_nodes:
        if cmds.objExists(rig_node):
            cmds.delete(rig_node)

    if base_fbx_destination_folder == None:
        base_fbx_destination_folder =os.path.dirname(rig_file_path)


    #cmds.loadPlugin("fbxmaya", qt=True)
    
    
    #fbx_export_path =  os.path.join(base_fbx_destination_folder, f"fbx_model/{namespace}_base.fbx")

    fbx_export_path = base_fbx_destination_folder + f"/{namespace}_fbx_model/{Lo_Mid_Hi}/{namespace}_base.fbx"
    if not os.path.exists(os.path.dirname(fbx_export_path)):

        # Create the folder
        os.makedirs(os.path.dirname(fbx_export_path))
    # delete all but the needed tier
    for tier in ["Lo", "Mid", "Hi"]: 
        if cmds.objExists(f'{namespace}:{tier}'):
            cmds.showHidden(f'{namespace}:{tier}')
            if tier != Lo_Mid_Hi:
                cmds.delete(f'{namespace}:{tier}') 
    if Lo_Mid_Hi == "Lo":
        
        cmds.select(cmds.ls(f"{namespace}:*Main_*_*_jnt"))
        cmds.select(f"{namespace}:SubmentalSldMain_C0_0_jnt", d=True)
        cmds.delete(cmds.ls(sl=True))
    cmds.select(model_container, global_joint )
    # Include animations
    cmds.FBXExportBakeComplexAnimation("-v", "false")
    # Export the fbx file

    cmds.FBXExport("-file", fbx_export_path, "-s")

    val = cmds.confirmDialog( title='Confirm', message='Open the created fbx?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
    
    print ("fbx_export_path=", fbx_export_path)
    print ("""cmds.FBXExportBakeComplexAnimation("-v", "false")""")
    # Export the fbx file

    print ("""cmds.FBXExport("-file", fbx_export_path, "-s")""")

    if val == "Yes":    

        cmds.file(fbx_export_path, open=True, force=True)
    return fbx_export_path



len(cmds.ls(sl=True))



'''
generate_fbx_model(base_fbx_destination_folder=None, model_container_wo_namespace="export_grp", Lo_Mid_Hi = "Lo")


cmds.select( "JR3_exportRN")
generate_fbx_animations(base_fbx_destination_folder = None, 
                            model_container_wo_namespace="export_grp", 
                            bypass_selection_export_all=False,
                            Lo_Mid_Hi = "Lo")


D:/Projects/Whack-a-Punk_Project/assets/aperture/rig/animations/aperture_fbx_animations/Lo/aperture_closing.fbx
D:/Projects/Whack-a-Punk_Project/assets/aperture/rig/animations/aperture_fbx_animations/Lo/aperture_open.fbx
cmds.select("JR3:export_grp", "JR3:global_C0_0_jnt" )
fbx_export_path= "D:/Working/dev/git/_figures/variants/FT_ZombieFemale_JR3-AJ5-KEA2/_rig/JR3_fbx_model/Lo/JR3_base.fbx"
cmds.FBXExportBakeComplexAnimation("-v", "false")
cmds.FBXExport("-file", fbx_export_path, "-s")


generate_fbx_animations(Lo_Mid_Hi = "Lo")

'''
