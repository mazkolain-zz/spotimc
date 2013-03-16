'''
Copyright 2011 Mikel Azkolain

This file is part of Spotimc.

Spotimc is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Spotimc is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Spotimc.  If not, see <http://www.gnu.org/licenses/>.
'''


import os.path, xbmcaddon, xbmcgui, gc, traceback


#Set global addon information first
__addon_id__ = 'script.audio.spotimc'
addon_cfg = xbmcaddon.Addon(__addon_id__)
__addon_path__ = addon_cfg.getAddonInfo('path')
__addon_version__ = addon_cfg.getAddonInfo('version')

#Open the loading window
loadingwin = xbmcgui.WindowXML("loading-window.xml", __addon_path__, "DefaultSkin")
loadingwin.show()

#Surround the rest of the init process
try:
    
    #Set font & include manager vars
    fm = None
    im = None
    
    #Set local library paths
    libs_dir = os.path.join(__addon_path__, "resources/libs")
    sys.path.insert(0, libs_dir)
    sys.path.insert(0, os.path.join(libs_dir, "XbmcSkinUtils.egg"))
    sys.path.insert(0, os.path.join(libs_dir, "CherryPy.egg"))
    sys.path.insert(0, os.path.join(libs_dir, "TaskUtils.egg"))
    sys.path.insert(0, os.path.join(libs_dir, "PyspotifyCtypes.egg"))
    sys.path.insert(0, os.path.join(libs_dir, "PyspotifyCtypesProxy.egg"))
    
    #And perform the rest of the import statements
    from envutils import set_library_paths
    from skinutils import reload_skin
    from skinutils.fonts import FontManager
    from skinutils.includes import IncludeManager
    from spotimcgui import main
    from _spotify import unload_library
    
    #Add the system specific library path
    set_library_paths('resources/dlls')
    
    #Install custom fonts
    fm = FontManager()
    skin_dir = os.path.join(__addon_path__, "resources/skins/DefaultSkin")
    xml_path = os.path.join(skin_dir, "720p/font.xml")
    font_dir = os.path.join(skin_dir, "fonts")
    fm.install_file(xml_path, font_dir)
    
    #Install custom includes
    im = IncludeManager()
    include_path = os.path.join(__addon_path__, "resources/skins/DefaultSkin/720p/includes.xml")
    im.install_file(include_path)
    reload_skin()
    
    #Load & start the actual gui, no init code beyond this point
    main(__addon_path__)
    
    #Do a final garbage collection after main
    gc.collect()
    
    #from _spotify.utils.moduletracker import _tracked_modules
    #print "tracked modules after: %d" % len(_tracked_modules)
    
    #import objgraph
    #objgraph.show_backrefs(_tracked_modules, max_depth=5)

except (SystemExit, Exception) as ex:
    if str(ex) != '':
        dlg = xbmcgui.Dialog()
        dlg.ok(ex.__class__.__name__, str(ex))
        traceback.print_exc()


finally:
    
    unload_library("libspotify")
    
    #Cleanup includes and fonts
    if im is not None:
        del im
    
    if fm is not None:
        del fm
    
    #Close the background loading window
    loadingwin.close()
