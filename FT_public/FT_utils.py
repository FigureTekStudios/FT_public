'''public utilities - functions to faciiltate working with Figure-Tek Rigs'''

#    @@@@@@ @@   @@@@  @@   @@ @@@@Z  @@@@@@     @@@@@@ @@@@@@ @@  @@@            
#    @@     @@ @@      @@   @@ @@  @@ @@           @@   @@     @@@@              
#    @@@@   @@ @@  @@@ @@   @@ @@@@@  @@@@&  @@@   @@   @@@@@  @@@@Z             
#    @@     @@ @@    @ @@   @@ @@ @@  @@           @@   @@     @@  @@@  
#    @@     @@ @@@@@@    @@@   @@  @@ @@@@@@       @@   @@@@@@ @@   @@

import maya.cmds as cmds

def select_all(namespace="*"):
    
    rig_catch = cmds.ls( f"{namespace}:rig_*", type = "transform")
    if namespace=="*":
        rig_catch += cmds.ls( f"rig_*", type = "transform")
        
    rig_names = []
    for rig_transform in rig_catch:
        if cmds.attributeQuery("is_rig", node=rig_transform, exists=True):
            rig_names.append(rig_transform)
    
    cmds.select(cl = True)
    for rig_name in rig_names:
        
        ################################################
        controllers_grp = cmds.ls(f"{rig_name}_controllers_grp") + cmds.ls(f"{namespace}:{rig_name}_controllers_grp")
        
        cmds.select(controllers_grp,add=True)
        
        faceSliders_grp = cmds.ls(f"{rig_name}_faceSliders_grp") + cmds.ls(f"{namespace}:{rig_name}_faceSliders_grp")
        if faceSliders_grp:
            cmds.select(faceSliders_grp[0],add=True)
        sec_faceSliders_grp = cmds.ls(f"{rig_name}_faceSecondaryCtls_grp") + cmds.ls(f"{namespace}:{rig_name}_faceSecondaryCtls_grp")
        if sec_faceSliders_grp:
            cmds.select(sec_faceSliders_grp[0],add=True)

def set_bindpose():
    sel = cmds.ls(sl = True)
    controls = []
    for each in sel:
        if cmds.objExists(each + ".BindPose"):
            controls.append(each)
        else:
            #print ("tring to zero trans rot")
            for attr in ["tx","ty","tz","rx","ry","rz",]:
                try:
                    cmds.setAttr(each + "." + attr, 0)
                except:
                    pass  
            for attr in ["sx","sy","sz"]:
                try:
                    cmds.setAttr(each + "." + attr, 1)
                except:
                    pass  

    
    for control in controls:
        #control ="arm_L0_fk1_ctl"    
        attr_dic = eval(cmds.getAttr(control + ".BindPose"))
        for attr in attr_dic.keys():
            try:
                cmds.setAttr(control + "." + attr,attr_dic[attr] )
            except:
                print ("failed", attr)



def set_tpose():
    cmds.setAttr("armUI_L0_ctl.arm_L0_blend",0)
    cmds.setAttr("legUI_L0_ctl.leg_L0_blend",0)
    cmds.setAttr("armUI_R0_ctl.arm_R0_blend",0)
    cmds.setAttr("legUI_R0_ctl.leg_R0_blend",0)
    
    for ctl in ['arm_L0_fk0_ctl',
                 'leg_L0_fk0_ctl',
                 'leg_L0_fk1_ctl',
                 'leg_L0_fk2_ctl',
                 'leg_R0_fk0_ctl',
                 'leg_R0_fk1_ctl',
                 'leg_R0_fk2_ctl',
                 'arm_R0_fk0_ctl',
                 'arm_R0_fk1_ctl',
                 'arm_R0_fk2_ctl']:
    
        for attr in ["tx", "ty", "tz", "rx", "ry", "rz"]:            
            cmds.setAttr(f"{ctl}.{attr}", 0)