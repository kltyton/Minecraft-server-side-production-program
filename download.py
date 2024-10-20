import json
import os
import requests
import re

def jump_download(filename):
    if os.path.exists(filename):
        return True
    else:
        return False

def validate_version(version: str) -> bool:
    # 简单的版本号格式验证
    pattern = r'^\d+(\.\d+)+$'
    return re.match(pattern, version) is not None

def choice(server_type, version, api_version, fa_setup_version):
    if server_type == "fabric":
        filename = "fabric-server.jar"
        if not jump_download(filename):
            url = f"https://meta.fabricmc.net/v2/versions/loader/{version}/{api_version}/{fa_setup_version}/server/jar"
            return url, filename
        else:
            url = None
            return url, filename
    else:
        filename = "forge-installer.jar"
        if not jump_download(filename):
            url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{version}-{api_version}/forge-{version}-{api_version}-installer.jar"
            return url, filename
        else:
            url = None
            return url, filename

def download_file(url: str, filename: str) -> bool:
    if not jump_download(filename):
        try:
            response = requests.get(url)
            response.raise_for_status()  # 检查请求是否成功
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"文件 {filename} 下载完成")
            return True
        except requests.exceptions.RequestException as e:
            print(f"下载失败: {e}")
            return False
    else:
        print(f"文件 {filename} 已存在，跳过下载步骤")
        return False

def main():
    server_folder = "服务端"
    os.chdir(server_folder)
    # 读取 JSON 文件
    with open('客户端mod信息.json','r', encoding='utf-8') as f:
        data = json.load(f)
    server_type = data['mod加载器类型']
    version = data['mc版本']
    api_version = data["mod加载器版本"]
    fa_setup_version = data["fabric安装器版本"]
    url, filename = choice(server_type, version, api_version, fa_setup_version)
    data['下载链接'] = url
    data['服务器核心文件路径'] = filename
    if download_file(url, filename):
        with open("客户端mod信息.json", "w", encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()