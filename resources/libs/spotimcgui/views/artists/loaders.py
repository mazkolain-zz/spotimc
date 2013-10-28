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
from spotify import artistbrowse, albumbrowse, link
from spotify.album import AlbumType as SpotifyAlbumType
from spotify.track import TrackAvailability
from spotify.artistbrowse import BrowseType
from taskutils.decorators import run_in_thread
from taskutils.threads import current_task
from taskutils.utils import ConditionList
import weakref


class AlbumType:
    Album = 0
    Single = 1
    Compilation = 2
    AppearsIn = 3


class AlbumCallbacks(albumbrowse.AlbumbrowseCallbacks):
    __task = None

    def __init__(self, task):
        self.__task = task

    def albumbrowse_complete(self, albumbrowse):
        self.__task.notify()


class ArtistCallbacks(artistbrowse.ArtistbrowseCallbacks):
    __artistalbumloader = None

    def __init__(self, artistalbumloader):
        self.__artistalbumloader = weakref.proxy(artistalbumloader)

    def artistbrowse_complete(self, artistbrowse):
        self.__artistalbumloader.check()


class ArtistAlbumLoader:
    __condition_list = None
    __session = None
    __artist = None
    __album_data = None
    __artistbrowse = None
    __is_loaded = None
    __sorted_albums = None
    __loader_task = None

    def __init__(self, session, artist):
        self.__condition_list = ConditionList()
        self.__session = session
        self.__artist = artist
        self.__album_data = {}
        self.__is_loaded = False
        self.__loader_task = None

        #Avoid locking this thread and continue in another one
        self.continue_in_background()

    def check(self):
        self.__loader_task.notify()

    def _wait_for_album_info(self, album_info):
        def info_is_loaded():
            return album_info.is_loaded()

        if not info_is_loaded():
            current_task().condition_wait(info_is_loaded, 10)

    def _num_available_tracks(self, album_info):
        count = 0

        #Return true if it has at least one playable track
        for track in album_info.tracks():
            track_status = track.get_availability(self.__session)
            if track_status == TrackAvailability.Available:
                count += 1

        return count

    def _is_same_artist(self, artist1, artist2):
        album1_str = link.create_from_artist(artist1).as_string()
        album2_str = link.create_from_artist(artist2).as_string()

        return album1_str == album2_str

    def _get_album_type(self, album):
        if album.type() == SpotifyAlbumType.Single:
            return AlbumType.Single

        elif album.type() == SpotifyAlbumType.Compilation:
            return AlbumType.Compilation

        if not self._is_same_artist(self.__artist, album.artist()):
            return AlbumType.AppearsIn

        else:
            return AlbumType.Album

    @run_in_thread(group='load_artist_albums', max_concurrency=5)
    def load_album_info(self, index, album):

        # Directly discard unavailable albums
        if not album.is_available():
            self.__album_data[index] = {
                'available_tracks': 0,
                'type': self._get_album_type(album),
            }

        # Otherwise load its data
        else:
            cb = AlbumCallbacks(current_task())
            album_info = albumbrowse.Albumbrowse(self.__session, album, cb)

            # Now wait until it's loaded
            self._wait_for_album_info(album_info)

            # Populate its data
            self.__album_data[index] = {
                'available_tracks': self._num_available_tracks(album_info),
                'type': self._get_album_type(album),
            }

            # Tell that we're done
            self.check()

    def _wait_for_album_list(self):

        #Add the artistbrowse callbacks
        self.__artistbrowse = artistbrowse.Artistbrowse(
            self.__session, self.__artist,
            BrowseType.NoTracks, ArtistCallbacks(self)
        )

        if not self.__artistbrowse.is_loaded():
            current_task().condition_wait(
                self.__artistbrowse.is_loaded, 60  # Should be enough?
            )

    def _add_album_processed_check(self, index):
        def album_is_processed():
            return index in self.__album_data

        if not album_is_processed():
            self.__condition_list.add_condition(album_is_processed)

    @run_in_thread(group='load_artist_albums', max_concurrency=1)
    def continue_in_background(self):

        # Set the reference to the current task
        self.__loader_task = current_task()

        # Wait until the album list got loaded
        self._wait_for_album_list()

        # Now load albumbrowse data from each one
        for index, album in enumerate(self.__artistbrowse.albums()):

            # Add a condition for the next wait
            self._add_album_processed_check(index)

            # Start loading the info in the background
            self.load_album_info(index, album)

        # Now wait until all info gets loaded
        current_task().condition_wait(self.__condition_list, 60)

        # Final steps...
        self.__is_loaded = True
        xbmc.executebuiltin("Action(Noop)")

    def is_loaded(self):
        return self.__is_loaded

    def get_album_available_tracks(self, index):
        return self.__album_data[index]['available_tracks']

    def get_album_type(self, index):
        return self.__album_data[index]['type']

    def get_album(self, index):
        return self.__artistbrowse.album(index)

    def get_non_similar_albums(self):
        name_dict = {}

        for index, album in self.get_albums():
            name = album.name()
            available_tracks = self.get_album_available_tracks(index)

            # If that name is new to us just store it
            if name not in name_dict:
                name_dict[name] = (index, available_tracks)

            # If the album has more playable tracks than the stored one
            elif available_tracks > name_dict[name][1]:
                name_dict[name] = (index, available_tracks)

        # Now return the list if indexes
        return [item[0] for item in name_dict.itervalues()]

    def get_albums(self):
        def sort_func(album_index):
            # Sort by album type and then by year (desc)
            return (
                self.get_album_type(album_index),
                -self.__artistbrowse.album(album_index).year()
            )

        # Do nothing if is loading
        if self.is_loaded():
            # Build the sorted album list if needed
            if self.__sorted_albums is None:
                album_indexes = self.__album_data.keys()
                sorted_indexes = sorted(album_indexes, key=sort_func)
                ab = self.__artistbrowse
                self.__sorted_albums = [
                    (index, ab.album(index)) for index in sorted_indexes
                ]

            return self.__sorted_albums
