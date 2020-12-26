youtube-dl-gui - A simple video download application
====================================================


Rationale
---------

`youtube-dl` is a great tool to download videos, but it is not very convenient:

- Its user interface is a command line, not a GUI.

- Downloading several videos in parallel requires opening a command line window
  for each video.

- Monitoring progress requires the user to switch to each command line window
  in turn and read the progress message.

`youtube-dl-gui` is a GUI built on top of `youtube-dl`, using `gooey` and some
homemade extensions to `gooey`, in order to provide a more convenient user
interface for downloading videos.


  ![UI](Screenshot_1_UI.png)

  ![Mail](Screenshot_2_Mail.png)

UI1, UI2, Alt-Tab


Usage
-----

`youtube-dl-gui` allows a smooth workflow with minimal effort on the part of the
user:

- Copy the URL of the video you wish to download.

- Launch `youtube-dl-gui`.

- The URL present in the clipboard is detected and preloaded in the UI. If the
  default download directory suits you, simply press the `Enter` key to start
  downloading the video.

- `youtube-dl-gui` displays a nice green progress bar while the video is
  downloading, as well as an estimate of the remaining time.

- As soon as the title of the video is determined, it is displayed as the title
  for the `youtube-dl-gui` window. 

- On Windows, monitoring download progress is as simple as pressing `Alt+Tab`:
  `youtube-dl-gui` windows bear the title of the video they are downloading,
  and the green progress bar gives a visual indication of progress.

Keyboard shortcuts are available for the following buttons:

- `Start` - `Enter` key
- `Stop` - `S` key
- `Close` - `Escape` key
- `Edit` - `E` key
- `Restart` - 'R' key


Installation
------------

Clone the repo.

Install dependencies:

    pip install gooey
    pip install pyperclip

If your `youtube-dl-gui` directory is visible from `PYTHONPATH`, simply use
``python -m youtube-dl-gui`` to run the application.


Compatibility
-------------

`youtube-dl-gui` requires Python 3.7 or later.

I have only tested `youtube-dl-gui` under Windows 10, but it should be pretty
portable an run on any OS on which `youtube-dl`, `gooey` and `pyperclip` can
run. This presumably includes most Linux flavors, as well as MacOS, although I
have not made any tests on these OS's.
