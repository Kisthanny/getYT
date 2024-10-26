from pytubefix import YouTube
from pytubefix.cli import on_progress
import os

def download_audio_video(url):
    yt = YouTube(url, on_progress_callback = on_progress)

    title = yt.title

    print(title)
    
    #  highest resolution video
    video = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True, res='1080p')
    for v in video:
        print(v)

    audio = yt.streams.filter(only_audio=True)

    print('------ video ------')

    highset_res_video = video.get_highest_resolution(progressive=False)

    print(f"最高分辨率视频: {highset_res_video.resolution}")

    print('------ audio ------')

    # 按比特率降序排序音频流,并获取第一个(最高比特率)
    highest_bitrate_audio = sorted(audio, key=lambda x: int(x.abr[:-4]), reverse=True)[0]

    print(f"最高比特率音频: {highest_bitrate_audio.abr}")
    
    video_path = 'video.mp4'
    audio_path = 'audio.mp3'

    try:
        print('开始下载视频')
        highset_res_video.download(filename=video_path, max_retries=8)
        print(f"\n视频下载完成: {video_path}")
    except Exception as e:
        print(f"\n视频下载失败: {e}")
        if os.path.exists(video_path):
            os.remove(video_path)
    
    try:
        print('开始下载音频')
        highest_bitrate_audio.download(filename=audio_path, max_retries=8)
        print(f"\n音频下载完成: {audio_path}")
    except Exception as e:
        print(f"\n音频下载失败: {e}")
        if os.path.exists(audio_path):
            os.remove(audio_path)
    
    return title