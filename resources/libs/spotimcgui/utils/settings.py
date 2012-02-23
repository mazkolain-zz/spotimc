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
        return xbmc.getCondVisibility('Skin.HasSetting(%s)' % name)
    
    
    def set_bool_true(self, name):
        xbmc.executebuiltin('Skin.SetBool(%s)' % name)
    
    
    def toggle_bool(self, name):
        xbmc.executebuiltin('Skin.ToggleSetting(%s)' % name)
    
    
    def get_value(self, name):
        return xbmc.getInfoLabel('Skin.String(%s)' % name)
    
    
    def set_value(self, name, value):
        xbmc.executebuiltin('Skin.SetString(%s,%s)' % (name, value))
