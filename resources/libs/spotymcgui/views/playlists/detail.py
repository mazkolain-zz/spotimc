'''
Created on 27/10/2011

@author: mikel
'''
import xbmcgui
from spotymcgui.views import BaseView


class PlaylistDetailView(BaseView):
    __group_id = 1800
    __list_id = 1801
    
    
    def click(self, view_manager, window, control_id):
        pass
    
    
    def _get_list(self, window):
        return window.getControl(PlaylistDetailView.__list_id)
    
    
    def _add_track(self, list, title, artist, album, path, duration):
        item = xbmcgui.ListItem(path=path)
        item.setInfo(
            "music",
            {
             "title": title, "artist": artist, "album": album,
             "duration": duration
            }
        )
        list.addItem(item)
    
    
    def _set_playlist_properties(self, window, is_collaborative):
        if is_collaborative:
            window.setProperty("PlaylistDetailCollaborative", "True")
            print "playlist set as collaborative"
        else:
            window.setProperty("PlaylistDetailCollaborative", "False")
            print "playlist set as non-collaborative"
    
    
    def _set_playlist_image(self, window, thumbnails):
        if len(thumbnails) > 0:
            #Set cover info
            if len(thumbnails) < 4:
                window.setProperty("PlaylistDetailCoverLayout", "one")
            else:
                window.setProperty("PlaylistDetailCoverLayout", "four")
            
            #Now loop to set all the images
            for idx, thumb_item in enumerate(thumbnails):
                window.setProperty("PlaylistDetailCoverItem%d" % (idx + 1), thumb_item)
    
    
    def _populate_list(self, window):
        l = self._get_list(window)
        l.reset()
        
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 186)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 7560)
        self._add_track(l, "A very long track name that overflows the column", "A reasonably long artist name", "A long album name that overflows the column", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        
        
        #window.setProperty("AlbumCover", "http://www.me-pr.co.uk/axxis%20doom%20cover%20small.jpg")
        #window.setProperty("AlbumName", "Album Name")
        #window.setProperty("ArtistName", "Artist Name")
        #img.setImage("http://www.necramonium.com/photos/KISS-Album-Covers/cover_destroyer.jpg")
        
    
    def show(self, window):
        thumbnails = [
            'http://sleevage.com/wp-content/uploads/2007/08/keane_under_the_iron_sun.jpg',
            'http://images.mirror.co.uk/upl/dailyrecord3/oct2009/4/8/susan-boyle-album-cover-image-1-733838072.jpg',
            'http://musicalatinaymas.com/wp-content/uploads/2010/12/jennifer_lopez_love_album_cover_art-300x300.jpg',
            'http://2.bp.blogspot.com/_ketX-ka6ZkU/TFX1kJoKa3I/AAAAAAAAAZI/g6ahYp9yDS8/s400/David_Guetta_-_One_Love_(Official_Album_Cover).jpg',
        ]
        
        #Set playlist data
        self._set_playlist_properties(window, True)
        self._set_playlist_image(window, thumbnails)
        self._populate_list(window)
        
        c = window.getControl(PlaylistDetailView.__group_id)
        c.setVisibleCondition("true")
        print "show!"
    
    
    def hide(self, window):
        c = window.getControl(PlaylistDetailView.__group_id)
        c.setVisibleCondition("false")
        print "hide!"
