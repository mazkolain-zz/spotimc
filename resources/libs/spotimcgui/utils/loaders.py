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

import xbmc, xbmcgui
from spotify.utils.loaders import load_albumbrowse as _load_albumbrowse
from spotify import session, BulkConditionChecker, link



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



class TrackLoadCallback(session.SessionCallbacks):
    __checker = None
    
    
    def __init__(self, checker):
        self.__checker = checker
    
    
    def metadata_updated(self, session):
        self.__checker.check_conditions()



def load_track(sess_obj, track_obj):
    
    #FIXME: Doing all these things is just overkill!
    if not track_obj.is_loaded():
    
        #Set callbacks for loading the track
        checker = BulkConditionChecker()
        checker.add_condition(track_obj.is_loaded)
        callbacks = TrackLoadCallback(checker)
        sess_obj.add_callbacks(callbacks)
        
        try:
            #Wait until it's done (should be enough)
            checker.complete_wait(10)
        
        finally:
            #Remove that callback, or will be around forever
            sess_obj.remove_callbacks(callbacks)
    
    return track_obj
