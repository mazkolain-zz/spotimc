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
from appkey import appkey
from spotify import MainLoop, ConnectionType, ConnectionRules
from spotify.session import Session, SessionCallbacks
from spotifyproxy.httpproxy import ProxyRunner
from spotifyproxy.audio import BufferManager

from threading import Event

import weakref
import dialogs

from settings import SettingsManager, CacheManagement, StreamQuality

from __main__ import __addon_version__



class SpotimcCallbacks(SessionCallbacks):
    __mainloop = None
    __buf = None
    __logout_event = None
    
    def __init__(self, mainloop, buf, event):
        self.__mainloop = mainloop
        self.__buf = buf
        self.__logout_event = event
    
    def logged_in(self, session, error):
        xbmc.log("libspotify: logged in: %d" % error)
    
    def logged_out(self, session):
        xbmc.log("libspotify: logged out")
        self.__logout_event.set()
            
    def connection_error(self, session, error):
        xbmc.log("libspotify: conn error: %d" % error)
        
    def message_to_user(self, session, data):
        xbmc.log("libspotify: msg: %s" % data)
    
    def log_message(self, session, data):
        xbmc.log("libspotify log: %s" % data)
    
    def streaming_error(self, session, error):
        xbmc.log("libspotify: streaming error: %d" % error)
    
    def play_token_lost(self, session):
        xbmc.executebuiltin('playercontrol(stop)')
        dlg = xbmcgui.Dialog()
        dlg.ok('Playback stopped', 'This account is in use on another device.')
    
    def end_of_track(self, session):
        self.__buf.set_track_ended()
        
    def notify_main_thread(self, session):
        self.__mainloop.notify()
    
    def music_delivery(self, session, data, num_samples, sample_type, sample_rate, num_channels):
        return self.__buf.music_delivery(data, num_samples, sample_type, sample_rate, num_channels)
    
    def get_audio_buffer_stats(self, session):
        return self.__buf.get_stats()



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



def check_addon_version(settings_obj):
    #If current version is higher than the stored one...
    if __addon_version__ > settings_obj.get_last_run_version():
        settings_obj.set_last_run_version(__addon_version__)
        
        d  = xbmcgui.Dialog()
        l1 = 'Spotimc was updated since the last run.'
        l2 = 'Do you want to see the changelog?'
        
        if d.yesno('Spotimc', l1, l2):
            file = settings_obj.get_addon_obj().getAddonInfo('changelog')
            changelog = open(file).read()
            dialogs.text_viewer_dialog('ChangeLog', changelog)


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



def do_login(session, script_path, skin_dir):
    #If we have a remembered user let's relogin
    if session.remembered_user() is not None:
        session.relogin()
        return True
    
    #Otherwise let's do a normal login process
    else:
        loginwin = dialogs.LoginWindow(
            "login-window.xml", script_path, skin_dir, session
        )
        loginwin.doModal()
        return not loginwin.is_cancelled()


def main(addon_dir):
    #Check needed directories first
    data_dir, cache_dir, settings_dir = check_dirs()
    
    #Instantiate the settings obj
    settings_obj = SettingsManager()
    
    #Start checking the version
    check_addon_version(settings_obj)
    
    #Don't set cache folder if it's disabled
    if not settings_obj.get_cache_status():
        cache_dir = ''
    
    #Initialize spotify stuff
    ml = MainLoop()
    buf = BufferManager()
    logout_event = Event()
    callbacks = SpotimcCallbacks(ml, buf, logout_event)
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
   
    #If login was successful start main window
    if do_login(sess, addon_dir, "DefaultSkin"):
        proxy_runner = ProxyRunner(sess, buf, host='127.0.0.1')
        proxy_runner.start()
        
        print 'port: %s' % proxy_runner.get_port()
        
        #Start main window and enter it's main loop
        mainwin = windows.MainWindow("main-window.xml", addon_dir, "DefaultSkin")
        mainwin.initialize(sess, proxy_runner)
        mainwin.doModal()
        
        #Deinit sequence
        xbmc.executebuiltin('PlayerControl(Stop)')
        proxy_runner.stop()
        
        #Logout
        sess.logout()
        logout_event.wait(10)
    
    #Stop main loop
    ml_runner.stop()
    return sess
