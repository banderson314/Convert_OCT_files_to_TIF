macro "Reinstall this [q]" {
  run("Install...", "install=[U:/ImageJ/ImageJ/macros/Made_by_Brandon/OCT download program/Open_OCT_file_imagej_supplement_1.2.ijm]");
}

var directory = "";

macro "Define directory [w]" {
  var directory = getDir("Select the location of the images");
}


macro "Convert OCT to TIF [a]" {
  print("\\Clear");
  print("Converting OCT files to TIF files: --");
  print("Cropping TIF files: --");
  print("Averaging files: --");
  print("Enhancing contrast: --");

  setBatchMode(true);

  // Define the path to the text file
  path = directory + "Annotated_list_of_files.txt";
  fileContent = File.openAsString(path);   // Read the text file as a string
  fileNames = newArray();   // Create an empty list to store the extracted file names
  lines = split(fileContent, "\n"); // Split the file content by newline character to get individual lines
  print("\\Update0:Converting OCT files to TIF files: 0/" + lines.length);

  // Loop through each line
  for (i = 0; i < lines.length; i++) {
      elements = split(lines[i], ",");    // Split the line by comma to get individual elements

      // Extract the first element and remove the surrounding quotes
      fileName = replace(elements[0], "[", "");
      fileName = replace(fileName, "'", "");

      // Add the extracted file name to the fileNames list
      fileNames = Array.concat(fileNames, fileName);
  }

  // Making directory for tif images
  initial_tif_directory = directory + "initial_tif_images";
  File.makeDirectory(initial_tif_directory);


  // Running through the list of files
    for (i = 0; i < fileNames.length; i++) {
      octFile = directory + fileNames[i];

      run("OCT Reader", "select=[" + octFile +"]");

      //Saving the images as tif files
      tifFileName = replace(fileNames[i], ".OCT", "");
      saveLocation = initial_tif_directory + File.separator + tifFileName;


      saveAs("Tiff", saveLocation);

      close();
      print("\\Update0:Converting OCT files to TIF files: " + i+1 + "/" + lines.length);
  }
  setBatchMode(false);
}





macro "Crop TIF files [s]" {
  print("\\Update1:Cropping TIF files");

  setBatchMode(true);

  // Define the path to the text file and create new directory
  initial_tif_directory = directory + File.separator + "initial_tif_images";
  cropped_tif_images = directory + File.separator + "cropped_tif_images";
  File.makeDirectory(cropped_tif_images);
  individual_sequence_images = directory + File.separator + "individual_sequence_images";
  File.makeDirectory(individual_sequence_images);


  list_of_tifs = getFileList(initial_tif_directory);
  print("\\Update1:Cropping TIF files: 0/" + list_of_tifs.length);


  for (i = 0; i < list_of_tifs.length; i++) {
    file = initial_tif_directory + File.separator + list_of_tifs[i];
    newFile = cropped_tif_images + File.separator + list_of_tifs[i];

    open(file);

    run("Flip Vertically", "stack");
    run("Scale...", "x=- y=1.54 z=- width=640 height=1577 interpolation=Bilinear average process create");
    close("Oct Intensity Stack");


    //Getting the grey values from once vertical slice of the image
    makeLine(200, 0, 200, 1577);
    profile = getProfile();


    //Figuring out where the top intensities are
    Array.getStatistics(profile, min, max, mean, std);
    cutoff = 1.5*std + mean;

    topIntensities = newArray();
    for (j = 0; j < profile.length; j++) {
      if (profile[j] > cutoff) {
        topIntensities = Array.concat(topIntensities, j);
      }
    }

    //Finding the middle of the retina
    middleNumber = topIntensities.length / 2;   //This gives the median value, which works better than the mean
    middleOfRetina = topIntensities[middleNumber];


    //Making the box around the retina
    y = middleOfRetina - 250;
    makeRectangle(0, y, 640, 480);


    //Cropping the file to just have the retina
    run("Crop");
    saveAs("Tiff", newFile);
    run("Image Sequence... ", "dir=&individual_sequence_images format=TIFF digits=2");  //saving the individual files
    close("*");
    print("\\Update1:Cropping TIF files: " + i+1 + "/" + list_of_tifs.length);
  }
  setBatchMode(false);
}

var averaging_count = 0;
var number_of_averaged_images = 0;

macro "Averaging TIF images [d]" {

  if (averaging_count == 0) {
    // Figuring out how many files there are total
    individual_sequence_directory = directory + File.separator + "individual_sequence_images";
    list_of_individual_sequence_files = getFileList(individual_sequence_directory);

    uniqueCommonParts = newArray();

    // Extract the common part of the filenames and count unique occurrences
    for (i = 0; i < list_of_individual_sequence_files.length; i++) {
      already_there = false;

      filename = list_of_individual_sequence_files[i];
      commonPart = substring(filename, 0, filename.length - 6);

      // Check if the common part is already in the uniqueCommonParts array
      for (j = 0; j < uniqueCommonParts.length; j++) {
        if (commonPart == uniqueCommonParts[j]) {
          already_there = true;
        }
      }
      if (already_there == false) {
        uniqueCommonParts = Array.concat(uniqueCommonParts, commonPart);
      }
    }

    var number_of_averaged_images = uniqueCommonParts.length;
    print("\\Update2:Averaging files: " + averaging_count + "/" + number_of_averaged_images);
  }

  // Actually running the key part of this macro
  run("Register and Average Image Stacks");
  var averaging_count = averaging_count + 1;
  print("\\Update2:Averaging files: " + averaging_count + "/" + number_of_averaged_images);
}


macro "Enhancing contrast [f]" {
  setBatchMode(true);
  averaged_directory = directory + File.separator + "averaged_images";
  averaged_images = getFileList(averaged_directory);

  settings_file = directory + "ImageJ_contrast_settings.txt"
  settings_content = File.openAsString(settings_file)
  settings = split(settings_content, "\n");
  min_contrast = settings[0]  //Recommend 25
  max_contrast = settings[1]  //Recommend 215

  for (i = 0; i < averaged_images.length; i++) {
    open(averaged_directory + File.separator + averaged_images[i]);
    setMinAndMax(min_contrast, max_contrast);
    run("Apply LUT");
    run("Save");
    close();
    print("\\Update3:Enhancing contrast: " + i+1 + "/" + averaged_images.length);
  }
  setBatchMode(false);
}