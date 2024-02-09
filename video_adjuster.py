"""
This module contains a application for changing the title of video files to their filenames.
"""

import os
from pathlib import Path
import threading

import tkinter as tk

import chardet
import ffmpeg
from ffmpeg_progress_yield import FfmpegProgress

from tk_progress_bar import ProgressBar


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


def encode_to_utf8(file_path: Path | str):
    """
    Encode the given file to UTF-8.
    """
    file_path = str(file_path)

    if not file_path.endswith(".srt"):
        return

    with open(file_path, "rb") as f:
        rawdata = f.read()
        result = chardet.detect(rawdata)
        encoding = result["encoding"]

    with open(file_path, "r", encoding=encoding) as f:
        content = f.read()

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


class VideoAdjuster:
    """
    This class provides methods for adjusting videos.
    """

    def __init__(
        self,
        input_file: Path | str,
        output_file: Path | str = Path.cwd(),
        current_file: int = 1,
        total_files: int = 1,
    ) -> None:
        self.input_file = input_file
        self.output_file = output_file
        self.current_file = current_file
        self.total_files = total_files

    # def thread_function(self, command, current_file, total_files) -> None:
    #     """
    #     A function to run a command in a separate thread.
    #     """

    def run_converter(
        self,
        conversion_type: str = "video",
    ) -> None:
        """
        Converts a video file from input_file to output_file using ffmpeg.

        :param conversion_type: "audio" or "video", The type of conversion.

        :return: None
        """

        if conversion_type not in ("audio", "video"):
            return

        filename = Path(self.input_file).name

        message = message = (
            f'Convertendo o "{filename}"\n{self.current_file} de {self.total_files} arquivos'
        )

        if conversion_type == "audio":
            if not str(self.output_file).endswith(".mp3"):
                command = FfmpegProgress(
                    [
                        "ffmpeg",
                        "-i",
                        str(self.input_file),
                        "-vn",
                        "-acodec",
                        "aac",
                        "-q:a",
                        "0",
                        "-n",
                        str(self.output_file),
                    ]
                )

            else:
                Path(self.output_file).unlink(missing_ok=True)

                command = FfmpegProgress(
                    [
                        "ffmpeg",
                        "-i",
                        str(self.input_file),
                        "-vn",
                        "-acodec",
                        "mp3",
                        "-q:a",
                        "0",
                        "-n",
                        str(self.output_file),
                    ]
                )

        elif conversion_type == "video":
            if str(self.output_file).endswith(".mp3"):
                tk.messagebox.showerror(
                    "Erro", "Não é possível converter para um vídeo mp3."
                )
                return

            try:
                command = FfmpegProgress(
                    [
                        "ffmpeg",
                        "-i",
                        str(self.input_file),
                        "-c:v",
                        "copy",
                        "-c:a",
                        "copy",
                        str(self.output_file),
                    ]
                )

            except Exception:

                Path(self.output_file).unlink(missing_ok=True)

                command = FfmpegProgress(
                    [
                        "ffmpeg",
                        "-i",
                        str(self.input_file),
                        "-c:v",
                        "copy",
                        "-c:a",
                        "aac",
                        str(self.output_file),
                    ]
                )

        progress_bar_obj = ProgressBar()
        progress_bar_obj.create_progress_bar()

        progress_bar_obj.set_label_text(message)


        progress_thread = threading.Thread(
            target=progress_bar_obj.run_ffmpeg_with_progress, args=(command,)
        )
        progress_thread.start()

        progress_bar_obj.root.mainloop()

        progress_thread.join()

        progress_bar_obj.root.destroy()

    def change_video_title_to_filename(self) -> None:
        """
        A function to change the title of a video to match its filename,
        using a progress bar to display the progress of the operation.

        :return: None
        """

        filename = Path(self.input_file).name

        title = Path(filename).stem

        temp_output_file = str(self.input_file).replace(filename, f"mod_{filename}")

        message = (
            f'Modificando título do "{filename}"\n'
            f"{self.current_file} de {self.total_files} arquivos"
        )

        progress_bar_obj = ProgressBar()
        progress_bar_obj.create_progress_bar()

        progress_bar_obj.set_label_text(message)

        command = FfmpegProgress(
            [
                "ffmpeg",
                "-i",
                str(self.input_file),
                "-c",
                "copy",
                "-metadata",
                f"title={title}",
                str(temp_output_file),
            ],
        )

        progress_thread = threading.Thread(
            target=progress_bar_obj.run_ffmpeg_with_progress,
            args=(command,),
        )
        progress_thread.start()

        progress_bar_obj.root.mainloop()

        Path(self.input_file).unlink(missing_ok=True)
        Path(temp_output_file).rename(self.input_file)

        progress_thread.join()

        progress_bar_obj.root.destroy()

    def merge_video_to_subtitle(self) -> None:
        """
        Merge a video file with its corresponding subtitle file.

        :param input_file: Path to the video file or its name as a string.
        :param current_file: Current file number being processed (default is 1).
        :param total_files: Total number of files to be processed (default is 1).
        """

        self.input_file = str(self.input_file)

        # Get rid of quote characters
        os.rename(self.input_file, simplify_file_path(self.input_file))

        self.input_file = simplify_file_path(self.input_file)

        name = Path(self.input_file).stem
        file_name = Path(self.input_file).name

        # output file will be like "video.srt.mkv"
        merged = (
            simplify_file_path(Path(self.input_file).parent) + "/" + name + ".srt.mkv"
        )

        # Assume the subtitles have the same name as the video file
        subtitles = self.input_file.replace(file_name, name + ".srt")

        encode_to_utf8(subtitles)

        if os.path.exists(subtitles):
            os.rename(subtitles, simplify_file_path(subtitles))
            subtitles = simplify_file_path(subtitles)

        else:
            subtitles = ""

        command = FfmpegProgress(
            [
                "ffmpeg",
                "-i",
                self.input_file,
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
                "title=Pt-BR",
                # "language=pt",
                merged,
            ],
        )

        message = (
            "Juntando vídeo com a legenda do "
            f'"{file_name}"\n{self.current_file} de {self.total_files} arquivos'
        )

        progress_bar_obj = ProgressBar()
        progress_bar_obj.create_progress_bar()

        progress_bar_obj.set_label_text(message)

        progress_thread = threading.Thread(
            target=progress_bar_obj.run_ffmpeg_with_progress, args=(command,)
        )
        progress_thread.start()

        progress_bar_obj.root.mainloop()

        Path(self.input_file).unlink(missing_ok=True)
        Path(subtitles).unlink(missing_ok=True)

        progress_thread.join()

        progress_bar_obj.root.destroy()


if __name__ == "__main__":
    import glob

    path = glob.glob("*.mkv")

    progress_bar_obj_ = ProgressBar()

    for i, path_ in enumerate(path):

        progress_bar_obj_.create_progress_bar()

        total = len(path)

        video_adjuster_obj_ = VideoAdjuster(
            input_file=path_, current_file=i + 1, total_files=total
        )

        video_adjuster_obj_.change_video_title_to_filename()
        video_adjuster_obj_.merge_video_to_subtitle()
