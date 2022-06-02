# -*- coding: utf-8 -*-
'Functions for the OA Clock In'
__author__ = 'mars wong at 2020-06-09 10:17'

import argparse
import os
import shlex
import subprocess


class Command:
    def __init__(self) -> None:
        self.code = None
        self.out = None
        self.error = None
        self.success = False

    # 执行命令
    def exec(self, cmd):
        try:
            process = subprocess.run(shlex.split(cmd, posix=False), shell=False, capture_output=True)
            self.out = str(process.stdout, encoding='utf-8')
            self.code = process.returncode
            self.success = self.code == 0
            process.check_returncode()
        except subprocess.CalledProcessError as e:
            self.error = str(e.stderr, encoding='utf-8')
        return self

# 获取设备信息
def get_device_info():
    result = os.popen('adb devices -l')
    res = result.read()
    device_info = {}
    for line in res.splitlines():
        if line != 'List of devices attached':
            info = line.split(' ')
            serial_number = info[0]
            for content in info:
                if content.__len__() > 0 and content.__contains__('model') > 0:
                    device_info[serial_number] = content[content.index(':') + 1:]
    return device_info


# 安装应用
def install(serial_number, model, apk_path):
    print(f'Installing to the {model} ...')
    cmd = f'adb -s {serial_number} install -r -t -d {apk_path}'
    result = Command().exec(cmd)
    if result.success:
        print('Installed Success.')
    else:
        tip = input(f'Installed failed[code:{result.code}]: {result.error}\rTry again or push to SDCard? (t/p): ')
        if tip.lower() == 't':
            install(serial_number, model, apk_path)
        elif tip.lower() == 'p':
            push_to_sd_card(apk_path)


# push到SD卡
def push_to_sd_card(apk_path):
    cmd = 'adb shell echo $EXTERNAL_STORAGE'
    result = Command().exec(cmd)
    sdcard_dir = None
    if result.success:
        sdcard_dir = result.out.strip()
        file_name = os.path.basename(apk_path)
        print(f'Pushing {file_name} into {sdcard_dir} ...')
        cmd = f'adb push {apk_path} {sdcard_dir}'
        result = Command().exec(cmd)
    if result.success:
        print(f"Pushed Success. It's in SDCard root directory.")
    else:
        error_msg = [f'Pushed failed[code:{result.code}]: ']
        if result.error:
            error_msg.append('{result.error}\r')
        tip = input(f'{"".join(error_msg)}Try again? (y/n): ')
        if tip.lower() == 'y':
            push_to_sd_card(apk_path)


# 检测一个或多个设备
def detect_one_or_more(apk_path):
    device_info = get_device_info()
    if device_info.__len__() > 0:
        device_info_keys = device_info.keys()
        keys_length = device_info_keys.__len__()
        if keys_length > 1:
            index = 1
            # 若有多个设备，则列举出来供用户通过输入序号来选择
            print('---------------------------------------------------------')
            for info_key in device_info_keys:
                print('{}): {} ({})'.format(index, device_info.get(info_key), info_key))
                index = index + 1
            print('---------------------------------------------------------')
            number = eval(input('Please choose the target device, press zero for all: '))
            if number not in range(1, keys_length + 1):
                # 若超出索引范围，则置为0
                number = 0
            if number > 0:
                # 安装到所选序号的设备中
                serial_number = list(device_info_keys)[number - 1]
                install(serial_number, device_info.get(serial_number), apk_path)
            else:
                # 安装到所有设备
                for info_key in device_info_keys:
                    install(info_key, device_info.get(info_key), apk_path)
        else:
            # 如果只有一个设备，则只接安装到该设备
            serial_number = list(device_info_keys)[0]
            install(serial_number, device_info.get(serial_number), apk_path)

    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.description = 'Please drag apk file into this control panel or input the apk file path here:'
    parser.add_argument('-p', '--path', help='apk file path', dest='path', type=str)
    args = parser.parse_args()

    # 获取输入的绝对路径
    apk_abspath = os.path.abspath(args.path)
    detect_one_or_more(apk_abspath)
    pass
