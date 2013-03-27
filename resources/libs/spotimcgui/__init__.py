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


__all__ = ["mainwindow"]



import os
import os.path
import xbmc, xbmcgui
import windows
import threading
import gc
from appkey import appkey
from spotify import MainLoop, ConnectionType, ConnectionRules, ConnectionState, ErrorType, track as _track
from spotify.session import Session, SessionCallbacks
from spotifyproxy.httpproxy import ProxyRunner
from spotifyproxy.audio import BufferManager
from taskutils.decorators import run_in_thread

from threading import Event

import weakref
import dialogs

from settings import SettingsManager, CacheManagement, StreamQuality, GuiSettingsReader

from __main__ import __addon_version__

import playback



class Application:
    __vars = None
    
    
    def __init__(self):
        self.__vars = {}
    
    
    def set_var(self, name, value):
        self.__vars[name] = value
    
    
    def has_var(self, name):
        return name in self.__vars
    
    
    def get_var(self, name):
        return self.__vars[name]
    
    
    def remove_var(self, name):
        del self.__vars[name]



class SpotimcCallbacks(SessionCallbacks):
    __mainloop = None
    __audio_buffer = None
    __logout_event = None
    __app = None
    
    
    def __init__(self, mainloop, audio_buffer, app):
        self.__mainloop = mainloop
        self.__audio_buffer = audio_buffer
        self.__app = app
    
    def logged_in(self, session, error_num):
        #Log this event
        xbmc.log("libspotify: logged in: %d" % error_num)
        
        #Store last error code
        self.__app.set_var('login_last_error', error_num)
        
        #Take action if error status is not ok
        if error_num != ErrorType.Ok:
            
            #Close the main window if it's running
            if self.__app.has_var('main_window'):
                self.__app.get_var('main_window').close()
            
            #Otherwise, set the connstate event
            else:
                self.__app.get_var('connstate_event').set()
        
    def logged_out(self, session):
        xbmc.log("libspotify: logged out")
        self.__app.get_var('logout_event').set()
            
    def connection_error(self, session, error):
        xbmc.log("libspotify: conn error: %d" % error)
        
    def message_to_user(self, session, data):
        xbmc.log("libspotify: msg: %s" % data)
    
    def log_message(self, session, data):
        xbmc.log("libspotify log: %s" % data)
    
    def streaming_error(self, session, error):
        xbmc.log("libspotify: streaming error: %d" % error)
    
    @run_in_thread
    def play_token_lost(self, session):
        
        #Cancel the current buffer
        self.__audio_buffer.stop()
        
        if self.__app.has_var('playlist_manager'):
            self.__app.get_var('playlist_manager').stop(False)
        
        dlg = xbmcgui.Dialog()
        dlg.ok('Playback stopped', 'This account is in use on another device.')
    
    def end_of_track(self, session):
        self.__audio_buffer.set_track_ended()
        
    def notify_main_thread(self, session):
        self.__mainloop.notify()
    
    def music_delivery(self, session, data, num_samples, sample_type, sample_rate, num_channels):
        return self.__audio_buffer.music_delivery(data, num_samples, sample_type, sample_rate, num_channels)
    
    def connectionstate_changed(self, session):
        
        #Set the apropiate event flag, if available
        self.__app.get_var('connstate_event').set()



class MainLoopRunner(threading.Thread):
    __mainloop = None
    __session = None
    __proxy = None
    
    
    def __init__(self, mainloop, session):
        threading.Thread.__init__(self)
        self.__mainloop = mainloop
        self.__session = weakref.proxy(session)
    
    
    def run(self):
        self.__mainloop.loop(self.__session)
    
    
    def stop(self):
        self.__mainloop.quit()
        self.join(10)



def show_legal_warning(settings_obj):
    shown = settings_obj.get_legal_warning_shown()
    if not shown:
        settings_obj.set_legal_warning_shown(True)
        d = xbmcgui.Dialog()
        l1 = 'Spotimc uses SPOTIFY(R) CORE but is not endorsed,'
        l2 = 'certified or otherwise approved in any way by Spotify.'
        d.ok('Spotimc', l1, l2)



def check_addon_version(settings_obj):
    last_run_version = settings_obj.get_last_run_version()
    
    #If current version is higher than the stored one...
    if __addon_version__ > last_run_version:
        settings_obj.set_last_run_version(__addon_version__)
        
        #Don't display the upgrade message if it's the first run
        if last_run_version != '':
            d  = xbmcgui.Dialog()
            l1 = 'Spotimc was updated since the last run.'
            l2 = 'Do you want to see the changelog?'
            
            if d.yesno('Spotimc', l1, l2):
                file = settings_obj.get_addon_obj().getAddonInfo('changelog')
                changelog = open(file).read()
                dialogs.text_viewer_dialog('ChangeLog', changelog)


def get_audio_buffer_size():
    #Base buffer setting will be 5s
    buffer_size = 5
    
    try:
        reader = GuiSettingsReader()
        value = reader.get_setting('settings.musicplayer.crossfade')
        buffer_size += int(value)
    
    except:
        xbmc.log(
            'Failed reading crossfade setting. Using default value.',
            xbmc.LOGERROR
        )
    
    return buffer_size



def check_dirs():
    addon_data_dir = os.path.join(
        xbmc.translatePath('special://profile/addon_data'),
        'script.audio.spotimc'
    )
    
    #Auto-create profile dir if it does not exist
    if not os.path.exists(addon_data_dir):
        os.makedirs(addon_data_dir)
    
    #Libspotify cache & settings
    sp_cache_dir = os.path.join(addon_data_dir, 'libspotify/cache')
    sp_settings_dir = os.path.join(addon_data_dir, 'libspotify/settings')
    
    if not os.path.exists(sp_cache_dir):
        os.makedirs(sp_cache_dir)
    
    if not os.path.exists(sp_settings_dir):
        os.makedirs(sp_settings_dir)
    
    return (addon_data_dir, sp_cache_dir, sp_settings_dir)



def set_settings(settings_obj, session):
    #If cache is enabled set the following one
    if settings_obj.get_cache_status():
        if settings_obj.get_cache_management() == CacheManagement.Manual:
            cache_size_mb = settings_obj.get_cache_size() * 1024
            session.set_cache_size(cache_size_mb)
    
    #Bitrate...
    session.preferred_bitrate(settings_obj.get_audio_sp_bitrate())
    
    #And volume normalization
    session.set_volume_normalization(settings_obj.get_audio_normalize())    



def do_login(session, script_path, skin_dir, app):
    #Get the last error if we have one
    if app.has_var('login_last_error'):
        prev_error = app.get_var('login_last_error')
    else:
        prev_error = 0
    
    #If no previous errors and we have a remembered user
    if prev_error == 0 and session.remembered_user() is not None:
        session.relogin()
        status = True
    
    #Otherwise let's do a normal login process
    else:
        loginwin = dialogs.LoginWindow(
            "login-window.xml", script_path, skin_dir
        )
        loginwin.initialize(session, app)
        loginwin.doModal()
        status = not loginwin.is_cancelled()
    
    return status


def login_get_last_error(app):
    if app.has_var('login_last_error'):
        return app.get_var('login_last_error')
    else:
        return 0


def wait_for_connstate(session, app, state):
    
    #Store the previous login error number
    last_login_error = login_get_last_error(app)
    
    #Add a shortcut to the connstate event
    cs = app.get_var('connstate_event')
    
    #Wrap all the tests for the following loop
    def continue_loop():
        
        #Get the current login error
        cur_login_error = login_get_last_error(app)
        
        #Continue the loop while these conditions are met:
        #  * An exit was not requested
        #  * Connection state was not the desired one
        #  * No login errors where detected
        return (
            not app.get_var('exit_requested') and
            session.connectionstate() != state and (
                last_login_error == cur_login_error or
                cur_login_error == ErrorType.Ok
            )
        )
    
    #Keep testing until conditions are met
    while continue_loop():
        cs.wait(5)
        cs.clear()
    
    return session.connectionstate() == state


def get_preloader_callback(session, playlist_manager, buffer):
    session = weakref.proxy(session)
    def preloader():
        next_track = playlist_manager.get_next_item(session)
        if next_track is not None:
            ta = next_track.get_availability(session)
            if ta == _track.TrackAvailability.Available:
                buffer.open(session, next_track)
    
    return preloader



def main(addon_dir):
    #Initialize app var storage
    app = Application()
    logout_event = Event()
    connstate_event = Event()
    app.set_var('logout_event', logout_event)
    app.set_var('login_last_error', ErrorType.Ok)
    app.set_var('connstate_event', connstate_event)
    app.set_var('exit_requested', False)
    
    #Check needed directories first
    data_dir, cache_dir, settings_dir = check_dirs()
    
    #Instantiate the settings obj
    settings_obj = SettingsManager()
    
    #Show legal warning
    show_legal_warning(settings_obj)
    
    #Start checking the version
    check_addon_version(settings_obj)
    
    #Don't set cache folder if it's disabled
    if not settings_obj.get_cache_status():
        cache_dir = ''
    
    #Initialize spotify stuff
    ml = MainLoop()
    buf = BufferManager(get_audio_buffer_size())
    callbacks = SpotimcCallbacks(ml, buf, app)
    sess = Session(
        callbacks,
        app_key=appkey,
        user_agent="python ctypes bindings",
        settings_location=settings_dir,
        cache_location=cache_dir,
        initially_unload_playlists=False,
    )
    
    #Now that we have a session, set settings
    set_settings(settings_obj, sess)
    
    #Initialize libspotify's main loop handler on a separate thread
    ml_runner = MainLoopRunner(ml, sess)
    ml_runner.start()
   
    #Stay on the application until told to do so
    while not app.get_var('exit_requested'):
        
        #Set the exit flag if login was cancelled
        if not do_login(sess, addon_dir, "DefaultSkin", app):
            app.set_var('exit_requested', True)
        
        #Otherwise block until state is sane, and continue
        elif wait_for_connstate(sess, app, ConnectionState.LoggedIn):
            
            proxy_runner = ProxyRunner(sess, buf, host='127.0.0.1', allow_ranges=False)
            proxy_runner.start()
            
            print 'port: %s' % proxy_runner.get_port()
            
            #Instantiate the playlist manager
            playlist_manager = playback.PlaylistManager(proxy_runner)
            app.set_var('playlist_manager', playlist_manager)
            
            #Set the track preloader callback
            preloader_cb = get_preloader_callback(sess, playlist_manager, buf)
            proxy_runner.set_stream_end_callback(preloader_cb)
            
            #Start main window and enter it's main loop
            mainwin = windows.MainWindow("main-window.xml", addon_dir, "DefaultSkin")
            mainwin.initialize(sess, proxy_runner, playlist_manager, app)
            app.set_var('main_window', mainwin)
            mainwin.doModal()
            
            #Playback and proxy deinit sequence
            proxy_runner.clear_stream_end_callback()
            playlist_manager.stop()
            proxy_runner.stop()
            buf.cleanup()
            
            #Clear some vars and collect garbage
            proxy_runner = None
            preloader_cb = None
            playlist_manager = None
            mainwin = None
            app.remove_var('main_window')
            app.remove_var('playlist_manager')
            gc.collect()
            
            #Logout
            if sess.user() is not None:
                sess.logout()
                logout_event.wait(10)
    
    #Stop main loop
    ml_runner.stop()
