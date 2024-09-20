import os
import os.path as osp
import shutil

import configargparse


def main(folder: str, div: int):
    if not osp.isdir(folder):
        raise Exception(f'{folder} is not a directory path')
    
    files_list = sorted(os.listdir(folder))
    files = []
    for name in files_list:
        fn = osp.join(folder, name)
        if osp.isfile(fn):
            files.append(fn)
    
    folder = osp.normpath(folder)
    des_dirs = []
    for idx in range(div):
        dir = folder+"#"+str(idx)
        os.makedirs(dir, exist_ok=True)
        des_dirs.append(dir)
        
    file_per_subfolder = (len(files)+div-1)//div
    for idx, file in enumerate(files):
        shutil.copy2(src=file,
                     dst=des_dirs[idx//file_per_subfolder])


if __name__ == "__main__":
    args = {}
    parser = configargparse.ArgParser(formatter_class=configargparse.ArgumentDefaultsHelpFormatter,
                                      description='Folder splitter',
                                      prog='vsl')
    parser.add_argument('--folder',
                        type=str,
                        required=True,
                        help='The folder you want to split')
    parser.add_argument('--div',
                        type=int,
                        required=True,
                        help='The number of sub-folders will be created')
    args = vars(parser.parse_args())

    main(**args)