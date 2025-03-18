# convert_OCT_files.py
# Converting OCT files to tif and avi files
# Made by Brandon Anderson, University of Pennsylvania

# For this macro to work, you need the following files:
# OCT reader plugin - ImageJ macro
# OCT averager plugin - ImageJ macro

import os
import psutil       # For opening ImageJ
import subprocess   # For opening ImageJ
import time         # For opening ImageJ and tracking progress
import pyautogui    # For opening and manipulating ImageJ
import shutil       # For deleting directories
import pygetwindow as gw    #for making ImageJ an active window
import tkinter as tk    # For making dialog boxes
import tkinter.messagebox as messagebox
from tkinter import ttk, filedialog, messagebox, simpledialog
import inspect      # For error messages
import ast          # For converting variables in text file to proper variable formats
import sys          # For exiting dialog boxes
import pyscreeze
pyscreeze.USE_IMAGE_NOT_FOUND_EXCEPTION = False

# You will need to make sure to download psutil, pyautogui, and pygetwindow as they don't come with base Python

confidence = 0.95
# For updates, look for # Update:
# Update: volume scan
# Update: change peripheral folder checkbox to entry box
# Update: custom defaults 
# Update: extra options dialog box
# Update: other
# Update: handle multiple experiments from one date

# If update done, then it is finished with a "- done"


# Defining the location of the Open_OCT_file_preferences.txt
script_directory = os.path.dirname(os.path.abspath(__file__))
preference_file_name = "Open_OCT_file_preferences.txt"
preference_file = os.path.join(script_directory, preference_file_name)



def delete_directory(directory_path):
    try:
        shutil.rmtree(directory_path)
        #print(f"Directory '{directory_path}' successfully deleted.")
    except FileNotFoundError:
        pass
    except OSError as e:
        print(f"Error occurred while deleting directory '{directory_path}': {e}")



def show_error_message(message, root=None):
    frame = inspect.currentframe().f_back   # Identifying the line number that called this function
    line_number = frame.f_lineno

    if root is None:
        root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", f"Error on line number {line_number}\n\n{message}")


def wait_to_appear(image_file, max_wait_time):      # This looks for dialog boxes or buttons to appear, and won't let the script continue until it is found or if the time reaches the max wait time
    search_start_time = time.time()
    while time.time() - search_start_time < max_wait_time:
        if pyautogui.locateOnScreen(image_file, confidence=confidence):
            time.sleep(0.5)
            return True
        time.sleep(0.5)
    time.sleep(0.5)
    return False


def center_dialog_box(window):      # Moves the dialog box to the center of the screen
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x_coordinate = (screen_width - width) // 2
    y_coordinate = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")


# First we're going to get the details from the preference file, or, if it isn't there, it will make it
def manage_preferences_file():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_name = "Open_OCT_file_preferences.txt"
    file_path = os.path.join(script_directory, file_name)

    if os.path.exists(file_path):
        # File exists, read its contents
        with open(file_path, 'r') as file:
            preferences_data = file.readlines()

        # Process the preferences_data and extract variables
        variables = {}
        for line in preferences_data:
            variable_name, variable_value = parse_variable(line)
            if variable_name:
                variables[variable_name] = variable_value

        return variables

    else:
        # File doesn't exist, create an empty file
        with open(file_path, 'w'):
            pass
            #file.write(default_content)
        print("Creating preferences file")

def parse_variable(line):
    # Check if the line contains the variable name and value
    if "=" in line:
        # Split the line at the "=" sign and remove any leading/trailing whitespace
        variable_name, variable_value = line.split("=", 1)
        return variable_name.strip(), variable_value.strip()
    else:
        return None, None



# Call the function to get the variables from the txt file
try:
    preferences_variables = manage_preferences_file()
    if preferences_variables is None:
        preferences_variables = {}
except Exception as e:
    show_error_message(f"There is a problem with the preferences file:\n\n{e}")


def retrieve_variables(preferences_variables, key):
    try:
        return preferences_variables[key]
    except KeyError:        # If these variables don't exist in the document, here are the defaults
        if key == "preset_options_dict":
            return {"Previous settings": {"default_locations": ["horizontal, vertical", "temporal", "nasal", "delete, superior", "delete, inferior"], "default_scan_type": ["radial", "linear", "linear", "radial", "radial"], "default_subfolder": [False, True, True, True, True], "default_min_contrast": 25, "default_max_contrast": 215, "default_crop_amount": 480, "default_subfolder_name": "Peripheral images", "od_os_checkbox_boolean": True, "imagej_checkbox_boolean": False, "unaveraged_checkbox_boolean": False}}



preset_options_dict = retrieve_variables(preferences_variables, 'preset_options_dict')
if type(preset_options_dict) == str:
    preset_options_dict = ast.literal_eval(preset_options_dict)


image_location_list = preset_options_dict["Previous settings"]["default_locations"]
od_before_os = preset_options_dict["Previous settings"]["od_os_checkbox_boolean"]
scan_modes = preset_options_dict["Previous settings"]["default_scan_type"]
subfolder_entry = preset_options_dict["Previous settings"]["default_subfolder"]
subfolder_name = preset_options_dict["Previous settings"]["default_subfolder_name"]
unaveraged_images = preset_options_dict["Previous settings"]["unaveraged_checkbox_boolean"]
min_contrast = preset_options_dict["Previous settings"]["default_min_contrast"]
max_contrast = preset_options_dict["Previous settings"]["default_max_contrast"]
crop_amount = preset_options_dict["Previous settings"]["default_crop_amount"]





#This first dialog box checks to see what images were taken and in which order
def first_dialog_box():
    row_num = 1 # Starting row number for entry and checkbox widgets

    def add_entry_row(mode="linear", subfolder_mode=False):
        nonlocal row_num
        entry_row = tk.Entry(dialog_frame, width=50)
        entry_row.grid(row=row_num, column=0, sticky='w')
        entry_rows.append(entry_row)

        linear_var = tk.BooleanVar(value=(mode == "linear"))
        radial_var = tk.BooleanVar(value=(mode == "radial"))
        volume_var = tk.BooleanVar(value=(mode == "volume"))
        linear_vars.append(linear_var)
        radial_vars.append(radial_var)
        volume_vars.append(volume_var)

        checkbox_linear = tk.Checkbutton(dialog_frame, variable=linear_var, command=lambda i=len(linear_vars)-1: select_linear(i))
        checkbox_linear.grid(row=row_num, column=1, sticky='s')
        checkbox_linears.append(checkbox_linear)

        checkbox_radial = tk.Checkbutton(dialog_frame, variable=radial_var, command=lambda i=len(radial_vars)-1: select_radial(i))
        checkbox_radial.grid(row=row_num, column=2, sticky='s')
        checkbox_radials.append(checkbox_radial)
        
        checkbox_volume = tk.Checkbutton(dialog_frame, variable=volume_var, command=lambda i=len(volume_vars)-1: select_volume(i))
        checkbox_volume.grid(row=row_num, column=3, sticky='s')
        checkbox_volumes.append(checkbox_volume)



        # Adding subfolder checkboxes
        subfolder_var = tk.BooleanVar(value=subfolder_mode)
        checkbox_subfolder = tk.Checkbutton(dialog_frame, variable=subfolder_var)
        checkbox_subfolder.grid(row=row_num, column=4, sticky='s')
        checkbox_subfolders.append(checkbox_subfolder)
        subfolder_vars.append(subfolder_var)
        # Update: change peripheral folder checkbox to entry box

        # Change dialog box size to fit everything properly
        window.update_idletasks()
        window.geometry("")
        row_num += 1

    def remove_entry_row():
        if entry_rows:
            entry_row = entry_rows.pop()
            entry_row.destroy()

            linear_var = linear_vars.pop()
            radial_var = radial_vars.pop()
            volume_var = volume_vars.pop()

            checkbox_linear = checkbox_linears.pop()
            checkbox_linear.destroy()

            checkbox_radial = checkbox_radials.pop()
            checkbox_radial.destroy()

            checkbox_volume = checkbox_volumes.pop()
            checkbox_volume.destroy()



            # Update: change peripheral folder checkbox to entry box
            checkbox_subfolder = checkbox_subfolders.pop()
            checkbox_subfolder.destroy()
            subfolder_var = subfolder_vars.pop()
        
        # Change dialog box size to fit everything properly
        window.update_idletasks()
        window.geometry("")


    def select_linear(index):
        linear_vars[index].set(True)
        radial_vars[index].set(False)
        volume_vars[index].set(False)


    def select_radial(index):
        linear_vars[index].set(False)
        radial_vars[index].set(True)
        volume_vars[index].set(False)

    def select_volume(index):
        linear_vars[index].set(False)
        radial_vars[index].set(False)
        volume_vars[index].set(True)


    def set_new_preset(preset_option):
        # Update: custom defaults - need to define at function that sees user settings (much earlier in code)
        default_locations = preset_options_dict[preset_option]["default_locations"]
        default_scan_type = preset_options_dict[preset_option]["default_scan_type"]
        default_subfolder = preset_options_dict[preset_option]["default_subfolder"]
        default_min_contrast = preset_options_dict[preset_option]["default_min_contrast"]
        default_max_contrast = preset_options_dict[preset_option]["default_max_contrast"]
        default_crop_amount = preset_options_dict[preset_option]["default_crop_amount"]
        default_subfolder_name = preset_options_dict[preset_option]["default_subfolder_name"]
        od_os_checkbox_boolean = preset_options_dict[preset_option]["od_os_checkbox_boolean"]
        imagej_checkbox_boolean = preset_options_dict[preset_option]["imagej_checkbox_boolean"]
        unaveraged_checkbox_boolean = preset_options_dict[preset_option]["unaveraged_checkbox_boolean"]

        current_row_count = len(entry_rows)
        
        # If the current number of rows is less than five, add new rows
        while current_row_count < len(default_locations):
            add_entry_row()
            current_row_count += 1

        # If the current number of rows is more than five, remove excess rows
        while current_row_count > len(default_locations):
            remove_entry_row()
            current_row_count -= 1

        # Update the content of the first column with default values
        for i, default_value in enumerate(default_locations):
            entry_row = entry_rows[i]
            entry_row.delete(0, tk.END)  # Clear the current content
            entry_row.insert(tk.END, default_value)  # Set the default value

        # Set the checkboxes in the second and third columns based on default
        for i, mode in enumerate(default_scan_type):
            if mode == "radial": select_radial(i)
            elif mode == "linear": select_linear(i)
            elif mode == "volume": select_volume(i)


        # Set the checkboxes in the fifth column based on default
        # Update: change peripheral folder checkbox to entry box
        for i, default_value in enumerate(default_subfolder):
            if default_value == True:
                subfolder_vars[i].set(True)
            else:
                subfolder_vars[i].set(False)

        od_os_checkbox_var.set(od_os_checkbox_boolean)
        imagej_checkbox_var.set(imagej_checkbox_boolean)
        # Update: extra options dialog box - move this checkbox to an option elsewhere
        unaveraged_checkbox_var.set(unaveraged_checkbox_boolean)

        # Update: change peripheral folder checkbox to entry box - change the below to a report on number of subfolders to be made
        subfolder_name_entry.delete(0, tk.END)
        subfolder_name_entry.insert(0, default_subfolder_name)

        min_contrast_entry.delete(0, tk.END)
        min_contrast_entry.insert(0, str(default_min_contrast))
        max_contrast_entry.delete(0, tk.END)
        max_contrast_entry.insert(0, str(default_max_contrast))
        
        crop_amount_entry.delete(0, tk.END)
        crop_amount_entry.insert(0, default_crop_amount)

    def update_dropdown(new_selected_preset):
        # Update the preset dropdown menu to reflect changes in preset_options_dict when a new preset is created or deleted
        menu = preset_options_dropdown_menu['menu']
        menu.delete(0, 'end')  # Clear the existing menu options

        # Add updated options from preset_options_dict
        for option in preset_options_dict.keys():
            menu.add_command(
                label=option,
                command=lambda value=option: (selected_preset.set(value), set_new_preset(value))
            )

        # Update the displayed value
        selected_preset.set(new_selected_preset)


    def create_new_preset():
        # Gets the current information
        image_location_list = []
        scan_modes = []
        subfolder_entry = []

        for i, entry_row in enumerate(entry_rows):
            text = entry_row.get()
            if text:
                image_location_list.append(text)

            if linear_vars[i].get():
                scan_modes.append("linear")
            elif radial_vars[i].get():
                scan_modes.append("radial")
            elif volume_vars[i].get():
                scan_modes.append("volume")
            else:
                scan_modes.append("")

            subfolder_entry.append(subfolder_vars[i].get())

        od_before_os = od_os_checkbox_var.get()
        subfolder_name = subfolder_name_entry.get()
        unaveraged_images = unaveraged_checkbox_var.get()
        min_contrast = min_contrast_var.get()
        max_contrast = max_contrast_var.get()
        crop_amount = crop_amount_var.get()

        # Asks the user to give the preset a new name
        new_preset_name = simpledialog.askstring("Preset", "New preset name:")

        if new_preset_name:
            new_preset_details = {
                "default_locations": image_location_list,
                "default_scan_type": scan_modes,
                "default_subfolder": subfolder_entry,
                "default_min_contrast": min_contrast,
                "default_max_contrast": max_contrast,
                "default_crop_amount": crop_amount,
                "default_subfolder_name": subfolder_name,
                "od_os_checkbox_boolean": od_before_os,
                "imagej_checkbox_boolean": False,
                "unaveraged_checkbox_boolean": unaveraged_images
            }
            preset_options_dict[new_preset_name] = new_preset_details
            
            # Read the preference txt file and replace the line
            with open(preference_file, 'r') as file:
                lines = file.readlines()

            # Replace the preset_options_dict line
            for i, line in enumerate(lines):
                if line.strip().startswith("preset_options_dict"):
                    lines[i] = f"preset_options_dict = {preset_options_dict}" + "\n"
                    break

            # Write the modified lines back to the file
            with open(preference_file, 'w') as file:
                file.writelines(lines)

            # Update the dropdown menu with the new preset
            update_dropdown(new_preset_name)

            print(f"Created {new_preset_name}")

    def delete_preset():
        current_preset = selected_preset.get()
        if current_preset != "Previous settings":
            del preset_options_dict[current_preset]

            # Read the preference txt file and replace the line
            with open(preference_file, 'r') as file:
                lines = file.readlines()

            # Replace the preset_options_dict line
            for i, line in enumerate(lines):
                if line.strip().startswith("preset_options_dict"):
                    lines[i] = f"preset_options_dict = {preset_options_dict}" + "\n"
                    break

            # Write the modified lines back to the file
            with open(preference_file, 'w') as file:
                file.writelines(lines)

            # Update the dropdown menu with the new preset
            update_dropdown("")

            print(f"Deleted {current_preset}")

    def confirm(event=None):
        global image_location_list, od_before_os, scan_modes, subfolder_entry, subfolder_name, unaveraged_images, min_contrast, max_contrast, crop_amount
        
        image_location_list = []
        scan_modes = []
        subfolder_entry = []

        for i, entry_row in enumerate(entry_rows):
            text = entry_row.get()
            if text:
                image_location_list.append(text)

            if linear_vars[i].get():
                scan_modes.append("linear")
            elif radial_vars[i].get():
                scan_modes.append("radial")
            elif volume_vars[i].get():
                scan_modes.append("volume")
            else:
                scan_modes.append("")

            subfolder_entry.append(subfolder_vars[i].get())
            # Update: change peripheral folder checkbox to entry box


        od_before_os = od_os_checkbox_var.get()
        # Update: extra options dialog box - change line:
        imageJ_location_reenter = imagej_checkbox_var.get()
        # Update: change peripheral folder checkbox to entry box:
        subfolder_name = subfolder_name_entry.get()
        unaveraged_images = unaveraged_checkbox_var.get()
        min_contrast = min_contrast_var.get()
        max_contrast = max_contrast_var.get()
        crop_amount = crop_amount_var.get()


        window.destroy()
        window.master.destroy()

        preset_options_dict["Previous settings"]["default_locations"] = image_location_list
        preset_options_dict["Previous settings"]["default_scan_type"] = scan_modes
        preset_options_dict["Previous settings"]["default_subfolder"] = subfolder_entry
        preset_options_dict["Previous settings"]["default_min_contrast"] = min_contrast
        preset_options_dict["Previous settings"]["default_max_contrast"] = max_contrast
        preset_options_dict["Previous settings"]["default_crop_amount"] = crop_amount
        preset_options_dict["Previous settings"]["default_subfolder_name"] = subfolder_name
        preset_options_dict["Previous settings"]["od_os_checkbox_boolean"] = od_before_os
        preset_options_dict["Previous settings"]["imagej_checkbox_boolean"] = False
        preset_options_dict["Previous settings"]["unaveraged_checkbox_boolean"] = unaveraged_images

        # Removing variables that will be replaced
        with open(preference_file, 'r') as file:
            file_content = file.read()
        file_content = file_content.replace("\n\n\n", "\n") # Making sure we're not just adding a ton of extra lines over time
        variables_to_replace = [
            "preset_options_dict",
            "image_location_list",
            "od_before_os",
            "scan_modes",
            "subfolder_entry",
            "subfolder_name",
            "unaveraged_images",
            "min_contrast",
            "max_contrast",
            "crop_amount",
        ]
        lines_not_to_be_replaced = [line for line in file_content.splitlines() if not any(line.startswith(variable) for variable in variables_to_replace)]
        if imageJ_location_reenter == True:
            # Update: extra options dialog box - probably move this to wherever it is
            shortened_lines = []
            for i in lines_not_to_be_replaced:
                if not (i.startswith("screenshot_directory") or i.startswith("macro_location") or i.startswith("imagej_location")):
                    shortened_lines.append(i)
            lines_not_to_be_replaced = shortened_lines

        # Saving the user's inputs for future uses
        with open(preference_file, 'w') as file:
            file.write('\n'.join(lines_not_to_be_replaced))
            file.write(f"\npreset_options_dict = {preset_options_dict}")



    def on_dialog_close(event=None):
        window.master.destroy()
        exit()



    window = tk.Toplevel()
    window.title("Image settings")
    window.protocol("WM_DELETE_WINDOW", on_dialog_close)

    instruction_text = "Please enter the order that the images were taken in and what scan mode was used. These will be used for the file name. If you enter 'delete' for any location those images will be deleted. If radial scans are used, in the location box separate out the different images with a comma and space (i.e. angle0, angle90). The 'linear' mode also works for annular scans."
    instructions_label = tk.Label(window, text= instruction_text, wraplength=475, justify='left')
    instructions_label.grid(padx=10, sticky='w')

    dialog_frame = tk.Frame(window)
    dialog_frame.grid(padx=10, pady=10)

    entry_rows = []
    linear_vars = []
    radial_vars = []
    volume_vars = []
    checkbox_linears = []
    checkbox_radials = []
    checkbox_volumes = []
    subfolder_vars = []
    checkbox_subfolders = []


    # Adding  labels at the top of the columns
    label_location = tk.Label(dialog_frame, text="location")
    label_location.grid(row=0, column=0)
    label_linear = tk.Label(dialog_frame, text="linear")
    label_linear.grid(row=0, column=1)
    label_radial = tk.Label(dialog_frame, text="radial")
    label_radial.grid(row=0, column=2)
    label_volume = tk.Label(dialog_frame, text="volume")
    label_volume.grid(row=0, column=3)
    label_subfolder = tk.Label(dialog_frame, text="subfolder")
    label_subfolder.grid(row=0, column=4)



    # Adding existing entry rows with their corresponding checkboxes
    for i, location in enumerate(image_location_list):
        mode = scan_modes[i] if scan_modes and i < len(scan_modes) else "linear"    # Grabs the scan mode from scan_mode list, but if none available, default is "linear"
        # Update: change peripheral folder checkbox to entry box - this is making a checkbox
        subfolder_mode = subfolder_entry[i] if subfolder_entry and i < len(subfolder_entry) else False
        add_entry_row(mode, subfolder_mode)
        entry_row = entry_rows[-1]
        entry_row.insert(tk.END, location)




    row_num += 1
    button_frame = tk.Frame(window)
    button_frame.grid(row=row_num)
    add_button = tk.Button(button_frame, text="+", command=add_entry_row)
    add_button.pack(side='right')
    remove_button = tk.Button(button_frame, text="-", command=remove_entry_row)
    remove_button.pack(side='left')
    row_num += 1


    od_os_checkbox_var = tk.BooleanVar(value=od_before_os)
    od_os_checkbox = tk.Checkbutton(window, text="OD eyes were imaged before OS eyes", variable=od_os_checkbox_var)
    od_os_checkbox.grid(row=row_num, padx=10, sticky='w')
    row_num += 1

    # Update: custom defaults - make this part of a separate dialog box (or honestly make it a button)
    imagej_checkbox_var = tk.BooleanVar(value=False)
    imagej_checkbox = tk.Checkbutton(window, text="Re-enter ImageJ file location", variable=imagej_checkbox_var)
    imagej_checkbox.grid(padx=10, sticky='w')
    row_num += 1

    unaveraged_checkbox_var = tk.BooleanVar(value=unaveraged_images)
    unaveraged_checkbox = tk.Checkbutton(window, text="Save a copy of the unaveraged images", variable=unaveraged_checkbox_var)
    unaveraged_checkbox.grid(row=row_num, padx=10, sticky='w')
    row_num += 1
    

    # Getting user input on subfolder name
    # Update: change peripheral folder checkbox to entry box - replace with text that says how many subfolders will be made
    subfolder_frame = tk.Frame(window)
    subfolder_frame.grid(row=row_num, column=0, sticky='w', padx=10)  # Align to the left
    subfolder_name_var = tk.StringVar()
    subfolder_name_var.set(subfolder_name)
    subfolder_name_label = tk.Label(subfolder_frame, text="Subfolder name:")
    subfolder_name_label.pack(side='left')
    subfolder_name_entry = tk.Entry(subfolder_frame, textvariable=subfolder_name_var)
    subfolder_name_entry.pack(side='right')
    row_num += 1

    # Getting user input on contrast values (min and max) (0 and 255 are the ranges, 25 and 215 are recommended)
    contrast_frame = tk.Frame(window)
    contrast_frame.grid(row=row_num, column=0, sticky='w', padx=10)
    min_contrast_var = tk.StringVar()
    max_contrast_var = tk.StringVar()
    global min_contrast, max_contrast
    min_contrast_var.set(min_contrast)
    max_contrast_var.set(max_contrast)
    contrast_label = tk.Label(contrast_frame, text="Min and max contrast (ranges from 0 to 255): ")
    contrast_label.pack(side='left')
    min_contrast_entry = tk.Entry(contrast_frame, textvariable=min_contrast_var, width=6)
    max_contrast_entry = tk.Entry(contrast_frame, textvariable=max_contrast_var, width=6)
    min_contrast_entry.pack(side="left")
    max_contrast_entry.pack(side="right")
    row_num += 1

    # Getting user input on cropping
    crop_amount_frame = tk.Frame(window)
    crop_amount_frame.grid(row=row_num, column=0, sticky='w', padx=10)
    crop_amount_var = tk.StringVar()
    crop_amount_var.set(crop_amount)
    crop_label = tk.Label(crop_amount_frame, text="Vertically crop around the retina (recommend: 480 max: 1577): ")
    crop_label.grid(row=0, column=0)
    crop_amount_entry = tk.Entry(crop_amount_frame, textvariable=crop_amount_var, width=6)
    crop_amount_entry.grid(row=0, column=1)
    crop_unit_label = tk.Label(crop_amount_frame, text="µm")
    crop_unit_label.grid(row=0, column=2)
    row_num += 1

    # Creating preset setting dropdown menu
    presets_frame = tk.Frame(window)
    presets_frame.grid(row=row_num, column=0, sticky='w', padx=10)
    preset_label = tk.Label(presets_frame, text = "Preset options: ")
    preset_label.grid(row=0, column=0)
    selected_preset = tk.StringVar(value="Previous settings")
    preset_options_dropdown_menu = ttk.OptionMenu(
        presets_frame,
        selected_preset,
        selected_preset.get(),
        *preset_options_dict.keys(),
        command=lambda _: set_new_preset(selected_preset.get())
    )
    preset_options_dropdown_menu.grid(row=0, column=1)
    create_preset_button = tk.Button(presets_frame, text="Create preset", command=create_new_preset)
    create_preset_button.grid(row=0, column=2)
    delete_preset_button = tk.Button(presets_frame, text="Delete preset", command=delete_preset)
    delete_preset_button.grid(row=0, column=3)


    # Creating "Confirm" button at the bottom of the screen
    # Update: custom defaults - include button "Options"
    button_frame = tk.Frame(window)
    button_frame.grid()
    confirm_button = tk.Button(button_frame, text="Confirm", command=confirm)
    confirm_button.pack(pady=10, padx=10)



    window.bind("<Escape>", on_dialog_close)
    window.bind("<Return>", confirm)

    window.master.attributes("-alpha", 0)  # Set window opacity to 0 to make it invisible
    window.transient(window.master)
    window.grab_set()

    # Center the window on the screen
    window.after(1, lambda: center_dialog_box(window))

    window.mainloop()

# Starting up the initial dialog box
first_dialog_box()


print("image_location_list:", image_location_list)
print("od_before_os:", od_before_os)
print("unaveraged_images:", unaveraged_images)
print("scan_modes:", scan_modes)
# Update: change peripheral folder checkbox to entry box - this should be a list, not a boolean
print("subfolder_entry:", subfolder_entry)
print("subfolder_name:", subfolder_name)
print("min_contrast:", min_contrast)
print("max_contrast:", max_contrast)
print("crop_amount:", crop_amount)


def remove_underscores(list):       # This needs to be done because I count underscores later and I can't have the user adding them. I'll replace them later.
    for i, item in enumerate(list):
        list[i] = item.replace("_", "underscore")

underscore_list = [image_location_list] # Previously also had horizontal_image_list, vertical_image_list. Leaving as is in case need to clean any other list
for list in underscore_list:
    remove_underscores(list)


images_to_put_into_subfolder = []
# Update: change peripheral folder checkbox to entry box - need to make a tuplet to include what subfolder to be in
for i, image_type in enumerate(image_location_list):
    if subfolder_entry[i] is True:
        images_to_put_into_subfolder.append(image_type)



#SELECTING THE DIRECTORY
# Create the Tkinter root window
# Update: automatically select file directory
root = tk.Tk()
root.withdraw()  # Hide the root window

# Prompt the user to select a directory
image_directory = filedialog.askdirectory()

# Check if the user selected a directory or canceled the dialog
if image_directory:
    print("Selected directory:", image_directory)
else:
    print("Directory selection canceled")
    exit()


# Deleting all the directories previously made by this script if the user decides to run the script again in the same folder
# This is mainly for development to test the script
# Update: handle multiple experiments from one date - as is it will delete the final products if you run it twice on the same date for differenct experiments
delete_directory(os.path.join(image_directory, "averaged_images"))
delete_directory(os.path.join(image_directory, "cropped_tif_images"))
delete_directory(os.path.join(image_directory, "images_to_be_averaged"))
delete_directory(os.path.join(image_directory, "individual_sequence_images"))
delete_directory(os.path.join(image_directory, "unaveraged_images"))
delete_directory(os.path.join(image_directory, "initial_tif_images"))
delete_directory(os.path.join(image_directory, "volume_scans"))
if os.path.exists(os.path.join(image_directory, "Annotated_list_of_images.txt")):
    os.remove(os.path.join(image_directory, "Annotated_list_of_images.txt"))
if os.path.exists(os.path.join(image_directory, "Annotated_list_of_volume_scans.txt")):
    os.remove(os.path.join(image_directory, "Annotated_list_of_volume_scans.txt"))
imagej_settings_file = os.path.join(image_directory, "ImageJ_settings.txt")
if os.path.exists(imagej_settings_file):
    os.remove(imagej_settings_file)


# Saving the crop, min and max values so that ImageJ can access them
with open(imagej_settings_file, "w") as file:
    file.write(f"{crop_amount}\n{min_contrast}\n{max_contrast}\n")


# PUTTING FILE NAMES TOGETHER IN LIST
# Retrieve all file names in the directory
fileNames = [file for file in os.listdir(image_directory) if os.path.isfile(os.path.join(image_directory, file))]

# Update: volume scan - removed <and name.split("_")[2] != "V">
filtered_files = [name for name in fileNames if name.endswith(".OCT") and "RegAvg" not in name]  #Removing any files that contain "RegAvg" and aren't .OCT



# Determining which experiment to convert from that day
def user_selects_what_experiment_to_process(list_of_options):
    def on_confirm(event=None):
        nonlocal selected_option
        selected_option = options_var.get()
        window.destroy()
    
    def on_dialog_close(event=None):
        nonlocal selected_option
        selected_option = None
        window.destroy()

    window = tk.Toplevel()
    window.title("Experiment Selection")
    window.protocol("WM_DELETE_WINDOW", on_dialog_close)
    window.bind("<Escape>", on_dialog_close)
    window.bind("<Return>", on_confirm)
    
      
    # Instructions label
    instructions = tk.Label(window, text="Please select an experiment to process:")
    instructions.pack(pady=10)
    
    # Variable to store the selected option
    options_var = tk.StringVar(value=list_of_options[0])  # Default selection
    selected_option = list_of_options[0]  # Initialize selected option
            
    # Create radio buttons for each option
    for option in list_of_options:
        rb = tk.Radiobutton(window, text=option, variable=options_var, value=option)
        rb.pack(anchor="w")
    
    # Confirm button
    confirm_button = ttk.Button(window, text="Confirm", command=on_confirm)
    confirm_button.pack(pady=10)
    

    # Center the window on the screen
    center_dialog_box(window)

    window.wait_window()  # Wait for the window to close
    
    return selected_option

# If there are several different experiments for the date, user needs to select which one to run
experiment_list = []
selected_experiment = filtered_files[0].split("_")[0]
for file_name in filtered_files:
    date_and_experiment = file_name.split("_")[0]
    if date_and_experiment not in experiment_list:
        experiment_list.append(date_and_experiment)

if len(experiment_list) > 1:
    selected_experiment = user_selects_what_experiment_to_process(experiment_list)
    if selected_experiment is None:
        print("No option selected. Shutting down program.")
        exit()


    temp_list = []    
    for file_name in filtered_files:
        if file_name.split("_")[0] == selected_experiment:
            temp_list.append(file_name)
    filtered_files = temp_list



# Extracting info from the file names
annotated_list = [
    [
        file_name,
        file_name.split("_")[1],  # Extract the eye ("OS" or "OD")
        file_name.split("_")[2],  # Extract the image type ("L", "R", or "V")
        int(file_name.split("_")[-1].split(".")[0])  # Extract the identifying number
    ]
    for file_name in filtered_files
]


# Format: [file name, eye, image type, identifying number]
for sublist in annotated_list:   #interpreting what the image type is
    if sublist[2] == "R" or sublist[2] == "A":
        sublist[2] = "radial"
    elif sublist[2] == "L":
        sublist[2] = "linear"
    elif sublist[2] == "V":
        sublist[2] = "volume"

annotated_list.sort(key=lambda x: x[3])  #sorting the list by ID number (and thus by time it was taken)


#Assigning each mouse an arbitrary number assuming both eyes are imaged for every mouse
mouseNumber = 1
previousEye = None

for sublist in annotated_list:
    currentEye = sublist[1]
    if od_before_os is True:
        if previousEye is not None and previousEye == "OS" and currentEye == "OD":
            mouseNumber += 1
    else:
        if previousEye is not None and previousEye == "OD" and currentEye == "OS":
            mouseNumber += 1
    sublist.append(mouseNumber)
    previousEye = currentEye

number_of_mice = mouseNumber

#Next we will identify the location based off of the image type and order it appears in
previousEye = None
image_count_for_eye = 0

for sublist in annotated_list:
    currentEye = sublist[1]
    if currentEye != previousEye:
        image_count_for_eye = 0
    if sublist[2] == scan_modes[image_count_for_eye]:
        sublist.append(image_location_list[image_count_for_eye])
    else:
        sublist.append("")
    image_count_for_eye += 1
    previousEye = currentEye



# Figuring out how many images each mouse/eye has
# annotated_list format: [0 file name, 1 eye, 2 image type, 3 ID number, 4 arbitrary mouse number]
# Making a new list to define each eye image
# eye_images_list format: [0 mouse, 1 eye, 2 image locations]
eye_images_list = []

location_mapping = {image_location: image_location[0].upper() for image_location in image_location_list}

for sublist in annotated_list:
    mouse = sublist[4]  # Extract the mouse from the annotated_list item
    eye = sublist[1]  # Extract the eye from the annotated_list item
    location = sublist[5]  # Extract the location from the annotated_list item

    location = location_mapping.get(location, "?")  #If there isn't a valid dictionary entry, then it will return a "?". Otherwise it will give the abbreviated version

    found = False

    for item in eye_images_list:
        if mouse == item[0] and eye == item[1]:   #Checking if the mouse/eye combo are there
            item[2] += location
            found = True
            break

    if found == False:
        eye_images_list.append([mouse, eye, location])


#Having the user fill in the mouse numbers
def create_mouse_number_dialog_box():
    global edit
    edit = False

    def on_dialog_close(event=None):
        root.destroy()
        exit()

    def save_numbers():
        global inputted_mouse_numbers
        inputted_mouse_numbers = []
        for entry in entry_boxes:
            text = entry.get().strip()
            if text:
                inputted_mouse_numbers.append(text)
            else:
                inputted_mouse_numbers.append("")

    def on_arrow_key_press(event):
        focused_entry = window.focus_get()
        if focused_entry:
            focused_entry_idx = entry_boxes.index(focused_entry)
            if event.keysym == "Down":
                next_entry_idx = focused_entry_idx + 1
                if next_entry_idx < len(entry_boxes):
                    entry_boxes[next_entry_idx].focus_set()
            elif event.keysym == "Up":
                prev_entry_idx = focused_entry_idx - 1
                if prev_entry_idx >= 0:
                    entry_boxes[prev_entry_idx].focus_set()

    window = tk.Toplevel()
    window.title("Number Input")
    window.protocol("WM_DELETE_WINDOW", on_dialog_close)

    dialog_frame = ttk.Frame(window)
    dialog_frame.pack(padx=10, pady=10)



    # Add instructions label
    instructions_label = ttk.Label(dialog_frame, text="OD and OS columns signify what images the\nprogram thinks you have. If wrong, click Edit\nto manually adjust.")
    instructions_label.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="w")

    ttk.Label(dialog_frame, text=" ").grid(row=1, column=0, padx=5)
    ttk.Label(dialog_frame, text="Mouse").grid(row=1, column=1, padx=5)
    ttk.Label(dialog_frame, text="OD").grid(row=1, column=2, padx=5)
    ttk.Label(dialog_frame, text="OS").grid(row=1, column=3, padx=5)

    definition_of_acronymns = "\n".join([f"{value} = {key}" for key, value in location_mapping.items()])
    instructions_label2 = ttk.Label(dialog_frame, text=definition_of_acronymns)
    instructions_label2.grid(row=number_of_mice + 2, column=0, columnspan=4, padx=5, pady=5, sticky="w")

    entry_boxes = []
    for i in range(number_of_mice):
        ttk.Label(dialog_frame, text=str(i + 1)).grid(row=i + 2, column=0, padx=5)
        entry = ttk.Entry(dialog_frame)
        entry.grid(row=i + 2, column=1, padx=5)
        entry_boxes.append(entry)

        matching_item = next((item for item in eye_images_list if item[0] == i + 1 and item[1] == "OD"), None)
        if matching_item:
            last_three_items = ", ".join(map(str, matching_item[2:]))
            ttk.Label(dialog_frame, text=last_three_items).grid(row=i + 2, column=2, padx=5)

        matching_item = next((item for item in eye_images_list if item[0] == i + 1 and item[1] == "OS"), None)
        if matching_item:
            last_three_items = ", ".join(map(str, matching_item[2:]))
            ttk.Label(dialog_frame, text=last_three_items).grid(row=i + 2, column=3, padx=5)

    def on_confirm_button_click(event=None):
        save_numbers()
        root.destroy()

    def on_edit_button_click():
        save_numbers()
        global edit
        edit = True
        root.destroy()

    save_button = ttk.Button(dialog_frame, text="Confirm", command=on_confirm_button_click)
    save_button.grid(row=number_of_mice + 3, column=1, pady=10)

    edit_button = ttk.Button(dialog_frame, text="Edit", command=on_edit_button_click)
    edit_button.grid(row=number_of_mice + 3, column=2, pady=10)

    window.bind("<Escape>", on_dialog_close)
    window.bind("<Return>", on_confirm_button_click)
    window.bind("<Down>", on_arrow_key_press)
    window.bind("<Up>", on_arrow_key_press)

    window.grab_set()

    # Center the window on the screen
    window.after(10, lambda: center_dialog_box(window))

    window.mainloop()

create_mouse_number_dialog_box()

remove_underscores(inputted_mouse_numbers)  # This needs to be done because I count underscores later and I can't have the user adding them. I'll replace them later.

#Putting the inputted mouse numbers into a dictionary
i=1
mouse_number_dict = {}
for number in inputted_mouse_numbers:
    mouse_number_dict[i] = number
    i += 1

#Revising the annotated_list to include the real mouse numbers (or blanks if that was what was provided)
for sublist in annotated_list:
    newNumber = mouse_number_dict.get(sublist[4], "dialogBoxError")
    sublist[4] = newNumber


#If the user clicked on the "Edit" button in the previous dialog box, then this dialog box will appear
def create_individual_dialog_box(annotated_list):
    newannotated_list = []

    def on_dialog_close2(event=None):
        window.destroy()
        window.master.destroy()
        exit()

    def on_confirm_button_click2(event=None):
        nonlocal newannotated_list
        for i, (mouse_entry, eye_entry, location_entry) in enumerate(entry_boxes):
            mouse_value = mouse_entry.get().strip()
            eye_value = eye_entry.get().strip()
            location_value = location_entry.get().strip()
            newannotated_list[i] = [annotated_list[i][0], eye_value, annotated_list[i][2], annotated_list[i][3], mouse_value, location_value]
        window.destroy()  # Destroy the dialog window
        window.master.destroy()

    def onScroll(event):    #This allows you to scroll in the dialog box
        if event.num == 5 or event.delta < 0:
            canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            canvas.yview_scroll(-1, "units")

    def on_arrow_key_press(event): #This allows you to use the up and down arrow keys to navigate the entry boxes
        focused_entry = window.focus_get()
        for entry_box in entry_boxes:
            if entry_box[0] == focused_entry or entry_box[1] == focused_entry or entry_box[2] == focused_entry:
                focused_entry_idx = entry_boxes.index(entry_box)
                focused_entry_col = entry_box.index(focused_entry)  # Get the column index of the focused entry
                if event.keysym == "Down":
                    next_entry_idx = focused_entry_idx + 1
                    if next_entry_idx < len(entry_boxes):
                        next_entry_box = entry_boxes[next_entry_idx]
                        next_entry_box[focused_entry_col].focus_set()  # Focus the entry in the same column
                elif event.keysym == "Up":
                    prev_entry_idx = focused_entry_idx - 1
                    if prev_entry_idx >= 0:
                        prev_entry_box = entry_boxes[prev_entry_idx]
                        prev_entry_box[focused_entry_col].focus_set()  # Focus the entry in the same column
                break  # Exit the loop after finding the focused entry

    window = tk.Toplevel()
    window.title("Edit Individual Files")
    window.protocol("WM_DELETE_WINDOW", on_dialog_close2)

    dialog_frame = ttk.Frame(window)
    dialog_frame.pack(padx=10, pady=10)


    # Add instructions label
    instructions_label = ttk.Label(dialog_frame, text="These are all the image files and what the code thinks are their mouse numbers, eyes, and locations. Please update them\nas you see fit.\n\nThe file name is formatted as date+experiment (if multiple are done that day), eye, image type (r=radial, l=linear), and ends\nwith an ID number that the OCT computer assigned.")
    instructions_label.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="w")

    ttk.Label(dialog_frame, text="File Name").grid(row=1, column=0, padx=5)
    ttk.Label(dialog_frame, text="Mouse", justify="center").grid(row=1, column=1, padx=5)
    ttk.Label(dialog_frame, text="Eye").grid(row=1, column=2, padx=5)
    ttk.Label(dialog_frame, text="Location").grid(row=1, column=3, padx=5)

    canvas = tk.Canvas(dialog_frame, height=600, width=640)
    canvas.grid(row=2, columnspan=4, padx=5, pady=5)

    scrollbar = ttk.Scrollbar(dialog_frame, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=2, column=4, sticky="ns")

    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    entry_boxes = []
    for i, sublist in enumerate(annotated_list):
        ttk.Label(scrollable_frame, text=sublist[0]).grid(row=i, column=0, padx=5, sticky="w")
        mouse_entry = ttk.Entry(scrollable_frame)
        mouse_entry.grid(row=i, column=1, padx=5)
        mouse_entry.insert(tk.END, sublist[4])
        eye_entry = ttk.Entry(scrollable_frame)
        eye_entry.grid(row=i, column=2, padx=5)
        eye_entry.insert(tk.END, sublist[1])
        location_entry = ttk.Entry(scrollable_frame)
        location_entry.grid(row=i, column=3, padx=5)
        location_entry.insert(tk.END, sublist[5])
        newannotated_list.append(sublist[:])
        entry_boxes.append((mouse_entry, eye_entry, location_entry))

    confirm_button = ttk.Button(dialog_frame, text="Confirm", command=on_confirm_button_click2)
    confirm_button.grid(row=3, columnspan=4, pady=10)

    window.bind("<MouseWheel>", onScroll)
    window.bind("<Escape>", on_dialog_close2)
    window.bind("<Return>", on_confirm_button_click2)
    window.bind("<Down>", on_arrow_key_press)
    window.bind("<Up>", on_arrow_key_press)


    window.transient(window.master)
    window.grab_set()
    window.master.attributes("-alpha", 0)  # Set window opacity to 0 to make it invisible

    # Center the window on the screen
    window.after(1, lambda: center_dialog_box(window))

    window.mainloop()

    return newannotated_list

if edit == True:
    newannotated_list = create_individual_dialog_box(annotated_list)
    annotated_list = newannotated_list



# Dividing the images into list of videos and list of images
annotated_list_volume_scans = []
annotated_list_image_scans = []    # For radial and linear scans
for sublist in annotated_list:
    if sublist[2] == "volume":
        annotated_list_volume_scans.append(sublist)
    else:
        annotated_list_image_scans.append(sublist)



# Saving the annotated_list to a txt file in the image directory
annotated_volume_text_file = os.path.join(image_directory, "Annotated_list_of_volume_scans.txt")
annotated_images_text_file = os.path.join(image_directory, "Annotated_list_of_images.txt")

# Open the file in write mode
with open(annotated_volume_text_file, "w") as file:
    for sublist in annotated_list_volume_scans:
        # Convert the sublist to a string and write it to the file
        sublist_str = str(sublist)
        file.write(sublist_str)
        file.write('\n')  # Add a newline character after each sublist
with open(annotated_images_text_file, "w") as file:
    for sublist in annotated_list_image_scans:
        # Convert the sublist to a string and write it to the file
        sublist_str = str(sublist)
        file.write(sublist_str)
        file.write('\n')  # Add a newline character after each sublist

print(f"Number of images found: {len(annotated_list_image_scans)}")
print(f"Number of volume scans found: {len(annotated_list_volume_scans)}")



# Retrieving the location of the files and folders needed to run the ImageJ script.
# If it wasn't already in the Open_OCT_file_preferences.txt file then it will ask the user to identify them.
def identify_file_locations(preferences_variables, key):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_name = "Open_OCT_file_preferences.txt"
    file_path = os.path.join(script_directory, file_name)

    try:
        return preferences_variables[key]
    except KeyError:
        def handle_key_input(prompt, file_type):
            messagebox.showerror("User input needed", prompt)
            selected_location = None
            if file_type == "directory":
                selected_location = filedialog.askdirectory()
            elif file_type == "file":
                selected_location = filedialog.askopenfilename()

            if selected_location:
                preferences_variables[key] = selected_location
                with open(file_path, 'a') as file:
                    file.write(f"\n{key} = {selected_location}")
                return selected_location
            else:
                print("Selection canceled")
                exit()

        if key == "screenshot_directory":
            prompt = f"After clicking 'OK,' please select the location of the folder called \"ImageJ_clicking_files.\""
            return handle_key_input(prompt, "directory")

        elif key == "imagej_location":
            prompt = f"After clicking 'OK,' please select the location of the ImageJ program. It should be called \"ImageJ.exe.\""
            return handle_key_input(prompt, "file")

        elif key == "macro_location":
            prompt = f"After clicking 'OK,' please select the location of the file called \"Open_OCT_file_imagej_supplement_1.3.\""
            return handle_key_input(prompt, "file")

        return None

imagej_location = identify_file_locations(preferences_variables, 'imagej_location')
screenshot_directory = identify_file_locations(preferences_variables, 'screenshot_directory')
macro_location = identify_file_locations(preferences_variables, 'macro_location')

macro_location = macro_location.replace("/", "\\")
imagej_location = imagej_location.replace("/", "\\")



# Checking if ImageJ is open and if it isn't, opening it

def is_imagej_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'ImageJ.exe':
            program_windows = gw.getAllWindows()    # These next few lines are making ImageJ the active program
            for window in program_windows:
                if window.title == "ImageJ" and window.title.startswith("ImageJ"):
                    program_window = window
                    break
            program_window.activate()
            end_time1 = time.time()
            return True     # Letting the script know ImageJ is running
    return False

def is_imagej_logo_visible():
    logo_path = os.path.join(screenshot_directory, "ImageJ_logo.png")

    if os.path.exists(logo_path):
        logo_location = pyautogui.locateOnScreen(logo_path, confidence=confidence)
        return logo_location is not None

    return False



if is_imagej_running():
    print("ImageJ is currently running. Proceeding with installing the macro.")
else:
    print("ImageJ is not open. Attempting to open now.")
    try:
        subprocess.Popen(imagej_location)

        while not is_imagej_logo_visible():
            time.sleep(1)  # Wait for 1 second before checking again

        print("ImageJ has been opened")
        time.sleep(1)
    except FileNotFoundError:
        print("Failed to find ImageJ executable")
        exit()



#Installing the needed macros

def click_on_image_center(image_path):
    image_location = pyautogui.locateOnScreen(image_path, confidence=confidence)
    if image_location:
        center_x, center_y = pyautogui.center(image_location)
        pyautogui.click(center_x, center_y)
    else:
        show_error_message("Unable to locate button")
        exit()

# Click on the center of 'plugins_button.png'
wait_to_appear(os.path.join(screenshot_directory, "plugins_button.png"), 30)
plugins_button_path = os.path.join(screenshot_directory, "plugins_button.png")
click_on_image_center(plugins_button_path)

# Simulate keyboard actions to get to macro installation
pyautogui.press('down')    # Press the down arrow key
pyautogui.press('right')   # Press the right arrow key
pyautogui.press('enter')   # Press the enter key


# Entering in the ImageJ macro name
install_macros_png_path = os.path.join(screenshot_directory, "install_macros.png")

if wait_to_appear(install_macros_png_path, 10):
    pyautogui.typewrite(macro_location, interval=0.01)
    pyautogui.press('enter')
else:
    show_error_message(f"Something is wrong with the script and it cannot enter the name of the ImageJ macro. Please install this macro in ImageJ and then click okay:\n\n{macro_location}")



# Press 'w' key to trigger the ImageJ macro to define the working directory where the images are located
print("Sending directory location to ImageJ")
time.sleep(2)
pyautogui.press('w')

wait_to_appear(os.path.join(screenshot_directory, "select_the_location_of_the_images.png"), 10)

pyautogui.typewrite(image_directory, interval=0.01)
pyautogui.press('enter')
time.sleep(2)


# Making sure ImageJ is the active program still
is_imagej_running()

# Press 'a' key to trigger the ImageJ macro that converts OCT images to TIF images
print("Sending command to ImageJ to convert OCT files")
pyautogui.press('a')

time.sleep(2)



# Now the program will monitor the conversion of OCT images and will proceed with the rest of the
# code when the proper amount of images have appeared in the folder

def monitor_file_creation_in_directory(directory, annotated_list_of_files, file_type):
    # file_type should be '.tif' or '.avi' or some other similar string

    # Count the number of file_type files in the directory
    file_count = 0

    # Wait until the count matches the number of sublists in annotated_list
    while file_count != len(annotated_list_of_files):
        file_count = sum(1 for file in os.listdir(directory) if file.endswith(file_type))
        time.sleep(0.1)

# First will monitor the creation of .tif files
cropped_tif_images_directory = os.path.join(image_directory, "cropped_tif_images") # This was created in the ImageJ macro
monitor_file_creation_in_directory(cropped_tif_images_directory, annotated_list_image_scans, ".tif")
print("OCT files converted into TIF files and cropped")

# Then will monitor the creation of .avi files
volume_scan_directory = os.path.join(image_directory, "volume_scans") # This was created in the ImageJ macro
monitor_file_creation_in_directory(volume_scan_directory, annotated_list_volume_scans, ".avi")
print("OCT files converted into AVI files and cropped")

time.sleep(3)   # Give ImageJ time to close out of the image files





def rename_files(directory, annotated_list, is_volume_scan):    # This will convert the original file names into what I want the file names to be
    file_list = os.listdir(directory)
    file_count = len(file_list)
    
    # Determine the number of scans per image, if it isn't a volume scan
    number_of_images_in_scan = {}
    if not is_volume_scan:
        for file in file_list:
            base_name = file[:-8]   # Excludes the 4-digit image sequence number and ".tif"
            if base_name in number_of_images_in_scan:
                number_of_images_in_scan[base_name] += 1
            else:
                number_of_images_in_scan[base_name] = 1

    # Function to determine which of the location names within a radial scan to apply to a given image
    def determine_radial_scan_location_name(name_with_sequence_number, location):
        base_name = name_with_sequence_number[:-4]
        sequence_number = int(name_with_sequence_number[-4:])
        number_of_images = number_of_images_in_scan[base_name]
        
        location_list = location.split(", ")

        images_per_scan = number_of_images // len(location_list)
        scan_index = sequence_number // images_per_scan  # integer division to find the scan index
        specific_radial_image_location = location_list[scan_index]  # Get the corresponding scan name from the list

        return specific_radial_image_location



    for file_name_with_extension in file_list:
        file_name_without_extension = os.path.splitext(file_name_with_extension)[0]

        if not is_volume_scan:
            file_name_with_sequence_number = file_name_without_extension
            file_name_without_sequence_number = file_name_without_extension[:-4]  # Remove the last 4 characters - the image number from the image sequence
        else:
            file_name_without_sequence_number = file_name_without_extension   # Volume scans don't have the sequence number attached
        
        for sublist in annotated_list:
            annotated_file_name = sublist[0]
            annotated_list_name_without_extension = annotated_file_name[:-4]  # Remove the last 4 characters (".OCT")

            if file_name_without_sequence_number == annotated_list_name_without_extension:
                eye = sublist[1]
                location = sublist[5]
                mouse_number = sublist[4]
                scan_type = sublist[2]

                if scan_type == 'radial':
                    location = determine_radial_scan_location_name(file_name_with_sequence_number, location)

                # Figuring out the last part of the renamed file name
                if scan_type == 'volume':
                    micron_depth = int(crop_amount)
                    mm_depth = micron_depth / 1000
                    final_part_of_file_name = f"{mm_depth:.3f}".rstrip('0').rstrip('.') + "mmdepth.avi"     # Reports up to 3 decimal places in name
                else:   # For non-volume scans we need to keep the last identifier numbers. We'll add "mmdepth" later when averaging
                    final_part_of_file_name = file_name_with_extension[-8:] # includes the 4 sequence numbers and the ".tif"

                new_name = f"{mouse_number}_{eye}_{location}_{final_part_of_file_name}"
                break
            else:
                new_name = file_name_with_extension  # Use original file_name_with_extension if no match is found

        # Construct the full paths for the old and new names
        old_path = os.path.join(directory, file_name_with_extension)
        new_path = os.path.join(directory, new_name)

        # Rename the file if the location isn't "delete"
        if location == "delete":
            os.remove(old_path)
        else:
            os.rename(old_path, new_path)

    print(f"Renamed and/or deleted {file_count} files in {os.path.basename(directory)}")


# Renaming the individual sequence files and volume scan files
individual_sequence_images_directory = os.path.join(image_directory, "individual_sequence_images") # This was created in the ImageJ macro
rename_files(individual_sequence_images_directory, annotated_list_image_scans, False)    # This will convert the original file names into what I want the file names to be
rename_files(volume_scan_directory, annotated_list_volume_scans, True)



# Averaging the individual sequence images using the ImageJ macro
def averaging_images(directory_path, image_directory):

    def centerOfButton(locationOfWhatever):
        xCoordinate = locationOfWhatever.left + round(locationOfWhatever.width/2)
        yCoordinate = locationOfWhatever.top + round(locationOfWhatever.height/2)
        return([xCoordinate, yCoordinate])


    averaged_image_count = 1
    file_list = os.listdir(directory_path)

    # Group files based on mouse number, eye, and location
    groups = {}
    for filename in file_list:
        parts = filename.split("_")
        mouse_number = parts[0]
        eye = parts[1]
        location = parts[2]

        group_key = (mouse_number, eye, location)
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(filename)

    # Making a directory for averaged images
    averaged_images_directory = os.path.join(image_directory, "averaged_images")
    os.makedirs(averaged_images_directory, exist_ok=True)

    first_time = True       # The for loop needs to do a couple things unique to the first iteration
    # Iterate over the groups and process each one
    for group_files in groups.values():
        # Create the "images_to_be_averaged" directory
        images_to_be_averaged_directory = os.path.join(image_directory, "images_to_be_averaged")
        os.makedirs(images_to_be_averaged_directory, exist_ok=True)

        # Copy files from the current group to the output directory
        for file in group_files:
            file_path = os.path.join(directory_path, file)
            shutil.copy2(file_path, images_to_be_averaged_directory)

        # Identifying the active progam and saving that so it will return to it later after the OCT dialog box has been dealt with
        active_window = gw.getActiveWindow()
        original_program_title = active_window.title if active_window else None

        # Starting up the 'd' macro in ImageJ
        if is_imagej_running():     # Making ImageJ the active program
            pyautogui.press('d')
            time.sleep(0.5)
        else:
            show_error_message("ImageJ is no longer running. Program shutting down.")
            exit()


        # Checking (and waiting) to see if the OCT volume averager dialog box appears
        oct_volume_averager_text = os.path.join(screenshot_directory, "OCT_volume_averager.png")
        oct_volume_averager_text_alternate = os.path.join(screenshot_directory, "OCT_volume_averager2.png")
        search_start_time = time.time()
        while time.time() - search_start_time < 20:
            averager_text_location = pyautogui.locateOnScreen(oct_volume_averager_text, confidence=confidence)
            if averager_text_location is None:
                averager_text_location = pyautogui.locateOnScreen(oct_volume_averager_text_alternate, confidence=confidence)
                if averager_text_location is not None:
                    pyautogui.click(centerOfButton(averager_text_location))

            if averager_text_location is not None:
                break

            time.sleep(0.1)

        if averager_text_location is None:
            show_error_message("Unable to locate OCT Volume Averager dialog box. Script shutting down.")
            exit()




        # We only need to check for correct settings and input directories the first time

        if first_time:
            screen_width, screen_height = pyautogui.size()  # Moving the mouse off screen  temporarily so it doesn't interfere with the next bit of code
            original_mouse_position = pyautogui.position()
            pyautogui.moveTo(screen_width/2, 0)
            time.sleep(0.25)

            # Checking to make sure the correct settings are selected
            # Checking and potentially changing the read setting
            read_setting_location = pyautogui.locateOnScreen(os.path.join(screenshot_directory, "correct_read_setting.png"), confidence=confidence) or pyautogui.locateOnScreen(os.path.join(screenshot_directory, "correct_read_setting2.png"), confidence=confidence)
            if read_setting_location is None:
                read_setting_location = pyautogui.locateOnScreen(os.path.join(screenshot_directory, "incorrect_read_setting.png"), confidence=confidence) or pyautogui.locateOnScreen(os.path.join(screenshot_directory, "incorrect_read_setting2.png"), confidence=confidence)
                if read_setting_location is None:
                    show_error_message("The script is unable to identify the read settings properly in the OCT Volume Averager box. Please select the correct setting before clicking okay.")
                if read_setting_location is not None:
                    click_location = read_setting_location.left + 10, read_setting_location.top + 37
                    pyautogui.click(click_location)
                    time.sleep(5)


            # Checking and potentially changing the save setting
            save_setting_loation = pyautogui.locateOnScreen(os.path.join(screenshot_directory, "correct_save_setting.png"), confidence=confidence) or pyautogui.locateOnScreen(os.path.join(screenshot_directory, "correct_save_setting2.png"), confidence=confidence)
            if save_setting_loation is None:
                save_setting_loation = pyautogui.locateOnScreen(os.path.join(screenshot_directory, "incorrect_save_setting.png"), confidence=confidence) or pyautogui.locateOnScreen(os.path.join(screenshot_directory, "incorrect_save_setting2.png"), confidence=confidence)
                if save_setting_loation is None:
                    show_error_message("The script is unable to identify the save settings properly in the OCT Volume Averager box. Please select the correct setting before clicking okay.")
                if save_setting_loation is not None:
                    click_location = save_setting_loation.left + 10, save_setting_loation.top + 37
                    pyautogui.click(click_location)
                    time.sleep(5)


            # Locating the "okay" button
            pyautogui.moveTo(screen_width/2, 0)
            time.sleep(0.1)
            okay_button_location = pyautogui.locateOnScreen(os.path.join(screenshot_directory, "ok_button.png"), confidence=confidence) or pyautogui.locateOnScreen(os.path.join(screenshot_directory, "ok_button2.png"), confidence=confidence)
            if okay_button_location is None:
                show_error_message("The script is unable to locate the 'okay' button, either because it is being obscured or the style of the button has changed. If the later is the case, please take a screenshot of the button and save it in the ImageJ_clicking_files folder as ok_button.png. The script will now shut down.")


            # Checking the Options box
            options_box_loation = pyautogui.locateOnScreen(os.path.join(screenshot_directory, "correct_options_box_settings.png"), confidence=confidence) or pyautogui.locateOnScreen(os.path.join(screenshot_directory, "correct_options_box_settings2.png"), confidence=confidence)
            if options_box_loation is None:
                show_error_message("Incorrect settings are selected\nPlease make the following changes as needed:\n\nUncheck 'Inverted Image Stack (EDI)'\nUncheck 'Keep Intermediate .tiff Files'\nSet the 'Number of Pixels to Crop' to 0 for both boxes\n\nAlternatively, something is covering part of the OCT Volume Averager dialog box and the script is unable to complete its confirmation that the proper settings are selected. Please make sure the dialog box is not partially hidden.\n\nAnother possibility is the style of the box has changed. In which case you would need to take a screenshot of it and save it as correct_options_box_settings.png in ImageJ_clicking_files.\n\nClick the okay button in this dialog box when you have made the changes.")


            # Typing in the correct directories into the textboxes
            averager_text_right_coordinate = averager_text_location.left + averager_text_location.width
            averager_text_bottom_coordinate = averager_text_location.top + averager_text_location.height

            text_box_1 = read_setting_location.left + read_setting_location.width, read_setting_location.top + read_setting_location.height + 5
            pyautogui.click(text_box_1)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.typewrite(images_to_be_averaged_directory, interval=0.01)
            time.sleep(0.1)

            text_box_2 = save_setting_loation.left + save_setting_loation.width, save_setting_loation.top + save_setting_loation.height + 5
            pyautogui.click(text_box_2)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.typewrite(averaged_images_directory, interval=0.01)

            first_time = False
            pyautogui.moveTo(original_mouse_position.x, original_mouse_position.y)   # putting the mouse back in the original loctaion


        # Clicking on the okay button
        original_mouse_position = pyautogui.position()
        pyautogui.click(centerOfButton(okay_button_location))
        pyautogui.moveTo(original_mouse_position.x, original_mouse_position.y)   # putting the mouse back in the original loctaion


        # Going back to whatever program/window was active before the OCT dialog box appeared
        original_window = gw.getWindowsWithTitle(original_program_title)
        if original_window:
            original_window[0].activate()


        target_file = "regAvgImg.tif"   # The code is going to be looking for this file to appear, and when it does, it will continue
        target_file_path = os.path.join(averaged_images_directory, target_file)
        loop_start_time = time.time()

        # Wait until the target file appears or the total duration elapses
        while not os.path.exists(target_file_path) and time.time() - loop_start_time <= 60:
            if time.time() - loop_start_time > 60 and not os.path.exists(target_file_path):
                show_error_message("New file has not appeared in one minute. Program shutting down.")
                exit()
            time.sleep(1)


        old_path = target_file_path

        micron_depth = int(crop_amount)
        mm_depth = micron_depth / 1000
        mmdepth_text = f"{mm_depth:.3f}".rstrip('0').rstrip('.') + "mmdepth"     # Reports up to 3 decimal places in name

        file_name = group_files[0][:-8] + mmdepth_text + ".tif"
        new_path = os.path.join(averaged_images_directory, file_name)

        time.sleep(0.5)
        os.rename(old_path, new_path)

        averaged_image_count += 1


        # Delete the "images_to_be_averaged" directory
        delete_directory(images_to_be_averaged_directory)



# Call the averaging_images function
averaged_images_directory = os.path.join(image_directory, "averaged_images")
if annotated_list_image_scans:  # Only proceeds if there are items in annotated_list_image_scans
    averaging_images(individual_sequence_images_directory, image_directory)
    time.sleep(1)   # Waiting one second in order to properly delete "rotatedRegAvgImg.tif"
    os.remove(os.path.join(averaged_images_directory, "rotatedRegAvgImg.tif"))

# Creating an unaveraged image folder, if the user specified so
unaveraged_images_directory = os.path.join(image_directory, "unaveraged_images")
if annotated_list_image_scans and unaveraged_images is True:
    os.makedirs(unaveraged_images_directory, exist_ok=True)
    individual_sequence_files = os.listdir(individual_sequence_images_directory)
    # Group files based on mouse number, eye, and location
    groups = {}
    for filename in individual_sequence_files:
        parts = filename.split("_")
        mouse_number = parts[0]
        eye = parts[1]
        location = parts[2]

        group_key = (mouse_number, eye, location)
        if group_key not in groups:
            groups[group_key] = []
        groups[group_key].append(filename)

    # Copying the first image in each group to the unaveraged_images directory
    for i, image_group in enumerate(groups.values()):
        first_image = image_group[0]
        old_path = os.path.join(individual_sequence_images_directory, first_image)
        new_name = image_group[0][:-6] + ".tif"
        new_path = os.path.join(unaveraged_images_directory, new_name)
        shutil.copy(old_path, new_path)




# Enhancing the contrast of the images
if annotated_list_image_scans:  # Only proceeds if there are items in annotated_list_image_scans
    if is_imagej_running():     # Making ImageJ the active program
        print("Sending command to ImageJ to enhance contrast")
        pyautogui.press('f') # to pay respects
        number_of_images = len([f for f in os.listdir(averaged_images_directory) if os.path.isfile(os.path.join(averaged_images_directory, f))])
        time.sleep(1 + (number_of_images * 0.08))
    else:
        show_error_message("ImageJ is no longer running. Program shutting down.")
        exit()


# Putting images in subdirectory as specified by user
# Update: change peripheral folder checkbox to entry box
subfolder_exists = False    # this is just for the restore_underscore function down below
if annotated_list_image_scans:  # Only proceeds if there are items in annotated_list_image_scans
    for filename in os.listdir(averaged_images_directory):
        name_elements = filename.split('_')
        location_name = name_elements[2]
        if location_name in images_to_put_into_subfolder:
            subfolder_path = os.path.join(averaged_images_directory, subfolder_name)
            if not os.path.exists(subfolder_path):
                os.mkdir(subfolder_path)
                subfolder_exists = True
            src_path = os.path.join(averaged_images_directory, filename)
            dest_path = os.path.join(subfolder_path, filename)
            os.rename(src_path, dest_path)

# Putting the underscores back in the file names that were removed with remove_underscores()
def restore_underscores(directory):
    directory_files = os.listdir(directory)
    for file in directory_files:
        old_path = os.path.join(directory, file)
        new_name = file.replace("underscore", "_")
        new_path = os.path.join(directory, new_name)
        os.rename(old_path, new_path)

if annotated_list_image_scans:
    restore_underscores(averaged_images_directory)
if subfolder_exists:
    restore_underscores(subfolder_path)
if annotated_list_image_scans and unaveraged_images is True:
    restore_underscores(unaveraged_images_directory)


# Combining converted files into one subdirectory
def combining_directories(experiment):
    final_directory_name = f"{experiment} OCT images"
    final_directory_path = os.path.join(image_directory, final_directory_name)

    # Create the subdirectory if it doesn't exist
    if not os.path.exists(final_directory_path):
        os.makedirs(final_directory_path)
    else:
        delete_directory(final_directory_path)
        os.makedirs(final_directory_path)

    directories_to_move = ["averaged_images", "unaveraged_images", "volume_scans"]

    # Move each directory into the new subdirectory
    for directory in directories_to_move:
        source_directory = os.path.join(image_directory, directory)
        destination_directory = os.path.join(final_directory_path, directory)

        # Check if the source directory exists
        if os.path.exists(source_directory):
            shutil.move(source_directory, destination_directory)

        # Deleting if nothing is in the directory
        if os.path.isdir(destination_directory) and not os.listdir(destination_directory):
            os.rmdir(destination_directory)
    
    # If there is only one subdirectory, move all its contents out to final_directory_path and delete the subdirectory
    final_subdirectories_list = os.listdir(final_directory_path)
    number_of_subdirectories = len(final_subdirectories_list)
    
    if number_of_subdirectories == 1:
        only_subdirectory = final_subdirectories_list[0]
        only_subdirectory_path = os.path.join(final_directory_path, only_subdirectory)

        # Move all contents of the only_subdirectory to final_directory_path
        for item in os.listdir(only_subdirectory_path):
            item_path = os.path.join(only_subdirectory_path, item)
            destination_path = os.path.join(final_directory_path, item)

            # Move the item (file or subdirectory) to final_directory_path
            shutil.move(item_path, destination_path)

        # Delete the now-empty subdirectory
        os.rmdir(only_subdirectory_path)
    

combining_directories(selected_experiment)

# Deleting the intermediate directories
delete_directory(individual_sequence_images_directory)
delete_directory(cropped_tif_images_directory)
if os.path.exists(annotated_volume_text_file):
    os.remove(annotated_volume_text_file)
if os.path.exists(annotated_images_text_file):
    os.remove(annotated_images_text_file)
if os.path.exists(imagej_settings_file):
    os.remove(imagej_settings_file)
# Delete the directories if there are no images in them
if os.path.isdir(unaveraged_images_directory) and not os.listdir(unaveraged_images_directory):
    os.rmdir(unaveraged_images_directory)
if os.path.isdir(averaged_images_directory) and not os.listdir(averaged_images_directory):
    os.rmdir(averaged_images_directory)
if os.path.isdir(volume_scan_directory) and not os.listdir(volume_scan_directory):
    os.rmdir(volume_scan_directory)

print("Complete")