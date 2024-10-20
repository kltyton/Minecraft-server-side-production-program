
import json
import os
import subprocess
import sys
from packaging.version import Version

def run():
    if os.path.exists(f"启动服务器.bat"):
        subprocess.run("启动服务器.bat")
        sys.exit()
    return True

def accept_eula():
    eula_file = 'eula.txt'
    if not os.path.exists(eula_file):
        print(f"未找到 {eula_file} 文件，正在启动服务器以生成该文件...")
        return False
    with open(eula_file, 'r') as file:
        content = file.read()
    if 'eula=false' in content:
        print("请阅读并同意 EULA 协议 (https://account.mojang.com/documents/minecraft_eula)")
        eula_accept = input("输入 'true' 同意 EULA 协议：").strip().lower()
        if eula_accept == 'true':
            with open(eula_file, 'w') as file:
                file.write(content.replace('eula=false', 'eula=true'))
            print("已同意 EULA 协议")
            return True
        else:
            print("您需要同意 EULA 协议才能启动服务器")
            return False
    return True

def run_server(server_type, java_path, memory_size, filename, version_number, version, api_version):
        if server_type == "fabric":
            command = f"{java_path} -Xmx{memory_size} -jar {filename} nogui"
            if not os.path.exists("eula.txt"):
                try:
                    subprocess.run(command, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"启动服务器失败: {e}")
                    return
                finally:
                    input("启动服务器失败,可能因为你没有同意mojang的EULA 协议或其他原因,按回车退出")
            
            # 检查并同意 EULA 协议
            if not accept_eula():
                return
            
            # 再次启动服务器
            print("启动 Fabric 服务器...")
            with open("启动服务器.bat", "w", encoding='utf-8') as file:
                file.write(command)
            try:
                subprocess.run(command, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"启动服务器失败: {e}")
            finally:
                input("按回车键退出...") 
            
        elif server_type == "forge" and version_number >= Version("1.17"):
            forge_dir = f"libraries/net/minecraftforge/forge/{version}-{api_version}"
            if not os.path.exists(f"{forge_dir}/win_args.txt"):
                print("未找到 Forge 服务器核心，正在安装...")
                install_command = f"{java_path} -Xmx{memory_size} -jar {filename} --installServer"
                try:
                    subprocess.run(install_command, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"安装 Forge 服务器核心失败: {e}")
                    return
                finally:
                    input("按回车键退出...") 
            start_command = f"{java_path} -Xmx{memory_size} @user_jvm_args.txt @libraries/net/minecraftforge/forge/{version}-{api_version}/win_args.txt %* nogui"
            if not os.path.exists("eula.txt"):
            # 启动服务器以生成 eula.txt 文件
                print("启动 Forge 服务器以生成 eula.txt 文件...")
                try:
                    subprocess.run(start_command, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"启动服务器失败: {e}")
                    return
                finally:
                    input("按回车键退出...") 

            # 检查并同意 EULA 协议
            if not accept_eula():
                return

            # 再次启动服务器
            print("启动 Forge 服务器...")
            with open("启动服务器.bat", "w", encoding='utf-8') as file:
                file.write(start_command)
            try:
                subprocess.run(start_command, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"启动服务器失败: {e}")
                return
            finally:
                input("按回车键退出...") 

        elif server_type == "forge" and version_number <= Version("1.17"):
            if not os.path.exists(f"forge-{version}-{api_version}.jar"):
                print("未找到 Forge 服务器核心，正在安装...")
                install_command = f"{java_path} -Xmx{memory_size} -jar {filename} --installServer"
                try:
                    subprocess.run(install_command, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"安装 Forge 服务器核心失败: {e}")
                    return
                finally:
                    input("按回车键退出...") 
            start_command = f"{java_path} -Xmx{memory_size} -jar forge-{version}-{api_version}.jar nogui"
            if not os.path.exists("eula.txt"):
            # 启动服务器以生成 eula.txt 文件
                print("启动 Forge 服务器以生成 eula.txt 文件...")
                try:
                    subprocess.run(start_command, shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    print(f"启动服务器失败: {e}")
                    return
                finally:
                    input("按回车键退出...") 

            # 检查并同意 EULA 协议
            if not accept_eula():
                return

            # 再次启动服务器
            print("启动 Forge 服务器...")
            with open("启动服务器.bat", "w", encoding='utf-8') as file:
                file.write(start_command)
            try:
                subprocess.run(start_command, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"启动服务器失败: {e}")
                return
            finally:
                input("按回车键退出...")
                
def main():
    server_folder = "服务端"
    os.chdir(server_folder)
    run()
    with open('客户端mod信息.json','r', encoding='utf-8') as f:
        data = json.load(f)
    server_type = data['mod加载器类型']
    version = data['mc版本']
    api_version = data['mod加载器版本']
    java_path = data['选择的java路径']
    memory_size = data['分配的内存']
    filename = data['服务器核心文件路径']
    if version is not None:
        version_number = Version(version)
    else:
        version_number = None
    run_server(server_type, java_path, memory_size, filename, version_number, version, api_version)

if __name__ == "__main__":
    main()