# Convert .OCT files to .TIF and .AVI files
 A script that uses python and ImageJ to convert .OCT files into .TIF and .AVI files, crops them to just include the retina, renames them to the user's specifications, and enhances contrast.

This program is initiated by running the python file convert_OCT_files.py. That python script will automatically open up ImageJ and run the convert_OCT_files_imagej_supplement.ijm macro (also in this repository). The macro will need the following other macros (not in this repository) downloaded to the user's ImageJ macro folder:
1. OCT volume averager (https://github.com/jaxcs/octvolavg)
2. TurboReg (made by P. Thévenaz and coworkers)
3. StackReg (made by P. Thévenaz and coworkers)

Please note that ImageJ must be used, not FIJI.

The python script uses keyboard and mouse inputs to control the ImageJ macro, so it is recommended that the user not use the computer while it is running. The python script recognizes where the ImageJ buttons are by looking for specific images found in ImageJ_clicking_files. These images may need to be updated if the ImageJ program used by the user looks different than the images in that directory.

If you use this software to process data for any publication, please cite this code (see CITATION.cff or the "Cite this repository" option in the About section). In addition, because this code uses the OCT Volume Averager plugin, please cite these papers as well: 

        P. Thévenaz, U.E. Ruttimann, M. Unser, A Pyramid Approach to Subpixel
        Registration Based on Intensity. IEEE Transactions on Image
        Processing, vol. 7, no. 1, pp. 27-41, January 1998. 

        M.P. Krebs, M. Xiao, K. Sheppard, W. Hicks, P.M. Nishina, Bright-Field
        Imaging and Optical Coherence Tomography of the Mouse Posterior Eye.
        Methods in Molecular Biology. 2016;1438:
        DOI: 10.1007/978-1-4939-3661-8_20
