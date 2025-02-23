import requests
import time
from datetime import datetime
import re
import pyperclip
import inquirer

# 添加请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Origin': 'https://thepiratebay.org',
    'Referer': 'https://thepiratebay.org/'
}

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

RESOLUTION_CHOICES = [
    ("2160p (4K)", 1),
    ("1080p (Full HD)", 2),
    ("720p (HD)", 3)
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
    打印指定分辨率中Seeders最多的资源信息
    
    Args:
        results: 资源列表
        resolution: 分辨率描述(如 "1080p" 或 "720p")
        color: ANSI颜色代码(默认为普通颜色)
    """
    if results:
        max_seeder_item = max(results, key=lambda x: int(x.get('seeders', 0)))
        print(f"\n{color}{resolution}中Seeders最多的资源:")
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
    description_url = f"https://thepiratebay.org/description.php?id={id}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        # 解析响应数据
        torrent_data = response.json()
        
        # 获取info_hash和name
        info_hash = torrent_data.get('info_hash')
        name = torrent_data.get('name')
        
        if not info_hash or not name:
            raise ValueError("获取种子信息失败:缺少必要字段")
        
        if info_hash == "0000000000000000000000000000000000000000":
            raise ValueError(f"获取种子信息失败: info_hash=0000000000000000000000000000000000000000\n手动访问详情页: {description_url}")
                        
        magnet_link = generate_magnet_link(info_hash, name, TRACKERS)
        # 复制磁力链接到剪贴板
        pyperclip.copy(magnet_link)
        print(f"\033[95m{magnet_link}\033[0m")
        print("\033[95m磁力链接已复制到剪贴板\033[0m")
        
    except requests.RequestException as e:
        print(f"\033[91m获取磁力链接失败: {e}\033[0m")
    except ValueError as e:
        print(f"\033[91m{e}\033[0m")
    except Exception as e:
        print(f"\033[91m发生未知错误: {e}\033[0m")

def filter_by_quality(results, quality):
    """筛选指定质量的资源
    
    Args:
        results: 资源列表
        quality: 质量标准 ('1080p' 或 '720p')
    """
    return [r for r in results if match_pattern(r.get('name', ''), quality)]

def show_resource_selection(resources, quality, prefix_msg):
    if not resources:
        return None
        
    print(f"\033[92m{prefix_msg}{quality}内容共 {len(resources)} 条\033[0m")
    
    while True:
        # 创建选择列表，在开头添加退出选项
        choices = [("退出选择", "exit")] + [
            (f"{r.get('name')} (做种数: {r.get('seeders')})", r.get('id')) 
            for r in resources
        ]
        
        questions = [
            inquirer.List('resource_id',
                         message=f"请选择要下载的{quality}资源",
                         choices=choices)
        ]
        
        answers = inquirer.prompt(questions)
        choosen_seed_id = answers['resource_id'] if answers else None
        
        if not choosen_seed_id or choosen_seed_id == "exit":
            print("\033[93m退出选择\033[0m")
            break
            
        download_torrent(choosen_seed_id)
        # 下载完成后继续显示列表，让用户可以选择其他资源

def process_quality_results(results, prefix_msg="", max_resolution=1, list_choice=True):
    """处理不同质量的资源结果
    
    Args:
        results: 资源列表
        prefix_msg: 信息前缀(用于显示季数和集数)
        max_resolution: 要查询的最大分辨率(可选,可选值为1: 2160p, 2: 1080p, 3: 720p, 默认为1: 2160p)
    """
    res_2160p = filter_by_quality(results, r'2160p')
    res_1080p = filter_by_quality(results, r'1080p')
    res_720p = filter_by_quality(results, r'720p')
    
    if list_choice:
        if max_resolution < 2 and res_2160p:
            show_resource_selection(res_2160p, "2160p", prefix_msg)
        elif max_resolution < 3 and res_1080p:
            show_resource_selection(res_1080p, "1080p", prefix_msg)
        elif max_resolution < 4 and res_720p:
            show_resource_selection(res_720p, "720p", prefix_msg)
    else:
        if max_resolution < 2 and res_2160p:
            print(f"\033[92m{prefix_msg}2160p内容共 {len(res_2160p)} 条\033[0m")
            max_seeder_id = print_max_seeder_info(res_2160p, "2160p", "\033[92m")
            if max_seeder_id:
                download_torrent(max_seeder_id)
        elif max_resolution < 3 and res_1080p:
            print(f"\033[92m{prefix_msg}1080p内容共 {len(res_1080p)} 条\033[0m")
            max_seeder_id = print_max_seeder_info(res_1080p, "1080p", "\033[92m")
            if max_seeder_id:
                download_torrent(max_seeder_id)
        elif max_resolution < 4 and res_720p:
            print(f"\033[92m{prefix_msg}720p内容共 {len(res_720p)} 条\033[0m")
            max_seeder_id = print_max_seeder_info(res_720p, "720p", "\033[92m")
            if max_seeder_id:
                download_torrent(max_seeder_id)

def process_episode_results(filtered_results, season, episodes, max_resolution=1):
    """处理按集筛选的结果
    
    Args:
        filtered_results: 按季筛选后的结果
        season: 季数
        episodes: 集数列表
        max_resolution: 要查询的最大分辨率(可选,可选值为1: 2160p, 2: 1080p, 3: 720p, 默认为1: 2160p)
    """
    for ep in episodes:
        ep_pattern = f"E{str(ep).zfill(2)}|Episode {ep}"
        ep_results = [item for item in filtered_results if match_pattern(item.get('name', ''), ep_pattern)]
        
        if ep_results:
            print(f"\n第{season}季第{ep}集资源共 {len(ep_results)} 条")
            process_quality_results(ep_results, f"第{season}季第{ep}集", max_resolution, list_choice=False)
        else:
            print(f"\033[93m未找到第{season}季第{ep}集的资源\033[0m")

def poll_pirate_bay(query_name, season=None, episodes=None, max_resolution=1):
    """查询并下载指定电影/剧集的种子
    
    Args:
        query_name: 要查询的电影/剧集名称
        season: 要查询的季数(如果要筛选集数则必传)
        episodes: 要查询的集数列表(可选,但必须配合season使用)
        max_resolution: 要查询的最大分辨率(可选,可选值为1: 2160p, 2: 1080p, 3: 720p, 默认为1: 2160p)
    """
    if episodes and season is None:
        print("\033[91m错误: 筛选集数时必须指定季数\033[0m")
        return
        
    url = f"https://apibay.org/q.php?q={query_name}&cat=200"
    
    try:
        response = requests.get(url, headers=HEADERS)
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
                process_episode_results(filtered_results, season, episodes, max_resolution)
            else:
                process_quality_results(filtered_results, f"第{season}季", max_resolution)
        else:
            # 不按季筛选，直接处理所有资源
            process_quality_results(results, max_resolution=max_resolution)
                    
    except requests.RequestException as e:
        print(f"\033[91m请求出错: {e}\033[0m")
    except Exception as e:
        print(f"\033[91m发生未知错误: {e}\033[0m")

def main():
    print("开始调用 The Pirate Bay API...")
    print("按 Ctrl+C 停止程序")
    
    # 获取用户输入
    query_name = input("请输入要搜索的电影/剧集名称: ")
    
    questions = [
        inquirer.List('max_resolution',
                     message="请选择要搜索的最大分辨率",
                     choices=RESOLUTION_CHOICES,
                     default=RESOLUTION_CHOICES[0])
    ]
    
    answers = inquirer.prompt(questions)
    max_resolution = answers['max_resolution']
    
    # 季数输入验证
    while True:
        season_input = input("请输入要搜索的季数(直接回车跳过): ")
        if not season_input.strip():
            season = None
            break
        try:
            season = int(season_input)
            break
        except ValueError:
            print("\033[91m错误：请输入单个数字，例如：1\033[0m")
    
    episodes = None
    if season is not None:
        while True:
            episodes_input = input("请输入要搜索的集数(多集用逗号分隔,直接回车搜索整季): ")
            if not episodes_input.strip():
                break
            try:
                episodes = [int(e.strip()) for e in episodes_input.split(",")]
                break
            except ValueError:
                print("\033[91m错误：请输入正确的集数格式，例如：1,2,3\033[0m")
    
    if episodes:
        print("\033[92m开始轮询（每60秒查询一次）\033[0m")
        # 指定集数时，进入轮询
        while True:
            poll_pirate_bay(query_name, season, episodes, max_resolution)
            time.sleep(60)  # 等待60秒后再次查询
    else:
        # 不指定集数时，直接查询
        poll_pirate_bay(query_name, season, episodes, max_resolution)

if __name__ == "__main__":
    main()