"""
A module to create a progress bar in a Tkinter window.
"""

import time
import tkinter as tk
from tkinter import ttk, PhotoImage, BooleanVar, messagebox

from ffmpeg_progress_yield import FfmpegProgress
from utils.threading_utils import CustomThread

from utils.json_utils import load_translations, load_last_used_settings
from utils.window_utils import center_window

language = load_last_used_settings()[0]
translations = load_translations()[language]


class CustomProgressBar:
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

    Methods:
    - create_progress_bar()
    - create_pause_button()
    - set_label_text(text)
    - run_ffmpeg_with_progress(command)
    - run_progress_bar_sample()
    - update_progress(progress)
    """

    def __init__(
        self, master: tk.Tk | tk.Toplevel | None = None, with_pause_button: bool = True
    ) -> None:
        """
        Initializes the progress bar object.

        :param master: The Tkinter master window for the progress bar.
        :param with_pause_button: bool, Whether to display a pause button.

        :return: None.
        """
        self.master = master

        self.with_pause_button = with_pause_button

        self.json_progress_bar = translations["ProgressBar"]

        if self.master:
            theme = ttk.Style(master)
            self.root = tk.Toplevel(
                master=master, bg=theme.lookup("TLabel", "background")
            )

        else:
            self.root = tk.Tk()

        self.root.minsize(250, 80)

        if master:
            self.root.grab_set()

        self.root.wm_attributes("-topmost", True)
        self.root.lift()

        self.root.protocol("WM_DELETE_WINDOW", self._set_cancel_true)

        self.progress_bar_label = ttk.Label(self.root, text="")

        self.cancel_button_img = PhotoImage(file="./assets/cross-button.png").subsample(
            6, 6
        )

        self.cancel_button = ttk.Button(
            self.root, image=self.cancel_button_img, command=self._set_cancel_true
        )

        self.cancel = BooleanVar()
        self.cancel.set(False)

        self.cancel_all_button = ttk.Button(
            self.root,
            text=self.json_progress_bar["cancel_all_button"],
            command=self._set_cancel_all_true,
        )

        self.cancel_all = BooleanVar()
        self.cancel_all.set(False)

        if self.with_pause_button:
            self.play_btn_img = PhotoImage(file="./assets/play-button.png").subsample(
                6, 6
            )
            self.pause_btn_img = PhotoImage(file="./assets/pause-button.png").subsample(
                6, 6
            )
            self.pause_button = ttk.Button(
                self.root, image=self.pause_btn_img, command=self._pause_or_play
            )

            self.pause = BooleanVar()
            self.pause.set(False)

        self.progress_bar = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=200,
            mode="determinate",
        )
        self.progress_bar_percentage_label = ttk.Label(self.root, text="")

        # configure_binding = self.root.bind("<Configure>", print_window_size)

    def create_progress_bar(self) -> None:
        """
        Creates a progress bar and displays it on the screen.

        :return: None.
        """
        self.root.title(self.json_progress_bar["ProgressBar_title"])

        self.progress_bar_label.pack(side="top", anchor="nw")

        self.cancel_button.pack(side="top", anchor="ne")

        self.progress_bar["value"] = 0
        self.progress_bar.pack(fill="both", expand=True)

        self.progress_bar_percentage_label.config(text="0%", justify="center")
        self.progress_bar_percentage_label.pack(anchor="s")

        self.cancel_all_button.pack(side="bottom", anchor="s")

        center_window(self.root, self.master)

        self.root.resizable(False, False)

        if self.with_pause_button:
            self.create_pause_button()

    def set_label_text(self, text: str) -> None:
        """
        Function to set the text of the progress bar label.

        :param text: The text to be displayed in the progress bar label.

        :return: None.
        """
        self.progress_bar_label.config(text=text)

        center_window(self.root, self.master)

        self.root.resizable(False, False)

    def create_pause_button(self) -> None:
        """
        Function to create the pause button.

        :return: None.
        """
        # the pause button should be on the left side of the cancel button
        self.pause_button.place(
            x=self.cancel_button.winfo_x()
            - self.cancel_button.winfo_width()
            - self.pause_button.winfo_width(),
            y=self.cancel_button.winfo_y(),
        )

    def update_progress(self, progress: int | float) -> None:
        """
        Function to update the progress of the progress bar.

        :param progress: The progress to be displayed in the progress bar.

        :return: None.
        """
        self.root.deiconify()

        self.progress_bar["value"] = int(progress)
        self.progress_bar_percentage_label.config(text=f"{progress}%", justify="center")

        self.root.update_idletasks()

    def _update_progress(self, progress: int | float) -> None:
        """
        Updates the progress of a given ttk.Progressbar in a tk.Tk window.

        :param progress: The progress to be displayed in the progress bar.

        :return: None.
        """

        # print(self.progress)
        self.progress_bar["value"] = int(progress)
        self.progress_bar_percentage_label.config(text=f"{progress}%", justify="center")

        self.root.update_idletasks()

    def run_progress_bar_sample(self) -> None:
        """
        Runs a sample progress bar in a window.

        :return: None.
        """
        self.root.deiconify()

        for progress in range(0, 101):
            time.sleep(0.1)

            if self.cancel.get():
                break

            if self.cancel_all.get():
                break

            if not self.pause.get():
                self.root.after(10, self._update_progress, progress)

            else:
                self.root.wait_variable(self.pause)  # Wait for self.paused to change

        self.root.quit()

    def run_ffmpeg_with_progress(self, command: FfmpegProgress) -> bool:
        """
        Runs a command with progress updates in a window.

        :param command: FfmpegProgress - The command to run with progress.

        :raises tk.messagebox Error: If the command fails to run.

        :return: bool - True if the command ran successfully, False otherwise.
        """
        self.root.deiconify()

        try:
            for progress in command.run_command_with_progress({"shell": True}):
                if self.cancel.get():
                    command.quit_gracefully()
                    self.root.quit()
                    break

                if self.cancel_all.get():
                    command.quit_gracefully()
                    self.root.quit()
                    return False

                self.root.after(10, self._update_progress, progress)

        except RuntimeError:
            self.root.withdraw()
            messagebox.showerror(
                translations["MessageBox"]["error"],
                message=translations["MessageBox"]["error_ffmpeg_command"],
            )
            self.root.destroy()
            return False

        self.root.quit()

        return True

    def _pause_or_play(self) -> None:
        """
        Function to pause or play the progress bar.

        :return: None.
        """

        if self.pause.get():
            self.pause_button.config(image=self.pause_btn_img)
            self.pause.set(False)
        else:
            self.pause_button.config(image=self.play_btn_img)
            self.pause.set(True)

    def _set_cancel_true(self) -> None:
        """
        Function to close the window.

        :return: None.
        """
        self.cancel.set(True)

        try:
            if self.pause.get():
                self.pause.set(False)
            else:
                self.pause.set(True)

        except AttributeError:
            pass

    def _set_cancel_all_true(self) -> None:
        """
        Function to close the window and stop all the progresses

        :return: None.
        """
        self.cancel_all.set(True)

        try:
            if self.pause.get():
                self.pause.set(False)
            else:
                self.pause.set(True)

        except AttributeError:
            pass


if __name__ == "__main__":
    barra = CustomProgressBar()

    barra.create_progress_bar()

    barra.set_label_text("Carregando [nome do arquivo e subtitulo]...")

    progress_thread = CustomThread(target=barra.run_progress_bar_sample)

    progress_thread.start()

    barra.root.mainloop()

    progress_thread.join()
