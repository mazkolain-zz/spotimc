'''
Created on 13/06/2011

@author: mazkolain
'''
import os, os.path
script_dir = os.getcwd()

import envutils

#dll_dir = os.path.join(script_dir, "resources/dlls")
#envutils.set_library_path(dll_dir)

#print os.path.abspath("./resources/dlls")

#import sys
libs_dir = os.path.join(script_dir, "resources/libs")
sys.path.append(libs_dir)


#Load font & include stuff
from myscript.utils import reload_skin
from myscript.fonts import FontManager

skin_dir = os.path.join(script_dir, "resources/skins/DefaultSkin")
xml_path = os.path.join(skin_dir, "720p/font.xml")
font_dir = os.path.join(skin_dir, "fonts")
fm = FontManager()
fm.install_file(xml_path, font_dir)
reload_skin()


#Load main window
import spotymcgui.windows
mainwin = spotymcgui.windows.MainWindow("main-window.xml", script_dir, "DefaultSkin")
mainwin.doModal()


#Final cleanups
del mainwin
del fm
