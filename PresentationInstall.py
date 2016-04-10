
# blender -b --python /home/ubuntu/PresentationInstall.py
# ./blender -b --python /home/ubuntu/PresentationInstall.py

import os.path
import bpy
import zipfile

ver = "001"

basepath = "/home/ubuntu"
blender_version_path = os.path.join("blender-2.77a-linux-glibc211-x86_64", "2.77")
blender_resources_path= os.path.join(basepath, "PresentationMaterials.zip")
blender_resources_path_target= os.path.join(basepath, "blender_resources")
uber_path_file = os.path.join(basepath, "uber-" + ver + ".zip")
uber_path_target = os.path.join(basepath, "uber")

print("Install presentation addons")

# hdriZip = "D:\\Uber\\hdris.zip"
hdriZip = os.path.join(basepath, "hdris.zip")

# pro_lighting_library = "D:\\Uber\\library.zip"
pro_lighting_library = os.path.join(basepath, "library.zip")

# location = "D:\\dev\\Python\\Blender\\Presentation\\PresenationBlender.py"
location = os.path.join(basepath, "PresenationBlender.py")

# pro_skies_location = "D:\\Blender\\Addons\\pro_lighting_skies_ultimate_v1.2.zip"
pro_skies_location = os.path.join(basepath, "pro_lighting_skies_ultimate_v1.2.zip")

# pro_lighting_studio_location = "D:\\Blender\\Addons\\pro_lighting_studio.zip"
pro_lighting_studio_location = os.path.join(basepath, "pro_lighting_studio.zip")

# pro_skies_hdri_location = "C:\\Users\\mephisto\\AppData\\Roaming\\Blender Foundation\\Blender\\2.76\\scripts\\addons\\pro_lighting_skies_ultimate"
pro_skies_hdri_location = os.path.join(basepath, blender_version_path, "scripts/addons/pro_lighting_skies_ultimate")

# pro_lighting_studio_location_libs = "C:\\Users\\mephisto\\AppData\\Roaming\\Blender Foundation\\Blender\\2.76\\scripts\\addons\\pro_lighting_studio"
pro_lighting_studio_location_libs = os.path.join(basepath, blender_version_path, "scripts/addons/pro_lighting_studio")

# bpy.ops.wm.addon_install(overwrite=True, target='DEFAULT', filepath="", filter_folder=True, filter_python=True, filter_glob="*.py;*.zip")¶
bpy.ops.wm.addon_install(overwrite=True, target='DEFAULT', filepath=location, filter_folder=True, filter_python=True, filter_glob="*.py;*.zip")

bpy.ops.wm.addon_install(overwrite=True, target='DEFAULT', filepath=pro_skies_location, filter_folder=True, filter_python=True, filter_glob="*.py;*.zip")

bpy.ops.wm.addon_install(overwrite=True, target='DEFAULT', filepath=pro_lighting_studio_location, filter_folder=True, filter_python=True, filter_glob="*.py;*.zip")

def unzipToLocation(file, to):
    fh = open(file, 'rb')
    z = zipfile.ZipFile(fh)
    for name in z.namelist():
        outpath = to
        z.extract(name, outpath)
    fh.close()

unzipToLocation(uber_path_file, uber_path_target)
unzipToLocation(blender_resources_path, blender_resources_path_target)
unzipToLocation(hdriZip, pro_skies_hdri_location)
unzipToLocation(pro_lighting_library, pro_lighting_studio_location_libs)
# fh = open(hdriZip, 'rb')
# z = zipfile.ZipFile(fh)
# for name in z.namelist():
#     outpath = pro_skies_hdri_location
#     z.extract(name, outpath)
# fh.close()

# fh = open(pro_lighting_library, 'rb')
# z = zipfile.ZipFile(fh)
# for name in z.namelist():
#     outpath = pro_lighting_studio_location_libs
#     z.extract(name, outpath)
# fh.close()

#bpy.ops.wm.addon_enable(module="PresenationBlender")   
#bpy.ops.wm.addon_enable(module="pro_lighting_skies_ultimate")   