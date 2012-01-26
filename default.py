'''
Created on 13/06/2011

@author: mazkolain
'''
__addon_id__ = 'script.audio.spotymc'
__addon_version__ = '0.1'


#Gather addon information
import os.path, xbmcaddon
addon_cfg = xbmcaddon.Addon("script.audio.spotymc")
addon_dir = addon_cfg.getAddonInfo('path')

#Add the dll search path
import envutils
dll_dir = os.path.join(addon_dir, "resources/dlls")
envutils.set_library_path(dll_dir)

#Add the libraries
libs_dir = os.path.join(addon_dir, "resources/libs")
sys.path.append(libs_dir)

#Load font & include stuff
from myscript.utils import reload_skin
from myscript.fonts import FontManager
from myscript.includes import IncludeManager

#Install custom fonts
skin_dir = os.path.join(addon_dir, "resources/skins/DefaultSkin")
xml_path = os.path.join(skin_dir, "720p/font.xml")
font_dir = os.path.join(skin_dir, "fonts")
fm = FontManager()
fm.install_file(xml_path, font_dir)

#Install custom includes
include_path = os.path.join(addon_dir, "resources/skins/DefaultSkin/720p/includes.xml")
im = IncludeManager()
im.install_file(include_path)
reload_skin()

#Import spotify & friends
sys.path.append(os.path.join(libs_dir, "CherryPy.egg"))
sys.path.append(os.path.join(libs_dir, "PyspotifyCtypes.egg"))
sys.path.append(os.path.join(libs_dir, "PyspotifyCtypesProxy.egg"))

import gc
import xbmc

print 'gc objects: %d' % len(gc.get_objects())

#xbmc.log('gc objects before: %d,%d,%d' % gc.get_count())

#Load & start the actual gui, no init code beyond this point
from spotymcgui import main
main(addon_dir)


xbmc.log('garbage collection: %d objects' % gc.collect())
#print gc.garbage


import _spotify
_spotify.unload_library()


#import objgraph
#objgraph.show_backrefs(gc.garbage, max_depth=10)

#xbmc.log('gc objects before: %d,%d,%d' % gc.get_count())

#print 'gc objects: %d' % len(gc.get_objects())

#Cleanup fonts and includes
del fm
del im
