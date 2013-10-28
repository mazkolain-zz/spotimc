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


import xbmcgui
from spotimcgui.views import BaseListContainerView, album
from loaders import ArtistAlbumLoader, AlbumType
from spotimcgui.utils.settings import SkinSettings
from spotimcgui.utils.loaders import load_albumbrowse


class ArtistAlbumsView(BaseListContainerView):
    container_id = 2000
    list_id = 2001

    #Filtering controls
    context_menu_id = 6000
    context_play_album = 6002
    context_set_current = 6003
    filter_albums_button = 6011
    filter_singles_button = 6012
    filter_compilations_button = 6013
    filter_appears_in_button = 6014
    filter_hide_similar = 6016

    __artist = None
    __loader = None
    __settings = SkinSettings()

    def __init__(self, session, artist):
        self._init_config()
        self.__artist = artist
        self.__loader = ArtistAlbumLoader(session, artist)

    def _init_config(self):
        if not self.__settings.has_bool_true('spotimc_albumbrowse_album_init'):
            self.__settings.set_bool_true('spotimc_albumbrowse_album_init')
            self.__settings.set_bool_true('spotimc_artistbrowse_albums_albums')
            self.__settings.set_bool_true('spotimc_artistbrowse_albums_singles')
            self.__settings.set_bool_true('spotimc_artistbrowse_albums_compilations')
            self.__settings.set_bool_true('spotimc_artistbrowse_albums_appears_in')
            self.__settings.set_bool_true('spotimc_artistbrowse_albums_hide_similar')

    def _get_album_filter(self):
        filter_types = []

        if self.__settings.has_bool_true('spotimc_artistbrowse_albums_albums'):
            filter_types.append(AlbumType.Album)

        if self.__settings.has_bool_true('spotimc_artistbrowse_albums_singles'):
            filter_types.append(AlbumType.Single)

        if self.__settings.has_bool_true('spotimc_artistbrowse_albums_compilations'):
            filter_types.append(AlbumType.Compilation)

        if self.__settings.has_bool_true('spotimc_artistbrowse_albums_appears_in'):
            filter_types.append(AlbumType.AppearsIn)

        return filter_types

    def _get_similar_filter(self):
        return self.__settings.has_bool_true('spotimc_artistbrowse_albums_hide_similar')

    def _get_selected_album(self, view_manager):
        item = self.get_list(view_manager).getSelectedItem()
        real_index = int(item.getProperty('ListIndex'))
        return self.__loader.get_album(real_index)

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
        filter_controls = [
            ArtistAlbumsView.filter_albums_button,
            ArtistAlbumsView.filter_singles_button,
            ArtistAlbumsView.filter_compilations_button,
            ArtistAlbumsView.filter_appears_in_button,
            ArtistAlbumsView.filter_hide_similar
        ]

        #If the list was clicked...
        if control_id == ArtistAlbumsView.list_id:
            self._show_album(view_manager)

        elif control_id == ArtistAlbumsView.context_play_album:
            self._start_album_playback(view_manager)
            view_manager.get_window().setFocus(self.get_container(view_manager))

        elif control_id == ArtistAlbumsView.context_set_current:
            self._set_current_album(view_manager)
            view_manager.get_window().setFocus(self.get_container(view_manager))

        elif control_id in filter_controls:
            view_manager.show(False)

    def action(self, view_manager, action_id):
        #Run parent implementation's actions
        BaseListContainerView.action(self, view_manager, action_id)

        playlist_manager = view_manager.get_var('playlist_manager')

        #Do nothing if playing, as it may result counterproductive
        if action_id == 79 and not playlist_manager.is_playing():
            self._start_album_playback(view_manager)

    def get_container(self, view_manager):
        return view_manager.get_window().getControl(ArtistAlbumsView.container_id)

    def get_list(self, view_manager):
        return view_manager.get_window().getControl(ArtistAlbumsView.list_id)

    def get_context_menu_id(self):
        return ArtistAlbumsView.context_menu_id

    def render(self, view_manager):
        if self.__loader.is_loaded():
            playlist_manager = view_manager.get_var('playlist_manager')

            l = self.get_list(view_manager)
            l.reset()

            #Get the non-similar list, if asked to do so
            if self._get_similar_filter():
                non_similar_list = self.__loader.get_non_similar_albums()

            #Set the artist name
            window = view_manager.get_window()
            window.setProperty('artistbrowse_artist_name', self.__artist.name())

            #Get the album types to be shown
            filter_types = self._get_album_filter()

            #Now loop over all the loaded albums
            for index, album in self.__loader.get_albums():
                album_type = self.__loader.get_album_type(index)
                is_in_filter = album_type in filter_types
                is_available = self.__loader.get_album_available_tracks(index) > 0
                is_similar = self._get_similar_filter() and \
                    index not in non_similar_list

                #Discard unavailable/non-filtered/similar albums
                if is_available and is_in_filter and not is_similar:
                    image_url = playlist_manager.get_image_url(album.cover())
                    item = xbmcgui.ListItem(
                        album.name(), str(album.year()), image_url
                    )
                    item.setProperty('ListIndex', str(index))
                    l.addItem(item)

            return True
