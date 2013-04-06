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


import xbmc, os.path, xbmcaddon


#Set global addon information first
__addon_id__ = 'script.audio.spotimc'
addon_cfg = xbmcaddon.Addon(__addon_id__)
__addon_path__ = addon_cfg.getAddonInfo('path')

#Make spotimcgui available
sys.path.insert(0, os.path.join(__addon_path__, "resources/libs"))         
from spotimcgui.settings import InfoValueManager

#Print the spotimc window property
manager = InfoValueManager()
spotimc_window_id = manager.get_infolabel('spotimc_window_id')

if spotimc_window_id != '':
    xbmc.executebuiltin('ActivateWindow(%s)' % spotimc_window_id)
else:
    #print __addon_path__
    spotimc_path = os.path.join(__addon_path__, 'spotimc.py')
    xbmc.executebuiltin('RunScript("%s")' % spotimc_path)
