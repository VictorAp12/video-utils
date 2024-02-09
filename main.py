"""
This module contains two simple GUI application for converting video and audio files using ffmpeg,
changing the title of video files to their filenames and combining video with subtitles (srt).
"""

from abc import ABC, abstractmethod
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from typing import Literal, Tuple

from ttkthemes import ThemedStyle

from window_utils import center_window
from ffmpeg_utils import check, configure
from video_adjuster import is_video_or_audio_file, VideoAdjuster


class App(ABC):
    """
    This class represents the main application window.

    It initializes the GUI window and sets up various elements within the window.
    """

    def __init__(self, title: str) -> None:
        """
        Constructor method for initializing the GUI window and setting
        up various elements within the window.
        """

        self.root = tk.Tk()
        self.style = ThemedStyle(self.root)
        self.style.set_theme("black")

        self.root.configure(bg=self.style.lookup("TLabel", "background"))
        self.root.title(title)
        self.root.resizable(False, False)

        center_window(self.root)

        # make the window responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.create_menu_bar()

        self.create_input_folder_entry()

    @abstractmethod
    def create_menu_bar(self) -> Tuple[tk.Menu, tk.Menu]:
        """
        Abstract method to create the menu bar, to change between apps.
        """

        menu_bar = tk.Menu(self.root)

        menu_bar.configure(bg=self.style.lookup("TLabel", "background"))

        app_menu = tk.Menu(
            menu_bar,
            tearoff=0,
            bg=self.style.lookup("TLabel", "background"),
            fg="white",
        )

        menu_bar.add_cascade(label="Apps", menu=app_menu)

        self.root.config(menu=menu_bar)

        return menu_bar, app_menu

    def create_input_folder_entry(self) -> None:
        """
        Creates input folder entry and associated label and button.
        """

        input_folder_label = ttk.Label(
            self.root, text="Pasta dos arquivos:", justify="left"
        )
        input_folder_label.grid(row=0, column=0, padx=5, pady=5)

        self.input_folder_entry = ttk.Entry(self.root, width=50)
        self.input_folder_entry.grid(row=0, column=1, padx=5, pady=5)

        browse_input_button = ttk.Button(
            self.root,
            text="Procurar",
        )
        browse_input_button.grid(row=0, column=2, padx=5, pady=5)
        browse_input_button.bind(
            "<Button-1>", lambda event: self.browse_folder(self.input_folder_entry)
        )

    def browse_folder(self, folder_entry: tk.Entry) -> None:
        """
        Function to browse the folder and update the folder_entry
        with the selected folder path. No parameters and no return type.
        """
        folder = filedialog.askdirectory(mustexist=True)
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder)

    @abstractmethod
    def execute_function(self, function_name: str) -> None:
        """
        Abstract method to execute a function based on its name.
        """
        raise NotImplementedError("execute_function must be implemented")


class VideoConverterApp(App):
    """
    This class is used to create a GUI application for
    converting video and audio files using ffmpeg.
    """

    def __init__(self) -> None:
        """
        Constructor method for initializing the GUI window and setting
        up various elements within the window.
        """
        super().__init__("Conversor de Videos e Audios")

        self.create_output_folder_entry()

        self.create_input_extension_entry()
        self.create_output_extension_entry()

        self.create_conversion_type_radio_buttons()

        self.create_convert_button()

    def create_menu_bar(self) -> None:
        """
        Creates and configures the menu bar to change between apps.
        """
        menu_bar, app_menu = super().create_menu_bar()

        app_menu.add_command(
            label="Mudar Titulo Videos e modificar legenda",
            command=self.open_change_video_title_app,
        )

        self.root.config(menu=menu_bar)

    def open_change_video_title_app(self) -> None:
        """
        Opens the ChangeVideoTitleApp.
        """
        app = ChangeVideoTitleApp()
        app.root.mainloop()

    def create_output_folder_entry(self) -> None:
        """
        Create output folder entry widgets and place them in the root window.
        """

        output_folder_label = ttk.Label(
            self.root, text="Pasta de destino:", justify="left"
        )
        output_folder_label.grid(row=1, column=0, padx=5, pady=5)

        self.output_folder_entry = ttk.Entry(self.root, width=50)
        self.output_folder_entry.grid(row=1, column=1, padx=5, pady=5)

        browse_output_button = ttk.Button(
            self.root,
            text="Procurar",
        )
        browse_output_button.grid(row=1, column=2, padx=5, pady=5)
        browse_output_button.bind(
            "<Button-1>", lambda event: self.browse_folder(self.output_folder_entry)
        )

    def create_input_extension_entry(self) -> None:
        """
        Creates an input extension entry and label in the GUI.
        """

        input_extension_label = ttk.Label(self.root, text="Extensão procurada:")
        input_extension_label.grid(row=2, column=0, padx=5, pady=5)

        self.input_extension_entry = tk.Entry(self.root, width=50)
        self.input_extension_entry.insert(0, ".mp4")
        self.input_extension_entry.grid(row=2, column=1, padx=5, pady=5)

    def create_output_extension_entry(self) -> None:
        """
        Creates and configures the output extension entry in the GUI.
        """

        output_extension_label = ttk.Label(
            self.root, text="Extensão desejada:", justify="left"
        )
        output_extension_label.grid(row=3, column=0, padx=5, pady=5)

        self.output_extension_entry = tk.Entry(self.root, width=50)
        self.output_extension_entry.insert(0, ".mp3")
        self.output_extension_entry.grid(row=3, column=1, padx=5, pady=5)

    def create_conversion_type_radio_buttons(self) -> None:
        """
        Creates radio buttons for selecting the type of conversion.
        """

        conversion_type_label = ttk.Label(
            self.root, text="Tipo de conversão:", justify="left"
        )
        conversion_type_label.grid(row=4, column=0, padx=5, pady=5)

        self.conversion_type_var = tk.StringVar()

        audio_radio_button = ttk.Radiobutton(
            self.root, text="Audio", variable=self.conversion_type_var, value="audio"
        )
        audio_radio_button.grid(row=4, column=1, padx=5, pady=5)

        video_radio_button = ttk.Radiobutton(
            self.root, text="Video", variable=self.conversion_type_var, value="video"
        )
        video_radio_button.grid(row=4, column=1, padx=5, pady=5, sticky="e")

    def create_convert_button(self) -> None:
        """
        Creates and configures a convert button in the GUI.
        """

        convert_button = ttk.Button(
            self.root, text="Converter", command=self.convert_file
        )
        convert_button.grid(row=5, column=1, padx=5, pady=5)

    def execute_function(self, function_name: str) -> None:
        """
        Function to execute the selected function.
        """
        input_folder = Path(self.input_folder_entry.get())
        input_extension = self.input_extension_entry.get()

        input_files = [
            file for file in input_folder.iterdir() if is_video_or_audio_file(file)
        ]

        output_folder = Path(self.output_folder_entry.get())
        output_extension = self.output_extension_entry.get()
        conversion_type = self.conversion_type_var.get()

        if (
            not output_folder.is_dir()
            or not input_folder.is_dir()
            or conversion_type not in ("audio", "video")
        ):
            return

        for i, input_file in enumerate(input_files):
            output_file = (
                f"{output_folder}\\"
                + f"{input_file.name.replace(input_extension, output_extension)}"
            )
            input_file = input_folder / input_file

            video_adjuster = VideoAdjuster(
                input_file,
                output_file,
                i + 1,
                len(input_files),
            )

            if function_name == "audio_converter":
                video_adjuster.run_converter(conversion_type)

            elif function_name == "video_converter":
                video_adjuster.run_converter(conversion_type)

    def convert_file(self) -> None:
        """
        Convert files from one format to another based on the specified input and output
        folders, extensions, and conversion type. Uses audio_converter or video_converter
        based on the conversion type.
        """
        conversion_type = self.conversion_type_var.get()

        if conversion_type == "audio":
            self.execute_function("audio_converter")

        elif conversion_type == "video":
            self.execute_function("video_converter")


class ChangeVideoTitleApp(App):
    """
    This class is used to create a GUI application for
    changing the title of video file to its filename.
    """

    def __init__(self) -> None:
        """
        Constructor method for initializing the GUI window and setting
        up various elements within the window.
        """
        super().__init__("Mudar título de videos e audios")

        self.create_change_button()

        self.create_merge_button()

    def create_menu_bar(self) -> None:
        """
        Creates and configures the menu bar to change between apps.
        """
        menu_bar, app_menu = super().create_menu_bar()

        app_menu.add_command(
            label="Converter Videos e audios",
            command=self.open_video_converter_app,
        )

        self.root.config(menu=menu_bar)

    def open_video_converter_app(self):
        """
        Opens a new window that allows the user to convert video files.
        """
        app = VideoConverterApp()
        app.root.mainloop()

    def create_input_folder_entry(self) -> None:
        """
        Creates folder entry and associated label and button.
        """

        folder_label = ttk.Label(self.root, text="Pasta dos arquivos:", justify="left")
        folder_label.grid(row=0, column=0, padx=5, pady=5)

        self.folder_entry = ttk.Entry(self.root, width=50)
        self.folder_entry.grid(row=0, column=1, padx=5, pady=5)

        browse_input_button = ttk.Button(
            self.root, text="Procurar", command=self.browse_folder
        )
        browse_input_button.grid(row=0, column=2, padx=5, pady=5)

    def create_change_button(self) -> None:
        """
        Creates and configures a change title button in the GUI.
        """

        change_button = ttk.Button(
            self.root, text="Mudar título", command=self.change_title
        )
        change_button.grid(row=5, column=1, sticky="w", padx=5, pady=5)

    def create_merge_button(self) -> None:
        """
        Creates and configures a merge button in the GUI.
        """
        merge_button = ttk.Button(
            self.root,
            text="Juntar vídeo com legenda",
            command=self.merge_video_to_subtitle,
        )

        merge_button.grid(row=5, column=1, sticky="e", padx=5, pady=5)

    def browse_folder(self) -> None:
        """
        Function to browse the folder and update the folder_entry
        with the selected folder path. No parameters and no return type.
        """

        folder = filedialog.askdirectory(mustexist=True)
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, folder)

    def execute_function(
        self, name: Literal["change_title", "merge_video_to_subtitle"]
    ) -> None:
        """
        Function to execute the selected function.
        """
        input_folder = Path(self.folder_entry.get())

        input_files = [
            file for file in input_folder.iterdir() if is_video_or_audio_file(file)
        ]

        if not input_folder.exists():
            return

        for i, input_file in enumerate(input_files):

            input_file = input_folder / input_file

            video_adjuster = VideoAdjuster(
                input_file=input_file, current_file=i + 1, total_files=len(input_files)
            )

            if name == "change_title":
                video_adjuster.change_video_title_to_filename()

            elif name == "merge_video_to_subtitle":
                os.environ["FFMPEG_DIRECTORY"] = "C:\\Program Files\\ffmpeg"

                binaries = check()
                if not binaries:
                    return

                if os.name == "nt":
                    # Configure the fonts for the subtitles
                    configure(binaries)

                video_adjuster.merge_video_to_subtitle()

    def change_title(self) -> None:
        """
        Function to change the title of the video file to its filename.
        """
        self.execute_function("change_title")

    def merge_video_to_subtitle(self):
        """
        Function to merge the subtitles with the video.
        """
        self.execute_function("merge_video_to_subtitle")


if __name__ == "__main__":
    window = VideoConverterApp()
    window.root.mainloop()
