import bpy
import bpy.types
import inspect
import json
import math
import mathutils
from Util import debugPrint
from Constants import KEYPOINT_SETTINGS, ANIMATION_TRANSLATION, SCENE_SETTINGS, BLENDER_SETTINGS, CYCLESRENDERSETTINGS, IMAGE_SETTINGS
import os.path
from types import *


class BlenderToJson():
    def readScene(self, scene):
        result = {}
        self.setSettings(scene, result)
        self.setScenes(bpy.data.scenes, result)
        return result
    def addProperty(self, key, dict):
        split_key = key.split(".")
        temp = dict
        last = None
        for sk in split_key:
            if last != None:
                if temp[last] == None:
                    temp[last] = {}
                temp = temp[last]
            if sk not in temp:
                temp[sk] = None
            last = sk
    def getProperty(self, setting_key, object):
        keys = setting_key.split(".")
        try:
            temp = object
            for key in keys:
                temp = getattr(temp, key)
            return temp
        except:
            return None
    def translate(self, value):
        if isinstance(value, int) or isinstance(value, float) or isinstance(value, bool) or value == None or isinstance(value, str):
            return value
        return [f for f in value]
    def setPropertyValue(self, key , value, result):
        split_key = key.split(".")
        temp = result
        for sk in split_key:
            if sk in temp:
                if temp[sk] == None:
                    temp[sk] = self.translate(value)
                else:
                    temp = temp[sk]
            else:
                raise ValueError("Missing key in dictionary.")

    def setProperty(self, key, settings_key, scene, result):
        prop_value = self.getProperty(settings_key, scene)
        self.setPropertyValue(key, prop_value, result)

    def setSettings(self, scene, result):
        res = {}
        result["settings"] = res
        for _setting in BLENDER_SETTINGS:
            for key in _setting.keys():
                debugPrint(key)
                prop_value = self.getProperty(_setting[key], scene)
                if prop_value != None:
                    self.addProperty(key, res)
                    self.setProperty(key, _setting[key], scene, res)

    def readCameras(self, scene, objects, keyframes):
        for obj in scene.objects:
            if obj.type == "CAMERA":
                camera = {"type":"camera", "name":obj.name}
                objects.append(camera)
                self.readKeyFrames(obj, keyframes)

    def readKeyFrames(self, obj, keyframes):
        if hasattr(obj.animation_data, "action"):
            for f in obj.animation_data.action.fcurves:
                for k in f.keyframe_points:
                    fr = k.co[0]
                    bpy.context.scene.frame_set(fr)
                    frame = {}
                    frame["frame"] = fr
                    keyframes.append(frame)
                    objects = []
                    frame["objects"] = objects
                    object = {}
                    debugPrint("get name")
                    object["name"] = obj.name
                    objects.append(object)
                    self.setObjectKeyFrame(object, k, f, obj)
                    
        else:
            debugPrint("no actions")
    def setObjectKeyFrame(self, object, keyframe_point, fcurve, scene_obj):            
        debugPrint("get animation translation")
        animation_trans = self.getAnimationTranslation(fcurve.data_path)
        debugPrint("get animation prop")
        anim_property = self.getAnimationProp(fcurve.data_path)
        debugPrint("get animation property")
        prop = self.getAnimationProperty(animation_trans, fcurve.array_index)
        debugPrint("animation_trans {}  anim_property {}  prop {}".format(animation_trans, anim_property, prop))
        if anim_property not in object:
            object[anim_property] = {}
        value = self.getProperty(fcurve.data_path + "." + prop, scene_obj)
        if fcurve.data_path == "rotation_euler":
            value = value * 360 / (math.pi*2)
        object[anim_property][prop] = value
        _keyframe_point = {}
        object[anim_property][prop+"_keyframe_point"] = _keyframe_point
        for kfp in KEYPOINT_SETTINGS:
            for key in kfp.keys():
                self.addProperty(key, _keyframe_point)
                self.setProperty(key, kfp[key], keyframe_point, _keyframe_point)
    def getAnimationProperty(self, anim_trans, index):
        debugPrint("{}".format(anim_trans))
        for at in anim_trans:
            debugPrint("{}".format(at))
            for key in at.keys():
                if at[key] == index:
                    return key
        raise ValueError("Cant find the key: {} ".format(index))
    
    def getAnimationTranslation(self, path):
        for anim in ANIMATION_TRANSLATION:
            if path in anim:
                return anim[path]
        raise ValueError("Cant find the path: {} ".format(path))

    def getAnimationProp(self, path):
        for anim in ANIMATION_TRANSLATION:
            if path in anim:
                return anim["json"]
        raise ValueError("Cant find the path: {} ".format(path))

    def setScenes(self, scenes, result):
        _scenes = []
        result["scenes"] = _scenes
        for scene in scenes:
            _scene = {}
            for scene_setting in SCENE_SETTINGS:
                for key in scene_setting.keys():
                    self.addProperty(key, _scene)
                    self.setProperty(key, scene_setting[key], scene, _scene)
                objects = []
                keyframes = []
                _scene["objects"] = objects
                debugPrint("read cameras")
                self.readCameras(scene, objects, keyframes)
                _scene["keyframes"] = keyframes
            _scenes.append(_scene)

if __name__ == "__main__":
    ob = BlenderToJson()
    print(ob, "created")