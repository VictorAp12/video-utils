"""
This module contains a application for changing the title of video files to their filenames.
"""

import os
from datetime import datetime
from pathlib import Path
import threading
import tkinter as tk
from tkinter import messagebox
import subprocess
from typing import List

from ffmpeg_progress_yield import FfmpegProgress
import chardet

from tk_progress_bar import CustomProgressBar

from utils.threading_utils import CustomThread
from utils.json_utils import (
    load_translations,
    load_last_used_settings,
)

language = load_last_used_settings()[0]
translations = load_translations()[language]


def simplify_file_path(file_path: Path | str) -> str:
    """
    Make sure we get rid of quote characters in file name

    :param file_path: Path | str, The path to the file to be checked.

    :return: str, The simplified file path.
    """
    file_path = str(file_path)
    return file_path.replace('"', "").replace("'", "").replace(",", "")


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


def encode_to_utf8(file_path: Path | str) -> str | None:
    """
    Encode the given file to UTF-8.

    :param file_path: Path | str, The path to the file to be encoded.
    """
    file_path = str(file_path)

    if not file_path.endswith(".srt"):
        return None

    try:
        with open(file_path, "rb") as f:
            rawdata = f.read()
            result = chardet.detect(rawdata)
            encoding = result["encoding"]

    except FileNotFoundError:
        error_string = translations["MessageBox"]["error_subtitle_not_found"].format(
            filename=Path(file_path).stem
        )
        return error_string

    with open(file_path, "r", encoding=encoding) as f:
        content = f.read()

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return None


def extract_srt_from_mkv(mkv_file: Path, destiny_folder: Path) -> Path | None:
    """
    Extract the subtitles from the given MKV file.

    :param mkv_file: Path, The path to the MKV file.
    :param destiny_folder: Path, The path to the folder where the extracted SRT file will be saved.

    :return: Path, The path to the extracted SRT file.
    """
    dot_srt_file = mkv_file.name + ".srt"

    output_file = destiny_folder / dot_srt_file

    extract_command = [
        "ffmpeg",
        "-i",
        str(mkv_file),
        "-map",
        "0:s:0",
        str(output_file),
    ]

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        subprocess.run(
            extract_command,
            startupinfo=startupinfo,
            check=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    except subprocess.CalledProcessError:
        return None

    return output_file


class VideoAdjuster:
    """
    This class provides methods for adjusting videos.
    """

    def __init__(
        self,
        input_files: List[str] | List[Path],
        output_folder: Path | str = Path.cwd(),
        master: tk.Tk | tk.Toplevel | None = None,
    ) -> None:
        self.input_files = [str(input_file) for input_file in input_files]
        self.output_folder = Path(output_folder)

        self.total_files = len(input_files)
        self.master = master

    def thread_function(
        self, progress_bar_obj: CustomProgressBar, command: FfmpegProgress
    ) -> threading.Thread:
        """
        A function to run a command in a separate thread.

        :param progress_bar_obj: ProgressBar, The progress bar object.
        :param command: FfmpegProgress, The command to run in a separate thread.

        :return: threading.Thread
        """

        progress_thread = CustomThread(
            target=progress_bar_obj.run_ffmpeg_with_progress, args=(command,)
        )
        progress_thread.start()

        progress_bar_obj.root.mainloop()

        return progress_thread

    def setup_progress_bar(self) -> CustomProgressBar:
        """
        Sets up the progress bar object.

        :return: ProgressBar
        """

        progress_bar_obj = CustomProgressBar(
            master=self.master, with_pause_button=False
        )
        progress_bar_obj.create_progress_bar()

        return progress_bar_obj

    def run_converter(
        self,
        conversion_type: str = "video",
        output_extension: str = ".mp4",
    ) -> None:
        """
        Converts a video file from input_file to output_file using ffmpeg.

        :param conversion_type: "audio" or "video", The type of conversion.
        :param output_extension: str, The extension of the output file.

        :raises tk.messagebox error: If conversion_type is video and output_extension is .mp3

        :return: None.
        """

        if conversion_type not in ("audio", "video"):
            return

        progress_bar_obj = self.setup_progress_bar()

        for i, input_file in enumerate(self.input_files):
            output_file = (
                f"{self.output_folder}\\"
                + f"{Path(input_file).name.replace(Path(input_file).suffix, output_extension)}"
            )

            filename = Path(input_file).name

            message = translations["ProgressBar"]["converter_message"].format(
                filename=filename, current_file=i + 1, total_files=self.total_files
            )

            progress_bar_obj.set_label_text(message)

            if conversion_type == "audio":
                if not output_file.endswith(".mp3"):
                    command = FfmpegProgress(
                        [
                            "ffmpeg",
                            "-i",
                            input_file,
                            "-vn",
                            "-acodec",
                            "aac",
                            "-q:a",
                            "0",
                            "-n",
                            output_file,
                        ]
                    )

                else:
                    Path(output_file).unlink(missing_ok=True)

                    command = FfmpegProgress(
                        [
                            "ffmpeg",
                            "-i",
                            input_file,
                            "-vn",
                            "-acodec",
                            "mp3",
                            "-q:a",
                            "0",
                            "-n",
                            output_file,
                        ]
                    )

            elif conversion_type == "video":
                if output_file.endswith(".mp3"):
                    progress_bar_obj.root.destroy()
                    messagebox.showerror(
                        translations["MessageBox"]["error"],
                        message=translations["MessageBox"]["error_convert_video_mp3"],
                    )
                    return

                if input_file.endswith(".mkv"):
                    extract_srt_from_mkv(Path(input_file), Path(output_file).parent)

                try:
                    command = FfmpegProgress(
                        [
                            "ffmpeg",
                            "-i",
                            input_file,
                            "-c:v",
                            "copy",
                            "-c:a",
                            "copy",
                            output_file,
                        ]
                    )

                except Exception as e:
                    with open("log.txt", "a", encoding="utf-8") as f:
                        f.write(f"{datetime.now()} - {e}\n")

                    Path(output_file).unlink(missing_ok=True)

                    command = FfmpegProgress(
                        [
                            "ffmpeg",
                            "-i",
                            input_file,
                            "-c:v",
                            "copy",
                            "-c:a",
                            "aac",
                            output_file,
                        ]
                    )

            if Path(output_file).exists():
                progress_bar_obj.root.withdraw()
                delete_file = messagebox.askyesno(
                    translations["MessageBox"]["warning"],
                    message=translations["MessageBox"]["output_file_exists"].format(
                        output_file=Path(output_file).name
                    ),
                    parent=progress_bar_obj.root,
                )

                if delete_file:
                    Path(output_file).unlink(missing_ok=True)
                else:
                    progress_bar_obj.root.deiconify()
                    continue

            progress_thread = self.thread_function(progress_bar_obj, command)

            return_value = progress_thread.join()

            if not return_value:
                progress_bar_obj.root.destroy()
                break

        if progress_bar_obj.root:
            progress_bar_obj.root.destroy()

    def change_video_title_to_filename(self) -> None:
        """
        A function to change the title of a video to match its filename,
        using a progress bar to display the progress of the operation.

        :return: None.
        """

        progress_bar_obj = self.setup_progress_bar()

        for i, input_file in enumerate(self.input_files):
            filename = Path(input_file).name

            title = Path(filename).stem

            temp_output_file = input_file.replace(filename, f"mod_{filename}")

            message = translations["ProgressBar"]["change_title_message"].format(
                filename=filename, current_file=i + 1, total_files=self.total_files
            )

            progress_bar_obj.set_label_text(message)

            command = FfmpegProgress(
                [
                    "ffmpeg",
                    "-i",
                    input_file,
                    "-c",
                    "copy",
                    "-metadata",
                    f"title={title}",
                    temp_output_file,
                ],
            )

            progress_thread = self.thread_function(progress_bar_obj, command)

            Path(input_file).unlink(missing_ok=True)
            Path(temp_output_file).rename(input_file)

            return_value = progress_thread.join()

            if not return_value:
                progress_bar_obj.root.destroy()
                break

        if progress_bar_obj.root:
            progress_bar_obj.root.destroy()

    def merge_video_to_subtitle(self, subtitle_language: str = "Pt-BR") -> None:
        """
        Merge a video file with its corresponding subtitle file.

        :param subtitle_language: str, The language of the subtitle.
            This will appear in the video player available subtitles menu.

        :raises tk.messagebox error: If the subtitle file does not exist.

        :return: None.
        """

        progress_bar_obj = self.setup_progress_bar()

        for i, input_file in enumerate(self.input_files):

            # Get rid of quote characters
            os.rename(input_file, simplify_file_path(input_file))

            self.input_files = simplify_file_path(input_file)

            name = Path(input_file).stem
            filename = Path(input_file).name

            message = translations["ProgressBar"]["merge_to_subtitle_message"].format(
                filename=filename, current_file=i + 1, total_files=self.total_files
            )

            progress_bar_obj.set_label_text(message)

            # output file will be like "video.srt.mkv"
            merged = (
                simplify_file_path(Path(input_file).parent) + "/" + name + ".srt.mkv"
            )

            # Assume the subtitles have the same name as the video file
            subtitles = input_file.replace(filename, name + ".srt")

            subtitle_exists = encode_to_utf8(subtitles)

            if isinstance(subtitle_exists, str):
                progress_bar_obj.root.destroy()
                messagebox.showerror(
                    "Error",
                    message=subtitle_exists,
                )
                continue

            if os.path.exists(subtitles):
                os.rename(subtitles, simplify_file_path(subtitles))
                subtitles = simplify_file_path(subtitles)

            else:
                subtitles = ""

            command = FfmpegProgress(
                [
                    "ffmpeg",
                    "-i",
                    input_file,
                    "-i",
                    subtitles,
                    "-map",
                    "0",
                    "-map",
                    "1",
                    "-c:a",
                    "copy",
                    "-c:v",
                    "copy",
                    "-metadata:s:s:0",
                    f"title={subtitle_language}",
                    merged,
                ],
            )

            progress_thread = self.thread_function(progress_bar_obj, command)

            Path(input_file).unlink(missing_ok=True)
            Path(subtitles).unlink(missing_ok=True)

            return_value = progress_thread.join()

            if not return_value:
                progress_bar_obj.root.destroy()
                break

        if progress_bar_obj.root:
            progress_bar_obj.root.destroy()


if __name__ == "__main__":

    videos = []
    for video in os.listdir("./origin"):
        video = os.path.join(os.getcwd(), "origin", video)
        if is_video_or_audio_file(video):
            videos.append(video)

    print(*videos, sep="\n")

    progress_bar_obj_ = CustomProgressBar()

    progress_bar_obj_.create_progress_bar()

    # total = len(videos)

    video_adjuster_obj_ = VideoAdjuster(input_files=videos)

    video_adjuster_obj_.change_video_title_to_filename()
    # video_adjuster_obj_.merge_video_to_subtitle()
