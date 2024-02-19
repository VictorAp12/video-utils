"""
This module contains a class that creates a tooltip widget.
"""

import tkinter as tk


class ToolTip:
    """Creates a tooltip widget."""

    def __init__(self, widget: tk.Widget, text: str) -> None:
        """
        Initializes the tooltip widget.

        :param widget: The widget to attach the tooltip to.
        :param text: The text to display in the tooltip.

        :return: None.
        """
        self.widget = widget
        self.text = text
        self.tool_tip = None

        def on_enter(event: tk.Event) -> None:
            """
            Creates a tooltip when the mouse hovers over the widget.

            :param event (tk.Event): The event that triggered the function.

            :return: None.
            """
            self.tool_tip = tk.Toplevel()
            self.tool_tip.overrideredirect(True)
            self.tool_tip.geometry(f"+{event.x_root+15}+{event.y_root+10}")

            label = tk.Label(self.tool_tip, text=self.text)
            label.pack()
            self.tool_tip.update()

        def on_leave(event: tk.Event) -> None:  # pylint: disable=unused-argument
            """
            Closes the tooltip.

            :param event (tk.Event): The event that triggered the function.

            :return: None.
            """
            if self.tool_tip:
                self.tool_tip.destroy()

        self.widget.bind("<Enter>", on_enter)
        self.widget.bind("<Leave>", on_leave)
