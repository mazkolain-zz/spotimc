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


class SkinSettings:
    def has_bool_true(self, name):
        return xbmc.getCondVisibility('Skin.HasSetting({0})'.format(name))

    def set_bool_true(self, name):
        xbmc.executebuiltin('Skin.SetBool({0})'.format(name))

    def toggle_bool(self, name):
        xbmc.executebuiltin('Skin.ToggleSetting({0})'.format(name))

    def get_value(self, name):
        return xbmc.getInfoLabel('Skin.String({0})'.format(name))

    def set_value(self, name, value):
        xbmc.executebuiltin('Skin.SetString({0},{1})'.format(name, value))
