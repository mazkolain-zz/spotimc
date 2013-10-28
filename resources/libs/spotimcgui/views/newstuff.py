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
from spotimcgui.views import BaseListContainerView
from spotimcgui.views import album
from spotimcgui.utils.loaders import load_albumbrowse
from spotify import search
from taskutils.decorators import run_in_thread


class NewStuffCallbacks(search.SearchCallbacks):
    def search_complete(self, result):
        xbmc.executebuiltin("Action(Noop)")


class NewStuffView(BaseListContainerView):
    container_id = 1200
    list_id = 1201
    context_menu_id = 5200
    context_play_album = 5202
    context_set_current = 5203

    __search = None
    __initialized = None

    @run_in_thread
    def _initialize(self, session):
        cb = NewStuffCallbacks()
        self.__search = search.Search(
            session, 'tag:new', album_count=60, callbacks=cb
        )

        self.__initialized = True

        # FIXME: Poor man's way of dealing with race conditions (resend notifications)
        xbmc.executebuiltin("Action(Noop)")

    def __init__(self, session):
        self._initialize(session)

    def _get_selected_album(self, view_manager):
        pos = self.get_list(view_manager).getSelectedPosition()
        return self.__search.album(pos)

    def _show_album(self, view_manager):
        session = view_manager.get_var('session')
        album_obj = self._get_selected_album(view_manager)
        view_manager.add_view(album.AlbumTracksView(session, album_obj))

    def _start_album_playback(self, view_manager):
        session = view_manager.get_var('session')
        album_obj = self._get_selected_album(view_manager)
        albumbrowse = load_albumbrowse(session, album_obj)

        if albumbrowse is not None:
            playlist_manager = view_manager.get_var('playlist_manager')
            playlist_manager.play(albumbrowse.tracks(), session)

    def _set_current_album(self, view_manager):
        session = view_manager.get_var('session')
        album_obj = self._get_selected_album(view_manager)
        albumbrowse = load_albumbrowse(session, album_obj)

        if albumbrowse is not None:
            playlist_manager = view_manager.get_var('playlist_manager')
            playlist_manager.set_tracks(albumbrowse.tracks(), session)

    def click(self, view_manager, control_id):
        #Silently ignore events when not intialized
        if not self.__initialized:
            return

        #If the list was clicked...
        if control_id == NewStuffView.list_id:
            self._show_album(view_manager)

        elif control_id == NewStuffView.context_play_album:
            self._start_album_playback(view_manager)
            view_manager.get_window().setFocus(self.get_container(view_manager))

        elif control_id == NewStuffView.context_set_current:
            self._set_current_album(view_manager)
            view_manager.get_window().setFocus(self.get_container(view_manager))

    def action(self, view_manager, action_id):
        #Silently ignore events when not intialized
        if not self.__initialized:
            return

        #Run parent implementation's actions
        BaseListContainerView.action(self, view_manager, action_id)

        playlist_manager = view_manager.get_var('playlist_manager')

        #Do nothing if playing, as it may result counterproductive
        if action_id == 79 and not playlist_manager.is_playing():
            self._start_album_playback(view_manager)

    def get_container(self, view_manager):
        return view_manager.get_window().getControl(NewStuffView.container_id)

    def get_list(self, view_manager):
        return view_manager.get_window().getControl(NewStuffView.list_id)

    def get_context_menu_id(self):
        return NewStuffView.context_menu_id

    def render(self, view_manager):
        if not self.__initialized:
            return False

        if not self.__search.is_loaded():
            return False

        list_obj = self.get_list(view_manager)
        list_obj.reset()
        playlist_manager = view_manager.get_var('playlist_manager')

        for album in self.__search.albums():
            item = xbmcgui.ListItem(
                album.name(),
                album.artist().name(),
                playlist_manager.get_image_url(album.cover())
            )
            list_obj.addItem(item)

        return True
