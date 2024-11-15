import os
import subprocess
import sys
import venv
from pathlib import Path

def create_venv(venv_path):
    """创建虚拟环境"""
    print(f"正在创建虚拟环境: {venv_path}")
    venv.create(venv_path, with_pip=True)

def is_unix_shell():
    """判断是否为类Unix shell环境"""
    shell = os.environ.get('SHELL', '').lower()
    term = os.environ.get('TERM', '').lower()
    # 添加对 zsh 的判断，并检查是否是 Unix 类系统
    return ('bash' in shell or 
            'zsh' in shell or 
            'git' in term or 
            'unix' in term or 
            sys.platform != "win32")

def install_requirements(venv_path, requirements_file):
    """安装依赖项"""
    # 根据操作系统获取pip路径
    if sys.platform == "win32":
        pip_path = os.path.join(venv_path, "Scripts", "pip")
    else:
        pip_path = os.path.join(venv_path, "bin", "pip")
    
    # 读取requirements.txt，去除版本号
    with open(requirements_file) as f:
        packages = [line.split('==')[0].strip() for line in f if line.strip() and not line.startswith('#')]
    
    print("正在安装依赖项...")
    for package in packages:
        print(f"安装: {package}")
        subprocess.run([pip_path, "install", package])

def get_path(*path_parts):
    """根据系统和shell环境生成适当的路径"""
    return os.path.join(*path_parts)

def main():
    # 设置虚拟环境路径
    venv_path = Path("venv")
    requirements_file = "requirements.txt"

    # 检查requirements.txt是否存在
    if not os.path.exists(requirements_file):
        print("错误: requirements.txt 文件不存在")
        return

    # 创建虚拟环境
    create_venv(venv_path)
    
    # 安装依赖项
    install_requirements(venv_path, requirements_file)
    
    print("虚拟环境设置完成！")
    
    # 根据操作系统确定路径部分
    if sys.platform == "win32":
        activate_parts = [".", "venv", "Scripts", "activate"]
    else:
        activate_parts = [".", "venv", "bin", "activate"]
    
    # 生成激活命令
    activate_path = get_path(*activate_parts)
    if is_unix_shell():
        activate_cmd = f"source {activate_path}"
    else:
        activate_cmd = activate_path
    
    print("\n要激活虚拟环境，请运行以下命令：")
    print(f"\033[95m    {activate_cmd}\033[0m")

if __name__ == "__main__":
    main()