# Video Utils

Não entende inglês? [Clique aqui para ver esta página em português](https://github.com/VictorAp12/video-utils/blob/main/readme.md)

Performs conversions, changes the title attribute of the file, combines subtitles with video files and extracts all the subtitle tracks from a video file.

## In this project there are 2 applications:
1) Converts videos and audios to different formats;
2) Combines video (mkv) and subtitle (srt) into a single file, as well as changes the title attribute of a video or audio and finally, extracts video subtitles.

<h3 align="center">Video Converter App</h3>

<div align="center">
<img src="https://github.com/VictorAp12/video-utils/assets/148372228/0d897f59-ed86-4fde-b2d4-262c324cedd3" />
</div>

You know when you need to convert several videos to another format and can only find sites that do this very slowly or limitedly?
This program will solve your problems, as it does this for audios and videos in the fastest way and without quantity limit.

<h3 align="center">Change Video Attributes App</h3>

<div align="center">
<img src="https://github.com/VictorAp12/video-utils/assets/148372228/1ccff242-61d8-4645-9558-595adbdf61f7" />
</div>

You know when you are going to watch a video on some device and the title is totally random and even changing the file name the video name remains the same?
This program solves your problems, just press the "change title" button and the video / audio title will be the same as the file name, very useful for when you are using media streaming from a computer.

As for the "Combine video and subtitle" button, merges two files into one (video in mkv and subtitle in srt), very useful for when the device used does not have the option to search for a subtitle but provides to activate it by changing between subtitle tracks.

Finnaly the "Extract Subtitle" button finally extracts all video subtitle tracks. By default, the subtitles are in srt format, but it's also possible to use other formats such as .ass.

Contents:
- [Requirements](#requirements)
- [Installation](#installation)

## Requirements
- Python 3.8 or above
- ffmpeg v3.1 or above. Link: http://ffmpeg.org/ installed in your $PATH (If it's not in the system variables it won't work, see a tutorial on how to put ffmpeg in your system's Path)

## Installation

  ### As a Windows executable

  Simply download the .exe file through this link and start using the application (For Windows 64 bits, Windows 11 is recommended): [Download Video Utils](https://github.com/VictorAp12/video-utils/raw/main/Video%20Utils%20installer%2064%20bits.exe)

  ### As a Python Project

  - Download the project as a zip or using git clone https://github.com/VictorAp12/video-utils.git

  - Create a virtual environment in the project folder:
    ```bash
    python -m venv venv
    ````

  - Activate the virtual environment in the project folder:
    ```bash
    venv\Scripts\activate
    ```

  - Install the project dependencies:
    ```bash
    pip install -r requirements.txt
    ```

  - Run the main.py:
    ```bash
    python -m main
    ```
