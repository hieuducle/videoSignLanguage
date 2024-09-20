import os
import os.path as osp
import shutil
import configargparse
from tqdm import tqdm

from text2animation.load_dictionary import load_dictionary

def qipedc_filter(videos_folder, des_folder):
    os.makedirs(des_folder, exist_ok=True)
    usable_id = load_dictionary().values()
    for video in tqdm(os.listdir(videos_folder)):
        id = osp.splitext(video)[0]
        if id in usable_id:
            shutil.copy2(src=osp.join(videos_folder, video),
                         dst=des_folder)
    return des_folder


if __name__ == "__main__":
    args = {}
    parser = configargparse.ArgParser(formatter_class=configargparse.ArgumentDefaultsHelpFormatter,
                                      description='Qipedc filter',
                                      prog='vsl')
    parser.add_argument('--videos-folder',
                        type=str,
                        required=True,
                        help='Source folder')
    parser.add_argument('--des-folder',
                        type=str,
                        required=True,
                        help='Destination folder')
    args = vars(parser.parse_args())

    qipedc_filter(**args)