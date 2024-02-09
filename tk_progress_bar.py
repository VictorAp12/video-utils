"""
A module to create a progress bar in a Tkinter window.
"""

import tkinter as tk
from tkinter import ttk

from ffmpeg_progress_yield import FfmpegProgress

from window_utils import center_window


class ProgressBar:
    """
    A class to create and manage a progress bar in a Tkinter window.

    Warning: When Using a command you have to call a run method with threading in
    order to update the progress bar without freezing the master window.

    Example usage:
        progress_bar_obj = ProgressBar()
        progress_bar_obj.create_progress_bar()

        progress_bar_obj.set_label_text("Modifying title...")
        progress_thread = threading.Thread(
            target=progress_bar_obj.run_ffmpeg_with_progress,
            args=(command,),
        )
        progress_thread.start()

        progress_bar_obj.root.mainloop()

        ...

        progress_thread.join()
        progress_bar_obj.root.destroy()

    Attributes:
    - master: The Tkinter master window for the progress bar.
    - root: The Tkinter root window.
    - progress_bar_label: The label for the progress bar.
    - progress_bar: The progress bar widget.

    Methods:
    - create_progress_bar()
    - set_label_text(text)
    - run_ffmpeg_with_progress(command)
    """

    def __init__(self, master: tk.Tk | None = None) -> None:
        self.master = master

        self.root = tk.Tk()
        self.progress_bar_label = ttk.Label(self.root, text="")
        self.progress_bar = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=200,
            mode="determinate",
        )
        self.progress_bar_label_percentage = ttk.Label(self.root, text="")

    def create_progress_bar(self):  # -> tuple[tk.Tk, ttk.Progressbar, ttk.Label]:
        """
        Creates a progress bar and displays it on the screen.

        :return: tuple[tk.Tk, ttk.Progressbar, ttk.Label]
        """
        # self.root.overrideredirect(True)
        self.root.title("Progresso")

        center_window(self.root, self.master)

        self.progress_bar_label.pack()

        self.progress_bar["value"] = 0
        self.progress_bar.pack(fill="both", expand=True)

        self.progress_bar_label_percentage.config(text="0%", justify="center")
        self.progress_bar_label_percentage.pack()

        self.root.resizable(False, False)

    def set_label_text(self, text: str):
        """Function to set the text of the progress bar label."""
        self.progress_bar_label.config(text=text)

    def _update_progress(self, progress: int | float):
        """
        Updates the progress of a given ttk.Progressbar in a tk.Tk window.

        :return: None
        """

        # print(self.progress)
        self.progress_bar["value"] = int(progress)
        self.progress_bar_label_percentage.config(text=f"{progress}%", justify="center")

        self.root.update_idletasks()

    # runs a command with progress updates in a given window
    def run_ffmpeg_with_progress(self, command: FfmpegProgress):
        """
        Runs a command with progress updates in a window.

        :param command: FfmpegProgress - The command to run with progress.

        :return: None
        """

        self.root.deiconify()

        for progress in command.run_command_with_progress({"shell": True}):
            self.root.after(10, self._update_progress, progress)

        self.root.quit()


if __name__ == "__main__":
    barra = ProgressBar()

    barra.create_progress_bar()
    barra.root.mainloop()
