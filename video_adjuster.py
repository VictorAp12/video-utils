"""
This module contains a application for changing the title of video files to their filenames.
"""

import os
from datetime import datetime
from pathlib import Path
import threading
import tkinter as tk
from tkinter import messagebox

import chardet
import ffmpeg
from ffmpeg_progress_yield import FfmpegProgress

from tk_progress_bar import ProgressBar
from custom_thread import CustomThread


def simplify_file_path(file_path: Path | str) -> str:
    """
    Make sure we get rid of quote characters in file name

    :param file_path: Path | str, The path to the file to be checked.

    :return: str, The simplified file path.
    """
    file_path = str(file_path)
    return file_path.replace('"', "").replace("'", "").replace(",", "")


def is_video_or_audio_file(file_path: Path | str):
    """
    Check if the given file is a video or audio file.

    :param file_path: Path | str, The path to the file to be checked.

    :return: bool, True if the file is a video or audio file, False otherwise.
    """
    try:
        file_path = str(file_path)
        if file_path.endswith(".srt"):
            return False

        ffmpeg.probe(file_path)

        return True

    except ffmpeg.Error:
        return False


def encode_to_utf8(file_path: Path | str) -> bool | str:
    """
    Encode the given file to UTF-8.
    """
    file_path = str(file_path)

    if not file_path.endswith(".srt"):
        return False

    try:
        with open(file_path, "rb") as f:
            rawdata = f.read()
            result = chardet.detect(rawdata)
            encoding = result["encoding"]

    except FileNotFoundError:
        return f'"{Path(file_path).stem}" arquivo de legenda não encontrado!'

    with open(file_path, "r", encoding=encoding) as f:
        content = f.read()

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return True


class VideoAdjuster:
    """
    This class provides methods for adjusting videos.
    """

    def __init__(
        self,
        input_files: list[str],
        output_folder: Path | str = Path.cwd(),
        master: tk.Tk | tk.Toplevel | None = None,
    ) -> None:
        self.input_files = input_files
        self.output_folder = Path(output_folder)

        self.total_files = len(input_files)
        self.master = master

    def thread_function(
        self, progress_bar_obj: ProgressBar, command: FfmpegProgress
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

    def setup_progress_bar(self, message: str) -> ProgressBar:
        """
        Sets up the progress bar object.

        :param message: str, The message to display in the progress bar.

        :return: ProgressBar
        """

        progress_bar_obj = ProgressBar(master=self.master, with_pause_button=False)
        progress_bar_obj.create_progress_bar()

        progress_bar_obj.set_label_text(message)

        return progress_bar_obj

    def run_converter(
        self,
        conversion_type: str = "video",
        output_extension: str = ".mp4",
    ) -> None:
        """
        Converts a video file from input_file to output_file using ffmpeg.

        :param conversion_type: "audio" or "video", The type of conversion.

        :return: None
        """

        if conversion_type not in ("audio", "video"):
            return

        for i, input_file in enumerate(self.input_files):
            output_file = (
                f"{self.output_folder}\\"
                + f"{Path(input_file).name.replace(Path(input_file).suffix, output_extension)}"
            )

            filename = Path(input_file).name

            message = (
                f'Convertendo o "{filename}"\n{i+1} de {self.total_files} arquivos'
            )

            progress_bar_obj = self.setup_progress_bar(message)

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
                    messagebox.showerror(
                        "Erro", "Não é possível converter para um vídeo mp3."
                    )

                    return

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

            progress_thread = self.thread_function(progress_bar_obj, command)

            return_value = progress_thread.join()

            progress_bar_obj.root.destroy()

            if not return_value:
                break

    def change_video_title_to_filename(self) -> None:
        """
        A function to change the title of a video to match its filename,
        using a progress bar to display the progress of the operation.

        :return: None
        """

        for i, input_file in enumerate(self.input_files):
            filename = Path(input_file).name

            title = Path(filename).stem

            temp_output_file = input_file.replace(filename, f"mod_{filename}")

            message = (
                f'Modificando título do "{filename}"\n'
                f"{i + 1} de {self.total_files} arquivos"
            )

            progress_bar_obj = self.setup_progress_bar(message)

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

            progress_bar_obj.root.destroy()

            if not return_value:
                break

    def merge_video_to_subtitle(self, subtitle_language: str = "Pt-BR") -> None:
        """
        Merge a video file with its corresponding subtitle file.

        :param subtitle_language: str, The language of the subtitle.
            This will appear in the video player available subtitles menu.
        """

        for i, input_file in enumerate(self.input_files):

            # Get rid of quote characters
            os.rename(input_file, simplify_file_path(input_file))

            self.input_files = simplify_file_path(input_file)

            name = Path(input_file).stem
            file_name = Path(input_file).name

            message = (
                "Juntando vídeo com a legenda do "
                f'"{file_name}"\n{i+1} de {self.total_files} arquivos'
            )

            progress_bar_obj = self.setup_progress_bar(message)

            # output file will be like "video.srt.mkv"
            merged = (
                simplify_file_path(Path(input_file).parent) + "/" + name + ".srt.mkv"
            )

            # Assume the subtitles have the same name as the video file
            subtitles = input_file.replace(file_name, name + ".srt")

            subtitle_exists = encode_to_utf8(subtitles)

            if isinstance(subtitle_exists, str):
                progress_bar_obj.root.destroy()
                messagebox.showerror(
                    "Error",
                    message=f'"{Path(subtitles).stem}" arquivo de legenda não encontrado!\
                    \nEle deve possuir o mesmo nome do arquivo de video.',
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

            progress_bar_obj.root.destroy()

            if not return_value:
                break


if __name__ == "__main__":
    import glob

    path = glob.glob("*.mkv")

    progress_bar_obj_ = ProgressBar()

    progress_bar_obj_.create_progress_bar()

    total = len(path)

    video_adjuster_obj_ = VideoAdjuster(input_files=path)

    video_adjuster_obj_.change_video_title_to_filename()
    # video_adjuster_obj_.merge_video_to_subtitle()
