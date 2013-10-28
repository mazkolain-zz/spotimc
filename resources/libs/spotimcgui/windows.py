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
import xbmcgui
import views
import views.newstuff
import views.album
import views.search
import views.nowplaying
import views.playlists.list
import views.playlists.detail
import views.more
import weakref

from settings import SettingsManager, StartupScreen
from utils import environment


class MainWindow(xbmcgui.WindowXML):
    __view_manager = None
    __session = None
    __playlist_manager = None
    __application = None
    __active_tab = None

    #Button id constants
    now_playing_button = 201
    new_stuff_button = 212
    playlists_button = 213
    search_button = 214
    more_button = 215
    exit_button = 216

    #Loading gif id
    loading_image = 50

    def __init__(self, file, script_path, skin_dir):
        self.__view_manager = views.ViewManager(self)

    def initialize(self, session, proxy_runner, playlist_manager, application):
        self.__session = session
        self.__playlist_manager = playlist_manager
        self.__application = application

        #Shared vars with views
        self.__view_manager.set_var('playlist_manager',
                                    weakref.proxy(self.__playlist_manager))
        self.__view_manager.set_var('session', weakref.proxy(session))
        self.__view_manager.set_var('proxy_runner',
                                    weakref.proxy(proxy_runner))

    def show_loading(self):
        c = self.getControl(MainWindow.loading_image)
        c.setVisibleCondition("True")

    def hide_loading(self):
        c = self.getControl(MainWindow.loading_image)
        c.setVisibleCondition("False")

    def _set_active_tab(self, tab=None):

        #Update the variable and the infolabel
        if tab is not None:
            self.__active_tab = tab
            self.setProperty('MainActiveTab', tab)

        #Otherwise update again the current tab
        elif self.__active_tab is not None:
            self.setProperty('MainActiveTab', self.__active_tab)

    def _init_new_stuff(self):
        self._set_active_tab('newstuff')
        v = views.newstuff.NewStuffView(self.__session)
        self.__view_manager.add_view(v)

    def _init_playlists(self):
        self._set_active_tab('playlists')
        c = self.__session.playlistcontainer()
        pm = self.__playlist_manager
        v = views.playlists.list.PlaylistView(self.__session, c, pm)
        self.__view_manager.add_view(v)

    def onInit(self):
        # Check if we already added views because after
        # exiting music vis this gets called again.
        if self.__view_manager.num_views() == 0:
            #Get the startup view from the settings
            startup_screen = SettingsManager().get_misc_startup_screen()
            if startup_screen == StartupScreen.Playlists:
                self._init_playlists()

            #Always display new stuff as a fallback
            else:
                self._init_new_stuff()

        #Otherwise show the current view
        else:
            self._set_active_tab()
            self.__view_manager.show()

        #Store current window id
        manager = self.__application.get_var('info_value_manager')
        manager.set_infolabel('spotimc_window_id',
                              xbmcgui.getCurrentWindowId())

    def onAction(self, action):
        # TODO: Remove magic values
        if action.getId() in [9, 10, 92]:
            if self.__view_manager.position() > 0:
                self.__view_manager.previous()
            elif environment.has_background_support():
                #Flush caches before minimizing
                self.__session.flush_caches()
                xbmc.executebuiltin("XBMC.ActivateWindow(0)")

        #Noop action
        # TODO: Remove magic values
        elif action.getId() in [0, 999]:
            self.__view_manager.show()

        else:
            self.__view_manager.action(action.getId())

    def _process_layout_click(self, control_id):
        if control_id == MainWindow.now_playing_button:
            self._set_active_tab('nowplaying')
            v = views.nowplaying.NowPlayingView()
            self.__view_manager.clear_views()
            self.__view_manager.add_view(v)

        elif control_id == MainWindow.playlists_button:
            self.__view_manager.clear_views()
            self._init_playlists()

        elif control_id == MainWindow.new_stuff_button:
            self.__view_manager.clear_views()
            self._init_new_stuff()

        elif control_id == MainWindow.search_button:
            term = views.search.ask_search_term()
            if term:
                self._set_active_tab('search')
                v = views.search.SearchTracksView(self.__session, term)
                self.__view_manager.clear_views()
                self.__view_manager.add_view(v)

        elif control_id == MainWindow.more_button:
            self._set_active_tab('more')
            v = views.more.MoreView()
            self.__view_manager.clear_views()
            self.__view_manager.add_view(v)

        elif control_id == MainWindow.exit_button:
            self.__application.set_var('exit_requested', True)
            self.close()

    def onClick(self, control_id):
        #IDs lower than 1000 belong to the common layout
        if control_id < 1000:
            self._process_layout_click(control_id)

        #Hand the rest to the view manager
        else:
            self.__view_manager.click(control_id)

    def onFocus(self, controlID):
        pass
