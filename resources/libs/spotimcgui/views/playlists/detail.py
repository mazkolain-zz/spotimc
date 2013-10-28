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


import loaders
from spotimcgui.views import BaseListContainerView, iif
from spotify import track
from spotimcgui.views.album import AlbumTracksView
from spotimcgui.views.artists import open_artistbrowse_albums
from spotimcgui.settings import SettingsManager


class PlaylistDetailView(BaseListContainerView):
    container_id = 1800
    list_id = 1801

    BrowseArtistButton = 5811
    BrowseAlbumButton = 5812

    context_menu_id = 5800
    context_toggle_star = 5813

    __loader = None
    __playlist = None

    def __init__(self, session, playlist, playlist_manager):
        self.__playlist = playlist
        self.__loader = loaders.FullPlaylistLoader(
            session, playlist, playlist_manager
        )

    def _set_loader(self, loader):
        self.__loader = loader

    def _set_playlist(self, playlist):
        self.__playlist = playlist

    def _browse_artist(self, view_manager):
        item = self.get_list(view_manager).getSelectedItem()
        pos = int(item.getProperty('ListIndex'))
        track_obj = self.__loader.get_track(pos)
        artist_list = [artist for artist in track_obj.artists()]
        open_artistbrowse_albums(view_manager, artist_list)

    def _play_selected_track(self, view_manager):
        session = view_manager.get_var('session')
        item = self.get_list(view_manager).getSelectedItem()
        pos = int(item.getProperty('ListIndex'))
        playlist_manager = view_manager.get_var('playlist_manager')
        playlist_manager.play(self.__loader.get_tracks(), session, pos)

    def click(self, view_manager, control_id):
        if control_id == PlaylistDetailView.list_id:
            self._play_selected_track(view_manager)

        elif control_id == PlaylistDetailView.BrowseArtistButton:
            self._browse_artist(view_manager)

        elif control_id == PlaylistDetailView.BrowseAlbumButton:
            item = self.get_list(view_manager).getSelectedItem()
            pos = int(item.getProperty('ListIndex'))
            album = self.__loader.get_track(pos).album()
            v = AlbumTracksView(view_manager.get_var('session'), album)
            view_manager.add_view(v)

        elif control_id == PlaylistDetailView.context_toggle_star:
            item = self.get_list(view_manager).getSelectedItem()
            pos = int(item.getProperty("ListIndex"))

            if pos is not None:
                session = view_manager.get_var('session')
                current_track = self.__loader.get_track(pos)

                if item.getProperty('IsStarred') == 'true':
                    item.setProperty('IsStarred', 'false')
                    track.set_starred(session, [current_track], False)
                else:
                    item.setProperty('IsStarred', 'true')
                    track.set_starred(session, [current_track], True)

    def action(self, view_manager, action_id):
        #Run parent implementation's actions
        BaseListContainerView.action(self, view_manager, action_id)

        playlist_manager = view_manager.get_var('playlist_manager')

        #Do nothing if playing, as it may result counterproductive
        if not playlist_manager.is_playing():
            if action_id == 79:
                self._play_selected_track(view_manager)

    def get_container(self, view_manager):
        return view_manager.get_window().getControl(
            PlaylistDetailView.container_id)

    def get_list(self, view_manager):
        return view_manager.get_window().getControl(PlaylistDetailView.list_id)

    def get_context_menu_id(self):
        return PlaylistDetailView.context_menu_id

    def _get_playlist_length_str(self):
        total_duration = 0

        for track in self.__playlist.tracks():
            total_duration += track.duration() / 1000

        #Now the string ranges
        one_minute = 60
        one_hour = 3600
        one_day = 3600 * 24

        if total_duration > one_day:
            num_days = int(round(total_duration / one_day))
            if num_days == 1:
                return 'one day'
            else:
                return '%d days' % num_days

        elif total_duration > one_hour:
            num_hours = int(round(total_duration / one_hour))
            if num_hours == 1:
                return 'one hour'
            else:
                return '%d hours' % num_hours

        else:
            num_minutes = int(round(total_duration / one_minute))
            if num_minutes == 1:
                return 'one minute'
            else:
                return '%d minutes' % num_minutes

    def _set_playlist_properties(self, view_manager):
        window = view_manager.get_window()

        #Playlist name
        window.setProperty("PlaylistDetailName", self.__loader.get_name())

        #Owner info
        session = view_manager.get_var('session')
        current_username = session.user().canonical_name()
        playlist_username = self.__playlist.owner().canonical_name()
        show_owner = current_username != playlist_username
        window.setProperty("PlaylistDetailShowOwner",
                           iif(show_owner, "true", "false"))
        if show_owner:
            window.setProperty("PlaylistDetailOwner", str(playlist_username))

        #Collaboratie status
        is_collaborative_str = iif(self.__playlist.is_collaborative(),
                                   "true", "false")
        window.setProperty("PlaylistDetailCollaborative", is_collaborative_str)

        #Length data
        window.setProperty("PlaylistDetailNumTracks",
                           str(self.__playlist.num_tracks()))
        window.setProperty("PlaylistDetailDuration",
                           self._get_playlist_length_str())

        #Subscribers
        window.setProperty("PlaylistDetailNumSubscribers",
                           str(self.__playlist.num_subscribers()))

    def _set_playlist_image(self, view_manager, thumbnails):
        if len(thumbnails) > 0:
            window = view_manager.get_window()

            #Set cover layout info
            cover_layout_str = iif(len(thumbnails) < 4, "one", "four")
            window.setProperty("PlaylistDetailCoverLayout", cover_layout_str)

            #Now loop to set all the images
            for idx, thumb_item in enumerate(thumbnails):
                item_num = idx + 1
                is_remote = thumb_item.startswith("http://")
                is_remote_str = iif(is_remote, "true", "false")
                prop = "PlaylistDetailCoverItem{0:d}".format(item_num)
                window.setProperty(prop, thumb_item)
                prop = "PlaylistDetailCoverItem{0:d}IsRemote".format(item_num)
                window.setProperty(prop, is_remote_str)

    def render(self, view_manager):
        if self.__loader.is_loaded():
            session = view_manager.get_var('session')
            pm = view_manager.get_var('playlist_manager')
            list_obj = self.get_list(view_manager)
            sm = SettingsManager()

            #Set the thumbnails
            self._set_playlist_image(view_manager,
                                     self.__loader.get_thumbnails())

            #And the properties
            self._set_playlist_properties(view_manager)

            #Clear the list
            list_obj.reset()

            #Draw the items on the list
            for list_index, track_obj in enumerate(self.__loader.get_tracks()):
                show_track = (
                    track_obj.is_loaded() and
                    track_obj.error() == 0 and
                    (
                        (track_obj.get_availability(session) ==
                            track.TrackAvailability.Available) or
                        not sm.get_audio_hide_unplayable()
                    )
                )

                if show_track:
                    url, info = pm.create_track_info(track_obj, session,
                                                     list_index)
                    list_obj.addItem(info)

            return True


class SpecialPlaylistDetailView(PlaylistDetailView):
    def __init__(self, session, playlist, playlist_manager, name, thumbnails):
        self._set_playlist(playlist)
        loader = loaders.SpecialPlaylistLoader(
            session, playlist, playlist_manager, name, thumbnails
        )
        self._set_loader(loader)
