'''
Created on 13/06/2011

@author: mazkolain
'''

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
sys.path.append(os.path.join(libs_dir, "CherryPy-3.2.0-py2.4.egg"))
sys.path.append(os.path.join(libs_dir, "PyspotifyCtypes-0.1-py2.4.egg"))

#Load & start the actual gui, no init code beyond this point
from spotymcgui import main
main(addon_dir)

#Cleanup fonts and includes
del fm
del im
