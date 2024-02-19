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
import subprocess
from typing import List, Tuple
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

    :raises tk.messageboxes error: If the ffmpeg binaries cannot be found.
    :raises tk.messageboxes error: If the ffmpeg binaries are located in a restricted directory.

    :return: The path to the ffmpeg binaries if they pass all the checks, otherwise returns None.
    """
    load_dotenv(os.path.abspath(".env"), override=True, encoding="utf-8")

    os.environ["FFMPEG_DIRECTORY"] = str(os.getenv("FFMPEG_FOLDER"))

    translations = load_translations()
    json_translations = translations[load_last_used_settings()[0]]

    try:
        binaries = _check()

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


def _check():
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


def configure_font_subtitles_win(binaries):
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


def is_video_or_audio_file(file_path: Path | str) -> bool:
    """
    Check if the given file is a video or audio file.

    :param file_path: Path | str, The path to the file to be checked.

    :return: bool, True if the file is a video or audio file, False otherwise.
    """

    file_path = str(file_path)

    excluded_extensions = (".srt", ".jpg", ".png", ".jpeg", ".gif", ".bmp")

    if file_path.endswith(excluded_extensions):
        return False

    try:
        if os.name == "nt":
            # Option 1: Hide console window using startupinfo
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            subprocess.run(
                ["ffprobe", file_path],
                startupinfo=startupinfo,
                check=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Option 2: Hide console window using creationflags
            # subprocess.run(["ffprobe", file_path], creationflags=subprocess.CREATE_NO_WINDOW)

        else:
            subprocess.run(
                ["ffprobe", file_path],
                check=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        return True

    except subprocess.CalledProcessError:
        return False


def extract_subtitle(
    video_file: Path, destiny_folder: Path, target_subtitle_extension: str = ".srt"
) -> List[Path] | None:
    """
    Extract all the subtitles from the given video_file.

    :param video_file: Path, The path to the video_file.
    :param destiny_folder: Path, the folder where the extracted subtitle files will be saved.
    :param target_subtitle_extension: str, The extension of the extracted subtitle files.

    :return: list[Path], The paths to the extracted subtitle files, or None if extraction fails.
    """
    output_files: List[Path] = []

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        # Extract the subtitle tracks
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "s",
                "-show_entries",
                "stream=index",
                "-of",
                "default=nokey=1:noprint_wrappers=1",
                f"{str(video_file)}",
            ],
            startupinfo=startupinfo,
            check=False,
            capture_output=True,
            text=True,
        )

        subtitle_tracks = [
            line.strip() for line in result.stdout.split("\n") if line.strip()
        ]

        subtitle_titles_result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "s",
                "-show_entries",
                "stream_tags=title",
                "-of",
                "default=nokey=1:noprint_wrappers=1",
                f"{str(video_file)}",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        subtitle_titles = [
            line.strip() for line in subtitle_titles_result.stdout.split("\n")
        ]

        subtitle_titles = list(filter(None, subtitle_titles))

        for i, track in enumerate(subtitle_tracks):
            output_file = (
                destiny_folder
                / f"{video_file.stem}_NAME={subtitle_titles[i]}{target_subtitle_extension}"
            )
            extract_command = [
                "ffmpeg",
                "-i",
                f"{str(video_file)}",
                "-map",
                f"0:s:{track}",
                f"{str(output_file)}",
                "-y",
            ]
            subprocess.run(
                extract_command,
                check=True,
                startupinfo=startupinfo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            output_files.append(output_file)

        return output_files

    except subprocess.CalledProcessError:
        return None


def convert_subtitle(
    input_subtitle_files: List[Path],
    destiny_folder: Path,
    target_subtitle_extension: str,
) -> List[Path] | None:
    """
    Convert the given subtitle file to target format.

    :param input_subtitles_files: List[Path], The path to the subtitle file.

    :return: List[Path], The path to the converted file, or None.
    """
    output_subtitle_file = []

    try:
        for input_subtitle_file in input_subtitle_files:
            target_subtitle = (
                destiny_folder
                / input_subtitle_file.with_suffix(target_subtitle_extension).name
            )

            if target_subtitle.exists():
                target_subtitle.unlink()

            convert_command = [
                "ffmpeg",
                "-i",
                str(input_subtitle_file),
                str(target_subtitle),
                "-y",
            ]

            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            subprocess.run(
                convert_command,
                startupinfo=startupinfo,
                check=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            output_subtitle_file.append(target_subtitle)

        return output_subtitle_file

    except subprocess.CalledProcessError:
        return None


def ffmpeg_info_extractor(
    input_file: Path,
) -> Tuple[List[str], Tuple[List[str], List[str]]] | None:
    """
    Extract the video information using FFmpeg.

    :param input_file: Path, The path to the input file.

    :return: str, The video information, or None if extraction fails.
    """

    subtitle_titles_result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "s",
            "-show_entries",
            "stream_tags=title",
            "-of",
            "default=nokey=1:noprint_wrappers=1",
            f"{str(input_file)}",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    subtitle_titles = [
        line.strip() for line in subtitle_titles_result.stdout.split("\n")
    ]

    subtitle_titles = list(filter(None, subtitle_titles))

    audio_track_result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index:stream_tags=language",
            "-of",
            "default=noprint_wrappers=1",
            f"{str(input_file)}",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    audio_tracks = [
        line.strip() for line in audio_track_result.stdout.split("\n") if line.strip()
    ]

    audio_name: List[str] = []
    audio_index: List[str] = []
    for i, audio_track in enumerate(audio_tracks):
        if i % 2 == 0:
            audio_index.append(str(audio_track).replace("index=", ""))
        else:
            audio_name.append(str(audio_track).replace("TAG:", ""))

    return subtitle_titles, (audio_index, audio_name)


if __name__ == "__main__":
    import sys

    sys.path.append(os.getcwd())

    from video_adjuster import VideoAdjuster

    binaries_ = check_ffmpeg_tkinter()

    if binaries_:
        if os.name == "nt":
            # Configure the fonts for the subtitles
            configure_font_subtitles_win(binaries_)

        # Merge the subtitles with the video
        for root, dirs, files in os.walk(os.getcwd()):
            video_adjuster = VideoAdjuster(files)
            video_adjuster.merge_video_to_subtitle("pt_BR")
