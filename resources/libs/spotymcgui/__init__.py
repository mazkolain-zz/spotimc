'''
Created on 24/06/2011

@author: mikel
'''
__all__ = ["mainwindow"]



import os
import os.path
import xbmc
import windows
import threading
from appkey import appkey
from spotify import MainLoop, ConnectionType, ConnectionRules
from spotify.session import Session, SessionCallbacks
from spotifyproxy.httpproxy import ProxyRunner
from spotifyproxy.audio import BufferManager

from threading import Event

import weakref

from settings import SettingsManager, CacheManagement, StreamQuality


class SpotymcCallbacks(SessionCallbacks):
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



def check_dirs():
    addon_data_dir = os.path.join(
        xbmc.translatePath('special://profile/addon_data'),
        'script.audio.spotymc'
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



def main(addon_dir):
    #Check needed directories first
    data_dir, cache_dir, settings_dir = check_dirs()
    
    #Instantiate the settings obj
    settings_obj = SettingsManager()
    
    #Don't set cache folder if it's disabled
    if not settings_obj.get_cache_status():
        cache_dir = ''
    
    #Initialize spotify stuff
    ml = MainLoop()
    buf = BufferManager()
    logout_event = Event()
    callbacks = SpotymcCallbacks(ml, buf, logout_event)
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
    
    #Initialize & start proxy and mainloop runners
    ml_runner = MainLoopRunner(ml, sess)
    proxy_runner = ProxyRunner(sess, buf, host='0.0.0.0')
    ml_runner.start()
    proxy_runner.start()
    
    #Initialize window
    mainwin = windows.MainWindow("main-window.xml", addon_dir, "DefaultSkin")
    mainwin.initialize(sess, proxy_runner)
    
    #And finally the window's loop
    mainwin.doModal()
    
    #Deinit sequence
    xbmc.executebuiltin('PlayerControl(Stop)')
    proxy_runner.stop()
    ml_runner.stop()
    sess.logout()
    logout_event.wait(10)
    
    return sess
