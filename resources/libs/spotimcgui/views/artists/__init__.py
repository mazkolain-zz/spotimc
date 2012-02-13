import xbmcgui
import albums


def choose_artist(artist_list):
    if len(artist_list) > 1:
        d = xbmcgui.Dialog()
        artist_names = [artist.name() for artist in artist_list]
        result = d.select('Choose an artist', artist_names)
        if result != -1:
            return artist_list[result]
    
    else:
        return artist_list[0]


def open_artistbrowse_albums(view_manager, artist_list):
    artist = choose_artist(artist_list)
    if artist is not None:
        session = view_manager.get_var('session')
        v = albums.ArtistAlbumsView(session, artist)
        view_manager.add_view(v)
