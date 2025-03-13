# Convert .OCT files to .TIF and .AVI files
 A script that uses python and ImageJ to convert .OCT files into .TIF and .AVI files, crops them to just include the retina, renames them to the user's specifications, and enhances contrast.

This program is initiated by running Open_OCT_file_2.2.2.py. That python script will automatically open up ImageJ and run the Open_OCT_file_imagej_supplement_1.3.ijm macro (also in this repository). The macro will need the following other macros (not in this repository) installed:
1. OCT volume averager (https://github.com/jaxcs/octvolavg)
2. TurboReg (made by P. Thévenaz and coworkers)
3. StackReg (made by P. Thévenaz and coworkers)

Please note that ImageJ must be used, not FIJI.

The python script uses keyboard and mouse inputs to control the ImageJ macro, so it is recommended that the user not use the computer while it is running. The python script recognizes where the ImageJ buttons are by looking for specific images found in ImageJ_clicking_files. These images may need to be updated if the ImageJ program used by the user looks different than the images in that directory.

Version 1.4 was developed specifically for our lab's imaging protocol and is unlikely to be helpful to other labs. It also requires the user click "okay" on the dialog box that comes up every 10 seconds or so, or the user can also run clickTheButton.py when needed. We recommend ignoring 1.4 and just using 2.2.2, which is made for more of the general public.
