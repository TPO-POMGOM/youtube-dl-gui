""" Simple application to download videos, built on top of youtube-dl.

Simple video downloader based on youtube-dl, with a GUI built using gooey.

Dependencies: gooey, gooey_extensions, pyperclip, wx. """

from pathlib import Path

from gooey import Gooey, GooeyParser
import pyperclip
import wx

from .gooey_extensions import RegisterAccelerator, RegisterArgTransformer, \
    RegisterStdoutListener, set_gooey_window_title


DEFAULT_DIR = str(Path('~').expanduser() / 'Downloads')


def transform_output_arg(dir: str) -> str:
    """ Build youtube-dl '--output' option from directory selected by user. """
    dir = dir.strip('"')
    return rf'{dir}\%(title)s.%(ext)s'


def set_gooey_window_title_to_video_name(text: str) -> None:
    """ Extract video file name from youtube-dl stdout and set window title. """
    if text.startswith("[download] Destination: "):
        set_gooey_window_title(Path(text[24:]).stem)


@Gooey(target='youtube-dl --newline',
       program_name="Video downloader",
       suppress_gooey_flag=True,
       image_dir=str(Path(__file__).parent),
       progress_regex=r'^\[download\]\s+([0-9\.]+)*%',
       hide_progress_msg=True,
       timing_options={
           'show_time_remaining': True,
           'hide_time_remaining_on_complete': True,
       })
def main():
    clipboard = pyperclip.paste()
    parser = GooeyParser(description='Download videos using youtube-dl')
    parser.add_argument(
        'video URL',
        default=clipboard if clipboard.startswith('http') else '',
        metavar='Video URL',
        help='URL for the video to download')
    parser.add_argument(
        '-o', '--output',
        default=DEFAULT_DIR,
        metavar='Download Directory',
        help='Directory where the video is to be downloaded',
        widget='DirChooser')
    RegisterArgTransformer('-o', transform_output_arg)
    RegisterArgTransformer('--output', transform_output_arg)
    RegisterStdoutListener(set_gooey_window_title_to_video_name)
    RegisterAccelerator('start', wx.ACCEL_NORMAL, wx.WXK_RETURN)
    RegisterAccelerator('stop', wx.ACCEL_NORMAL, ord('S'))
    RegisterAccelerator('close', wx.ACCEL_NORMAL, wx.WXK_ESCAPE)
    RegisterAccelerator('edit', wx.ACCEL_NORMAL, ord('E'))
    RegisterAccelerator('restart', wx.ACCEL_NORMAL, ord('R'))
    parser.parse_args()


if __name__ == '__main__':
    main()
