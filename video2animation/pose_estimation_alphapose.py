import os

import os.path as osp

import env

import platform
import sys
import time

import numpy as np
import torch
from tqdm import tqdm
import natsort

from detector.apis import get_detector
from trackers.tracker_api import Tracker
from trackers.tracker_cfg import cfg as tcfg
from trackers import track
from alphapose.models import builder
from alphapose.utils.config import update_config
from alphapose.utils.detector import DetectionLoader
from alphapose.utils.file_detector import FileDetectionLoader
from alphapose.utils.transforms import flip, flip_heatmap
from alphapose.utils.vis import getTime
from alphapose.utils.webcam_detector import WebCamDetectionLoader
from alphapose.utils.writer import DataWriter

def pose_estimate(video_path):
    args = {}
    args['cfg'] = "C:\\workspace\\AlphaPose-master\\configs\\halpe_136\\resnet\\256x192_res50_lr1e-3_2x-regression.yaml"
    args['checkpoint'] = "C:\\workspace\\AlphaPose-master\\pretrained_models\\halpe136_fast50_regression_256x192.pth"
    args['sp'] = False
    args['detector'] = "yolo"
    args['detfile'] = ""
    args['inputpath'] = ""
    args['inputlist'] = ""
    args['inputimg'] = ""
    args['outputpath'] = "examples/res/"
    args['save_img'] = False
    args['vis'] = False
    args['showbox'] = False
    args['profile'] = False
    args['format'] = "open"
    args['min_box_area'] = 0
    args['detbatch'] = 5
    args['posebatch'] = 64
    args['eval'] = False
    args['gpus'] = "0"
    args['qsize'] = 1024
    args['flip'] = False
    args['debug'] = False
    args['video'] = video_path
    args['webcam'] = -1
    args['save_video'] = True
    args['vis_fast'] = False
    args['pose_flow'] = False
    args['pose_track'] = False

    cfg = update_config(args['cfg'])

    if platform.system() == 'Windows':
        args['sp'] = True

    args['gpus'] = [int(i) for i in args['gpus'].split(',')] if torch.cuda.device_count() >= 1 else [-1]
    args['device'] = torch.device("cuda:" + str(args['gpus'][0]) if args['gpus'][0] >= 0 else "cpu")
    args['detbatch'] = args['detbatch'] * len(args['gpus'])
    args['posebatch'] = args['posebatch'] * len(args['gpus'])
    args['tracking'] = args['pose_track'] or args['pose_flow'] or args['detector'] == 'tracker'

    if not args['sp']:
        torch.multiprocessing.set_start_method('forkserver', force=True)
        torch.multiprocessing.set_sharing_strategy('file_system')

    def check_input():
        # for wecam
        if args['webcam'] != -1:
            args['detbatch'] = 1
            return 'webcam', int(args['webcam'])

        # for video
        if len(args['video']):
            if os.path.isfile(args['video']):
                videofile = args['video']
                return 'video', videofile
            else:
                raise IOError('Error: --video must refer to a video file, not directory.')

        # for detection results
        if len(args['detfile']):
            if os.path.isfile(args['detfile']):
                detfile = args['detfile']
                return 'detfile', detfile
            else:
                raise IOError('Error: --detfile must refer to a detection json file, not directory.')

        # for images
        if len(args['inputpath']) or len(args['inputlist']) or len(args['inputimg']):
            inputpath = args['inputpath']
            inputlist = args['inputlist']
            inputimg = args['inputimg']

            if len(inputlist):
                im_names = open(inputlist, 'r').readlines()
            elif len(inputpath) and inputpath != '/':
                for root, dirs, files in os.walk(inputpath):
                    im_names = files
                im_names = natsort.natsorted(im_names)
            elif len(inputimg):
                args['inputpath'] = os.path.split(inputimg)[0]
                im_names = [os.path.split(inputimg)[1]]

            return 'image', im_names

        else:
            raise NotImplementedError

    def print_finish_info():
        print('===========================> Finish Model Running.')
        if (args['save_img'] or args['save_video']) and not args['vis_fast']:
            print('===========================> Rendering remaining images in the queue...')
            print('===========================> If this step takes too long, you can enable the --vis_fast flag to use fast rendering (real-time).')

    def loop():
        n = 0
        while True:
            yield n
            n += 1

    mode, input_source = check_input()

    if not os.path.exists(args['outputpath']):
        os.makedirs(args['outputpath'])

    # Load detection loader
    if mode == 'webcam':
        det_loader = WebCamDetectionLoader(input_source, get_detector(args), cfg, args)
        det_worker = det_loader.start()
    elif mode == 'detfile':
        det_loader = FileDetectionLoader(input_source, cfg, args)
        det_worker = det_loader.start()
    else:
        det_loader = DetectionLoader(input_source, get_detector(args), cfg, args, batchSize=args['detbatch'], mode=mode, queueSize=args['qsize'])
        det_worker = det_loader.start()

    # Load pose model
    pose_model = builder.build_sppe(cfg.MODEL, preset_cfg=cfg.DATA_PRESET)

    print('Loading pose model from %s...' % (args['checkpoint'],))
    pose_model.load_state_dict(torch.load(args['checkpoint'], map_location=args['device']))
    pose_dataset = builder.retrieve_dataset(cfg.DATASET.TRAIN)
    if args['pose_track']:
        tracker = Tracker(tcfg, args)
    if len(args['gpus']) > 1:
        pose_model = torch.nn.DataParallel(pose_model, device_ids=args['gpus']).to(args['device'])
    else:
        pose_model.to(args['device'])
    pose_model.eval()
    runtime_profile = {
    'dt': [],
    'pt': [],
    'pn': []
    }

    # Init data writer
    queueSize = 2 if mode == 'webcam' else args['qsize']
    if args['save_video'] and mode != 'image':
        from alphapose.utils.writer import DEFAULT_VIDEO_SAVE_OPT as video_save_opt
        if mode == 'video':
            video_save_opt['savepath'] = os.path.join(args['outputpath'], 'AlphaPose_' + os.path.basename(input_source))
        else:
            video_save_opt['savepath'] = os.path.join(args['outputpath'], 'AlphaPose_webcam' + str(input_source) + '.mp4')
        video_save_opt.update(det_loader.videoinfo)
        writer = DataWriter(cfg, args, save_video=True, video_save_opt=video_save_opt, queueSize=queueSize).start()
    else:
        writer = DataWriter(cfg, args, save_video=False, queueSize=queueSize).start()

    if mode == 'webcam':
        print('Starting webcam demo, press Ctrl + C to terminate...')
        sys.stdout.flush()
        im_names_desc = tqdm(loop())
    else:
        data_len = det_loader.length
        im_names_desc = tqdm(range(data_len), dynamic_ncols=True)

    batchSize = args['posebatch']
    if args['flip']:
        batchSize = int(batchSize / 2)

    video_path = osp.abspath(video_path)
    vid_name = osp.splitext(osp.split(video_path)[1])[0]
    output_folder = osp.join(env.OPENPOSE_OUTPUT_KEYPOINT, vid_name)
    os.makedirs(output_folder, exist_ok=True)
    try:
        for i in im_names_desc:
            start_time = getTime()
            with torch.no_grad():
                (inps, orig_img, im_name, boxes, scores, ids, cropped_boxes) = det_loader.read()
                if orig_img is None:
                    break
                if boxes is None or boxes.nelement() == 0:
                    writer.save(None, None, None, None, None, orig_img, im_name)
                    continue
                if args['profile']:
                    ckpt_time, det_time = getTime(start_time)
                    runtime_profile['dt'].append(det_time)
                # Pose Estimation
                inps = inps.to(args['device'])
                datalen = inps.size(0)
                leftover = 0
                if (datalen) % batchSize:
                    leftover = 1
                num_batches = datalen // batchSize + leftover
                hm = []
                for j in range(num_batches):
                    inps_j = inps[j * batchSize:min((j + 1) * batchSize, datalen)]
                    if args['flip']:
                        inps_j = torch.cat((inps_j, flip(inps_j)))
                    hm_j = pose_model(inps_j)
                    if args['flip']:
                        hm_j_flip = flip_heatmap(hm_j[int(len(hm_j) / 2):], pose_dataset.joint_pairs, shift=True)
                        hm_j = (hm_j[0:int(len(hm_j) / 2)] + hm_j_flip) / 2
                    hm.append(hm_j)
                hm = torch.cat(hm)
                if args['profile']:
                    ckpt_time, pose_time = getTime(ckpt_time)
                    runtime_profile['pt'].append(pose_time)
                if args['pose_track']:
                    boxes, scores, ids, hm, cropped_boxes = track(tracker, args, orig_img, inps, boxes, hm, cropped_boxes, im_name, scores)
                hm = hm.cpu()
                writer.save(boxes, scores, ids, hm, cropped_boxes, orig_img, im_name)
                if args['profile']:
                    ckpt_time, post_time = getTime(ckpt_time)
                    runtime_profile['pn'].append(post_time)

            if args['profile']:
                # TQDM
                im_names_desc.set_description(
                    'det time: {dt:.4f} | pose time: {pt:.4f} | post processing: {pn:.4f}'.format(                        dt=np.mean(runtime_profile['dt']), pt=np.mean(runtime_profile['pt']), pn=np.mean(runtime_profile['pn']))
                )

        print_finish_info()
        # output_folder = args['outputpath']
        args['outputpath'] = output_folder
        while writer.running():
            time.sleep(1)
            print('===========================> Rendering remaining ' + str(writer.count()) + ' images in the queue...', end='\r')
        writer.stop()
        det_loader.stop()
    except Exception as e:
        print(repr(e))
        print('An error as above occurs when processing the images, please check it')
        pass
    except KeyboardInterrupt:
        print_finish_info()
        # Thread won't be killed when press Ctrl+C
        if args['sp']:
            det_loader.terminate()
            while writer.running():
                time.sleep(1)
                print('===========================> Rendering remaining ' + str(writer.count()) + ' images in the queue...', end='\r')
            writer.stop()
        else:
            # subprocesses are killed, manually clear queues
            det_loader.terminate()
            writer.terminate()
            writer.clear_queues()
            det_loader.clear_queues()
    return output_folder

