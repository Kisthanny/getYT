import subprocess
import os
import re

def quote(s):
    return f'"{re.sub(r'[^a-zA-Z0-9_.\- ()]', '', s).replace('"', '\\"')}"'

def merge_audio_video(audio_path, video_path, output_path):
    cmd = f'ffmpeg -y -i {audio_path} -i {video_path} -c:a copy -c:v copy {quote(output_path)}'
    subprocess.call(cmd, shell=True)
    print('混合完成')
    os.remove(audio_path)
    os.remove(video_path)
    print('临时音频和视频文件已删除')