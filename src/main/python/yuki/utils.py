# -*- coding: utf-8 -*-
"""
module author: Long Hao <hoolongvfx@gmail.com>
"""

# Import built-in modules
import subprocess
import os
import re
from platform import system


def create_missing_directories(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)


def get_file_ext(path):
    if os.path.splitext(path)[1]:
        ext = os.path.splitext(path)[1]
        ext = ext.replace(".", "")
        return ext
    else:
        return ""


def assemble_command(ffmpeg, file_path, thumb_file):
    command = [
        ffmpeg,
        "-y",
        "-i",
        file_path,
        "-f",
        "image2",
        "-t",
        "0.001",
        "-vframes",
        # Make Thumb image in that frame.
        "10",
        "-vf",
        # Thumb file scale size.
        "scale=300:-1:sws_dither=ed",
        thumb_file
    ]
    return command


def create_thumb_file(ffmpeg, file_path, thumb_file):
    command = assemble_command(ffmpeg, file_path, thumb_file)
    subprocess.check_call(command, shell=True)


def video_infos_ffmpeg(ffmpeg, filepath):
    r"""
    Parses the information from a video using ffmpeg.
    Uses subprocess to get the information through a pipe.
    Parameters
    ----------
    filepath : `Path`
        absolute path to the video file which information to extract
    Returns
    -------
    infos : `dict`
        keys are width, height (size of the frames)
        duration (duration of the video in seconds)
        n_frames
    """

    # Read information using ffmpeg - the call below intentionally causes
    # an error about no output from FFMPEG in order to terminate faster - hence
    # reading the output from stderr.
    command = [ffmpeg, "-i", str(filepath), "-"]
    raw_infos = subprocess.getoutput(subprocess.list2cmdline(command))
    # Note: we use '\d+\.?\d*' so we can match both int and float for the fps
    video_info = re.search(
        r"Video:.*(?P<width> \d+)x(?P<height>\d+).*(?P<fps> \d+\.?\d*) fps",
        raw_infos, re.DOTALL).groupdict()

    # Some videos don't have a valid duration
    time = re.search(
        r"Duration:\s(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),",
        raw_infos, re.DOTALL).groupdict()
    if time is None:
        raise ValueError('Unable to determine duration for video - please '
                         'install and use ffprobe for accurate yuki count '
                         'computation.')

    hours = float(time["hours"])
    minutes = float(time["minutes"])
    seconds = float(time["seconds"])

    duration = 60 * 60 * hours + 60 * minutes + seconds

    fps = round(float(video_info["fps"]))
    n_frames = round(duration * fps)
    width = int(video_info["width"])
    height = int(video_info["height"])

    # Create the resulting dictionary
    infos = {
        'fps': fps,
        'duration': duration,
        'width': width,
        'height': height,
        'frames': n_frames
    }

    return infos


def get_ffmpeg_name():
    os_name = system().lower()
    mappings = {
        "windows": "ffmpeg.exe",
        "mac": "ffmpeg",
        "linux": "ffmpeg"
    }
    return mappings.get(os_name, "ffmpeg")
