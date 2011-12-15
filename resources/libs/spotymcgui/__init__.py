'''
Created on 24/06/2011

@author: mikel
'''
__all__ = ["mainwindow"]



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
    
    def streaming_error(self, error):
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



def main(addon_dir):
    profile_dir = os.path.join(
        xbmc.translatePath('special://profile/addon_data'), 'script.audio.spotymc'
    )
    
    #Initialize spotify stuff
    ml = MainLoop()
    buf = BufferManager()
    logout_event = Event()
    callbacks = SpotymcCallbacks(ml, buf, logout_event)
    sess = Session(
        callbacks,
        app_key=appkey,
        user_agent="python ctypes bindings",
        settings_location=os.path.join(profile_dir, 'libspotify'),
        cache_location=os.path.join(profile_dir, 'libspotify'),
        initially_unload_playlists=True,
    )
    
    proxy_runner = ProxyRunner(sess, buf)
    
    #Initialize window
    mainwin = windows.MainWindow("main-window.xml", addon_dir, "DefaultSkin", sess)
    
    #Run the (libspotify) loop in a separate thread (XBMC requires this for doModal()
    ml_runner = MainLoopRunner(ml, sess)
    ml_runner.start()
    proxy_runner.start()
    
    #And finally the window's loop
    mainwin.doModal()
    
    #Deinit sequence
    xbmc.executebuiltin('PlayerControl(Stop)')
    proxy_runner.stop()
    ml_runner.stop()
    sess.logout()
    logout_event.wait(10)
    
    return sess
