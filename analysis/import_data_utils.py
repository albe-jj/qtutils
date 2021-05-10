# -*- coding: utf-8 -*-
# @Author: atosato
# @Date:   2021-04-10 13:11:18
# @Last Modified by:   atosato
# @Last Modified time: 2021-04-10 13:39:04


from pathlib import Path
import datetime

def get_last_measure(base_folder, days=30):
    data_path = Path(base_folder)/Path('data')
    list_of_day_folders = data_path.glob('*')
    latest_day_folder = max(list_of_day_folders, key=lambda p: p.lstat().st_mtime)
    list_meas = latest_day_folder.glob('*')
    latest_meas = max(list_meas, key=lambda p: p.lstat().st_mtime)
    return '/'.join(latest_meas.parts[-3:])