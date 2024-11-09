import requests
import time
from datetime import datetime
import re
import pyperclip

TRACKERS = [
    "udp://tracker.opentrackr.org:1337",
    "udp://open.stealth.si:80/announce",
    "udp://tracker.torrent.eu.org:451/announce",
    "udp://tracker.bittor.pw:1337/announce",
    "udp://public.popcorn-tracker.org:6969/announce",
    "udp://tracker.dler.org:6969/announce",
    "udp://exodus.desync.com:6969",
    "udp://open.demonii.com:1337/announce"
]

def match_pattern(text, pattern):
    """
    在文本中匹配指定模式
    
    Args:
        text: 要搜索的文本字符串
        pattern: 要匹配的正则表达式模式
        
    Returns:
        bool: 是否匹配成功
    """
    return bool(re.search(pattern, text, re.IGNORECASE))

def print_max_seeder_info(results, resolution, color="\033[0m"):
    reset = "\033[0m"
    """
    打印指定分辨率中种子数最多的资源信息
    
    Args:
        results: 资源列表
        resolution: 分辨率描述(如 "1080p" 或 "720p")
        color: ANSI颜色代码(默认为普通颜色)
    """
    if results:
        max_seeder_item = max(results, key=lambda x: int(x.get('seeders', 0)))
        print(f"\n{color}{resolution}中种子数最多的资源:")
        print(f"名称: {max_seeder_item.get('name')}")
        print(f"ID: {max_seeder_item.get('id')}")
        print(f"做种数: {max_seeder_item.get('seeders')}{reset}")
        return max_seeder_item.get('id')
    
def generate_magnet_link(hash_value, display_name, trackers):
    # 基础磁力链接格式
    base = f"https://thepiratebay.org/magnet:?xt=urn:btih:{hash_value}"
    
    # URL编码文件名
    import urllib.parse
    encoded_name = urllib.parse.quote(display_name)
    name_param = f"&dn={encoded_name}"
    
    # URL编码并添加tracker
    tracker_params = ""
    for tracker in trackers:
        encoded_tracker = urllib.parse.quote(tracker)
        tracker_params += f"&tr={encoded_tracker}"
    
    return base + name_param + tracker_params

def download_torrent(id):
    url = f"https://apibay.org/t.php?id={id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # 解析响应数据
        torrent_data = response.json()
        
        # 获取info_hash和name
        info_hash = torrent_data.get('info_hash')
        name = torrent_data.get('name')
        
        if not info_hash or not name:
            raise ValueError("获取种子信息失败:缺少必要字段")
            
        magnet_link = generate_magnet_link(info_hash, name, TRACKERS)
        # 复制磁力链接到剪贴板
        pyperclip.copy(magnet_link)
        print(f"\033[95m{magnet_link}\033[0m")
        print("\033[95m磁力链接已复制到剪贴板\033[0m")
        
    except requests.RequestException as e:
        print(f"\033[91m获取磁力链接失败: {e}\033[0m")
    except ValueError as e:
        print(f"\033[91m{e}\033[0m")

def filter_by_quality(results, quality):
    """筛选指定质量的资源
    
    Args:
        results: 资源列表
        quality: 质量标准 ('1080p' 或 '720p')
    """
    return [r for r in results if match_pattern(r.get('name', ''), quality)]

def process_quality_results(results, prefix_msg=""):
    """处理不同质量的资源结果
    
    Args:
        results: 资源列表
        prefix_msg: 信息前缀(用于显示季数和集数)
    """
    res_1080p = filter_by_quality(results, r'1080p')
    res_720p = filter_by_quality(results, r'720p')
    
    if res_1080p:
        print(f"\033[92m{prefix_msg}1080p内容共 {len(res_1080p)} 条\033[0m")
        max_seeder_id = print_max_seeder_info(res_1080p, "1080p", "\033[92m")
        if max_seeder_id:
            download_torrent(max_seeder_id)
    elif res_720p:
        print(f"\033[94m{prefix_msg}720p内容共 {len(res_720p)} 条\033[0m")
        max_seeder_id = print_max_seeder_info(res_720p, "720p", "\033[94m")
        if max_seeder_id:
            download_torrent(max_seeder_id)

def process_episode_results(filtered_results, season, episodes):
    """处理按集筛选的结果
    
    Args:
        filtered_results: 按季筛选后的结果
        season: 季数
        episodes: 集数列表
    """
    for ep in episodes:
        ep_pattern = f"E{str(ep).zfill(2)}|Episode {ep}"
        ep_results = [item for item in filtered_results if match_pattern(item.get('name', ''), ep_pattern)]
        
        if ep_results:
            print(f"\n第{season}季第{ep}集资源共 {len(ep_results)} 条")
            process_quality_results(ep_results, f"第{season}季第{ep}集")
        else:
            print(f"\033[93m未找到第{season}季第{ep}集的资源\033[0m")

def poll_pirate_bay(query_name, season=None, episodes=None):
    """查询并下载指定电影/剧集的种子
    
    Args:
        query_name: 要查询的电影/剧集名称
        season: 要查询的季数(如果要筛选集数则必传)
        episodes: 要查询的集数列表(可选,但必须配合season使用)
    """
    if episodes and season is None:
        print("\033[91m错误: 筛选集数时必须指定季数\033[0m")
        return
        
    url = f"https://apibay.org/q.php?q={query_name}&cat=200"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{current_time}] 查询结果:")
        
        results = response.json()
        if not results:
            print("\033[93m未找到相关结果\033[0m")
            return
            
        print(f"共找到 {len(results)} 条结果")
        
        # 按季筛选
        if season is not None:
            season_pattern = f"S{str(season).zfill(2)}|Season {season}"
            filtered_results = [item for item in results if match_pattern(item.get('name', ''), season_pattern)]
            print(f"第{season}季内容共 {len(filtered_results)} 条")
            
            if not filtered_results:
                print(f"\033[93m未找到第{season}季的资源\033[0m")
                return
                
            # 处理按集筛选或整季资源
            if episodes:
                process_episode_results(filtered_results, season, episodes)
            else:
                process_quality_results(filtered_results, f"第{season}季")
        else:
            # 不按季筛选，直接处理所有资源
            process_quality_results(results)
                    
    except requests.RequestException as e:
        print(f"\033[91m请求出错: {e}\033[0m")

def main():
    print("开始轮询 The Pirate Bay API...")
    print("按 Ctrl+C 停止程序")
    
    while True:
        poll_pirate_bay('arcane', 2, [1, 2, 3])
        time.sleep(60)  # 等待60秒后再次查询

if __name__ == "__main__":
    main()