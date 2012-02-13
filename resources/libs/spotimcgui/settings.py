'''
Created on 11/01/2012

@author: mazkolain
'''
import xbmcaddon
from __main__ import __addon_id__
from spotify import Bitrate



class CacheManagement:
    Automatic = 0
    Manual = 1



class StreamQuality:
    Low = 0
    Medium = 1
    High = 2



class SettingsManager:
    __addon = None
    
    
    def __init__(self):
        self.__addon = xbmcaddon.Addon(id=__addon_id__)
    
    
    def _get_setting(self, name):
        return self.__addon.getSetting(name)
    
    
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
    
    
    def get_audio_sp_bitrate(self):
        settings_quality = self.get_audio_quality()
        
        if settings_quality == StreamQuality.Low:
            return Bitrate.Rate96k
        
        elif settings_quality == StreamQuality.Medium:
            return Bitrate.Rate160k
        
        elif settings_quality == StreamQuality.High:
            return Bitrate.Rate320k
    
    
    def show_dialog(self, session):
        #Store current values beore they change
        before_cache_status = self.get_cache_status()
        before_cache_management = self.get_cache_management()
        before_cache_size = self.get_cache_size()
        before_audio_normalize = self.get_audio_normalize()
        before_audio_quality = self.get_audio_quality()
        
        #Show the dialog
        self.__addon.openSettings()
        
        after_cache_status = self.get_cache_status()
        after_cache_management = self.get_cache_management()
        after_cache_size = self.get_cache_size()
        after_audio_normalize = self.get_audio_normalize()
        after_audio_quality = self.get_audio_quality()
        
        #Change these only if cache was and is enabled
        if before_cache_status and after_cache_status:
            #If cache management changed
            if before_cache_management != after_cache_management:
                if after_cache_management == CacheManagement.Automatic:
                    session.set_cache_size(0)
                elif after_cache_management == CacheManagement.Manual:
                    session.set_cache_size(after_cache_size * 1024)
            
            #If manual size changed
            if after_cache_management == CacheManagement.Manual and before_cache_size != after_cache_size:
                session.set_cache_size(after_cache_size * 1024)
        
        #Change volume normalization
        if before_audio_normalize != after_audio_normalize:
            session.set_volume_normalization(after_audio_normalize)
        
        #Change stream quality
        if before_audio_quality != after_audio_quality:
            session.preferred_bitrate(self.get_audio_sp_bitrate())
