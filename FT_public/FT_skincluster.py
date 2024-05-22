import maya.cmds as cmds
from maya.api import OpenMaya, OpenMayaAnim
import xml.etree.ElementTree as et
import os

def get_skin_clusters(msh_name):
    """
    Get the skinClusters attached to the specified node.
    msh_name = (str) Mesh object
    """
    shp_nde = OpenMaya.MSelectionList().add(msh_name).getDagPath(0)
    history = cmds.listHistory(shp_nde, pruneDagObjects=True, il=2) or []
    skin = [x for x in history if cmds.nodeType(x) == 'skinCluster']
    if skin:
        return skin[0]
    return None

def get_skin_cluster_influences(skin_cluster, full_path=False):
    """Get skin_cluster influences.

    Args:
        skin_cluster (str): skinCluster node
        full_path (bool): If true returns full path, otherwise partial path of
            influence names.

    Return:
        list(str,): influences
    """
    name = "fullPathName" if full_path else "partialPathName"
    skin_cluster_obj = OpenMaya.MSelectionList().add(skin_cluster).getDependNode(0)
    inf_objs = OpenMayaAnim.MFnSkinCluster(skin_cluster_obj).influenceObjects()
    influences = [getattr(x, name)() for x in inf_objs]
    return influences

def import_skin_weights(obj, weights_file_path):
    """Imports skin weights from an XML file and applies them to the specified object.

    Args:
        obj (str): Name of the mesh object to which the weights will be applied.
        weights_file_path (str): Path to the XML file containing the skin weights.
    """
    weight_file = os.path.basename(weights_file_path)
    skin_file_xml = et.parse(weights_file_path)
    influences = [elem.get('source') for elem in skin_file_xml.findall('weights')]
    
    # Filter existing influences
    skn_infl = [jnt for jnt in influences if cmds.objExists(jnt)]
    
    if cmds.objExists(obj) and skn_infl:
        # Check for existing skinCluster
        curr_skin = get_skin_clusters(obj)
        if curr_skin:
            curr_infl = get_skin_cluster_influences(curr_skin)
            to_add = [x for x in skn_infl if x not in curr_infl]
            if to_add:
                cmds.skinCluster(curr_skin, e=1, ai=to_add, lw=1, wt=0)
            cmds.deformerWeights(weights_file_path, im=1, df=curr_skin, m='index')
            [cmds.setAttr(infs + '.liw', 0) for infs in cmds.skinCluster(curr_skin, q=1, inf=1)]
            cmds.skinPercent(curr_skin, obj, nrm=1)
        else:
            skin = cmds.skinCluster(obj, skn_infl, tsb=1)[0]
            cmds.deformerWeights(os.path.basename(weights_file_path), path = os.path.dirname(weights_file_path), im=1, df=skin, m='index')
            cmds.skinPercent(skin, obj, nrm=1)
    else:
        cmds.warning('Skin object or influences do not exist in the scene')
