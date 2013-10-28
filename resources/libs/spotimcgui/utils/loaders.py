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

import xbmc
import xbmcgui
from spotify.utils.loaders import load_albumbrowse as _load_albumbrowse


def load_albumbrowse(session, album):
    def show_busy_dialog():
        xbmc.executebuiltin('ActivateWindow(busydialog)')

    load_failed = False

    #start loading loading the album
    try:
        albumbrowse = _load_albumbrowse(
            session, album, ondelay=show_busy_dialog
        )

    #Set the pertinent flags if a timeout is reached
    except:
        load_failed = True

    #Ensure that the busy dialog gets closed
    finally:
        if xbmc.getCondVisibility('Window.IsVisible(busydialog)'):
            xbmc.executebuiltin('Dialog.Close(busydialog)')

    if load_failed:
        d = xbmcgui.Dialog()
        d.ok('Error', 'Unable to load album info')

    else:
        return albumbrowse
