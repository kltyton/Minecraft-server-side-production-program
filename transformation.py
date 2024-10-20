import hashlib
import os
import shutil
import struct
import requests
import json
from tqdm import tqdm
from tkinter import Tk, filedialog, messagebox, simpledialog

# 初始化
unknown_mods = []
hash_dict = []
log_entries = []
side_translation = {
    "required": "必需",
    "optional": "可选",
    "unsupported": "不支持"
}
modrinth_base_url = "https://api.modrinth.com/v2"
curseforge_base_url = "https://api.curseforge.com/v1"
unknown_folder = "服务端/需要人工排查的mod文件"

# 初始化日志
def log(message):
    print(message)
    log_entries.append(message)

#curseforge哈希值解密(murmurhash2,seed = 1)
def read_file_bytes(file_path):
    with open(file_path, 'rb') as f:
        return f.read()

def murmurhash2(data, seed=1):
    m = 0x5bd1e995
    r = 24
    length = len(data)
    h = seed ^ length

    for i in range(0, length - 3, 4):
        k = struct.unpack_from('<I', data, i)[0]
        k = (k * m) & 0xFFFFFFFF
        k ^= k >> r
        k = (k * m) & 0xFFFFFFFF
        h = (h * m) & 0xFFFFFFFF
        h ^= k

    if length % 4 != 0:
        remaining = data[length - (length % 4):]
        if len(remaining) == 3:
            h ^= remaining[2] << 16
        if len(remaining) >= 2:
            h ^= remaining[1] << 8
        if len(remaining) >= 1:
            h ^= remaining[0]
        h = (h * m) & 0xFFFFFFFF

    h ^= h >> 13
    h = (h * m) & 0xFFFFFFFF
    h ^= h >> 15

    return h

def get_curseforge_hash(file_path):
    data = read_file_bytes(file_path)
    filtered_data = bytearray(b for b in data if b not in (9, 10, 13, 32))
    hash_value = murmurhash2(filtered_data)
    return hash_value

#使用curseforge获得信息
def get_mod_info_curseforge(hash_value, use_curseforge, api_key=None):
    if use_curseforge:
        game_id = 432
        fingerprint = hash_value
        url = f"{curseforge_base_url}/fingerprints/{game_id}"
        headers = {"x-api-key": api_key}
        payload = {"fingerprints": [fingerprint]}
        # 发送POST请求
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            mod_info = response.json()['data']
            return mod_info
        else:
            log(f"获取模组信息时发生HTTP错误，Hash值: {hash_value}，错误: {response.status_code}")
            return None

def is_server_pack(mod_info):
    if mod_info:
        latest_files = mod_info.get('exactMatches', [])
        for file in latest_files:
            file_data = file.get('file', {})
            if file_data.get('isServerPack', None):
                return True
    return None

# 获得mod当前版本信息
def get_mod_info(hash_value):
    url = f"{modrinth_base_url}/version_file/{hash_value}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        mod_info = response.json()
        project_id = mod_info.get('project_id')
        return mod_info, project_id
    except requests.exceptions.HTTPError as http_err:
        log(f"获取模组信息时发生HTTP错误，Hash值: {hash_value}，错误: {http_err}")
        return None, None
    except Exception as err:
        log(f"获取模组信息时发生其他错误，Hash值: {hash_value}，错误: {err}")
        return None, None
    finally:
        os.system('cls')

#获得mod当前项目信息
def get_project_info(mod_file, project_id):
    url = f"{modrinth_base_url}/project/{project_id}"
    headers = {}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        log(f"获取模组信息时发生HTTP错误，ID: {mod_file}，错误: {http_err}")
    except Exception as err:
        log(f"获取模组信息时发生其他错误，ID: {mod_file}，错误: {err}")
    return None

# 通过哈希数值区分服务端客户端（modrinth）
def process_mod_file(mods_folder, mod_file, project_id, hash_value):
    project_info = get_project_info(mod_file, project_id)
    if project_info:
        client_side = project_info.get('client_side')
        server_side = project_info.get('server_side')
        client_side_cn = side_translation.get(client_side, "未知")
        server_side_cn = side_translation.get(server_side, "未知")

        if client_side and server_side:
            folder_name = f"服务端{server_side_cn}客户端{client_side_cn}"
            target_folder = os.path.join(mods_folder, folder_name)
            os.makedirs(target_folder, exist_ok=True)
            source_path = os.path.join(mods_folder, mod_file)
            target_path = os.path.join(target_folder, mod_file)
            if os.path.exists(source_path):
                try:
                    shutil.move(source_path, target_path)
                    log(f"已将 {mod_file} 移动到 {target_folder}")
                    hash_dict.append({"文件名": mod_file, "Hash值": hash_value, "项目ID": project_id, "客户端":client_side_cn, "服务端":server_side_cn})
                except Exception as e:
                    log(f"移动文件 {mod_file} 时发生错误: {e}")
                finally:
                    os.system('cls')
            else:
                log(f"文件 {source_path} 不存在")
                os.system('cls')
        else:
            log(f"模组 {mod_file} 的客户端或服务端环境未知: client_side={client_side}, server_side={server_side}")
            hash_dict.append({"文件名": mod_file, "Hash值": hash_value, "项目ID": project_id, "客户端":client_side_cn, "服务端":server_side_cn})
            os.system('cls')
    else:
        log(f"未找到模组 {mod_file} 的信息")
        unknown_mods.append(mod_file)
        log(f"未知的mod: {mod_file}")
        source_path = os.path.join(mods_folder, mod_file)
        target_path = os.path.join(unknown_folder, mod_file)
        if os.path.exists(source_path):
            try:
                shutil.move(source_path, target_path)
                log(f"已将 {mod_file} 移动到 {unknown_folder}")
            except Exception as e:
                log(f"移动未知文件 {mod_file} 时发生错误: {e}")
            finally:
                os.system('cls')
        else:
            log(f"文件 {source_path} 不存在")

# 输入forge密匙
def get_api_key():
    config_path = 'config.json'
    api_key = None

    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            api_key = config.get('api-key')

    if not api_key:
        api_key = simpledialog.askstring("输入API密钥", "请输入CurseForge的API密钥:")
        if api_key:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump({'api-key': api_key}, f, ensure_ascii=False, indent=4)

    return api_key

# 计算哈希值
def calculate_hash(file_path):
    hasher = hashlib.sha1()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
    except IOError as e:
        log(f"无法读取文件 {file_path}: {e}")
        return None
    return hasher.hexdigest()

#选择客户端文件夹
def select_client_folder():
    mods_folder = filedialog.askdirectory(title="选择客户端文件夹")
    if mods_folder:
        return mods_folder
    if not mods_folder:
        log("未选择文件夹，程序退出")
        return
    log(f"选择客户端文件夹: {mods_folder}")

#获得mods文件夹所有文件
def get_mods_files(mods_folder):
    # 获取mods文件夹中的所有mod文件
    mod_files = [f for f in os.listdir(mods_folder) if f.endswith('.jar')]
    return mod_files

#核心代码
def code(mod_files, mods_folder, use_curseforge, api_key):
    for mod_file in tqdm(mod_files, desc="处理模组文件"):
        file_path = os.path.join(mods_folder, mod_file)
        log(f"正在处理模组: {mod_file}")
        #MODRINTH
        if not use_curseforge:
            hash_value = calculate_hash(file_path)
            if hash_value:
                mod_info, project_id = get_mod_info(hash_value)
                if mod_info:
                    process_mod_file(mods_folder, mod_file, project_id, hash_value)
        #FORGE
        elif use_curseforge:
            hash_value = get_curseforge_hash(file_path)
            mod_info = get_mod_info_curseforge(hash_value, use_curseforge, api_key)
            is_server = is_server_pack(mod_info)
            target_server_folder = "服务端mod"
            target_client_folder = "客户端mod"
            target_server_path = os.path.join(mods_folder, target_server_folder)
            target_client_path = os.path.join(mods_folder, target_client_folder)
            if not os.path.exists(target_server_path) or not os.path.exists(target_client_path):
                os.makedirs(target_server_path)
                os.makedirs(target_client_path)
            if is_server:
                shutil.move(file_path, target_server_path)
                hash_dict.append({"文件名": mod_file, "Hash值": hash_value, "客户端":not is_server, "服务端":is_server})
            elif not is_server:
                shutil.move(file_path, target_client_path)
                hash_dict.append({"文件名": mod_file, "Hash值": hash_value, "客户端":not is_server, "服务端":is_server})
            else:
                shutil.move(file_path, unknown_folder)
                hash_dict.append({"文件名": mod_file, "Hash值": hash_value, "客户端":"未知", "服务端":"未知"})

def secondary(mods_folder, use_curseforge):
    #没使用curseforge APi
    if not use_curseforge:
        mod_files = get_mods_files(mods_folder)
        if not mod_files:
            log("使用modrinth的API区分mod完成")
            log("但仍有以下mod未能获取到信息（它们可能来自于CurseForge或者自制mod，而你未使用CurseForge的api）")
            log(mod_files)
            log("你可以手动排除或者使用CurseForge进行查询")
            log("PS:如果你实在没有CurseForgeAPI密匙或者无法申请可以私信FUFU借用一下")
            choice = input("输入y使用CurseForge进行查询区分mods文件,其他键返回主菜单并输出人工区分mod列表：")
            if choice == "y":
                api_key = get_api_key()
                if not api_key:
                    log("未提供CurseForge的API密钥，程序退出")
                    return
                else:
                    use_curseforge = True
                    code(mod_files, mods_folder, use_curseforge, api_key)
            else:
                for mod_file in tqdm(mod_files, desc="处理模组文件"):
                    unknown_mods.append(mod_file)
                    source_path = os.path.join(mods_folder, mod_file)
                    target_path = os.path.join(unknown_folder, mod_file)
                    if os.path.exists(source_path):
                        try:
                            shutil.move(source_path, target_path)
                            log(f"已将 {mod_file} 移动到 {unknown_folder}")
                            os.system('cls')
                        except Exception as e:
                            log(f"移动未知文件 {mod_file} 时发生错误: {e}")
                            os.system('cls')
                    else:
                        log(f"文件 {source_path} 不存在")
                        os.system('cls')
# 主函数
def main():
    print("开始执行")
    #选择forge/fabric
    root = Tk()
    root.withdraw()
    use_curseforge = messagebox.askyesno("选择API", "是否使用CurseForge的API？")
    api_key = None
    if use_curseforge:
        api_key = get_api_key()
        if not api_key:
            log("未提供CurseForge的API密钥，程序退出")
            return

    #选择客户端文件夹
    log("请选择客户端整合包文件夹")
    mods_folder = select_client_folder()
    client_folder = "客户端缓存文件夹"
    shutil.copytree(mods_folder, client_folder, dirs_exist_ok=True)
    log("成功复制")
    os.system('cls')

    #获得mods文件夹所有文件
    mods_folder = os.path.join(client_folder, 'mods')
    mod_files = get_mods_files(mods_folder)

    #核心代码
    code(mod_files, mods_folder, use_curseforge, api_key)
    
    script_path = "服务端"
    
    log("执行第一次移动")
    move(script_path, mods_folder)

    # 将错误文件信息（需要人工排查）写入JSON文件
    with open('需要人工排查mod列表.json', 'w', encoding='utf-8') as json_file:
        json.dump(unknown_mods, json_file, ensure_ascii=False, indent=4)
        log("需要人工排查mod列表信息已写入 需要人工排查mod列表.json 文件")

    # 将哈希值信息写入JSON文件
    with open('MOD信息.json', 'w', encoding='utf-8') as json_file:
        json.dump(hash_dict, json_file, ensure_ascii=False, indent=4)
        log("哈希值信息已写入 哈希信息.json 文件")

    # 保存日志
    with open('log.json', 'w', encoding='utf-8') as f:
        json.dump(log_entries, f, ensure_ascii=False, indent=4)
    log("日志已保存到 log.json")
    log("执行完毕")

if __name__ == "__main__":
    main()
