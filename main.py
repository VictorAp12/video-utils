"""
This module contains two simple GUI application for converting video and audio files using ffmpeg,
changing the title of video files to their filenames and combining video with subtitles (srt).
"""

import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal, Tuple
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
import webbrowser

from ttkthemes import ThemedStyle
from PIL import ImageTk, Image

from utils.json_utils import (
    load_last_used_settings,
    save_last_used_settings,
    load_translations,
)
from utils.window_utils import center_window
from utils.ffmpeg_utils import check, configure
from video_adjuster import is_video_or_audio_file, VideoAdjuster


# Load translations
translations = load_translations()


class App(ABC):
    """
    This class represents the main application window.

    It initializes the GUI window and sets up various elements within the window.
    """

    def __init__(
        self,
        title: str,
        language: Literal["pt_BR", "en_US"] = load_last_used_settings()[0],
    ) -> None:
        """
        Constructor method for initializing the GUI window and setting
        up various elements within the window.
        """
        self.json_translations = translations[language]

        self.root = tk.Tk()

        self.style = ThemedStyle(self.root)
        self.style.set_theme(load_last_used_settings()[1])
        self.root.configure(bg=self.style.lookup("TLabel", "background"))
        self.root.title(title)
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # make the window responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.create_menu_bar()

        self.create_input_folder_entry()

        self.treeview = ttk.Treeview(self.root, columns=(1,))

        self.checked_image = ImageTk.PhotoImage(
            Image.open("assets/checked-checkbox.png").resize((20, 20))
        )
        self.unchecked_image = ImageTk.PhotoImage(
            Image.open("assets/blank-check-box.png").resize((20, 20))
        )

    @abstractmethod
    def create_menu_bar(self) -> Tuple[tk.Menu, tk.Menu]:
        """
        Abstract method to create the menu bar, to change between apps.
        """
        json_menu = self.json_translations["Menu"]

        menu_bar = tk.Menu(
            self.root,
        )

        app_menu = tk.Menu(tearoff=0)

        menu_bar.add_cascade(label="Apps", menu=app_menu)

        theme_menu = tk.Menu(tearoff=0)

        theme_menu.add_command(
            label=json_menu["theme_menu_light_mode"],
            command=lambda: self._change_theme("default"),
        )

        theme_menu.add_command(
            label=json_menu["theme_menu_dark_mode"],
            command=lambda: self._change_theme("black"),
        )

        menu_bar.add_cascade(label=json_menu["theme_menu_name"], menu=theme_menu)

        language_menu = tk.Menu(tearoff=0)

        language_menu.add_command(
            label=json_menu["language_menu_portuguese"],
            command=lambda: self._change_language("pt_BR"),
        )

        language_menu.add_command(
            label=json_menu["language_menu_english"],
            command=lambda: self._change_language("en_US"),
        )

        menu_bar.add_cascade(label=json_menu["language_menu_name"], menu=language_menu)

        about_menu = tk.Menu(tearoff=0)

        about_menu.add_command(
            label=json_menu["about_menu_project_link"],
            command=lambda: webbrowser.open(
                "https://github.com/VictorAp12/video-utils"
            ),
        )

        about_menu.add_command(
            label=json_menu["about_menu_author"],
            command=lambda: webbrowser.open("https://github.com/VictorAp12"),
        )

        # ToDo: add documentation
        about_menu.add_command(label=json_menu["about_menu_documentation"], command="")

        menu_bar.add_cascade(label=json_menu["about_menu_name"], menu=about_menu)

        self.root.config(menu=menu_bar)

        return menu_bar, app_menu

    def _change_theme(self, theme: Literal["default", "black"]) -> None:
        """
        Changes the theme of the application.
        """
        if theme == load_last_used_settings()[1]:
            return

        # print(self.style.get_themes())

        self.style.set_theme(theme)
        self.root.config(bg=self.style.lookup("TLabel", "background"))

        center_window(self.root)

        # update user settings
        save_last_used_settings("last_used_theme", theme=theme)

    def _change_language(
        self, language: Literal["pt_BR", "en_US"] = load_last_used_settings()[0]
    ) -> None:
        """
        Changes the language of the application.

        :param language Literal["pt_BR", "en_US"]: Defaults to the last used language.

        :return: None.
        """

        if language == load_last_used_settings()[0]:
            return

        self.json_translations = translations[language]

        # update user settings
        save_last_used_settings("last_used_language", language=language)

        self.root.destroy()
        self.__init__(language=language)  # type: ignore

    def create_input_folder_entry(self) -> None:
        """
        Creates input folder entry and associated label and button.
        """
        json_widgets = self.json_translations["Widgets"]

        input_folder_label = ttk.Label(
            self.root, text=json_widgets["input_folder_label"], justify="left"
        )
        input_folder_label.grid(row=0, column=0, padx=5, pady=5)

        self.input_folder_entry = ttk.Entry(self.root, width=50)
        self.input_folder_entry.grid(row=0, column=1, padx=5, pady=5)

        browse_input_button = ttk.Button(
            self.root,
            text=json_widgets["browse_input_button"],
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

    def create_treeview(self, files: list[Path]) -> None:
        """
        Creates a treeview to display the files in the input folder.
        """
        json_widgets = self.json_translations["Widgets"]

        self.treeview.delete(*self.treeview.get_children())

        self.treeview.tag_configure("checked", image=self.checked_image)
        self.treeview.tag_configure("unchecked", image=self.unchecked_image)
        self.treeview.bind("<Button 1>", self.toggle_check)

        self.treeview.heading("#0", text="")
        self.treeview.column(
            "#0", width=50, minwidth=50, anchor="center", stretch=False
        )

        self.treeview.heading("#1", text=json_widgets["treeview_column1"])

        for file in files:
            name = file.name

            self.treeview.insert("", "end", tags="checked", values=(name,))

        self.treeview.grid(row=10, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        center_window(self.root)

    def toggle_check(self, event):
        """
        A function to toggle the check status of a row in the treeview widget.

        :param event (event): The event that triggered the function.

        :return: None
        """
        try:
            row_id = self.treeview.identify_row(event.y)
            tag = self.treeview.item(row_id, "tags")[0]
            tags = list(self.treeview.item(row_id, "tags"))
            tags.remove(tag)
            self.treeview.item(row_id, tags=tags)

            if tag == "checked":
                self.treeview.item(row_id, tags="unchecked")

            else:
                self.treeview.item(row_id, tags="checked")

        except IndexError:
            pass

    @abstractmethod
    def execute_function(self, function_name: str):
        """
        Abstract method to execute a function based on its name.

        :param function_name: The name of the function to execute.

        :return: list[Path] | None
        """
        json_messagebox = self.json_translations["MessageBox"]

        if not self.treeview.get_children():
            messagebox.showwarning(
                json_messagebox["warning"],
                message=json_messagebox["error_treeview_files_not_found"]
                + "\n"
                + json_messagebox["verify_button_not_clicked"],
            )
            return None

        input_folder = Path(self.input_folder_entry.get())

        input_files = []
        for row_id in self.treeview.get_children():
            tags = self.treeview.item(row_id, "tags")
            if "checked" in tags:
                input_files.append(
                    input_folder / self.treeview.item(row_id, "values")[0]
                )

        return input_files

    def on_closing(self) -> None:
        """
        Function to close the window.
        """
        sys.exit()


class VideoConverterApp(App):
    """
    This class is used to create a GUI application for
    converting video and audio files using ffmpeg.
    """

    def __init__(
        self, language: Literal["pt_BR", "en_US"] = load_last_used_settings()[0]
    ) -> None:
        """
        Constructor method for initializing the GUI window and setting
        up various elements within the window.
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

        center_window(self.root)

    def create_menu_bar(self) -> None:
        """
        Creates and configures the menu bar to change between apps.
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
        """
        # Destroy this window
        self.root.destroy()

        app = ChangeVideoAttributesApp()

        # Show the ChangeVideoTitleApp
        app.root.mainloop()

        # Show the main window above everything
        app.root.lift()

        app.root.focus()

    def create_output_folder_entry(self) -> None:
        """
        Create output folder entry widgets and place them in the root window.
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
        browse_output_button.grid(row=1, column=2, padx=5, pady=5)
        browse_output_button.bind(
            "<Button-1>", lambda event: self.browse_folder(self.output_folder_entry)
        )

    def create_input_extension_entry(self) -> None:
        """
        Creates an input extension entry and label in the GUI.
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
        """Create a button to verify the files in the input folder."""
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

    def execute_function(self, function_name: str) -> None:
        """
        Function to execute the selected function.
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
        """

        if not self.input_folder_entry.get() and not self.input_extension_entry.get():
            return
        if not self.input_folder_entry.get() or not self.input_extension_entry.get():
            return
        input_files = []
        for file in Path(self.input_folder_entry.get()).iterdir():
            if (
                file.suffix == self.input_extension_entry.get()
                and is_video_or_audio_file(file)
            ):
                input_files.append(file)

        self.create_treeview(input_files)

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


class ChangeVideoAttributesApp(App):
    """
    This class is used to create a GUI application for
    changing the title of video file to its filename.
    """

    def __init__(
        self, language: Literal["pt_BR", "en_US"] = load_last_used_settings()[0]
    ) -> None:
        """
        Constructor method for initializing the GUI window and setting
        up various elements within the window.
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

        center_window(self.root)

        self.root.focus_set()

    def create_menu_bar(self) -> None:
        """
        Creates and configures the menu bar to change between apps.
        """
        menu_bar, app_menu = super().create_menu_bar()

        app_menu.add_command(
            label=self.json_translations["Change Video Attributes"][
                "ChangeVideoAttributesApp_title"
            ],
            command=self.open_video_converter_app,
        )

        self.root.config(menu=menu_bar)

    def open_video_converter_app(self):
        """
        Opens a new window that allows the user to convert video files.
        """
        # Destroy this window
        self.root.destroy()

        app = VideoConverterApp()

        # Show the ChangeVideoTitleApp
        app.root.mainloop()

        # Show the main window above everything
        app.root.lift()

        app.root.focus()

    def create_verify_files_button(self):
        """
        Verifies the input folder and extension entries, creates a list of input files,
        and updates the treeview with the input files. Returns True if successful,
        or None if the input folder or extension entries are empty.
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

    def browse_folder(self, folder_entry: tk.Entry) -> None:
        """
        Function to browse the folder and update the folder_entry
        with the selected folder path. No parameters and no return type.
        """

        folder = filedialog.askdirectory(mustexist=True)
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder)

    def execute_function(
        self, function_name: Literal["change_title", "merge_video_to_subtitle"]
    ) -> bool:
        """
        Function to execute the selected function.
        """
        input_files = super().execute_function(function_name)

        if not input_files:
            return False

        input_files = [str(input_file) for input_file in input_files]

        video_adjuster = VideoAdjuster(input_files=input_files, master=self.root)

        if function_name == "change_title":
            video_adjuster.change_video_title_to_filename()

        elif function_name == "merge_video_to_subtitle":
            os.environ["FFMPEG_DIRECTORY"] = "C:\\Program Files\\ffmpeg"

            binaries = check()
            if not binaries:
                return False

            if os.name == "nt":
                # Configure the fonts for the subtitles
                configure(binaries)

            user_input = simpledialog.askstring(
                self.json_change_video_attributes_app["simple_dialog_title"],
                self.json_change_video_attributes_app["simple_dialog_text"],
            )

            if user_input:
                video_adjuster.merge_video_to_subtitle(subtitle_language=user_input)
            else:
                video_adjuster.merge_video_to_subtitle()

        return True

    def verify_files(self):
        """
        Verifies the input folder and extension entries, creates a list of input files,
        and updates the treeview with the input files. Returns True if successful,
        or None if the input folder or extension entries are empty.
        """
        if not self.input_folder_entry.get():
            return

        input_files = []
        for file in Path(self.input_folder_entry.get()).iterdir():
            if is_video_or_audio_file(file):
                input_files.append(file)

        self.create_treeview(input_files)

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


class ToolTip:
    """Creates a tooltip widget."""

    def __init__(self, widget, text: str):
        """Initializes the tooltip widget."""
        self.widget = widget
        self.text = text
        self.tool_tip = None

        def on_enter(event):
            """Creates a tooltip when the mouse hovers over the widget."""
            self.tool_tip = tk.Toplevel()
            self.tool_tip.overrideredirect(True)
            self.tool_tip.geometry(f"+{event.x_root+15}+{event.y_root+10}")

            label = tk.Label(self.tool_tip, text=self.text)
            label.pack()
            self.tool_tip.update()
            self.tool_tip.lift()

        def on_leave(event):
            """Closes the tooltip."""
            if self.tool_tip:
                self.tool_tip.destroy()

        self.widget.bind("<Enter>", on_enter)
        self.widget.bind("<Leave>", on_leave)


if __name__ == "__main__":
    window = VideoConverterApp()
    window.root.mainloop()
