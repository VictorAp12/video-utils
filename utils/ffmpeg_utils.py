"""
This module contains a function that merges video and subtitle files using ffmpeg.

The MIT License (MIT)

Copyright (c) 2016

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
from pathlib import Path
from tkinter import messagebox, filedialog

from dotenv import load_dotenv

if __name__ == "__main__":
    from json_utils import load_translations, load_last_used_settings
else:
    from utils.json_utils import load_translations, load_last_used_settings


def check_ffmpeg_tkinter() -> str | None:
    """
    Check if the base directory environment variable is defined,
    and verify the location of the ffmpeg binaries.
    """
    load_dotenv(os.path.abspath(".env"), override=True, encoding="utf-8")

    os.environ["FFMPEG_DIRECTORY"] = str(os.getenv("FFMPEG_FOLDER"))

    translations = load_translations()
    json_translations = translations[load_last_used_settings()[0]]

    try:
        binaries = check()

        return binaries

    except (FileNotFoundError, KeyError, ValueError) as e:
        if isinstance(e, ValueError):
            messagebox.showerror(
                json_translations["MessageBox"]["error"],
                message=json_translations["MessageBox"]["error_ffmpeg_restricted"],
            )
        else:
            messagebox.showerror(
                json_translations["MessageBox"]["error"],
                message=json_translations["MessageBox"]["error_ffmpeg_not_found"],
            )

        ffmpeg_folder = filedialog.askdirectory(mustexist=True)

        with open(".env", "w", encoding="utf-8") as f:
            f.write(f'FFMPEG_FOLDER = "{Path(ffmpeg_folder).as_posix()}"')

        load_dotenv(os.path.abspath(".env"), override=True, encoding="utf-8")

        os.environ["FFMPEG_DIRECTORY"] = str(os.getenv("FFMPEG_FOLDER"))

        return None


def check():
    """
    Check if the base directory environment variable is defined,
    and verify the location of the ffmpeg binaries.
    Returns the path to the ffmpeg binaries if they pass all the checks, otherwise returns None.
    """
    ffmpeg_dir = ""
    try:
        ffmpeg_dir = os.environ["FFMPEG_DIRECTORY"]

    except KeyError as exc:
        raise KeyError(
            "Point FFMPEG_DIRECTORY environment variable to the location of FFMPEG"
        ) from exc

    # Check if the binaries are not located in restricted directory
    if -1 != ffmpeg_dir.lower().find("system32"):
        raise ValueError("The ffmpeg binaries cannot be under system32 directory")

    # Check if the binaries exist
    binaries = ffmpeg_dir + os.sep + "bin" + os.sep
    if not (
        os.path.exists(binaries + "ffmpeg") or os.path.exists(binaries + "ffmpeg.exe")
    ):
        raise FileNotFoundError(
            "Please download the ffmpeg binaries from www.ffmpeg.org"
        )

    return binaries


def configure(binaries):
    """
    Configure the fonts for the subtitles on windows.
    """

    # The fonts.conf must be under the directory with ffmpeg executable
    fonts = binaries + "fonts"

    # Neme of the config file must be fonts.conf
    name = "fonts.conf"

    # Point ffmped to its fonts.conf
    os.environ["FC_CONFIG_DIR"] = fonts
    os.environ["FC_CONFIG_FILE"] = fonts + os.sep + name

    # Check the presence of fonts directory
    if not os.path.exists(os.environ["FC_CONFIG_DIR"]):
        os.mkdir(os.environ["FC_CONFIG_DIR"])

    # Check the presence of fonts.conf
    if not os.path.exists(os.environ["FC_CONFIG_FILE"]):
        fc_config_file = open(os.environ["FC_CONFIG_FILE"], "wb")
        fc_config_file.write(
            "<fontconfig><dir>C:\\WINDOWS\\Fonts</dir></fontconfig>".encode("utf-8")
        )
        fc_config_file.close()


if __name__ == "__main__":
    import sys

    sys.path.append(os.getcwd())

    from video_adjuster import VideoAdjuster

    binaries_ = check_ffmpeg_tkinter()

    if binaries_:
        if os.name == "nt":
            # Configure the fonts for the subtitles
            configure(binaries_)

        # Merge the subtitles with the video
        for root, dirs, files in os.walk(os.getcwd()):
            video_adjuster = VideoAdjuster(files)
            video_adjuster.merge_video_to_subtitle("pt_BR")
