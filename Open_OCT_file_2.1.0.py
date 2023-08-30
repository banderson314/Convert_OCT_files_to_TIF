#Open_OCT_file_2.1.0.py
#Converting OCT files to tif files
#Made by Brandon Anderson, University of Pennsylvania
#Last updated on August 18, 2023

#For this macro to work, you need the following files:
#OCT reader plugin - ImageJ macro
#OCT averager plugin - ImageJ macro

import os
import psutil       # For opening ImageJ
import subprocess   # For opening ImageJ
import time         # For opening ImageJ and tracking progress
import pyautogui    # For opening and manipulating ImageJ
import shutil       # For deleting directories
import pygetwindow as gw    #for making ImageJ an active window
import tkinter as tk    # For making dialog boxes
import tkinter.messagebox as messagebox
from tkinter import ttk, filedialog, messagebox
import inspect      # For error messages

# You will need to make sure to download psutil, pyautogui, and pygetwindow as they don't come with base Python


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
        if pyautogui.locateOnScreen(image_file):
            time.sleep(0.5)
            return True
        time.sleep(0.5)
    time.sleep(0.5)
    return False


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
        if key == "image_location_list":
            return ["central", "temporal", "nasal", "superior", "inferior"]
        elif key == "od_before_os":
            return True
        elif key == "scan_modes":
            return ['radial', 'linear', 'linear', 'radial', 'radial']
        elif key == "subfolder_entry":
            return [False, True, True, True, True]
        elif key == "subfolder_name":
            return "Peripheral images"
        elif key == "horizontal_image_list":
            return ["horizontal", "", "", "", ""]
        elif key == "vertical_image_list":
            return ["vertical", "", "", "superior", "inferior"]
        elif key == "unaveraged_images":
            return False
        elif key == "min_contrast":
            return "25"
        elif key == "max_contrast":
            return "215"


image_location_list = retrieve_variables(preferences_variables, 'image_location_list')
od_before_os = retrieve_variables(preferences_variables, 'od_before_os')
scan_modes = retrieve_variables(preferences_variables, 'scan_modes')
subfolder_entry = retrieve_variables(preferences_variables, 'subfolder_entry')
subfolder_name = retrieve_variables(preferences_variables, 'subfolder_name')
horizontal_image_list = retrieve_variables(preferences_variables, 'horizontal_image_list')
vertical_image_list = retrieve_variables(preferences_variables, 'vertical_image_list')
unaveraged_images = retrieve_variables(preferences_variables, 'unaveraged_images')
min_contrast = retrieve_variables(preferences_variables, 'min_contrast')
max_contrast = retrieve_variables(preferences_variables, 'max_contrast')


# Converting str to whatever it actually is, since only strings come from the txt file
if type(image_location_list) == str:
    image_location_list = eval(image_location_list)
if type(od_before_os) == str:
    od_before_os = eval(od_before_os)
if type(unaveraged_images) == str:
    unaveraged_images = eval(unaveraged_images)
if type(scan_modes) == str:
    scan_modes = eval(scan_modes)
if type(subfolder_entry) == str:
    subfolder_entry = eval(subfolder_entry)
if type(horizontal_image_list) == str:
    horizontal_image_list = eval(horizontal_image_list)
if type(vertical_image_list) == str:
    vertical_image_list = eval(vertical_image_list)



#This first dialog box checks to see what images were taken and in which order
def location_input_dialog_box():
    row_num = 1 # Starting row number for entry and checkbox widgets

    def add_entry_row(mode="linear", subfolder_mode=False):
        nonlocal row_num
        entry_row = tk.Entry(dialog_frame)
        entry_row.grid(row=row_num, column=0, sticky='w')
        entry_rows.append(entry_row)

        linear_var = tk.BooleanVar(value=(mode == "linear"))
        radial_var = tk.BooleanVar(value=(mode == "radial"))
        linear_vars.append(linear_var)
        radial_vars.append(radial_var)

        checkbox_linear = tk.Checkbutton(dialog_frame, variable=linear_var, command=lambda i=len(linear_vars)-1: select_linear(i))
        checkbox_linear.grid(row=row_num, column=1, sticky='s')
        checkbox_linears.append(checkbox_linear)

        checkbox_radial = tk.Checkbutton(dialog_frame, variable=radial_var, command=lambda i=len(radial_vars)-1: select_radial(i))
        checkbox_radial.grid(row=row_num, column=2, sticky='s')
        checkbox_radials.append(checkbox_radial)


        # Adding the horizontal and vertical entry boxes
        entry_horizontal = tk.Entry(dialog_frame)
        entry_horizontal.grid(row=row_num, column=3, sticky='w')
        entry_horizontals.append(entry_horizontal)

        entry_vertical = tk.Entry(dialog_frame)
        entry_vertical.grid(row=row_num, column=4, sticky='w')
        entry_verticals.append(entry_vertical)

        # Adding subfolder checkboxes
        subfolder_var = tk.BooleanVar(value=subfolder_mode)
        checkbox_subfolder = tk.Checkbutton(dialog_frame, variable=subfolder_var)
        checkbox_subfolder.grid(row=row_num, column=5, sticky='s')
        checkbox_subfolders.append(checkbox_subfolder)
        subfolder_vars.append(subfolder_var)

        row_num += 1

    def remove_entry_row():
        if entry_rows:
            entry_row = entry_rows.pop()
            entry_row.destroy()

            linear_var = linear_vars.pop()
            radial_var = radial_vars.pop()

            checkbox_linear = checkbox_linears.pop()
            checkbox_linear.destroy()

            checkbox_radial = checkbox_radials.pop()
            checkbox_radial.destroy()

            # Remove the corresponding horizontal and vertical entry boxes from the lists and destroy them
            entry_horizontal = entry_horizontals.pop()
            entry_horizontal.destroy()

            entry_vertical = entry_verticals.pop()
            entry_vertical.destroy()

            checkbox_subfolder = checkbox_subfolders.pop()
            checkbox_subfolder.destroy()
            subfolder_var = subfolder_vars.pop()


    def select_linear(index):
        linear_vars[index].set(True)
        radial_vars[index].set(False)

    def select_radial(index):
        linear_vars[index].set(False)
        radial_vars[index].set(True)

    def restore_defaults():
        default_values = ["central", "temporal", "nasal", "superior", "inferior"]
        default_horizontal = ["horizontal", "", "", "", ""]
        default_radial_or_linear = ["radial", "linear", "linear", "radial", "radial"]
        default_vertical = ["vertical", "", "", "superior", "inferior"]
        default_subfolder = [False, True, True, True, True]
        current_row_count = len(entry_rows)

        # If the current number of rows is less than five, add new rows
        while current_row_count < 5:
            add_entry_row()
            current_row_count += 1

        # If the current number of rows is more than five, remove excess rows
        while current_row_count > 5:
            remove_entry_row()
            current_row_count -= 1

        # Update the content of the first column with default values
        for i, default_value in enumerate(default_values):
            entry_row = entry_rows[i]
            entry_row.delete(0, tk.END)  # Clear the current content
            entry_row.insert(tk.END, default_value)  # Set the default value

        # Set the checkboxes in the second and third columns based on default
        for i, mode in enumerate(default_radial_or_linear):
            if mode == "radial":
                linear_vars[i].set(False)
                radial_vars[i].set(True)
            else:  # Assuming "linear" as the other mode
                linear_vars[i].set(True)
                radial_vars[i].set(False)

        # Set the horizontal and vertical entry boxes with default values
        for i, default_value in enumerate(default_horizontal):
            entry_horizontal = entry_horizontals[i]
            entry_horizontal.delete(0, tk.END)
            entry_horizontal.insert(tk.END, default_value)

        for i, default_value in enumerate(default_vertical):
            entry_vertical = entry_verticals[i]
            entry_vertical.delete(0, tk.END)
            entry_vertical.insert(tk.END, default_value)

        # Set the checkboxes in the fifth column based on default
        for i, default_value in enumerate(default_subfolder):
            if default_value == True:
                subfolder_vars[i].set(True)
            else:
                subfolder_vars[i].set(False)

        od_os_checkbox_var.set(True)
        imagej_checkbox_var.set(False)
        unaveraged_checkbox_var.set(False)

        subfolder_name_entry.delete(0, tk.END)
        subfolder_name_entry.insert(0, "Peripheral images")

        min_contrast_entry.delete(0, tk.END)
        min_contrast_entry.insert(0, str(25))
        max_contrast_entry.delete(0, tk.END)
        max_contrast_entry.insert(0, str(215))


    def confirm(event=None):
        global image_location_list, od_before_os, scan_modes, subfolder_entry, subfolder_name, horizontal_image_list, vertical_image_list, unaveraged_images, min_contrast, max_contrast

        image_location_list = []
        scan_modes = []
        subfolder_entry = []
        horizontal_image_list = []
        vertical_image_list = []

        for i, entry_row in enumerate(entry_rows):
            text = entry_row.get()
            if text:
                image_location_list.append(text)

            if linear_vars[i].get():
                scan_modes.append("linear")
            elif radial_vars[i].get():
                scan_modes.append("radial")
            else:
                scan_modes.append("")

            subfolder_entry.append(subfolder_vars[i].get())

        for i, entry_horizontal in enumerate(entry_horizontals):
            text = entry_horizontal.get()
            if text:
                horizontal_image_list.append(text)
            else:
                horizontal_image_list.append("")

        for i, entry_vertical in enumerate(entry_verticals):
            text = entry_vertical.get()
            if text:
                vertical_image_list.append(text)
            else:
                vertical_image_list.append("")

        od_before_os = od_os_checkbox_var.get()
        imageJ_location_reenter = imagej_checkbox_var.get()
        subfolder_name = subfolder_name_entry.get()
        unaveraged_images = unaveraged_checkbox_var.get()
        min_contrast = min_contrast_var.get()
        max_contrast = max_contrast_var.get()

        window.destroy()
        window.master.destroy()


        # Removing variables that will be replaced
        with open(preference_file, 'r') as file:
            file_content = file.read()
        file_content = file_content.replace("\n\n\n", "\n") # Making sure we're not just adding a ton of extra lines over time
        variables_to_replace = [
            "image_location_list",
            "od_before_os",
            "scan_modes",
            "subfolder_entry",
            "subfolder_name",
            "horizontal_image_list",
            "vertical_image_list",
            "unaveraged_images",
            "min_contrast",
            "max_contrast"
        ]
        lines = [line for line in file_content.splitlines() if not any(line.startswith(variable) for variable in variables_to_replace)]
        if imageJ_location_reenter == True:
            shortened_lines = []
            for i in lines:
                if not (i.startswith("screenshot_directory") or i.startswith("macro_location") or i.startswith("imagej_location")):
                    shortened_lines.append(i)
            lines = shortened_lines

        # Saving the user's inputs for future uses
        with open(preference_file, 'w') as file:
            file.write('\n'.join(lines))
            file.write(f"\nimage_location_list = {image_location_list}")
            file.write(f"\nod_before_os = {od_before_os}")
            file.write(f"\nscan_modes = {scan_modes}")
            file.write(f"\nsubfolder_entry = {subfolder_entry}")
            file.write(f"\nsubfolder_name = {subfolder_name}")
            file.write(f"\nhorizontal_image_list = {horizontal_image_list}")
            file.write(f"\nvertical_image_list = {vertical_image_list}")
            file.write(f"\nunaveraged_images = {unaveraged_images}")
            file.write(f"\nmin_contrast = {min_contrast}")
            file.write(f"\nmax_contrast = {max_contrast}")


    def onDialogClose3(event=None):
        window.master.destroy()
        exit()



    window = tk.Toplevel()
    window.title("Image settings")
    window.protocol("WM_DELETE_WINDOW", onDialogClose3)

    instructions_label = tk.Label(window, text="Please enter the order that the images were taken in and what scan mode was used. If radial\nscans were used, record what the horizontal and vertical images represent. If this is not\nprovided for the radial images, then the image will not be processed. These will be used for the\nfile name.", justify='left')
    instructions_label.grid(padx=10, sticky='w')

    dialog_frame = tk.Frame(window)
    dialog_frame.grid(padx=10, pady=10)

    entry_rows = []
    linear_vars = []
    radial_vars = []
    checkbox_linears = []
    checkbox_radials = []
    entry_horizontals = []
    entry_verticals = []
    subfolder_var = []
    subfolder_vars = []
    checkbox_subfolders = []

    # Adding  labels at the top of the columns
    label_location = tk.Label(dialog_frame, text="location")
    label_location.grid(row=0, column=0)
    label_linear = tk.Label(dialog_frame, text="linear")
    label_linear.grid(row=0, column=1)
    label_radial = tk.Label(dialog_frame, text="radial")
    label_radial.grid(row=0, column=2)
    label_horizontal = tk.Label(dialog_frame, text="horizontal")
    label_horizontal.grid(row=0, column=3, sticky='s')
    label_vertical = tk.Label(dialog_frame, text="vertical")
    label_vertical.grid(row=0, column=4, sticky='s')
    label_subfolder = tk.Label(dialog_frame, text="subfolder")
    label_subfolder.grid(row=0, column=5)



    # Adding existing entry rows with their corresponding checkboxes
    for i, location in enumerate(image_location_list):
        mode = scan_modes[i] if scan_modes and i < len(scan_modes) else "linear"
        subfolder_mode = subfolder_entry[i] if subfolder_entry and i < len(subfolder_entry) else False
        add_entry_row(mode, subfolder_mode)
        entry_row = entry_rows[-1]
        entry_row.insert(tk.END, location)

        # Access entry_horizontal and entry_vertical from the lists
        entry_horizontal = entry_horizontals[-1]
        entry_vertical = entry_verticals[-1]
        entry_horizontal.insert(tk.END, horizontal_image_list[i])
        entry_vertical.insert(tk.END, vertical_image_list[i])

        row_num += 1


    button_frame = tk.Frame(window)
    button_frame.grid()
    add_button = tk.Button(button_frame, text="+", command=add_entry_row)
    add_button.pack(side='right')
    remove_button = tk.Button(button_frame, text="-", command=remove_entry_row)
    remove_button.pack(side='left')

    od_os_checkbox_var = tk.BooleanVar(value=od_before_os)
    od_os_checkbox = tk.Checkbutton(window, text="OD eyes were imaged before OS eyes", variable=od_os_checkbox_var)
    od_os_checkbox.grid(padx=10, sticky='w')

    imagej_checkbox_var = tk.BooleanVar(value=False)
    imagej_checkbox = tk.Checkbutton(window, text="Re-enter ImageJ file location", variable=imagej_checkbox_var)
    imagej_checkbox.grid(padx=10, sticky='w')

    unaveraged_checkbox_var = tk.BooleanVar(value=unaveraged_images)
    unaveraged_checkbox = tk.Checkbutton(window, text="Save a copy of the unaveraged images", variable=unaveraged_checkbox_var)
    unaveraged_checkbox.grid(padx=10, sticky='w')

    # Getting user input on subfolder name
    subfolder_frame = tk.Frame(window)
    subfolder_frame.grid(row=row_num+5, column=0, sticky='w', padx=10)  # Align to the left
    subfolder_name_var = tk.StringVar()
    subfolder_name_var.set(subfolder_name)
    subfolder_name_label = tk.Label(subfolder_frame, text="Subfolder name:")
    subfolder_name_label.pack(side='left')
    subfolder_name_entry = tk.Entry(subfolder_frame, textvariable=subfolder_name_var)
    subfolder_name_entry.pack(side='right')

    # Getting user input on contrast values (min and max) (0 and 255 are the ranges, 25 and 215 are recommended)
    contrast_frame = tk.Frame(window)
    contrast_frame.grid(row=row_num+6, column=0, sticky='w', padx=10)
    min_contrast_var = tk.StringVar()
    max_contrast_var = tk.StringVar()
    global min_contrast, max_contrast   # Don't know why this is needed but it is
    min_contrast_var.set(min_contrast)
    max_contrast_var.set(max_contrast)
    contrast_label = tk.Label(contrast_frame, text="Min and max contrast (ranges from 0 to 255): ")
    contrast_label.pack(side='left')
    min_contrast_entry = tk.Entry(contrast_frame, textvariable=min_contrast_var, width=6)
    max_contrast_entry = tk.Entry(contrast_frame, textvariable=max_contrast_var, width=6)
    min_contrast_entry.pack(side="left")
    max_contrast_entry.pack(side="right")

    button_frame = tk.Frame(window)
    button_frame.grid()
    restore_button = tk.Button(button_frame, text="Restore defaults", command=restore_defaults)
    restore_button.pack(side='left', pady=10)
    confirm_button = tk.Button(button_frame, text="Confirm", command=confirm)
    confirm_button.pack(side='right', pady=10, padx=10)


    window.bind("<Escape>", onDialogClose3)
    window.bind("<Return>", confirm)

    window.master.attributes("-alpha", 0)  # Set window opacity to 0 to make it invisible
    window.transient(window.master)
    window.grab_set()
    window.mainloop()

# Starting up the initial dialog box
location_input_dialog_box()


print("image_location_list:", image_location_list)
print("od_before_os:", od_before_os)
print("unaveraged_images:", unaveraged_images)
print("scan_modes:", scan_modes)
print("subfolder_entry:", subfolder_entry)
print("subfolder_name:", subfolder_name)
print("horizontal_image_list:", horizontal_image_list)
print("vertical_image_list:", vertical_image_list)
print("min_contrast:", min_contrast)
print("max_contrast:", max_contrast)


def remove_underscores(list):       # This needs to be done because I count underscores later and I can't have the user adding them. I'll replace them later.
    for i, item in enumerate(list):
        list[i] = item.replace("_", "underscore")

underscore_list = [image_location_list, horizontal_image_list, vertical_image_list]
for list in underscore_list:
    remove_underscores(list)


images_to_put_into_subfolder = []
for i, image_type in enumerate(image_location_list):
    if subfolder_entry[i] is True:
        images_to_put_into_subfolder.append(image_type)
        if horizontal_image_list[i] != "":
            images_to_put_into_subfolder.append(horizontal_image_list[i])
        if vertical_image_list[i] != "":
            images_to_put_into_subfolder.append(vertical_image_list[i])


#SELECTING THE DIRECTORY
# Create the Tkinter root window
root = tk.Tk()
root.withdraw()  # Hide the root window

# Prompt the user to select a directory using a dialog
image_directory = filedialog.askdirectory()

# Check if the user selected a directory or canceled the dialog
if image_directory:
    print("Selected directory:", image_directory)
else:
    print("Directory selection canceled")
    exit()


# Deleting all the directories previously made by this script if the user decides to run the script again in the same folder
# This is mainly for me to test my script
delete_directory(os.path.join(image_directory, "averaged_images"))
delete_directory(os.path.join(image_directory, "cropped_tif_images"))
delete_directory(os.path.join(image_directory, "images_to_be_averaged"))
delete_directory(os.path.join(image_directory, "individual_sequence_images"))
delete_directory(os.path.join(image_directory, "unaveraged_images"))
annotated_text_file = os.path.join(image_directory, "Annotated_list_of_files.txt")
if os.path.exists(annotated_text_file):
    os.remove(annotated_text_file)
imagej_settings_file = os.path.join(image_directory, "ImageJ_contrast_settings.txt")
if os.path.exists(imagej_settings_file):
    os.remove(imagej_settings_file)


# Saving the min and max values so that ImageJ can access them
with open(imagej_settings_file, "w") as file:
    file.write(str(min_contrast))
    file.write("\n")
    file.write(str(max_contrast))


#PUTTING FILE NAMES TOGETHER IN LIST
# Retrieve all file names in the directory
fileNames = [file for file in os.listdir(image_directory) if os.path.isfile(os.path.join(image_directory, file))]

filteredFiles = [name for name in fileNames if name.endswith(".OCT") and "RegAvg" not in name and name.split("_")[2] != "V"]  #Removing any files that contain "RegAvg" and aren't .OCT and aren't volume scans

#Checking to make sure all images are from the same date and experiment
experimentDate = filteredFiles[0].split("_")[0]
for file_name in filteredFiles:
    if file_name.split("_")[0] != experimentDate:
        messagebox.showerror("Error", "You must only use images from one date.\n\nIf multiple experiments were done on that date, you can only process one experiment at a time.\n\nYour image files start with the date followed by a number (e.g. 2023-05-08-001). The number and date has to be the same for all files.")
        exit()

#Extracting info from the file names
annotated_list = [
    [
        file_name,
        file_name.split("_")[1],  # Extract the eye ("OS" or "OD")
        file_name.split("_")[2],  # Extract the image type ("L", "R", or "V")
        int(file_name.split("_")[-1].split(".")[0])  # Extract the identifying number
    ]
    for file_name in filteredFiles
]
#Format: [file name, eye, image type, identifying number]
for sublist in annotated_list:   #interpreting what the image type is
    if sublist[2] == "R":
        sublist[2] = "radial"
    elif sublist[2] == "L":
        sublist[2] = "linear"
    elif sublist[2] == "V":     #These shouldn't be in the list so if they are this is a problem
        sublist[2] = "volume"
        print("Volume scan detected. This is a problem.")

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

numberOfMice = mouseNumber

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


#Figuring out how many images each mouse/eye has
#annotated_list format: [0 file name, 1 eye, 2 image type, 3 ID number, 4 arbitrary mouse number]
#Making a new list to define each eye image
#eyeImagesList format: [0 mouse, 1 eye, 2 image locations]
eyeImagesList = []

location_mapping = {image_location: image_location[0].upper() for image_location in image_location_list}

for sublist in annotated_list:
    mouse = sublist[4]  # Extract the mouse from the annotated_list item
    eye = sublist[1]  # Extract the eye from the annotated_list item
    location = sublist[5]  # Extract the location from the annotated_list item

    location = location_mapping.get(location, "?")  #If there isn't a valid dictionary entry, then it will return a "?". Otherwise it will give the abbreviated version

    found = False

    for item in eyeImagesList:
        if mouse == item[0] and eye == item[1]:   #Checking if the mouse/eye combo are there
            item[2] += location
            found = True
            break

    if found == False:
        eyeImagesList.append([mouse, eye, location])


#Having the user fill in the mouse numbers
def createMouseNumberDialogBox():
    global edit
    edit = False

    def onDialogClose(event=None):
        root.destroy()
        exit()

    def saveNumbers():
        global inputted_mouse_numbers
        inputted_mouse_numbers = []
        for entry in entry_boxes:
            text = entry.get().strip()
            if text:
                inputted_mouse_numbers.append(text)
            else:
                inputted_mouse_numbers.append("")

    def onArrowKeyPress(event):
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
    window.protocol("WM_DELETE_WINDOW", onDialogClose)

    dialog_frame = ttk.Frame(window)
    dialog_frame.pack(padx=10, pady=10)

    ttk.Label(dialog_frame, text=" ").grid(row=1, column=0, padx=5)
    ttk.Label(dialog_frame, text="Mouse").grid(row=1, column=1, padx=5)
    ttk.Label(dialog_frame, text="OD").grid(row=1, column=2, padx=5)
    ttk.Label(dialog_frame, text="OS").grid(row=1, column=3, padx=5)

    # Add instructions label
    instructions_label = ttk.Label(dialog_frame, text="OD and OS columns signify what images the\nprogram thinks you have. If wrong, click Edit\nto manually adjust.")
    instructions_label.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky="w")

    definition_of_acronymns = "\n".join([f"{value} = {key}" for key, value in location_mapping.items()])
    instructions_label2 = ttk.Label(dialog_frame, text=definition_of_acronymns)
    instructions_label2.grid(row=numberOfMice + 2, column=0, columnspan=4, padx=5, pady=5, sticky="w")

    entry_boxes = []
    for i in range(numberOfMice):
        ttk.Label(dialog_frame, text=str(i + 1)).grid(row=i + 2, column=0, padx=5)
        entry = ttk.Entry(dialog_frame)
        entry.grid(row=i + 2, column=1, padx=5)
        entry_boxes.append(entry)

        matching_item = next((item for item in eyeImagesList if item[0] == i + 1 and item[1] == "OD"), None)
        if matching_item:
            last_three_items = ", ".join(map(str, matching_item[2:]))
            ttk.Label(dialog_frame, text=last_three_items).grid(row=i + 2, column=2, padx=5)

        matching_item = next((item for item in eyeImagesList if item[0] == i + 1 and item[1] == "OS"), None)
        if matching_item:
            last_three_items = ", ".join(map(str, matching_item[2:]))
            ttk.Label(dialog_frame, text=last_three_items).grid(row=i + 2, column=3, padx=5)

    def onConfirmButtonClick(event=None):
        saveNumbers()
        root.destroy()

    def onEditButtonClick():
        saveNumbers()
        global edit
        edit = True
        root.destroy()

    save_button = ttk.Button(dialog_frame, text="Confirm", command=onConfirmButtonClick)
    save_button.grid(row=numberOfMice + 3, column=1, pady=10)

    edit_button = ttk.Button(dialog_frame, text="Edit", command=onEditButtonClick)
    edit_button.grid(row=numberOfMice + 3, column=2, pady=10)

    window.bind("<Escape>", onDialogClose)
    window.bind("<Return>", onConfirmButtonClick)
    window.bind("<Down>", onArrowKeyPress)
    window.bind("<Up>", onArrowKeyPress)

    window.grab_set()
    window.mainloop()

createMouseNumberDialogBox()

remove_underscores(inputted_mouse_numbers)  # This needs to be done because I count underscores later and I can't have the user adding them. I'll replace them later.

#Putting the inputted mouse numbers into a dictionary
i=1
mouseNumberDict = {}
for number in inputted_mouse_numbers:
    mouseNumberDict[i] = number
    i += 1

#Revising the annotatedList to include the real mouse numbers (or blanks if that was what was provided)
for sublist in annotated_list:
    newNumber = mouseNumberDict.get(sublist[4], "dialogBoxError")
    sublist[4] = newNumber


#If the user clicked on the "Edit" button in the previous dialog box, then this dialog box will appear
def createIndividualDialogBox(annotated_list):
    newannotated_list = []

    def onDialogClose2(event=None):
        window.destroy()
        window.master.destroy()
        exit()

    def onConfirmButtonClick2(event=None):
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

    def onArrowKeyPress(event): #This allows you to use the up and down arrow keys to navigate the entry boxes
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
    window.protocol("WM_DELETE_WINDOW", onDialogClose2)

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

    confirm_button = ttk.Button(dialog_frame, text="Confirm", command=onConfirmButtonClick2)
    confirm_button.grid(row=3, columnspan=4, pady=10)

    window.bind("<MouseWheel>", onScroll)
    window.bind("<Escape>", onDialogClose2)
    window.bind("<Return>", onConfirmButtonClick2)
    window.bind("<Down>", onArrowKeyPress)
    window.bind("<Up>", onArrowKeyPress)


    window.transient(window.master)
    window.grab_set()
    window.master.attributes("-alpha", 0)  # Set window opacity to 0 to make it invisible
    window.mainloop()

    return newannotated_list

if edit == True:
    newannotated_list = createIndividualDialogBox(annotated_list)
    annotated_list = newannotated_list


#Saving the annotated_list to a txt file in the image directory
annotated_text_file = "Annotated_list_of_files.txt" # Name of text file

filepath = f"{image_directory}/{annotated_text_file}" # Create the full path to the text file

# Open the file in write mode
with open(filepath, "w") as file:
    for sublist in annotated_list:
        # Convert the sublist to a string and write it to the file
        sublist_str = str(sublist)
        file.write(sublist_str)
        file.write('\n')  # Add a newline character after each sublist

print(f"Number of images found: {len(annotated_list)}")



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
            prompt = f"After clicking 'OK,' please select the location of the file called \"Open_OCT_file_imagej_supplement_1.2.\""
            return handle_key_input(prompt, "file")

        return None

imagej_location = identify_file_locations(preferences_variables, 'imagej_location')
screenshot_directory = identify_file_locations(preferences_variables, 'screenshot_directory')
macro_location = identify_file_locations(preferences_variables, 'macro_location')

macro_location = macro_location.replace("/", "\\")
imagej_location = imagej_location.replace("/", "\\")



# From 2.0.3b:

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
        logo_location = pyautogui.locateOnScreen(logo_path)
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
    image_location = pyautogui.locateOnScreen(image_path)
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

# Simulate keyboard actions
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
time.sleep(0.5)


# Press 'a' key to trigger the ImageJ macro that converts OCT images to TIF images
print("Sending command to ImageJ to convert OCT files to TIF files")
pyautogui.press('a')
start_time = time.time()

time.sleep(2)



#Now the program will monitor the conversion of TIF images and will proceed with the rest of the
#code when the proper amount of images have appeared in the folder

# Define the subdirectory
subdirectory = "initial_tif_images" #This was created in the ImageJ macro
initial_tif_images_directory = os.path.join(image_directory, subdirectory)

# Count the number of .tif files in the initial_tif_images_directory
file_count = sum(1 for file in os.listdir(initial_tif_images_directory) if file.endswith('.tif'))

# Wait until the count matches the number of sublists in annotated_list
while file_count != len(annotated_list):
    file_count = sum(1 for file in os.listdir(initial_tif_images_directory) if file.endswith('.tif'))
    time.sleep(0.1)

# Reporting that that process is done
end_time = time.time()
completion_time = int(end_time - start_time)
print(f"OCT files converted to TIF images. Time to completion: {completion_time} s")


if is_imagej_running():     # Making ImageJ the active program
    print("Sending command to ImageJ to crop TIF images")
else:
    show_error_message("ImageJ is no longer running. Program shutting down.")
    exit()



# Cropping the TIF images - this is done via ImageJ macro which is triggered by pressing 's'
pyautogui.press('s')
start_time = time.time()
time.sleep(1)

# Define the subdirectory
subdirectory = "cropped_tif_images" #This was created in the ImageJ macro
cropped_tif_images_directory = os.path.join(image_directory, subdirectory)

# Count the number of .tif files in the subdirectory
file_count = sum(1 for file in os.listdir(cropped_tif_images_directory) if file.endswith('.tif'))

# Wait until the count matches the number of sublists in annotated_list     # I don't think this is waiting a proper amount of time. Fix please
while file_count != len(annotated_list):
    file_count = sum(1 for file in os.listdir(cropped_tif_images_directory) if file.endswith('.tif'))
    time.sleep(0.1)

# Reporting that that process is done
end_time = time.time()
completion_time = int(end_time - start_time)
print(f"TIF images cropped. Time to completion: {completion_time} s")



delete_directory(initial_tif_images_directory)








#From 2.0.3c:

def rename_files(directory, annotated_list):    # This will convert the original file names into what I want the file names to be
    file_list = os.listdir(directory)
    file_count = len(file_list)

    for filename in file_list:
        individual_sequence_file_name = os.path.splitext(filename)[0]
        individual_sequence_file_name_base = individual_sequence_file_name[:-2]  # Remove the last 2 characters - the image number from the image sequence

        for sublist in annotated_list:
            annotated_file_name = sublist[0]
            annotated_list_name_without_extension = annotated_file_name[:-4]  # Remove the last 4 characters

            if individual_sequence_file_name_base == annotated_list_name_without_extension:
                eye = sublist[1]
                location = sublist[5]
                mouse_number = sublist[4]
                new_name = f"{mouse_number}_{eye}_{location}_{filename[-6:]}"
                break
        else:
            new_name = filename  # Use original filename if no match is found

        # Construct the full paths for the old and new names
        old_path = os.path.join(directory, filename)
        new_path = os.path.join(directory, new_name)

        # Rename the file
        os.rename(old_path, new_path)

    print(f"Renamed {file_count} files.")




# Renaming the individual sequence files
individual_sequence_images_directory = os.path.join(image_directory, "individual_sequence_images")
rename_files(individual_sequence_images_directory, annotated_list)    # This will convert the original file names into what I want the file names to be


# Deleting the unneeded horizontal images
def edit_and_delete_sequence_images(directory_path):
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


    horizontal_only_radial_images = []
    vertical_only_radial_images = []
    both_radial_images = []
    delete_radial_images = []

    horizontal_key = {}
    vertical_key = {}
    both_key = {}

    for i, location in enumerate(image_location_list):
        if scan_modes[i] == "radial":
            if horizontal_image_list[i] == "" and vertical_image_list[i] != "":
                vertical_only_radial_images.append(location)
                vertical_key[location] = vertical_image_list[i]
            elif vertical_image_list[i] == "" and horizontal_image_list[i] != "":
                horizontal_only_radial_images.append(location)
                horizontal_key[location] = horizontal_image_list[i]
            elif horizontal_image_list[i] != "" and vertical_image_list != "":
                both_radial_images.append(location)
                both_key[location] = [horizontal_image_list[i], vertical_image_list[i]]
            elif horizontal_image_list[i] == "" and vertical_image_list[i] == "":
                delete_radial_images.append(location)


    # Delete unnecessary files within each group
    for group_files in groups.values():
        # Determine the midpoint for the current group
        image_numbers = [int(file.split("_")[3].split(".")[0]) for file in group_files]
        midpoint = (max(image_numbers) + 1) // 2

        if len(group_files) > 0 and group_files[0].split("_")[2] in delete_radial_images:
            for file in group_files:
                file_path = os.path.join(directory_path, file)
                os.remove(file_path)

        # Delete files with image numbers less than the midpoint (deleting the horizontal images)
        if len(group_files) > 0 and group_files[0].split("_")[2] in vertical_only_radial_images:
            location = group_files[0].split("_")[2]
            for file in group_files:
                image_number = int(file.split("_")[3].split(".")[0])
                if image_number < midpoint:
                    file_path = os.path.join(directory_path, file)
                    os.remove(file_path)
                else:
                    new_name = file.replace(location, vertical_key[location])
                    new_path = os.path.join(directory_path, new_name)
                    os.rename(os.path.join(directory_path, file), new_path)

        # Delete files with image numbers greater than the midpoint (deleting the vertical images)
            # This only matters for radial images so if the user wants this they should just take linear images instead of taking radial and then deleting half of the image
        if len(group_files) > 0 and group_files[0].split("_")[2] in horizontal_only_radial_images:
            location = group_files[0].split("_")[2]
            print("horizontal:", midpoint)
            for file in group_files:
                image_number = int(file.split("_")[3].split(".")[0])
                if image_number >= midpoint:
                    file_path = os.path.join(directory_path, file)
                    os.remove(file_path)
                else:
                    new_name = file.replace(location, horizontal_key[location])
                    new_path = os.path.join(directory_path, new_name)
                    os.rename(os.path.join(directory_path, file), new_path)

        # Rename files if location is using both horizontal and vertical images
        for location in both_radial_images:
            if len(group_files) > 0 and group_files[0].split("_")[2] == location:
                for i, file in enumerate(group_files):
                    if i < midpoint:
                        new_name = file.replace(location, both_key[location][0])
                    else:
                        new_name = file.replace(location, both_key[location][1])

                    new_path = os.path.join(directory_path, new_name)
                    os.rename(os.path.join(directory_path, file), new_path)


# Initiating edit_and_delete_sequence_images()
edit_and_delete_sequence_images(individual_sequence_images_directory)
print("Deleted unneeded files and renamed radial files")




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
            averager_text_location = pyautogui.locateOnScreen(oct_volume_averager_text)
            if averager_text_location is None:
                averager_text_location = pyautogui.locateOnScreen(oct_volume_averager_text_alternate)
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
            read_setting_loation = pyautogui.locateOnScreen(os.path.join(screenshot_directory, "correct_read_setting.png")) or pyautogui.locateOnScreen(os.path.join(screenshot_directory, "correct_read_setting2.png"))
            if read_setting_loation is None:
                read_setting_loation = pyautogui.locateOnScreen(os.path.join(screenshot_directory, "incorrect_read_setting.png")) or pyautogui.locateOnScreen(os.path.join(screenshot_directory, "incorrect_read_setting2.png"))
                if read_setting_loation is None:
                    show_error_message("The script is unable to identify the read settings properly in the OCT Volume Averager box. Please select the correct setting before clicking okay.")
                if read_setting_loation is not None:
                    click_location = read_setting_loation.left + 10, read_setting_loation.top + 37
                    pyautogui.click(click_location)
                    time.sleep(5)


            # Checking and potentially changing the save setting
            save_setting_loation = pyautogui.locateOnScreen(os.path.join(screenshot_directory, "correct_save_setting.png")) or pyautogui.locateOnScreen(os.path.join(screenshot_directory, "correct_save_setting2.png"))
            if save_setting_loation is None:
                save_setting_loation = pyautogui.locateOnScreen(os.path.join(screenshot_directory, "incorrect_save_setting.png")) or pyautogui.locateOnScreen(os.path.join(screenshot_directory, "incorrect_save_setting2.png"))
                if save_setting_loation is None:
                    show_error_message("The script is unable to identify the save settings properly in the OCT Volume Averager box. Please select the correct setting before clicking okay.")
                if save_setting_loation is not None:
                    click_location = save_setting_loation.left + 10, save_setting_loation.top + 37
                    pyautogui.click(click_location)
                    time.sleep(5)


            # Locating the "okay" button
            pyautogui.moveTo(screen_width/2, 0)
            time.sleep(0.1)
            okay_button_location = pyautogui.locateOnScreen(os.path.join(screenshot_directory, "ok_button.png")) or pyautogui.locateOnScreen(os.path.join(screenshot_directory, "ok_button2.png"))
            if okay_button_location is None:
                show_error_message("The script is unable to locate the 'okay' button, either because it is being obscured or the style of the button has changed. If the later is the case, please take a screenshot of the button and save it in the ImageJ_clicking_files folder as ok_button.png. The script will now shut down.")


            # Checking the Options box
            options_box_loation = pyautogui.locateOnScreen(os.path.join(screenshot_directory, "correct_options_box_settings.png")) or pyautogui.locateOnScreen(os.path.join(screenshot_directory, "correct_options_box_settings2.png"))
            if options_box_loation is None:
                show_error_message("Incorrect settings are selected\nPlease make the following changes as needed:\n\nUncheck 'Inverted Image Stack (EDI)'\nUncheck 'Keep Intermediate .tiff Files'\nSet the 'Number of Pixels to Crop' to 0 for both boxes\n\nAlternatively, something is covering part of the OCT Volume Averager dialog box and the script is unable to complete its confirmation that the proper settings are selected. Please make sure the dialog box is not partially hidden.\n\nAnother possibility is the style of the box has changed. In which case you would need to take a screenshot of it and save it as correct_options_box_settings.png in ImageJ_clicking_files.\n\nClick the okay button in this dialog box when you have made the changes.")


            # Typing in the correct directories into the textboxes
            averager_text_right_coordinate = averager_text_location.left + averager_text_location.width
            averager_text_bottom_coordinate = averager_text_location.top + averager_text_location.height

            text_box_1 = averager_text_right_coordinate, averager_text_bottom_coordinate + 60
            pyautogui.click(text_box_1)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.typewrite(images_to_be_averaged_directory, interval=0.01)
            time.sleep(0.1)

            text_box_2 = text_box_1 = averager_text_right_coordinate, averager_text_bottom_coordinate + 180
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
        file_name = group_files[0][:-6] + "0.48mmdepth.tif"
        new_path = os.path.join(averaged_images_directory, file_name)

        time.sleep(0.5)
        os.rename(old_path, new_path)

        averaged_image_count += 1


        # Delete the "images_to_be_averaged" directory
        delete_directory(images_to_be_averaged_directory)



# Call the averaging_images function
averaging_images(individual_sequence_images_directory, image_directory)
time.sleep(1)   # Waiting one second in order to properly delete "rotatedRegAvgImg.tif"
averaged_images_directory = os.path.join(image_directory, "averaged_images")
os.remove(os.path.join(averaged_images_directory, "rotatedRegAvgImg.tif"))

# Creating an unaveraged image folder, if the user specified so
if unaveraged_images is True:
    unaveraged_images_directory = os.path.join(image_directory, "unaveraged_images")
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
if is_imagej_running():     # Making ImageJ the active program
    print("Sending command to ImageJ to enhance contrast")
    pyautogui.press('f') # to pay respects
    number_of_images = len([f for f in os.listdir(averaged_images_directory) if os.path.isfile(os.path.join(averaged_images_directory, f))])
    time.sleep(1 + (number_of_images * 0.08))
else:
    show_error_message("ImageJ is no longer running. Program shutting down.")
    exit()


# Putting images in subdirectory as specified by user
subfolder_exists = False    # this is just for the restore_underscore function down below
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

restore_underscores(averaged_images_directory)
if subfolder_exists:
    restore_underscores(subfolder_path)
if unaveraged_images is True:
    restore_underscores(unaveraged_images_directory)


# Deleting the intermediate directories
delete_directory(individual_sequence_images_directory)
annotated_text_file = os.path.join(image_directory, "Annotated_list_of_files.txt")
if os.path.exists(annotated_text_file):
    os.remove(annotated_text_file)
if os.path.exists(imagej_settings_file):
    os.remove(imagej_settings_file)
delete_directory(os.path.join(image_directory, "cropped_tif_images"))
