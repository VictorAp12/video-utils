"""
This module contains two simple GUI application for converting video and audio files using ffmpeg,
changing the title of video files to their filenames and combining video with subtitles (srt).
"""

import os
from pathlib import Path
from typing import List, Literal
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog

from app.App import App
from app.tooltips import ToolTip
from utils.json_utils import (
    load_last_used_settings,
    save_last_used_settings,
    load_translations,
)
from utils.threading_utils import CustomThread
from utils.window_utils import center_window
from utils.ffmpeg_utils import (
    configure_font_subtitles_win,
    check_ffmpeg_tkinter,
    is_video_or_audio_file,
    extract_subtitle,
)
from video_adjuster import VideoAdjuster


# Load translations
translations = load_translations()


class VideoConverterApp(App):
    """
    This class is used to create a GUI application for
    converting video and audio files using ffmpeg.
    """

    def __init__(self, language: Literal["pt_BR", "en_US"]) -> None:
        """
        Constructor method for initializing the GUI window and setting
        up various elements within the window.

        :param language: The language to be used in the application.

        :return: None.
        """
        self.json_translations = translations[language]
        self.json_video_converter_app = self.json_translations[
            "Video and Audio Converter"
        ]

        super().__init__(
            self.json_video_converter_app["VideoConverterApp_title"],
            language=language,
        )

        self.create_output_folder_entry()

        self.create_input_extension_entry()
        self.create_output_extension_entry()

        self.create_conversion_type_radio_buttons()

        self.create_verify_files_button()

        self.create_convert_button()

        # self.create_subtitle_converter_button()

        center_window(self.root)

    def create_menu_bar(self) -> None:
        """
        Creates and configures the menu bar to change between apps.

        :return: None.
        """

        menu_bar, app_menu = super().create_menu_bar()

        app_menu.add_command(
            label=self.json_translations["Change Video Attributes"][
                "ChangeVideoAttributesApp_title"
            ],
            command=self.open_change_video_title_app,
        )

        self.root.config(menu=menu_bar)

    def open_change_video_title_app(self) -> None:
        """
        Opens the ChangeVideoTitleApp.

        :return: None.
        """
        # Destroy this window
        self.root.destroy()

        language = load_last_used_settings()[0]

        save_last_used_settings(
            "last_used_language",
            language=language,
            used_app="ChangeVideoAttributesApp",
        )

        app = ChangeVideoAttributesApp(language)

        # Show the ChangeVideoTitleApp
        app.root.mainloop()

        # Show the main window above everything
        app.root.lift()

        app.root.focus()

    def create_output_folder_entry(self) -> None:
        """
        Create output folder entry widgets and place them in the root window.

        :return: None.
        """
        json_widgets = self.json_translations["Widgets"]

        output_folder_label = ttk.Label(
            self.root, text=json_widgets["output_folder_label"], justify="left"
        )
        output_folder_label.grid(row=1, column=0, padx=5, pady=5)

        self.output_folder_entry = ttk.Entry(self.root, width=50)
        self.output_folder_entry.grid(row=1, column=1, padx=5, pady=5)

        browse_output_button = ttk.Button(
            self.root,
            text=json_widgets["browse_output_button"],
        )
        browse_output_button.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        browse_output_button.bind(
            "<Button-1>", lambda event: self.browse_folder(self.output_folder_entry)
        )

    def create_input_extension_entry(self) -> None:
        """
        Creates an input extension entry and label in the GUI.

        :return: None.
        """
        input_extension_label = ttk.Label(
            self.root,
            text=self.json_video_converter_app["input_extension_label"],
        )
        input_extension_label.grid(row=2, column=0, padx=5, pady=5)

        self.input_extension_entry = tk.Entry(self.root, width=50)
        self.input_extension_entry.insert(0, ".mp4")
        self.input_extension_entry.grid(row=2, column=1, padx=5, pady=5)

    def create_output_extension_entry(self) -> None:
        """
        Creates and configures the output extension entry in the GUI.

        :return: None.
        """

        output_extension_label = ttk.Label(
            self.root,
            text=self.json_video_converter_app["output_extension_label"],
            justify="left",
        )
        output_extension_label.grid(row=3, column=0, padx=5, pady=5)

        self.output_extension_entry = tk.Entry(self.root, width=50)
        self.output_extension_entry.insert(0, ".mp3")
        self.output_extension_entry.grid(row=3, column=1, padx=5, pady=5)

    def create_conversion_type_radio_buttons(self) -> None:
        """
        Creates radio buttons for selecting the type of conversion.

        :return: None.
        """

        conversion_type_label = ttk.Label(
            self.root,
            text=self.json_video_converter_app["conversion_type_label"],
            justify="left",
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

    def create_verify_files_button(self) -> None:
        """
        Create a button to verify the files in the input folder.

        :return: None.
        """
        json_widgets = self.json_translations["Widgets"]

        verify_files_button = ttk.Button(
            self.root,
            text=json_widgets["verify_files_button"],
            command=self.verify_files,
        )
        verify_files_button.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        ToolTip(
            verify_files_button,
            self.json_translations["Tooltips"]["verify_files_button_tooltip"],
        )

    def create_convert_button(self) -> None:
        """
        Creates and configures a convert button in the GUI.

        :return: None.
        """

        convert_button = ttk.Button(
            self.root,
            text=self.json_video_converter_app["convert_button"],
            command=self.convert_file,
        )
        convert_button.grid(row=5, column=1, padx=5, pady=5, sticky="e")

        ToolTip(
            convert_button,
            self.json_translations["Tooltips"]["convert_button_tooltip"],
        )

    # def create_subtitle_converter_button(self) -> None:
    #     """
    #     Creates and configures a subtitle converter button in the GUI.

    #     :return: None.
    #     """

    #     subtitle_converter_button = ttk.Button(
    #         self.root,
    #         text=self.json_video_converter_app["subtitle_converter_button"],
    #         # command=self.subtitle_converter,
    #     )
    #     subtitle_converter_button.grid(row=5, column=2, padx=5, pady=5, sticky="e")

    #     ToolTip(
    #         subtitle_converter_button,
    #         self.json_translations["Tooltips"]["subtitle_converter_button_tooltip"],
    #     )

    def execute_function(self, function_name: str) -> None:
        """
        Function to execute the selected function.

        :param function_name: str, The name of the function to execute.

        :raises tk.messagebox warning: If the fields are not filled.

        :return: None.
        """
        input_files = super().execute_function(function_name)

        if not input_files:
            return

        input_folder = Path(self.input_folder_entry.get())
        output_folder = Path(self.output_folder_entry.get())
        output_extension = self.output_extension_entry.get()
        conversion_type = self.conversion_type_var.get()

        if (
            not output_folder.is_dir()
            or not input_folder.is_dir()
            or conversion_type not in ("audio", "video")
        ):
            messagebox.showwarning(
                self.json_translations["MessageBox"]["warning"],
                message=self.json_translations["MessageBox"]["error_missing_field"],
            )
            return

        binaries = check_ffmpeg_tkinter()

        if binaries is None:
            return

        video_adjuster = VideoAdjuster(
            input_files=input_files,
            output_folder=output_folder,
            master=self.root,
        )

        if function_name == "audio_converter":
            video_adjuster.run_converter(conversion_type, output_extension)

        elif function_name == "video_converter":
            video_adjuster.run_converter(conversion_type, output_extension)

    def verify_files(self):
        """
        Verifies the input folder and extension entries, creates a list of input files,
        and updates the treeview with the input files. Returns True if successful,
        or None if the input folder or extension entries are empty.

        :raises tk.messagebox error: If the folder does not exist.
        :raises tk.messagebox info: If the number of input files is greater than 50.

        :return: None.
        """
        if not self.input_folder_entry.get() and not self.input_extension_entry.get():
            return
        if not self.input_folder_entry.get() or not self.input_extension_entry.get():
            return

        input_folder = Path(self.input_folder_entry.get())

        if not input_folder.exists():
            messagebox.showerror(
                self.json_translations["MessageBox"]["error"],
                self.json_translations["MessageBox"]["error_folder_does_not_exist"],
            )
            return

        input_files = list(input_folder.glob("*" + self.input_extension_entry.get()))

        if not input_files:
            messagebox.showerror(
                self.json_translations["MessageBox"]["error"],
                self.json_translations["MessageBox"]["error_files_not_found"],
            )
            return
        if len(input_files) > 50:
            messagebox.showinfo(
                self.json_translations["MessageBox"]["info"],
                self.json_translations["MessageBox"]["too_many_files"],
                parent=self.root,
            )

        def check_files(files: List[Path]) -> List[Path]:
            input_files = [file for file in files if is_video_or_audio_file(file)]

            return input_files

        thread = CustomThread(target=check_files, args=(input_files,))
        thread.start()

        result = thread.join()

        input_files = result
        if input_files:
            self.create_treeview(input_files)

    def convert_file(self) -> None:
        """
        Convert files from one format to another based on the specified input and output
        folders, extensions, and conversion type. Uses audio_converter or video_converter
        based on the conversion type.

        :return: None.
        """
        conversion_type = self.conversion_type_var.get()

        if conversion_type == "audio":
            self.execute_function("audio_converter")

        elif conversion_type == "video":
            self.execute_function("video_converter")


class ChangeVideoAttributesApp(App):
    """
    This class is used to create a GUI application for
    changing the title of video file to its filename.
    """

    def __init__(self, language: Literal["pt_BR", "en_US"]) -> None:
        """
        Constructor method for initializing the GUI window and setting
        up various elements within the window.

        :param language: The language to be used in the application.

        :return: None.
        """
        self.json_translations = translations[language]
        self.json_change_video_attributes_app = self.json_translations[
            "Change Video Attributes"
        ]

        super().__init__(
            self.json_change_video_attributes_app["ChangeVideoAttributesApp_title"],
            language=language,
        )

        self.create_verify_files_button()

        self.create_change_button()

        self.create_merge_button()

        self.create_extract_subtitles_button()

        center_window(self.root)

        self.root.focus_set()

    def create_menu_bar(self) -> None:
        """
        Creates and configures the menu bar to change between apps.

        :return: None.
        """
        menu_bar, app_menu = super().create_menu_bar()

        app_menu.add_command(
            label=self.json_translations["Video and Audio Converter"][
                "VideoConverterApp_title"
            ],
            command=self.open_video_converter_app,
        )

        self.root.config(menu=menu_bar)

    def open_video_converter_app(self) -> None:
        """
        Opens a new window that allows the user to convert video files.

        :return: None.
        """
        # Destroy this window
        self.root.destroy()

        language = load_last_used_settings()[0]

        save_last_used_settings(
            "last_used_language",
            language=language,
            used_app="VideoConverterApp",
        )

        app = VideoConverterApp(language)

        # Show the ChangeVideoTitleApp
        app.root.mainloop()

        # Show the main window above everything
        app.root.lift()

        app.root.focus()

    def create_verify_files_button(self) -> None:
        """
        Verifies the input folder and extension entries, creates a list of input files,
        and updates the treeview with the input files. Returns True if successful,
        or None if the input folder or extension entries are empty.

        :return: None.
        """
        json_widgets = self.json_translations["Widgets"]
        verify_files_button = ttk.Button(
            self.root,
            text=json_widgets["verify_files_button"],
            command=self.verify_files,
        )
        verify_files_button.grid(row=5, column=0, padx=5, pady=5, sticky="w")

        ToolTip(
            verify_files_button,
            self.json_translations["Tooltips"]["verify_files_button_tooltip"],
        )

    def create_change_button(self) -> None:
        """
        Creates and configures a change title button in the GUI.

        :return: None.
        """

        change_button = ttk.Button(
            self.root,
            text=self.json_change_video_attributes_app["change_button"],
            command=self.change_title,
        )
        change_button.grid(row=5, column=1, sticky="w", padx=5, pady=5)

        ToolTip(
            change_button,
            self.json_translations["Tooltips"]["change_button_tooltip"],
        )

    def create_merge_button(self) -> None:
        """
        Creates and configures a merge button in the GUI.

        :return: None.
        """
        merge_button = ttk.Button(
            self.root,
            text=self.json_change_video_attributes_app["merge_button"],
            command=self.merge_video_to_subtitle,
        )

        merge_button.grid(row=5, column=1, sticky="e", padx=5, pady=5)

        ToolTip(
            merge_button,
            self.json_translations["Tooltips"]["merge_button_tooltip"],
        )

    def create_extract_subtitles_button(self) -> None:
        """
        Creates and configures an extract subtitles button in the GUI.

        :return: None.
        """

        extract_subtitles_button = ttk.Button(
            self.root,
            text=self.json_change_video_attributes_app["extract_button"],
            command=self.extract_subtitles,
        )
        extract_subtitles_button.grid(row=5, column=2, padx=5, pady=5, sticky="w")

        ToolTip(
            extract_subtitles_button,
            self.json_translations["Tooltips"]["extract_button_tooltip"],
        )

    def browse_folder(self, folder_entry: tk.Entry) -> None:
        """
        Function to browse the folder and update the folder_entry
        with the selected folder path. No parameters and no return type.

        :param folder_entry: The entry widget to update with the selected folder path.

        :return: None.
        """

        folder = filedialog.askdirectory(mustexist=True)
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder)

    def execute_function(
        self,
        function_name: Literal[
            "change_title", "merge_video_to_subtitle", "extract_subtitles"
        ],
    ) -> None:
        """
        Function to execute the selected function.

        :param function_name: The name of the function to execute.

        :return: None.
        """
        input_files = super().execute_function(function_name)

        if not input_files:
            return

        input_files = [str(input_file) for input_file in input_files]

        video_adjuster = VideoAdjuster(input_files=input_files, master=self.root)

        binaries = check_ffmpeg_tkinter()

        if binaries is None:
            return

        if function_name == "change_title":
            video_adjuster.change_video_title_to_filename()

        elif function_name == "merge_video_to_subtitle":

            if os.name == "nt":
                # Configure the fonts for the subtitles
                configure_font_subtitles_win(binaries)

            user_input = simpledialog.askstring(
                self.json_change_video_attributes_app["simple_dialog_merge_title"],
                self.json_change_video_attributes_app["simple_dialog_merge_text"],
            )

            if user_input:
                video_adjuster.merge_video_to_subtitle(subtitle_language=user_input)
            else:
                video_adjuster.merge_video_to_subtitle()

        elif function_name == "extract_subtitles":
            extract_subtitle_extension = simpledialog.askstring(
                self.json_change_video_attributes_app["simple_dialog_extract_title"],
                self.json_change_video_attributes_app["simple_dialog_extract_text"],
                initialvalue=".srt",
                parent=self.root,
            )

            if not extract_subtitle_extension:
                extract_subtitle_extension = ".srt"

            for input_file in input_files:
                input_file = Path(input_file)
                result = extract_subtitle(
                    input_file,
                    input_file.parent,
                    extract_subtitle_extension,
                )

            if result:
                messagebox.showinfo(
                    self.json_translations["MessageBox"]["success"],
                    self.json_translations["MessageBox"]["success_message"],
                )

    def verify_files(self) -> None:
        """
        Verifies the input folder and extension entries, creates a list of input files,
        and updates the treeview with the input files. Returns True if successful,
        or None if the input folder or extension entries are empty.

        :raises tk.messagebox error: If the input folder does not exist.
        :raises tk.messagebox info: If the number of input files is greater than 50.

        :return: None.
        """
        if not self.input_folder_entry.get():
            return

        input_folder = Path(self.input_folder_entry.get())

        if not input_folder.exists():
            messagebox.showerror(
                self.json_translations["MessageBox"]["error"],
                self.json_translations["MessageBox"]["error_folder_does_not_exist"],
            )
            return

        input_files = list(input_folder.glob("*"))

        if len(input_files) > 50:
            messagebox.showinfo(
                "Info",
                "There are too many videos in this folder, it will take a while",
                parent=self.root,
            )

        def check_files(files: List[Path]) -> List[Path]:
            input_files = [file for file in files if is_video_or_audio_file(file)]

            return input_files

        thread = CustomThread(target=check_files, args=(input_files,))
        thread.start()

        result = thread.join()

        input_files = result
        if input_files:
            self.create_treeview(input_files)

    def change_title(self) -> None:
        """
        Function to change the title of the video file to its filename.

        :return: None.
        """
        self.execute_function("change_title")

    def merge_video_to_subtitle(self) -> None:
        """
        Function to merge the subtitles with the video.

        :return: None.
        """
        self.execute_function("merge_video_to_subtitle")

    def extract_subtitles(self) -> None:
        """
        Extracts subtitles from video files based on the specified input and output
        folders, extensions, and conversion type. Uses extract_subtitles.

        :return: None.
        """
        self.execute_function("extract_subtitles")


if __name__ == "__main__":
    if load_last_used_settings()[2] == "VideoConverterApp":
        window = VideoConverterApp(load_last_used_settings()[0])
        window.root.mainloop()
    else:
        window = ChangeVideoAttributesApp(load_last_used_settings()[0])
        window.root.mainloop()
