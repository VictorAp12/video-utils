# Video Utils

Não entende inglês? [Clique aqui para ver esta página em português](https://github.com/VictorAp12/video-utils/blob/main/readme.md)

Performs conversions, combines subtitles with video files, and changes the title attribute of the file.

## In this project there are 2 applications:
1) Converts videos and audios to different formats;
2) Combines video (mkv) and subtitle (srt) into a single file, as well as changes the title attribute of a video or audio.

### Video Converter App

You know when you need to convert several videos to another format and can only find sites that do this very slowly or limitedly?
This program will solve your problems, as it does this for audios and videos in the fastest way and without quantity limit.

### Change Video Attributes App

You know when you are going to watch a video on some device and the title is totally random and even changing the file name the video name remains the same?
This program solves your problems, just press the change title button and the video / audio title will be the same as the file name, very useful for when you are using media streaming from a computer.

As for the button to join video and subtitle, it combines two files into one (video in mkv and subtitle in srt), very useful for when the device used does not have the option to search for a subtitle but provides to activate it by changing between subtitle tracks.

Contents:
- [Requirements](#requirements)
- [Installation](#installation)

## Requirements
- Python 3.8 or above
- ffmpeg v3.1 or above. Link: http://ffmpeg.org/ installed in your $PATH

## Installation

The easiest way is simply by downloading the video utils installer windows 64 bits.exe. [Click here to go to the download file](https://github.com/VictorAp12/video-utils/blob/main/video%20utils%20installer%20win%2064.exe)

Or if you prefer to download the entire project:

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
    python -m main.py
    ```
