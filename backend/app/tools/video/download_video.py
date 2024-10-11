from pytubefix import YouTube
from pytube.innertube import _default_clients

_default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"

def download_youtube_video(url, output_path='.'):
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        stream.download(output_path)
        print(f"Download concluído! Vídeo salvo em: {output_path}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

video_url = 'https://www.youtube.com/watch?v=YIMjJVzGkwY'
download_youtube_video(video_url, output_path='videos/')