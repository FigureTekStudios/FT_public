import maya.cmds as mc
import maya.mel as mm

def bake_transform_animation(transforms, sample_by = 1, bakeSRT = True, skipSRT=[],
                                bakeAttrs = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz'], 
                                minimizeRotation=False):
    """
    Bake transforms down to keyframes
    bakeSrt (bool) fixes the flips after the bake is complete
    """
    #set_nodes = mc.sets(engine_joints, query=True)
    start_frame = mc.playbackOptions(query=True, minTime=True)
    end_frame = mc.playbackOptions(query=True, maxTime=True)

    #log.info("Baking animation curves for joints under %s:" % engine_joints)

    #swap to a panel that doesnt render
    model_panel = set_dull_panel()

    mc.bakeResults(transforms,
                     #hierarchy = "below",
                     simulation=True,
                     t=(int(start_frame), int(end_frame)),
                     sampleBy = sample_by,
                     #oversamplingRate=1,
                     attribute=bakeAttrs,
                     disableImplicitControl=True,
                     preserveOutsideKeys=False,
                     sparseAnimCurveBake=False,
                     removeBakedAttributeFromLayer=False,
                     removeBakedAnimFromLayer=False,
                     bakeOnOverrideLayer=False,
                     minimizeRotation=minimizeRotation,
                     controlPoints=False,
                     #shape=True
                     )

    if bakeSRT == True:
        for transform in transforms:
            if transform not in skipSRT:
                try:
                    maya_bakeSRT_runCommand_new(transform)
                except:
                    print ("skipped:", transform)
        print ("no flip bake fix completed")

    #swap back to model panel viewer
    set_model_panel(model_panel)

def set_dull_panel():
    """
    Temporarily change to dope sheet or another "dull" window for baking purposes
    Can be used to toggle on a limited basis(at least within the same script scope in most cases).
    """
    #Get the visible model panel - assumes only one!
    visible_panels = mc.getPanel(visiblePanels = True)
    model_panel = None
    if visible_panels:
        for panel in visible_panels:
            if panel.find("modelPanel")!=-1:
                model_panel = panel
                #Temporarily change to dope sheet or another "dull" window
                mc.scriptedPanel('dopeSheetPanel1', rp=model_panel, e=1)
    return model_panel

def set_model_panel(model_panel):
    """
    Set the model panel from a scriptedPanel
    """
    if model_panel:
        mc.modelPanel(model_panel, rp="dopeSheetPanel1", e=1)

def maya_bakeSRT_runCommand_new(transform):

    """
    Takes transforms and fixes gimbal issues one frame at a time using some conditional math.
    """

    t0 = float(mc.playbackOptions(q=1, ast=1))
    t1 = float(mc.playbackOptions(q=1, aet=1))

    # get keys - should be same for all channels since we baked them in that range
    k = 0
    nKeys = int(mc.keyframe(transform + ".rotateX", query=1, keyframeCount=1))
    rotX = mc.keyframe(transform + ".rotateX", valueChange=1, query=1)
    rotY = mc.keyframe(transform + ".rotateY", valueChange=1, query=1)
    rotZ = mc.keyframe(transform + ".rotateZ", valueChange=1, query=1)

    for k in range(1,nKeys):
        x_diff = 0.0
        y_diff = 0.0
        z_diff = 0.0
        x_diff = rotX[k] - rotX[k - 1]

        if x_diff<-90:
            rotX[k]+=float(float((((int((x_diff + 90)) / -360) + 1) * 360)))
        x_diff=rotX[k] - rotX[k - 1]

        if x_diff>270:
            rotX[k]-=float(float((((int((x_diff - 270)) / 360) + 1) * 360)))
        z_diff=rotZ[k] - rotZ[k - 1]

        if z_diff<-90:
            rotZ[k]+=float(float((((int((z_diff + 90)) / -360) + 1) * 360)))
        z_diff=rotZ[k] - rotZ[k - 1]

        if z_diff>270:
            rotZ[k]-=float(float((((int((z_diff - 270)) / 360) + 1) * 360)))
        x_diff=rotX[k] - rotX[k - 1]

        if (x_diff>90) and (x_diff<270):
            rotX[k]=rotX[k] - 180
            rotY[k]=float(180 - rotY[k])
            rotZ[k]=rotZ[k] - 180
        y_diff=rotY[k] - rotY[k - 1]

        if y_diff>180:
            rotY[k]-=float(float((((int((y_diff - 180)) / 360) + 1) * 360)))
        y_diff=rotY[k] - rotY[k - 1]

        if y_diff<-180:
            rotY[k]+=float(float((((int((y_diff + 180)) / -360) + 1) * 360)))

    # set keyframes
    for k in range(0,nKeys):

        mc.keyframe((transform + ".rotateX"),
            edit=1, index=(k,k), valueChange=rotX[k])
        mc.keyframe((transform + ".rotateY"),
            edit=1, index=(k,k), valueChange=rotY[k])
        mc.keyframe((transform + ".rotateZ"),
            edit=1, index=(k,k), valueChange=rotZ[k])

#transforms = mc.ls(sl= True)
#bake.bake_transform_animation(transforms)

def remove_flip(joints):

    start_frame = mc.playbackOptions(q=1, min=1)
    end_frame = mc.playbackOptions(q=1, max=1)+1

    for i in range(int(start_frame), int(end_frame)):
        mc.currentTime(i)

        for joint in joints:

            # repo worldSpace
            rot = mc.xform(joint, q=1, ws=1, ro=1)
            mc.xform(joint, ws=1, ro=rot)

            # repo precsisioio
            abs_rot = mc.xform(joint, q=1, a=1, ro=1)
            abs_rot = [round(v, 3) for v in abs_rot]
            mc.xform(joint, a=1, ro=abs_rot)

            # unroll -180

            mc.setKeyframe(joint+'.rx')
            mc.setKeyframe(joint+'.ry')
            mc.setKeyframe(joint+'.rz')
