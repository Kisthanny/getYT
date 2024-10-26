from download_audio_video import download_audio_video
from merge_audio_video import merge_audio_video

# sabrina carpenter
# https://www.youtube.com/watch?v=eVli-tstM5E
# https://www.youtube.com/watch?v=KEG7b851Ric
# https://www.youtube.com/watch?v=cF1Na4AIecM
# https://www.youtube.com/watch?v=YcSP1ZUf1eQ
# https://www.youtube.com/watch?v=kLbn61Z4LDI
# https://www.youtube.com/watch?v=1YUBbF24H44

# chappelle roan
# https://www.youtube.com/watch?v=xaPNR-_Cfn0
# https://www.youtube.com/watch?v=6ENzV125lWc

# olivia rodrigo
# https://www.youtube.com/watch?v=ZmDBbnmKpqQ
# https://www.youtube.com/watch?v=gNi_6U5Pm_o
# https://www.youtube.com/watch?v=cii6ruuycQA
# https://www.youtube.com/watch?v=ZQFmRXgeR-s
# https://www.youtube.com/watch?v=CRrf3h9vhp8
# https://www.youtube.com/watch?v=RlPNh_PBZb4
# https://www.youtube.com/watch?v=OGUy2UmRxJ0
# https://www.youtube.com/watch?v=ZsJ-BHohXRI
# https://www.youtube.com/watch?v=Dj9qJsJTsjQ
# https://www.youtube.com/watch?v=5myKp4ZD2KQ

# taylor swift
# https://www.youtube.com/watch?v=tCXGJQYZ9JA
# https://www.youtube.com/watch?v=b1kbLwvqugk
# https://www.youtube.com/watch?v=K-a8s8OLBSE
# https://www.youtube.com/watch?v=JLf9q36UsBk
# https://www.youtube.com/watch?v=RsEZmictANA
# https://www.youtube.com/watch?v=q3zqJs7JUCQ
# https://www.youtube.com/watch?v=AqAJLh9wuZ0

# post malone
# https://www.youtube.com/watch?v=ApXoWvfEYVU
# https://www.youtube.com/watch?v=SC4xMk98Pdc
# https://www.youtube.com/watch?v=UceaB4D0jpo
# https://www.youtube.com/watch?v=au2n7VVGv_c
# https://www.youtube.com/watch?v=wXhTHyIgQ_U
# https://www.youtube.com/watch?v=UYwF-jdcVjY
# https://www.youtube.com/watch?v=ba7mB8oueCY
# https://www.youtube.com/watch?v=393C3pr2ioY

# the weeknd
# https://www.youtube.com/watch?v=34Na4j8AVgA
# https://www.youtube.com/watch?v=yzTuBuRdAyA
# https://www.youtube.com/watch?v=XXYlFuWEuKI
# https://www.youtube.com/watch?v=4NRXx6U8ABQ
# https://www.youtube.com/watch?v=waU75jdUnYw
# https://www.youtube.com/watch?v=LIIDh-qI9oI

# ariana grande
# https://www.youtube.com/watch?v=QYh6mYIJG2Y
# https://www.youtube.com/watch?v=iS1g8G_njx8
# https://www.youtube.com/watch?v=ffxKSjUwKdU
# https://www.youtube.com/watch?v=g5qU7p7yOY8
# https://www.youtube.com/watch?v=gl1aHhXnN1k
# https://www.youtube.com/watch?v=tcYodQoapMg
# https://www.youtube.com/watch?v=B6_iQvaIjXw

# lana del rey
# https://www.youtube.com/watch?v=Bag1gUxuU0g
# https://www.youtube.com/watch?v=cE6wxDqdOV0
# https://www.youtube.com/watch?v=o_1aF54DO60
# https://www.youtube.com/watch?v=7NyPEtPUTRg

from pytubefix import YouTube
import subprocess
import os
import re
def download_and_merge(url):

    title = download_audio_video(url)

    output_path = f'{title}.mp4'

    print(output_path)

    merge_audio_video('audio.mp3', 'video.mp4', output_path)

urls = [
    "https://www.youtube.com/watch?v=7NyPEtPUTRg"
]

def get_caption(url):
    yt = YouTube(url)
    
    captions = yt.captions
    print(captions)
    
    caption = next(iter(captions), None)
    print(caption)
    
    if caption:
        caption.save_captions("captions.srt")
        
        video_path = 'video.mp4'
        caption_path = 'captions.srt'
        
        cmd = f'ffmpeg -i {video_path} -i {caption_path} -c copy -c:s mov_text output.mp4'
        subprocess.call(cmd, shell=True)
    else:
        print("未找到字幕")

for url in urls:
    # download_and_merge(url)
    get_caption(url)
