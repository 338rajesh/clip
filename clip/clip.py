"""

    Command Line Interactive Parser

"""

import argparse
import tkinter as tk
from tkinter import ttk, filedialog


class SelectFile(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class SelectDir(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


class CLIParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument("-g", "--gui", action="store_true", help="Enable terminal")
        self.root = tk.Tk()
        self.root.title("Command Line Interactive Parser")
        self.entries = {}
        self.args = None

    def parse_args(self, args=None, namespace=None):
        ka, _ = self.parse_known_args(args, namespace)

        if not ka.gui:  # If GUI is not requested, parse arguments normally
            self.args = super().parse_args(args, namespace)
            self.args.__delattr__('gui')
            return self.args

        # If GUI is requested, create a GUI for supplying arguments
        for (idx, arg_info) in enumerate(self._actions):
            arg_dest_name = arg_info.dest
            if arg_dest_name in ('help', 'gui'):
                continue  # Skip the help and GUI argument

            arg_default = arg_info.default
            arg_help = arg_info.help or ""
            arg_choices = arg_info.choices
            arg_nargs = arg_info.nargs

            label = ttk.Label(self.root, text=f"{arg_dest_name}: {arg_help}")
            label.grid(row=idx, column=0, sticky=tk.W)

            # Handle boolean flags with checkboxes
            if isinstance(arg_info, argparse._StoreTrueAction):
                self.entries[arg_dest_name] = tk.BooleanVar(value=arg_default)
                check = ttk.Checkbutton(self.root, variable=self.entries[arg_dest_name])
                check.grid(row=idx, column=1, sticky=tk.W)

            # Handle dropdown with choices
            elif arg_choices is not None:
                self.entries[arg_dest_name] = tk.StringVar(value=arg_default)
                if arg_nargs == '+':  # Handle multiple selection case
                    listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE, exportselection=False)
                    for choice in arg_choices:
                        listbox.insert(tk.END, choice)
                    listbox.grid(row=idx, column=1, sticky=tk.W)
                    self.entries[arg_dest_name] = listbox
                else:
                    dropdown = ttk.Combobox(self.root, textvariable=self.entries[arg_dest_name], values=arg_choices)
                    dropdown.grid(row=idx, column=1, sticky=tk.W)

            # Handle file or folder input
            elif isinstance(arg_info, (SelectFile, SelectDir)):
                if isinstance(arg_info, SelectFile):
                    self.entries[arg_dest_name] = tk.StringVar(value=arg_default)
                    entry = ttk.Entry(self.root, textvariable=self.entries[arg_dest_name])
                    entry.grid(row=idx, column=1, sticky=tk.W)
                    button = ttk.Button(
                        self.root, text="Browse",
                        command=lambda arg_dst_name=arg_dest_name: self.select_file(arg_dst_name)
                    )
                    button.grid(row=idx, column=2, sticky=tk.W)
                elif isinstance(arg_info, SelectDir):
                    self.entries[arg_dest_name] = tk.StringVar(value=arg_default)
                    entry = ttk.Entry(self.root, textvariable=self.entries[arg_dest_name])
                    entry.grid(row=idx, column=1, sticky=tk.W)
                    button = ttk.Button(
                        self.root, text="Browse",
                        command=lambda arg_dst_name=arg_dest_name: self.select_dir(arg_dst_name)
                    )
                    button.grid(row=idx, column=2, sticky=tk.W)
            else:  # Handle regular string or numerical input
                self.entries[arg_dest_name] = tk.StringVar(value=arg_default)
                entry = ttk.Entry(self.root, textvariable=self.entries[arg_dest_name])
                entry.grid(row=idx, column=1, sticky=tk.W)

        submit_button = ttk.Button(self.root, text="Submit", command=self.submit)
        submit_button.grid(row=len(self._actions) + 1, column=0, columnspan=1)

        clear_button = ttk.Button(self.root, text="Clear", command=self.clear)
        clear_button.grid(row=len(self._actions) + 1, column=1, columnspan=1)

        close_button = ttk.Button(self.root, text="Close", command=self.root.destroy)
        close_button.grid(row=len(self._actions) + 1, column=2, columnspan=1)

        self.root.mainloop()

        return self.args

    def submit(self):
        args = {}
        for key, value in self.entries.items():
            if isinstance(value, tk.Listbox):  # Handle multiple selections
                selections = value.curselection()
                selected_values = [value.get(i) for i in selections]
                args[key] = selected_values
            elif isinstance(value, tk.BooleanVar):  # Handle Boolean
                args[key] = value.get()
            else:
                args[key] = value.get()

        self.args = argparse.Namespace(**args)
        self.root.destroy()

    def clear(self):
        for entry in self.entries.values():
            if isinstance(entry, tk.StringVar):
                entry.set("")
            elif isinstance(entry, tk.BooleanVar):
                entry.set(False)
            elif isinstance(entry, tk.Listbox):
                entry.selection_clear(0, tk.END)

    def select_file(self, arg_name):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.entries[arg_name].set(file_path)

    def select_dir(self, arg_name):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.entries[arg_name].set(folder_path)
