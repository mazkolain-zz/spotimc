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
from spotimcgui.views import BaseListContainerView
from spotify import search, track
from spotimcgui.views.artists import open_artistbrowse_albums
from spotimcgui.views.album import AlbumTracksView


def ask_search_term():
    kb = xbmc.Keyboard('', 'Enter a search term')
    kb.doModal()

    if kb.isConfirmed():
        return kb.getText()


class SearchTracksCallbacks(search.SearchCallbacks):
    def search_complete(self, result):
        xbmc.executebuiltin("Action(Noop)")


class SearchTracksView(BaseListContainerView):
    container_id = 1500
    list_id = 1520

    button_did_you_mean = 1504
    button_new_search = 1510

    context_menu_id = 5500
    context_browse_artist_button = 5502
    context_browse_album_button = 5503
    context_toggle_star = 5504
    context_add_to_playlist = 5505

    __session = None
    __query = None
    __search = None

    def _do_search(self, query):
        self.__query = query
        cb = SearchTracksCallbacks()
        self.__search = search.Search(
            self.__session, query,
            track_offset=0, track_count=200,
            callbacks=cb
        )

    def __init__(self, session, query):
        self.__session = session
        self._do_search(query)

    def _get_current_track(self, view_manager):
        item = self.get_list(view_manager).getSelectedItem()
        pos = int(item.getProperty('ListIndex'))

        if pos is not None:
            return self.__search.track(pos)

    def _play_selected_track(self, view_manager):
        item = self.get_list(view_manager).getSelectedItem()
        pos = int(item.getProperty('ListIndex'))
        session = view_manager.get_var('session')
        playlist_manager = view_manager.get_var('playlist_manager')
        playlist_manager.play(self.__search.tracks(), session, pos)

    def click(self, view_manager, control_id):
        if control_id == SearchTracksView.button_did_you_mean:
            if self.__search.did_you_mean():
                self._do_search(self.__search.did_you_mean())
                view_manager.show()

        elif control_id == SearchTracksView.button_new_search:
            term = ask_search_term()
            if term:
                self._do_search(term)
                view_manager.show()

        elif control_id == SearchTracksView.list_id:
            self._play_selected_track(view_manager)

        elif control_id == SearchTracksView.context_browse_artist_button:
            current_track = self._get_current_track(view_manager)
            artist_list = [artist for artist in current_track.artists()]
            open_artistbrowse_albums(view_manager, artist_list)

        elif control_id == SearchTracksView.context_browse_album_button:
            album = self._get_current_track(view_manager).album()
            session = view_manager.get_var('session')
            v = AlbumTracksView(session, album)
            view_manager.add_view(v)

        elif control_id == SearchTracksView.context_toggle_star:
            item = self.get_list(view_manager).getSelectedItem()
            current_track = self._get_current_track(view_manager)

            if current_track is not None:
                if item.getProperty('IsStarred') == 'true':
                    item.setProperty('IsStarred', 'false')
                    track.set_starred(self.__session, [current_track], False)
                else:
                    item.setProperty('IsStarred', 'true')
                    track.set_starred(self.__session, [current_track], True)

    def action(self, view_manager, action_id):
        #Run parent implementation's actions
        BaseListContainerView.action(self, view_manager, action_id)

        playlist_manager = view_manager.get_var('playlist_manager')

        #Do nothing if playing, as it may result counterproductive
        if not playlist_manager.is_playing():
            if action_id == 79:
                self._play_selected_track(view_manager)

    def get_container(self, view_manager):
        return view_manager.get_window().getControl(SearchTracksView.container_id)

    def get_list(self, view_manager):
        return view_manager.get_window().getControl(SearchTracksView.list_id)

    def get_context_menu_id(self):
        return SearchTracksView.context_menu_id

    def _set_search_info(self, view_manager):
        window = view_manager.get_window()
        window.setProperty("SearchQuery", self.__query)

        did_you_mean = self.__search.did_you_mean()
        if did_you_mean:
            window.setProperty("SearchDidYouMeanStatus", "true")
            window.setProperty("SearchDidYouMeanString", did_you_mean)
        else:
            window.setProperty("SearchDidYouMeanStatus", "false")

    def render(self, view_manager):
        if self.__search.is_loaded():
            session = view_manager.get_var('session')
            pm = view_manager.get_var('playlist_manager')

            #Some view vars
            self._set_search_info(view_manager)

            #Reset list
            list_obj = self.get_list(view_manager)
            list_obj.reset()

            #Iterate over the tracks
            for list_index, track in enumerate(self.__search.tracks()):
                url, info = pm.create_track_info(track, session, list_index)
                list_obj.addItem(info)

            #Tell that the list is ready to render
            return True
