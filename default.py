'''
Created on 13/06/2011

@author: mazkolain
'''
__addon_id__ = 'script.audio.spotimc'
__addon_version__ = '0.1'


#Gather addon information
import os.path, xbmcaddon, xbmcgui
addon_cfg = xbmcaddon.Addon("script.audio.spotimc")
addon_dir = addon_cfg.getAddonInfo('path')

#Open the loading window
loadingwin = xbmcgui.WindowXML("loading-window.xml", addon_dir, "DefaultSkin")
loadingwin.show()

#Add the dll search path
import envutils
dll_dir = os.path.join(addon_dir, "resources/dlls")
envutils.set_library_path(dll_dir)

#Add the libraries
libs_dir = os.path.join(addon_dir, "resources/libs")
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
    skin_dir = os.path.join(addon_dir, "resources/skins/DefaultSkin")
    xml_path = os.path.join(skin_dir, "720p/font.xml")
    font_dir = os.path.join(skin_dir, "fonts")
    fm.install_file(xml_path, font_dir)
    
    #Install custom includes
    im = IncludeManager()
    include_path = os.path.join(addon_dir, "resources/skins/DefaultSkin/720p/includes.xml")
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
    main(addon_dir)
    
    
    xbmc.log('garbage collection: %d objects' % gc.collect())
    #print gc.garbage
    
    
    import _spotify
    _spotify.unload_library()
    
    
    #import objgraph
    #objgraph.show_backrefs(gc.garbage, max_depth=10)
    
    #xbmc.log('gc objects before: %d,%d,%d' % gc.get_count())
    
    #print 'gc objects: %d' % len(gc.get_objects())

finally:
    #Cleanup fonts and includes
    if fm is not None:
        del fm
    
    if im is not None:
        del im
    
    #Close the background loading window
    loadingwin.close()
