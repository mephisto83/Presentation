
bl_info = {
    "name": "Composite Writer",
    "description": "Blender projects can be generated with json files of a specific format.",
    "category": "Uber",
    "author": "aporter",
    "version": (0,0,1,0),
    "blender": (2, 80, 0),
    "category": "Animation",
    "location": "View3D"
}


import bpy
import bpy.types
import inspect
import json
import math
import mathutils
import os.path
from types import *

movie_propeties = ["name", "filepath","frame_start","frame_duration","frame_offset", "source",  "use_fake_user"]
image_properties = ["name", "filepath", "filepath_raw", "source", "alpha_mode",  "use_fake_user"]
composite_image_node_properties = [ "frame_duration", "frame_start","use_cyclic","use_auto_refresh", "frame_offset"]
validmembers = ["image","clip", "layer","frame_duration", "frame_start","use_cyclic","use_auto_refresh", "frame_offset", "node_tree","alpha","specular_alpha","raytrace_transparency","specular_shader","specular_intensity","specular_hardness","transparency_method","use_transparency","translucency","ambient","emit","use_specular_map","specular_color","diffuse_color", "halo","volume", "diffuse_shader", "tonemap_type","f_stop","source","bokeh","contrast","adaptation","correction","index","use_antialiasing","offset","size",  "use_min", "use_max", "max","min", "threshold_neighbor","use_zbuffer", "master_lift","intensity","blur_max", "highlights_lift","midtones_lift","use_variable_size","use_bokeh","shadows_lift","midtones_end","midtones_start","blue","green","red", "shadows_gain", "midtones_gain", "highlights_gain","use_curved", "master_gain","speed_min","speed_max", "factor", "samples", "master_gamma", "highlights_gamma", "midtones_gamma", "shadows_gamma","hue_interpolation","interpolation","use_gamma_correction","use_relative", "shadows_contrast","operation", "use_antialias_z", "midtones_contrast", "master_saturation", "highlights_saturation", "midtones_saturation", "shadows_saturation", "master_contrast","highlights_contrast", "gain", "gamma","lift", "mapping", "height", "width", "premul", "use_premultiply","fade","angle_offset","streaks", "threshold", "mix","color_ramp", "color_modulation", "iterations","quality", "glare_type","filter_type", "ray_length", "use_projector","sigma_color","sigma_space", "use_jitter", "use_fit", "x", "y","rotation", "mask_type", "filter_type", "use_relative", "size_x","color_mode", "size_y", "use_clamp", "color_hue", "color_saturation", "color_value", "use_alpha", "name", "zoom","spin", "angle", "distance", "center_y", "center_x","use_wrap","blend_type","color_space", "projection", "label","base_path"]

debugmode = True
def debugPrint(val=None):
    if debugmode and val:
        print(val)

class CompositeWriter():
    node_count = 0
    forceRelative = False
    directJoin = False
    replaceAnd = False
    useName = False
    created_node_list = []
    def readComp(self, scene):
        mat_value = {}
        mat = { "name" : scene.name, "value": mat_value }
        # materials.append(mat)
        
        if scene.node_tree == None:
            mat["blender_render"] = True
        self.readObjectToDictionary(scene, mat, mat_value)
        return mat_value
    def readComps(self, scenes):
        _scenes = []
        for _scene in scenes:
            mat_value = {}
            mat = { "name" : _scene.name, "value": mat_value }
            _scenes.append(mat)
            
            if _scene.node_tree == None:
                mat["blender_render"] = True
            # if material.node_tree != None:
            self.readObjectToDictionary(_scene, mat, mat_value)
            t = [f for f in _scenes if f["name"] == _scene.name]
            if len(t) == 0:
                _scenes.append(mat)
        return _scenes

    def readMats(self, _materials):
        materials = []
        for material in _materials:
            mat_value = {}
            mat = { "name" : material.name, "value": mat_value }
            materials.append(mat)
            
            if material.node_tree == None:
                mat["blender_render"] = True
            # if material.node_tree != None:
            self.readObjectToDictionary(material, mat, mat_value)
            t = [f for f in materials if f["name"] == material.name]
            if len(t) == 0:
                materials.append(mat)
        return materials

    def readGroups(self, nodeGroups):
        groups = []
        debugPrint("read groups")
        for group in nodeGroups:
            mat_value = {}
            mat = { "name": group.name, "value": mat_value }
            groups.append(mat)

            self.readGroupToDictionary(group, mat, mat_value)
            t = [f for f in groups if f["name"] == group.name]
            if len(t) == 0:
                groups.append(mat)
        return groups
    
    def readWorlds(self, worlds):
        _worlds = []
        for world in worlds:
            mat_value = {}
            mat = { "name": world.name, "value": mat_value }
            _worlds.append(mat)
            debugPrint("read worlds")
            debugPrint(world)
            self.readObjectToDictionary(world, mat, mat_value)
            t = [f for f in _worlds if f["name"] == world.name]
            if len(t) == 0:
                _worlds.append(mat)
        return _worlds

    def readGroupToDictionary(self, group_tree, mat, mat_value):
        nodes = []
        nodes_ref = []
        links = []
        debugPrint("read group to dictionary")
        mat_value["nodes"] = nodes
        mat_value["links"] = links
        for _node in group_tree.nodes:
            self.processNode(_node, nodes, nodes_ref, links, group_tree, mat, mat_value)
        for _link in group_tree.links:
            self.processLinks(_link, nodes, nodes_ref, links, group_tree, mat, mat_value)

    def readObjectToDictionary(self, material, mat, mat_value):
        if material.node_tree == None:
            mat["blender_render"] = True
            members = inspect.getmembers(material)
            for member in members:
                mval = member[1]
                if isinstance(member[1], int) or isinstance(member[1], float) or isinstance(member[1], bool):
                    mat_value[member[0]] = member[1]
                elif isinstance(member[1], mathutils.Color):
                    mat_value[member[0]] = [f for f in member[1]]
                else: # isinstance(mval, bpy.types.MaterialHalo):
                    mat_value[member[0]] = self.packProperties(member[1])
        if material.node_tree != None:
            nodes = []
            nodes_ref = []
            links = []
            mat_value["nodes"] = nodes
            mat_value["links"] = links
            try:
                for _node in material.node_tree.nodes:
                    self.processNode(_node, nodes, nodes_ref, links, material, mat, mat_value)
                for _link in material.node_tree.links:
                    self.processLinks(_link, nodes, nodes_ref, links, material, mat, mat_value)
            except Exception as e:
                debugPrint(e)

    def processLinks(self,_link, nodes, nodes_ref, links, material, mat, mat_value):
        try:
            from_ = self.selectNodeName(_link.from_node, nodes_ref)
            to_ = self.selectNodeName(_link.to_node, nodes_ref)
            to_index = self.getIndexOf(_link.to_socket, _link.to_node.inputs)
            from_index = self.getIndexOf(_link.from_socket, _link.from_node.outputs)
            links.append( { "from": {"index": from_index ,  "port": _link.from_socket.name , "name": from_ }, "to": {"index": to_index , "port": _link.to_socket.name, "name": to_ } })
        except Exception as e:
            debugPrint(e)

    def processNode(self,_node, nodes, nodes_ref, links, material, mat, mat_value):
        inputs = []
        node_count = self.node_count
        node_name = "node_{}".format(node_count)
        bl_idname = _node.bl_idname
        if not "dependencies" in mat_value:
            mat_value["dependencies"] = []
        location = [f for f in _node.location]
        node = {"_type" :  bl_idname, "inputs": inputs, "_name" : node_name, "location": location }
        nodes_ref.append({"node": _node, "name": node_name })
        self.node_count =  node_count + 1
        node_count = self.node_count
        nodes.append(node)
        if bl_idname == "ShaderNodeGroup":
            mat_value["dependencies"].append(_node.name)
        members = inspect.getmembers(_node)
        for member in members:
            if any(member[0] in s for s in validmembers):
                try:
                    try:
                        mval = member[1]
                        #debugPrint("found " + member[0])
                        if isinstance(mval, bpy.types.ShaderNodeTree):
                            debugPrint(member[1].name )
                            node[member[0]] = member[1].name
                        elif isinstance(mval, bpy.types.CurveMapping):
                            curvemap = { "data" : [] }
                            node[member[0]] = curvemap
                            curves = [curve for curve in mval.curves]
                            k = 0 
                            for curve in curves:
                                curve_data = {"data" :  [] , "index": k}
                                k = k + 1
                                points = [f for f in curve.points]
                                i = 0
                                for point in points:
                                    point_data = {"index": i}
                                    i = i + 1
                                    point_data["location"] = [point.location[0], point.location[1]]
                                    point_data["handle_type"] = point.handle_type
                                    curve_data["data"].append(point_data)
                                curvemap["data"].append(curve_data)
                        elif isinstance(mval, bpy.types.Image):
                            debugPrint("found an image")
                            image_data = { }
                            node[member[0]] = image_data
                            for imageprop in image_properties:
                                image_data[imageprop] = getattr(mval, imageprop)
                            if self.forceRelative:
                                filepath = getattr(mval, "filepath")
                                debugPrint("filepath  :  {}".format(filepath) )
                                debugPrint("filepath basename  :  {}".format(os.path.basename(filepath)))
                                head, tail = os.path.split(filepath)
                                if self.relativePath == False:
                                    head = head.replace(self.replaceText, self.replaceWith)
                                    if self.replaceAnd:
                                        head = head.replace(self.replaceAnd, self.replaceWith)
                                    image_data["filepath_raw"] = head
                                    image_data["filepath"] =  head
                                else:
                                    if self.useName:
                                        head = image_data["name"]
                                    debugPrint("head {}".format(head))
                                    debugPrint("tail {}".format(tail))
                                    if self.directJoin:
                                        image_data["filepath_raw"] = self.relativePath + head
                                        image_data["filepath"] = self.relativePath + head
                                    else:
                                        image_data["filepath_raw"] = os.path.join(self.relativePath, head)
                                        image_data["filepath"] = os.path.join(self.relativePath, head)
                        elif isinstance(mval, bpy.types.MovieClip):
                            debugPrint("found a movie")
                            movie_data = {}
                            node[member[0]] = movie_data
                            for movieprop in movie_propeties:
                                movie_data[movieprop] = getattr(mval, movieprop)
                            if self.forceRelative:
                                filepath = getattr(mval, "filepath")
                                debugPrint("filepath  :  {}".format(filepath) )
                                debugPrint("filepath basename  :  {}".format(os.path.basename(filepath)))
                                head, tail = os.path.split(filepath)
                                if self.relativePath == False:
                                    head = head.replace(self.replaceText, self.replaceWith)
                                    if self.replaceAnd:
                                        head = head.replace(self.replaceAnd, self.replaceWith)
                                    movie_data["filepath_raw"] = head
                                    movie_data["filepath"] =  head
                                else:
                                    if self.useName:
                                        head = movie_data["name"]
                                    if self.directJoin:
                                        movie_data["filepath_raw"] = self.relativePath + head
                                        movie_data["filepath"] = self.relativePath + head
                                    else:
                                        movie_data["filepath_raw"] = os.path.join(self.relativePath, head)
                                        movie_data["filepath"] = os.path.join(self.relativePath, head)
                        elif isinstance(mval, bpy.types.ColorRamp):
                            color_ramp = {"data": [] }
                            node[member[0]] = color_ramp
                            elements = [element for element in mval.elements]
                            for element in elements:
                                element_data = { "alpha": element.alpha, "position": element.position, "color": [c for c in element.color] }
                                color_ramp["data"].append(element_data) 
                        elif isinstance(mval, bool) or isinstance(mval,  float) or isinstance(mval,  int) or isinstance(mval, str):
                            node[member[0]] = member[1]
                        else:
                            node[member[0]] = [f for f in member[1]]
                    except  Exception as e:
                        debugPrint(e)
                        mval = member[1]
                        if isinstance(mval, bool) or isinstance(mval,  float) or isinstance(mval,  int) or isinstance(mval, list):
                            node[member[0]] = member[1]
                except:
                    debugPrint(member)
        if hasattr(_node, "inputs"):
            for i in range(len(_node.inputs)):
                input = _node.inputs[i]
                if hasattr(input, "default_value"):
                    # if hasattr(input.default_value, "data") and input.default_value.data.type == "RGBA":
                    try:
                        try:
                            inputs.append({"index": i, "value": [f for f in input.default_value] })
                        # elif isinstance(input.default_value, float) or isinstance(input.default_value, int) or isinstance(input.default_value, str) or isinstance(input.default_value, bool ):
                        except:
                            inputs.append({"index": i, "value": input.default_value })
                    except:
                        debugPrint("didnt set anything")

    def getIndexOf(self, socket, inputs):
        c = 0
        for puts in inputs.items():
            if puts[1] == socket:
                return c
            c = c + 1
        return -1
    def selectNodeName(self, target, refs):
        for ndata in refs:
            if ndata["node"] == target:
                return ndata["name"]       
        return None             

    def packProperties(self, obj):
        debugPrint("packing properties")
        members = inspect.getmembers(obj)
        result = {}
        for member in members:
            try:
                if isinstance(member[1], int) or isinstance(member[1], float) or isinstance(member[1], bool):
                    result[member[0]] = result[member[1]]
                elif isinstance(member[1], mathutils.Color):
                    result[member[0]] = [f for f in member[1]]
            except Exception as e:
                debugPrint(e)
        return result
        
        
    def defineMaterial(self,  custom_mat, presentation_material_animation_points):
        if "name" in custom_mat:
            mat_name = custom_mat["name"]
            if self.doesMaterialExistAlready(mat_name):
                return
            debugPrint("create material called {}".format(mat_name))
            mat = bpy.data.materials.new(name=mat_name)
            if mat == None:
                raise ValueError("no material created")
            if "blender_render" in custom_mat:
                self.defineBlenderRenderMaterial(mat, custom_mat["value"])
            else:
                mat.use_nodes = True
                # clear all nodes to start clean
                for node in mat.node_tree.nodes:
                    mat.node_tree.nodes.remove(node)
                self.defineNodeTree(mat.node_tree, custom_mat, presentation_material_animation_points)
            return mat
        return None

    def doesMaterialExistAlready(self, name):
        for item in bpy.data.materials:
            if item.name == name:
                debugPrint("found material")
                return True
        debugPrint("no material found")
        return False

    def defineBlenderRenderMaterial(self, material, custom_mat_value):
        debugPrint("define blender render material")
        for property in custom_mat_value.keys():
            debugPrint("property {}".format(property))
            try:
                if isinstance(custom_mat_value[property], bool) or isinstance(custom_mat_value[property], float) or isinstance(custom_mat_value[property], int) or isinstance(custom_mat_value[property], str):
                    setattr(material, property, custom_mat_value[property])
                elif isinstance(custom_mat_value[property], list):
                    setattr(material, property,  [f for f in custom_mat_value[property]])
                else:
                    mat_prop = getattr(material, property)
                    for p in custom_mat_value[property]:
                        if hasattr(mat_prop, p):
                            setattr(mat_prop, p, mat_prop[p])
            except Exception as e:
                debugPrint(e)

    def setupComposite(self, scene, context, presentation_material_animation_points):
        if "composite" in scene:
            composite_settings = scene["composite"]
            if "file" in composite_settings:
                f = open(composite_settings["file"], 'r')
                filecontents = f.read()
                composite_settings = json.loads(filecontents)
            else:
                debugPrint("not using file")
            if "composite" in composite_settings: 
                custom_mat = { "name":"composite", "value": composite_settings["composite"] }
                # switch on nodes and get reference
                debugPrint("switch on nodes and get reference")
                context.scene.use_nodes = True
                tree = bpy.context.scene.node_tree

                debugPrint("clear default nodes")
                # clear default nodes
                for node in tree.nodes:
                    tree.nodes.remove(node)
                self.defineNodeTree(tree, custom_mat, presentation_material_animation_points)
    def setupWorld(self, world, context, presentation_material_animation_points):
        #composite_settings["groups"]
        
        bpy.data.worlds.new(world["name"])
        newworld = bpy.data.worlds[world["name"]]
        debugPrint("newworld")
        debugPrint(world["name"])
        debugPrint(newworld)
        newworld.use_nodes = True
        
        for node in newworld.node_tree.nodes:
            newworld.node_tree.nodes.remove(node)

        self.defineNodeTree(newworld.node_tree, world, presentation_material_animation_points)
    def setup(self, config, context, presentation_material_animation_points):
        if "groups" in config:
            self.setupGroups(config["groups"], context, presentation_material_animation_points)
    
    def setupGroups(self, configs, context, presentation_material_animation_points):
        debugPrint("setup groups")
        if "groups" in configs:
            debugPrint("setting one more level down, hopefully to a list/array")
            configs = configs["groups"]
        else:
            debugPrint("no group property found, this is good")
            try:
                debugPrint("{}".format(len(configs)))
            except Exception as e:
                debugPrint("couldnt find the len of config")
        if len(configs) == 1:
            sortedConfigs = configs
            debugPrint("{}".format(configs))
            debugPrint("only one config")
        else:
            sortedConfigs = self.sortByDependencies(configs)
        for group in sortedConfigs:
            debugPrint("setup group {}".format(group["name"]))
            self.setupGroup(group, context, presentation_material_animation_points)
        debugPrint("groups are setup")
    def sortByDependencies(self, configs):
        res = []
        debugPrint("sort by dependencies")
        for  i in range(len(configs)):
            for j in range(len(configs)):
                config = configs[j]
                debugPrint("config name :  {}".format(config["name"]))
                if self.containsDeps(res, config["value"]["dependencies"]):
                    if self.notIn(res, config):
                        res.append(config)
        
        return res
    def notIn(self, res, config):
        for r in res:
            if config == r:
                return False
        return True
    def containsDeps(self, res, deps):
        for d in deps:
            found = False
            for r in res:
                if r["name"] == d:
                    found = True
            if not found:
                return False
        return True

    def setupGroup(self, config, context, presentation_material_animation_points):
        node_tree = bpy.data.node_groups.new(config["name"], 'ShaderNodeTree')
        self.defineNodeTree(node_tree, config, presentation_material_animation_points)
        
    def hasImage(self, imageName):
        for key in bpy.data.images.keys():
            if key == imageName:
                return True
        return False
        
    def hasMovie(self, movieName):
        for key in bpy.data.movieclips.keys():
            if key == movieName:
                return True
        return False

    def defineImage(self, node_image, newnode, node):
        debugPrint("node_image : {}".format(node_image))
        debugPrint("node : {}".format(node))
        image_name = os.path.basename(node_image["filepath"])# node_image["name"]
        if image_name == "" or image_name == None:
            image_name = node_image["filepath"].split("/")[-1]
        _image_properties = node_image
        if self.hasImage(image_name) == False:
            debugPrint("does not have image " + image_name)
            bpy.data.images.load(filepath=_image_properties["filepath"])
        else:
            debugPrint("has image " + image_name)
        
        newnode.image = bpy.data.images[image_name]
        image_node = newnode.image
        if "layer" in node:
            setattr(newnode, "layer", node["layer"])
        image_data = node_image
        debugPrint("image properties")
        for image_prop in image_properties:
            debugPrint(" setting {} to {}".format(image_prop, image_data[image_prop]))
            setattr(image_node, image_prop, image_data[image_prop])
        
        image_node.name = image_name
        debugPrint("composite image node properties")
        for node_prop in composite_image_node_properties:
            if node_prop in node:
                setattr(newnode, node_prop, node[node_prop])

    def defineMovie(self, node_movie, newnode, node):
        movie_name = node_movie["name"]
        movie_properties = node_movie
        if self.hasMovie(movie_name) == False:
            debugPrint("does not have movie {}".format(movie_name))
            bpy.data.movieclips.load(filepath=movie_properties["filepath"])
        else:
            debugPrint("has movie {}".format(movie_name))
        newnode.clip = bpy.data.movieclips[movie_name]
        movie_node = newnode.clip
    def addCreatedNode(self, node, type):
        self.created_node_list.append({"node": node, "type": type})
    def getCreatedNodesOfType(self, type):
        res = []
        for i in self.created_node_list:
            if i["type"] == type:
                res.append(i)
        return res    
    def defineNodeTree(self, node_tree, custom_mat, presentation_material_animation_points):
        debugPrint("create material")
        if "name" in custom_mat:
            debugPrint("created new material")
            if "value" in custom_mat:
                material_definition = custom_mat["value"]
                debugPrint("material definition found")
                node_tree_dict = {}
                if "nodes" in material_definition:
                    debugPrint("creating nodes in material")
                    node_definitions = material_definition["nodes"]
                    for node in node_definitions:
                        debugPrint("creating {}".format(node["_type"]))
                        newnode = node_tree.nodes.new(type=node["_type"])
                        self.addCreatedNode(newnode, node["_type"])
                        if "location" in node:
                            newnode.location = node["location"]
                        debugPrint("created type")
                        
                        node_tree_dict[node["_name"]] = newnode
                        members = inspect.getmembers(newnode)
                        if isinstance(newnode, bpy.types.CompositorNodeMovieClip):
                            debugPrint("defining movie")
                            self.defineMovie(node["clip"], newnode, node)
                        elif isinstance(newnode, bpy.types.CompositorNodeImage):
                            self.defineImage(node["image"], newnode, node)
                        else:
                            for member in members:
                                if any(member[0] in s for s in validmembers):
                                    debugPrint("found {}".format(member[0]))
                                    if member[0] in node:
                                        try:
                                            if member[0] == "node_tree":
                                                debugPrint("setting shader node tree " + node[member[0]])
                                                newnode.node_tree = bpy.data.node_groups[node[member[0]]]
                                                debugPrint("set node groups")
                                            elif isinstance(member[1], bpy.types.CurveMapping) and member[1] != None:
                                                debugPrint(member)
                                                debugPrint("curve mapping {} ".format(member[0]))
                                                curvemap = getattr(newnode, member[0])
                                                curves =  node[member[0]]["data"]
                                                i = -1
                                                for curve in curves:
                                                    i = i + 1
                                                    debugPrint("curves")
                                                    debugPrint(curve)
                                                    j = -1 
                                                    for point in curve["data"]:
                                                        j = j + 1
                                                        debugPrint("points {}".format( len (curvemap.curves[i].points)))
                                                        if len (curvemap.curves[i].points) <= j :
                                                            debugPrint("adding new curve")
                                                            res = curvemap.curves[i].points.new(point["location"][0], point["location"][1])
                                                            res.handle_type = point["handle_type"]
                                                            debugPrint("added new curve")
                                                        else:
                                                            debugPrint("update existing curve")
                                                            curvemap.curves[i].points[j].location = point["location"]
                                                            curvemap.curves[i].points[j].handle_type = point["handle_type"]
                                            elif isinstance(member[1], bpy.types.ColorRamp):
                                                color_ramp_node = getattr(newnode, member[0])
                                                elements =  node[member[0]]["data"]
                                                j = -1
                                                for element in elements:
                                                    j = j + 1
                                                    if len(color_ramp_node.elements) <= j:
                                                        res = color_ramp_node.elements.new(element["position"])
                                                        res.alpha = element["alpha"]
                                                        res.color = element["color"]
                                                    else:
                                                        res = color_ramp_node.elements[j]
                                                        res.alpha = element["alpha"]
                                                        res.color = element["color"]
                                                        res.position = element["position"]
                                                    # element_data = { "alpha": element.alpha, "position": element.position, "color": [c for c in element.color] }
                                                    # color_ramp["data"].append(element_data)
                                            elif member[0] == "clip":
                                                movie_data = node[member[0]]
                                                self.defineMovie(node["clip"], newnode, node)
                                            elif member[0] == "image":
                                                # "image": {
                                                #     "alpha_mode": "STRAIGHT",
                                                #     "filepath": "D:\\Render\\Presenatation\\Test\\3\\Bricks01_SPEC.jpg",
                                                #     "filepath_raw": "D:\\Render\\Presenatation\\Test\\3\\Bricks01_SPEC.jpg",
                                                #     "name": "Bricks01_SPEC.jpg",
                                                #     "source": "FILE",
                                                #     "use_fake_user": false
                                                # }
                                                debugPrint("defining image_data")
                                                debugPrint("{}".format(newnode))
                                                image_data = node[member[0]]
                                                self.defineImage(node["image"], newnode, node)
                                            else:
                                                setattr(newnode, member[0], node[member[0]])
                                        except Exception as e:
                                            debugPrint(e)
                                            debugPrint("couldnt set propertY")
                        if "inputs" in node:
                            debugPrint("input defintions in node")
                            for inputs in node["inputs"]:
                                debugPrint("setting node's input")
                                debugPrint("{}".format(inputs["value"]))
                                try:
                                    newnode.inputs[inputs["index"]].default_value = inputs["value"]
                                except Exception as e:
                                            debugPrint(e)
                        if "_animation" in node:
                            _animationPoints = node["_animation"]
                            for _animationPoint in _animationPoints:
                                point = { 
                                            "material": custom_mat["name"], 
                                            "name" : _animationPoint["name"], 
                                            "index": _animationPoint["index"], 
                                            "node" : newnode 
                                            }
                                presentation_material_animation_points.append(point)
                if "links" in material_definition:
                    debugPrint("links in material definition found")
                    link_definitions = material_definition["links"]
                    debugPrint("link definitions")
                    links = node_tree.links
                    for link in link_definitions:
                        try:
                            debugPrint("link defintions ")
                            from_node = link["from"]["name"]
                            from_port = link["from"]["port"]
                            from_index = None
                            if "index" in link["from"]:
                                from_index = link["from"]["index"]
                            to_node = link["to"]["name"]
                            to_port = link["to"]["port"]
                            to_index = None
                            if "index" in link["to"]:
                                to_index = link["to"]["index"]
                            debugPrint("from_node : {}".format(from_node))
                            debugPrint("from_port : {}".format(from_port))
                            debugPrint("to_node : {}".format(to_node))
                            debugPrint("to_port : {}".format(to_port))

                            if to_index == None:
                                output = node_tree_dict[from_node].outputs[from_port]
                            else:
                                output = node_tree_dict[from_node].outputs[from_index]

                            if from_index == None:
                                input = node_tree_dict[to_node].inputs[to_port]
                            else:
                                input = node_tree_dict[to_node].inputs[to_index]

                            links.new(output, input)
                        except Exception as e:
                            debugPrint(e)
                        
            else : 
                debugPrint("no material definition found")
                raise ValueError("no material definition found")
        else:
            raise ValueError("no material name found")


if __name__ == "__main__":
    ob = CompositeWriter()
    print(ob, "created")