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
import albums


def choose_artist(artist_list):
    if len(artist_list) > 1:
        d = xbmcgui.Dialog()
        artist_names = [artist.name() for artist in artist_list]
        result = d.select('Choose an artist', artist_names)
        if result != -1:
            return artist_list[result]
    
    else:
        return artist_list[0]


def open_artistbrowse_albums(view_manager, artist_list):
    artist = choose_artist(artist_list)
    if artist is not None:
        session = view_manager.get_var('session')
        v = albums.ArtistAlbumsView(session, artist)
        view_manager.add_view(v)
