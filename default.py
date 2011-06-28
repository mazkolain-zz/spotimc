'''
Created on 13/06/2011

@author: mazkolain
'''
import os, os.path
#os.chdir(os.path.abspath(os.path.dirname(__file__)))
script_dir = os.getcwd()

import envutils

#dll_dir = os.path.join(script_dir, "resources/dlls")
#envutils.set_library_path(dll_dir)

#print os.path.abspath("./resources/dlls")

#import sys
libs_dir = os.path.join(script_dir, "resources/libs")
sys.path.append(libs_dir)

#print sys.path

#import ctypes
#print "ctypes loaded ok!"

#import spotify

import spotymcgui.windows

#from resources.libs import spotymcgui



mainwin = spotymcgui.windows.MainWindow("main-window.xml", script_dir, "DefaultSkin")
#mydisplay.getControl(51)
mainwin.doModal()


del mainwin
