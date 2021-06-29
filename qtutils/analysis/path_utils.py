from pathlib import Path
from shutil import copyfile, copytree, rmtree
import win32api


# def get_root(root):
#     'get V drive if not M'
#     if not root.is_dir():
#         path_ls = Path(root).parts
#         root = Path('V://').joinpath(*path_ls[1:])
#     return root

def get_root(root):
    'search for root in other drives'
    if root.is_dir():
        return root
    else:
        # print('searching for root..')
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        path_ls = Path(root).parts

        for drive in drives:
            path = Path(drive).joinpath(*path_ls[1:])
            if path.is_dir():
                print('found root in: ', path)
                return path

        #for bea's webdrive
        for drive in drives:
            path = Path(drive).joinpath('staff-groups',*path_ls[1:])
            if path.is_dir():
                print('found root in: ', path)
                return path

        print('could not find', root)
        return root

def upload_to_Mdrive(data_path, network_data_folder):
    'copy the file from network_location to drive if not in base_folder'
    print('importing data from network')
    src = network_data_folder / data_path.name
    dst = data_path
    if src.is_file():
        copyfile(src, dst)
    elif src.is_dir():
        Path(dst).mkdir(parents=True, exist_ok=True)
        rmtree(dst) 
        copytree(src, dst)
    else:
        print('could not find', network_data_folder)


