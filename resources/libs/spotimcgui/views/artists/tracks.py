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
from spotimcgui.views import BaseView


class ArtistTracksView(BaseView):
    __group_id = 1400
    __list_id = 1401

    def click(self, view_manager, window, control_id):
        pass

    def _get_list(self, window):
        return window.getControl(ArtistTracksView.__list_id)

    def _add_track(self, list, title, path, duration, number):
        item = xbmcgui.ListItem(path=path)
        item.setInfo(
            "music",
            {"title": title, "duration": duration, "tracknumber": number}
        )
        list.addItem(item)

    def _populate_list(self, window):
        l = self._get_list(window)
        l.reset()

        self._add_track(l, "Track 1", "", 186, 1)
        self._add_track(l, "Track 2", "", 120, 2)
        self._add_track(l, "Track 3", "", 5, 3)
        self._add_track(l, "Track 4", "", 389, 4)
        self._add_track(l, "Track 5", "", 7200, 5)
        self._add_track(l, "Track 1", "", 186, 6)
        self._add_track(l, "Track 2", "", 120, 7)
        self._add_track(l, "Track 3", "", 5, 8)
        self._add_track(l, "Track 4", "", 389, 9)
        self._add_track(l, "Track 5", "", 7200, 10)
        self._add_track(l, "Track 1", "", 186, 11)
        self._add_track(l, "Track 2", "", 120, 12)
        self._add_track(l, "Track 3", "", 5, 13)
        self._add_track(l, "Track 4", "", 389, 14)
        self._add_track(l, "Track 5", "", 7200, 15)
        self._add_track(l, "Track 1", "", 186, 16)
        self._add_track(l, "Track 2", "", 120, 17)
        self._add_track(l, "Track 3", "", 5, 18)
        self._add_track(l, "Track 4", "", 389, 19)
        self._add_track(l, "Track 5", "", 7200, 100)

        window.setProperty("ArtistName", "Artist Name")

    def show(self, window):
        self._populate_list(window)
        c = window.getControl(ArtistTracksView.__group_id)
        c.setVisibleCondition("true")

    def hide(self, window):
        c = window.getControl(ArtistTracksView.__group_id)
        c.setVisibleCondition("false")
