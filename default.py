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


__addon_id__ = 'script.audio.spotimc'


#Gather addon information
import os.path, xbmcaddon, xbmcgui
addon_cfg = xbmcaddon.Addon(__addon_id__)
__addon_path__ = addon_cfg.getAddonInfo('path')
__addon_version__ = addon_cfg.getAddonInfo('version')

#Open the loading window
loadingwin = xbmcgui.WindowXML("loading-window.xml", __addon_path__, "DefaultSkin")
loadingwin.show()

#Add the dll search path
import envutils
dll_dir = os.path.join(__addon_path__, "resources/dlls")
envutils.set_library_path(dll_dir)

#Add the libraries
libs_dir = os.path.join(__addon_path__, "resources/libs")
sys.path.append(libs_dir)

#Add the skinutils module
sys.path.append(os.path.join(libs_dir, "XbmcSkinUtils.egg"))

#Load font & include stuff
from skinutils import reload_skin
from skinutils.fonts import FontManager
from skinutils.includes import IncludeManager

try:
    #Set font & include manager vars
    fm = None
    im = None
    
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
    
    #Import spotify & friends
    sys.path.append(os.path.join(libs_dir, "CherryPy.egg"))
    sys.path.append(os.path.join(libs_dir, "PyspotifyCtypes.egg"))
    sys.path.append(os.path.join(libs_dir, "PyspotifyCtypesProxy.egg"))
    
    import gc
    import xbmc
    
    print 'gc objects: %d' % len(gc.get_objects())
    
    #xbmc.log('gc objects before: %d,%d,%d' % gc.get_count())
    
    #Load & start the actual gui, no init code beyond this point
    from spotimcgui import main
    main(__addon_path__)
    
    
    xbmc.log('garbage collection: %d objects' % gc.collect())
    #print gc.garbage
    
    
    import _spotify
    _spotify.unload_library()
    
    
    #import objgraph
    #objgraph.show_backrefs(gc.garbage, max_depth=10)
    
    #xbmc.log('gc objects before: %d,%d,%d' % gc.get_count())
    
    #print 'gc objects: %d' % len(gc.get_objects())

finally:
    #Cleanup includes and fonts
    if im is not None:
        del im
    
    if fm is not None:
        del fm
    
    #Close the background loading window
    loadingwin.close()
