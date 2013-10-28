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
from spotify import Bitrate
from spotimcgui.views import BaseListContainerView
from spotimcgui.settings import SettingsManager, CacheManagement, StreamQuality


class MoreView(BaseListContainerView):
    container_id = 1900
    list_id = 1901

    def _do_logout(self, view_manager):
        #Ask the user first
        dlg = xbmcgui.Dialog()
        response = dlg.yesno(
            'Sign Off',
            'This will forget the remembered user.',
            'Are you sure?'
        )

        if response:
            session = view_manager.get_var('session')
            session.forget_me()
            view_manager.get_window().close()

    def _do_settings(self, view_manager):
        settings = SettingsManager()
        session = view_manager.get_var('session')

        #Store current values before they change
        before_cache_status = settings.get_cache_status()
        before_cache_management = settings.get_cache_management()
        before_cache_size = settings.get_cache_size()
        before_audio_normalize = settings.get_audio_normalize()
        before_audio_quality = settings.get_audio_quality()

        #Show the dialog
        settings.show_dialog()

        after_cache_status = settings.get_cache_status()
        after_cache_management = self.get_cache_management()
        after_cache_size = settings.get_cache_size()
        after_audio_normalize = settings.get_audio_normalize()
        after_audio_quality = settings.get_audio_quality()

        #Change these only if cache was and is enabled
        if before_cache_status and after_cache_status:

            #If cache management changed
            if before_cache_management != after_cache_management:
                if after_cache_management == CacheManagement.Automatic:
                    session.set_cache_size(0)
                elif after_cache_management == CacheManagement.Manual:
                    session.set_cache_size(after_cache_size * 1024)

            #If manual size changed
            if (after_cache_management == CacheManagement.Manual and
                    before_cache_size != after_cache_size):
                session.set_cache_size(after_cache_size * 1024)

        #Change volume normalization
        if before_audio_normalize != after_audio_normalize:
            session.set_volume_normalization(after_audio_normalize)

        #Change stream quality
        #FIXME: Repeated code, should be moved to utils
        br_map = {
            StreamQuality.Low: Bitrate.Rate96k,
            StreamQuality.Medium: Bitrate.Rate160k,
            StreamQuality.High: Bitrate.Rate320k,
        }
        if before_audio_quality != after_audio_quality:
            session.preferred_bitrate(br_map[after_audio_quality])

    def _handle_list_click(self, view_manager):
        item = self.get_list(view_manager).getSelectedItem()

        if item is not None:
            key = item.getLabel2()

            if key == 'settings':
                self._do_settings(view_manager)

            elif key == 'sign-off':
                self._do_logout(view_manager)

    def click(self, view_manager, control_id):
        if control_id == MoreView.list_id:
            self._handle_list_click(view_manager)

    def get_container(self, view_manager):
        return view_manager.get_window().getControl(MoreView.container_id)

    def get_list(self, view_manager):
        return view_manager.get_window().getControl(MoreView.list_id)

    def _add_item(self, list_obj, key, label, icon):
        list_obj.addItem(
            xbmcgui.ListItem(label=label, label2=key, iconImage=icon)
        )

    def render(self, view_manager):
        list_obj = self.get_list(view_manager)
        list_obj.reset()

        #Add the items
        self._add_item(list_obj, 'settings', "Settings",
                       "common/more-settings-icon.png")
        self._add_item(list_obj, 'sign-off', "Sign Off",
                       "common/more-logout-icon.png")

        return True
