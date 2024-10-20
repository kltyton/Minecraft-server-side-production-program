import os
import shutil
import tkinter as tk
from tkinter import filedialog

def main():
    print("请选择客户端整合包所在的文件夹")
    # 创建Tkinter窗口
    root = tk.Tk()
    root.withdraw() 

    # 弹出选择文件夹对话框
    folder_path = filedialog.askdirectory(title="客户端所在文件夹")
    if folder_path:
        print("客户端整合包所在的文件夹路径是:", folder_path)
    else:
        print("未选择任何文件夹路径")
    print("请选择服务器所在文件夹") 
    script_dir = filedialog.askdirectory(title= "服务端所在文件夹")
    if script_dir:
        print("服务器所在文件夹路径是:", script_dir)
    else:
        print("未选择任何文件夹路径")

    # 黑名单文件夹和文件
    blacklist_dirs = ["mods", "libraries", "assets", "logs", ".fabric", ".mixin.out", ".vscode", "PCL", "saves",
                      ".earlyloadingscreen-transformer-output", "crash-reports", "fancymenu_data", "map exports",
                      "natives-windows-x86_64", "presencefootsteps", "replay_recordings", "screenshots", "shaderpacks",
                      "XaeroWaypoints", "XaeroWaypoints_BACKUP032021", "XaeroWorldMap", "versions",".physics_mod_cache"]
    blacklist_files = ["ffmpeg.exe", "options.txt", "usercache.json", "usernamecache.json"]

    # 遍历目标文件夹及其子文件夹
    for root_folder, dirs, files in os.walk(folder_path):
        # 过滤黑名单文件夹
        dirs[:] = [d for d in dirs if d not in blacklist_dirs]

        for f in files:
            # 获取文件的完整路径
            file_path = os.path.join(root_folder, f)

            # 检查文件是否在黑名单中
            if f not in blacklist_files:
                # 计算相对路径
                relative_path = os.path.relpath(file_path, folder_path)

                # 检查文件是否在黑名单文件夹及其子文件夹中
                if not any(relative_path.startswith(d + os.sep) for d in blacklist_dirs):
                    # 目标路径
                    dest_path = os.path.join(script_dir, relative_path)

                    # 创建目标路径中的目录
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                    # 移动文件到目标路径
                    shutil.move(file_path, dest_path)

    print("移动完成！")

if __name__ == "__main__":
    main()