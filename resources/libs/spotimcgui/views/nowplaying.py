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
from spotimcgui.views import BaseContainerView
from spotimcgui.views.artists import open_artistbrowse_albums
from spotimcgui.views.album import AlbumTracksView


class PlayerCallbacks(xbmc.Player):
    def onPlayBackStopped(self):
        xbmc.executebuiltin('SetFocus(212)')
    
    
    def onPlayBackEnded(self):
        pl = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        if pl.getposition() < 0:
            xbmc.executebuiltin('SetFocus(212)')


class NowPlayingView(BaseContainerView):
    container_id = 1600

    browse_artist_button = 1621
    browse_album_button = 1622
    
    __player_callbacks = None

    def _get_current_track(self, view_manager):
        playlist_manager = view_manager.get_var('playlist_manager')
        session = view_manager.get_var('session')
        return playlist_manager.get_current_item(session)

    def _do_browse_artist(self, view_manager):
        track = self._get_current_track(view_manager)
        artist_list = [artist for artist in track.artists()]
        open_artistbrowse_albums(view_manager, artist_list)

    def _do_browse_album(self, view_manager):
        track = self._get_current_track(view_manager)
        session = view_manager.get_var('session')
        v = AlbumTracksView(session, track.album())
        view_manager.add_view(v)

    def click(self, view_manager, control_id):
        if control_id == NowPlayingView.browse_artist_button:
            self._do_browse_artist(view_manager)

        elif control_id == NowPlayingView.browse_album_button:
            self._do_browse_album(view_manager)

    def get_container(self, view_manager):
        return view_manager.get_window().getControl(NowPlayingView.container_id)
    
    def show(self, view_manager, set_focus=True):
        self.__player_callbacks = PlayerCallbacks()
        return BaseContainerView.show(self, view_manager, set_focus=True)
    
    def hide(self, view_manager):
        self.__player_callbacks = None
        BaseContainerView.hide(self, view_manager)

    def render(self, view_manager):
        pl = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        if pl.getposition() < 0:
            xbmc.executebuiltin('SetFocus(212)')
        return True
