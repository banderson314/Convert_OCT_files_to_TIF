# Process OCT files
 A script that uses python and ImageJ to convert .OCT files into .TIF files, crops them to just include the retina, renames them to the user's specifications, and enhances contrast.

This program is initiated by running Open_OCT_file_2.1.0.py. That python script will automatically open up ImageJ and run the Open_OCT_file_imagej_supplement_1.2.ijm macro (also in this repository). The macro will need the following other macros (not in this repository) installed:
1. 
2. 
3. 

Please note that ImageJ must be used, not FIJI.

Version 1.4 was developed specifically for our lab's imaging protocol and is unlikely to be helpful to other labs. It also requires the user click "okay" on the dialog box that comes up every 10 seconds or so, or the user can also run clickTheButton.py when needed. We recommend ignoring 1.4 and just using 2.1.0, which is made for more of the general public.
