import pafy
import vlc
 
def stream_video(url):

    video = pafy.new(url)
    best = video.getbest()
    playurl = best.url

    Instance = vlc.Instance()

    player = Instance.media_player_new()
    Media = Instance.media_new(playurl)
    Media.get_mrl()

    player.set_media(Media)

    return player, video.title, video.duration