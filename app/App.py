"""
This module contains the base class for the application window.
"""
import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Literal, Tuple
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import webbrowser

from ttkthemes import ThemedStyle
from PIL import ImageTk, Image

from utils.json_utils import (
    load_last_used_settings,
    save_last_used_settings,
    load_translations,
)

from utils.window_utils import center_window

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
        language: Literal["pt_BR", "en_US"],
    ) -> None:
        """
        Constructor method for initializing the GUI window and setting
        up various elements within the window.

        :param title: str, The title of the window.
        :param language: Literal["pt_BR", "en_US"], The language to be used in the window.

        :return: None.
        """
        self.json_translations = translations[language]

        self.root = tk.Tk()

        self.style = ThemedStyle(self.root)
        self.style.set_theme(load_last_used_settings()[1])
        self.root.configure(bg=self.style.lookup("TLabel", "background"))
        self.root.title(title)
        self.root.iconbitmap("assets/video-util.ico")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # make the window responsive
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.create_menu_bar()

        self.create_input_folder_entry()

        self.selected_files = 0
        self.setup_treeview()

    @abstractmethod
    def create_menu_bar(self) -> Tuple[tk.Menu, tk.Menu]:
        """
        Abstract method to create the menu bar, to change between apps.

        :return: Tuple[tk.Menu, tk.Menu], The menu bar and the app menu.
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

        :param theme Literal["default", "black"]: Defaults to the last used theme.

        :return: None.
        """
        if theme == load_last_used_settings()[1]:
            return

        # print(self.style.get_themes())

        self.style.set_theme(theme)
        self.root.config(bg=self.style.lookup("TLabel", "background"))

        center_window(self.root)

        # update user settings
        save_last_used_settings(
            "last_used_theme",
            theme=theme,
            used_app=self.__class__.__name__,  # type: ignore
        )

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
        save_last_used_settings(
            "last_used_language",
            language=language,
            used_app=self.__class__.__name__,  # type: ignore
        )

        self.root.destroy()
        self.__init__(language=language)  # type: ignore

    def create_input_folder_entry(self) -> None:
        """
        Creates input folder entry and associated label and button.

        :return: None.
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
        browse_input_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        browse_input_button.bind(
            "<Button-1>", lambda event: self.browse_folder(self.input_folder_entry)
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

    def open_folder(self) -> None:
        """
        Opens the input folder.

        :return: None.
        """
        if self.input_folder_entry.get() == "":
            return

        os.startfile(self.input_folder_entry.get())

    def setup_treeview(self) -> None:
        """
        Sets up the treeview widget.

        :return: None.
        """
        # table
        self.treeview = ttk.Treeview(self.root, columns=(1,))

        # table scrollbar
        self.scrollbar = ttk.Scrollbar(self.root, command=self.treeview.yview)

        # treeview images
        self.checked_image = ImageTk.PhotoImage(
            Image.open("assets/checked-checkbox.png").resize((20, 20))
        )
        self.unchecked_image = ImageTk.PhotoImage(
            Image.open("assets/blank-check-box.png").resize((20, 20))
        )

        # select all items from treeview
        self.select_all = tk.BooleanVar()

        # select all button
        self.select_all_button = ttk.Button(
            self.root,
            text=self.json_translations["Widgets"]["unselect_all_button"],
            command=self.select_all_rows,
        )

        # open folder button
        self.open_folder_button = ttk.Button(
            self.root,
            text=self.json_translations["Widgets"]["open_folder_button"],
            command=self.open_folder,
        )

        # found files
        self.found_files_label = ttk.Label(self.root, text="")

        # selected files
        self.selected_files_label = ttk.Label(self.root, text="")

    def create_treeview(self, files: List[Path]) -> None:
        """
        Creates a treeview to display the files in the input folder.

        :param files: list[Path], The list of files in the input folder.

        :return: None.
        """
        json_widgets = self.json_translations["Widgets"]

        self.treeview.delete(*self.treeview.get_children())

        self.treeview.tag_configure("checked", image=self.checked_image)
        self.treeview.tag_configure("unchecked", image=self.unchecked_image)
        self.treeview.bind("<Button 1>", self.toggle_check)

        self.treeview.heading("#0", text="", command=self.select_all_rows)
        self.treeview.column(
            "#0", width=50, minwidth=50, anchor="center", stretch=False
        )

        self.treeview.heading("#1", text=json_widgets["treeview_column1"])

        self.select_all.set(True)

        for file in files:
            name = file.name
            self.treeview.insert("", "end", tags="checked", values=(name,))

        self.scrollbar.grid(row=10, column=3, padx=5, pady=5, sticky="ns")

        self.treeview.configure(yscrollcommand=self.scrollbar.set)

        self.treeview.grid(row=10, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.select_all_button.grid(row=11, column=0, padx=5, pady=5)

        self.open_folder_button.grid(row=11, column=1, padx=5, pady=5, sticky="w")

        self.found_files_label.grid(row=11, column=1, padx=5, pady=5, sticky="e")

        self.selected_files = len(files)

        self.found_files_label.config(
            text=json_widgets["found_files_label"].format(count=self.selected_files)
        )

        self.selected_files_label.grid(
            row=11, column=2, columnspan=3, padx=5, pady=5, sticky="w"
        )
        self.selected_files_label.config(
            text=json_widgets["selected_files_label"].format(count=len(files))
        )

        center_window(self.root)

    def toggle_check(self, event: tk.Event) -> None:
        """
        A function to toggle the check status of a row in the treeview widget.

        :param event (tk.Event): The event that triggered the function.

        :return: None.
        """
        try:
            row_id = self.treeview.identify_row(event.y)
            tag = self.treeview.item(row_id, "tags")[0]
            tags = list(self.treeview.item(row_id, "tags"))
            tags.remove(tag)
            self.treeview.item(row_id, tags=tags)

            if tag == "checked":
                self.treeview.item(row_id, tags="unchecked")

                self.selected_files -= 1
                self.selected_files_label.config(
                    text=self.json_translations["Widgets"][
                        "selected_files_label"
                    ].format(count=self.selected_files)
                )

            else:
                self.treeview.item(row_id, tags="checked")

                self.selected_files += 1
                self.selected_files_label.config(
                    text=self.json_translations["Widgets"][
                        "selected_files_label"
                    ].format(count=self.selected_files)
                )

        except IndexError:
            pass

    def select_all_rows(self) -> None:
        """
        A function to select all rows in the treeview widget.

        :return: None.
        """
        if self.select_all.get():
            for row_id in self.treeview.get_children():
                self.treeview.item(row_id, tags="unchecked")
            self.select_all.set(False)
            self.select_all_button.config(
                text=self.json_translations["Widgets"]["select_all_button"]
            )

            self.selected_files = 0
            self.selected_files_label.config(
                text=self.json_translations["Widgets"]["selected_files_label"].format(
                    count=self.selected_files
                )
            )

        else:
            for row_id in self.treeview.get_children():
                self.treeview.item(row_id, tags="checked")
            self.select_all.set(True)
            self.select_all_button.config(
                text=self.json_translations["Widgets"]["unselect_all_button"]
            )

            self.selected_files = len(self.treeview.get_children())
            self.selected_files_label.config(
                text=self.json_translations["Widgets"]["selected_files_label"].format(
                    count=self.selected_files
                )
            )

    @abstractmethod
    def execute_function(self, function_name: str) -> List[Path] | None:
        """
        Abstract method to execute a function based on its name.

        :param function_name: The name of the function to execute.

        :raises tk.messagebox warning: If the treeview is empty.

        :return: List[Path] | None.
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

        :return: None.
        """
        sys.exit()
