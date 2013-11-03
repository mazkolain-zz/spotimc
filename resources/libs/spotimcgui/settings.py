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
import xbmcaddon
import xbmcgui
from __main__ import __addon_id__
import xml.etree.ElementTree as ET


class CacheManagement:
    Automatic = 0
    Manual = 1


class StreamQuality:
    Low = 0
    Medium = 1
    High = 2


class StartupScreen:
    NewStuff = 0
    Playlists = 1


class SettingsManager:
    __addon = None

    def __init__(self):
        self.__addon = xbmcaddon.Addon(id=__addon_id__)

    def _get_setting(self, name):
        return self.__addon.getSetting(name)

    def _set_setting(self, name, value):
        return self.__addon.setSetting(name, value)

    def get_addon_obj(self):
        return self.__addon

    def get_legal_warning_shown(self):
        return self._get_setting('_legal_warning_shown') == 'true'

    def set_legal_warning_shown(self, status):
        if status:
            str_status = 'true'
        else:
            str_status = 'false'

        return self._set_setting('_legal_warning_shown', str_status)

    def get_last_run_version(self):
        return self._get_setting('_last_run_version')

    def set_last_run_version(self, version):
        return self._set_setting('_last_run_version', version)

    def get_cache_status(self):
        return self._get_setting('general_cache_enable') == 'true'

    def get_cache_management(self):
        return int(self._get_setting('general_cache_management'))

    def get_cache_size(self):
        return int(float(self._get_setting('general_cache_size')))

    def get_audio_hide_unplayable(self):
        return self._get_setting('audio_hide_unplayable') == 'true'

    def get_audio_normalize(self):
        return self._get_setting('audio_normalize') == 'true'

    def get_audio_quality(self):
        return int(self._get_setting('audio_quality'))

    def get_misc_startup_screen(self):
        return int(self._get_setting('misc_startup_screen'))

    def show_dialog(self):
        #Show the dialog
        self.__addon.openSettings()


class GuiSettingsReader:
    __guisettings_doc = None

    def __init__(self):
        settings_path = xbmc.translatePath('special://profile/guisettings.xml')
        self.__guisettings_doc = ET.parse(settings_path)

    def get_setting(self, query):
        #Check if the argument is valid
        if query == '':
            raise KeyError()

        #Get the steps to the node
        step_list = query.split('.')
        root_tag = step_list[0]

        if len(step_list) > 1:
            path_remainder = '/'.join(step_list[1:])
        else:
            path_remainder = ''

        #Fail if the first tag does not match with the root
        if self.__guisettings_doc.getroot().tag != root_tag:
            raise KeyError()

        #Fail also if the element is not found
        el = self.__guisettings_doc.find(path_remainder)
        if el is None:
            raise KeyError()

        return el.text


class InfoValueManager:
    __infolabels = None

    def __init__(self):
        self.__infolabels = []

    def _get_main_window(self):
        return xbmcgui.Window(10000)

    def set_infolabel(self, name, value):
        self._get_main_window().setProperty(name, str(value))
        self.__infolabels.append(name)

    def get_infolabel(self, name):
        return self._get_main_window().getProperty(name)

    def deinit(self):
        window = self._get_main_window()
        for item in self.__infolabels:
            window.clearProperty(item)
