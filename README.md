# Convert .OCT files to .TIF files
 A script that uses python and ImageJ to convert .OCT files into .TIF files, crops them to just include the retina, renames them to the user's specifications, and enhances contrast.

This program is initiated by running Open_OCT_file_2.1.0.py. That python script will automatically open up ImageJ and run the Open_OCT_file_imagej_supplement_1.2.ijm macro (also in this repository). The macro will need the following other macros (not in this repository) installed:
1. OCT volume averager (https://github.com/jaxcs/octvolavg)
2. TurboReg (made by P. Thévenaz and coworkers)
3. StackReg (made by P. Thévenaz and coworkers)

Please note that ImageJ must be used, not FIJI.

The python script uses keyboard and mouse inputs to control the ImageJ macro, so it is recommended that the user not use the computer while it is running. The python script recognizes where the ImageJ buttons are by looking for specific images found in ImageJ_clicking_files. These images may need to be updated if the ImageJ program used by the user looks different than the images in that directory.

Version 1.4 was developed specifically for our lab's imaging protocol and is unlikely to be helpful to other labs. It also requires the user click "okay" on the dialog box that comes up every 10 seconds or so, or the user can also run clickTheButton.py when needed. We recommend ignoring 1.4 and just using 2.1.0, which is made for more of the general public.

Open_OCT_file_2.2.0.py was added later with the ability to convert volume scans into .avi files, among other QOL additions. It goes with the Open_OCT_file_imagej_supplement_1.3.ijm macro. Please note that there are a couple minor bugs that still need to be worked out with this addition.
