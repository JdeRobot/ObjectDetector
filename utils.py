# Created on Feb. 2020
import yaml
import os
from cprint import cprint


VALID_SOURCES = ['Local', 'Video', 'ROS', 'ICE']


def readConfig(yaml_file):
    '''Parse the YAML configuration file.'''
    with open(yaml_file, 'r') as f:
        all_cfg = yaml.safe_load(f)
    # Return only the source we will use
    source = all_cfg['Source']
    return source, all_cfg[source], all_cfg['Network']


def getVideoSource(source, params):
    """Return the camera abstract object to iterate the
    video source."""
    # Validate the source

    if source not in VALID_SOURCES:
        msg = f'The chosen source {source} is not supported. Please choose one of: {VALID_SOURCES}'
        cprint.fatal(msg, interrupt=True)

    if source == 'Local':
        from Camera.local_camera import Camera as LocalCamera
        # Local camera device selected.
        cam_idx = params['DeviceNo']
        cprint.info(f'Selected device: local camera #{cam_idx}')

        cam = LocalCamera(cam_idx)
    elif source == 'Video':
        from Camera.local_video import Camera as LocalVideo
        # Video file selected.
        video_path = os.path.expanduser(params['Path'])
        if not os.path.isfile(video_path):
            msg = f'The chosen video file {video_path} does not exist. Please check the file name.'
            cprint.fatal(msg, interrupt=True)

        cprint.info(f'Selected video: {video_path}')
        cam = LocalVideo(video_path)
    else:
        from Camera.roscam import ROSCam
    # source = cfg['ObjectDetector']['Source']
    # if source.lower() == 'local':
    #     from Camera.local_camera import Camera
    #     cam_idx = cfg['ObjectDetector']['Local']['DeviceNo']
    #     print('  Chosen source: local camera (index %d)' % (cam_idx))
    #     cam = Camera(cam_idx)
    # elif source.lower() == 'video':
    #     from Camera.local_video import Camera
    #     video_path = cfg['ObjectDetector']['Video']['Path']
    #     print('  Chosen source: local video (%s)' % (video_path))
    #     cam = Camera(video_path)
    # elif source.lower() == 'stream':
    #     # comm already prints the source technology (ICE/ROS)
    #     import comm
    #     import config
    #     cfg = config.load(sys.argv[1])
    #     jdrc = comm.init(cfg, 'ObjectDetector')
    #     proxy = jdrc.getCameraClient('ObjectDetector.Stream')
    #     from Camera.stream_camera import Camera
    #     cam = Camera(proxy)
    # else:
    #     raise SystemExit(('%s not supported! Supported source: Local, Video, Stream') % (source))

    return cam
