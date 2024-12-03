var directory = "";
var total_min = 1577;
var total_max = 0;
var slice_mins = newArray();
var slice_maxes = newArray();


macro "Define directory [w]" {
  print("\\Clear");
  var directory = getDir("Select the location of the images");
  print("Location of images to process:");
  print(directory);
}


macro "Convert OCT and crop [a]" {
  print("\\Clear");
  print("Converting OCT files to TIF files: --");   // Line 0
  print("Cropping TIF files: --");   // Line 1
  print("Averaging files: --");   // Line 2
  print("Enhancing contrast: --");   // Line 3
  print("-------------------------------------");
  print("Converting OCT volume scans to AVI files: --");   // Line 5
  print("Cropping volume scans: --");   // Line 6
  print("Enhancing contrast of volume scans: --");   // Line 7

  setBatchMode(true);

  // Define the path to the text file of images
  image_path = directory + "Annotated_list_of_images.txt";
  image_file_content = File.openAsString(image_path);   // Read the text file as a string
  image_file_names = newArray();   // Create an empty list to store the extracted file names
  image_file_lines = split(image_file_content, "\n"); // Split the file content by newline character to get individual image_file_lines
  print("\\Update0:Converting OCT files to TIF files: 0/" + image_file_lines.length);
  if (image_file_lines.length == 0) {
    print("\\Update0:Converting OCT files to TIF files: No images found");
  }

  // Define the path to the text file of volume scans
  volume_path = directory + "Annotated_list_of_volume_scans.txt";
  volume_file_content = File.openAsString(volume_path);   // Read the text file as a string
  volume_file_names = newArray();   // Create an empty list to store the extracted file names
  volume_file_lines = split(volume_file_content, "\n"); // Split the file content by newline character to get individual image_file_lines
  print("\\Update5:Converting OCT volume scans to AVI files: 0/" + volume_file_lines.length);


  // Read min and max settings defined by user
  settings_file = directory + "ImageJ_settings.txt";
  settings_content = File.openAsString(settings_file);
  settings = split(settings_content, "\n");
  min_contrast = settings[1];  //Recommend 25
  max_contrast = settings[2];  //Recommend 215

  // Getting user input on how much cropping to do
  settings_file = directory + "ImageJ_settings.txt";
  settings_content = File.openAsString(settings_file);
  settings = split(settings_content, "\n");
  crop_amount = settings[0];
  crop_amount = parseInt(crop_amount);


  // Creating directories for the processed files
  cropped_tif_directory = directory + "cropped_tif_images";
  File.makeDirectory(cropped_tif_directory);
  individual_sequence_images = directory + File.separator + "individual_sequence_images";
  File.makeDirectory(individual_sequence_images);
  initial_avi_directory = directory + "volume_scans";
  File.makeDirectory(initial_avi_directory);


  // Processing radial and linear files
  if (image_file_lines.length > 0) {
    // Loop through each line to extract names of files
    for (i = 0; i < image_file_lines.length; i++) {
        elements = split(image_file_lines[i], ",");    // Split the line by comma to get individual elements

        // Extract the first element and remove the surrounding quotes
        fileName = replace(elements[0], "[", "");
        fileName = replace(fileName, "'", "");

        // Add the extracted file name to the image_file_names list
        image_file_names = Array.concat(image_file_names, fileName);
    }

    // Running through the list of images
    for (i = 0; i < image_file_names.length; i++) {
      oct_file = directory + image_file_names[i];

      run("OCT Reader", "select=[" + oct_file +"]");

      // Transforming the image
      run("Flip Vertically", "stack");
      run("Scale...", "x=- y=1.54 z=- width=640 height=1577 interpolation=Bilinear average process create");
      close("Oct Intensity Stack");


      // Cropping the image

      slice_mins = newArray();
      slice_maxes = newArray();
      total_min = 1577;
      total_max = 0;
  
      for (j=50; j<630; j+=50) {
          find_retina_boundary(j);
      }

      // Replacing total_min with lower min from slice, if within standard deviation of other mins
      Array.getStatistics(slice_mins, _, _, slice_min_mean, slice_min_std);
      for (k=0; k < slice_mins.length; k++) {
          if (slice_mins[k] > slice_min_mean - slice_min_std){
              if (slice_mins[k] < total_min) {
                  total_min = slice_mins[k];
              }
          }
      }
      
      // Replacing total_max with lower max from slice, if within standard deviation of other maxes
      Array.getStatistics(slice_maxes, _, _, slice_max_mean, slice_max_std);
      for (k=0; k < slice_maxes.length; k++) {
          if (slice_maxes[k] < slice_max_mean + slice_max_std){
              if (slice_maxes[k] > total_max) {
                  total_max = slice_maxes[k];
              }
          }
      }

    height = total_max - total_min;
    if (height < crop_amount) {
        middle_of_crop_image = total_min + (height / 2);
        total_min = middle_of_crop_image - (crop_amount / 2);
        height = crop_amount;
    }

    makeRectangle(0, total_min, 640, height);
    run("Crop");
    print("\\Update1:Cropping TIF files: " + i+1 + "/" + image_file_names.length);


    //Saving the images as tif files
    tif_file_name = replace(image_file_names[i], ".OCT", "");
    saveLocation = cropped_tif_directory + File.separator + tif_file_name;


    saveAs("Tiff", saveLocation);
    run("Image Sequence... ", "dir=&individual_sequence_images format=TIFF digits=4");  //saving the individual files
    close("*");

    print("\\Update0:Converting OCT files to TIF files: " + i+1 + "/" + image_file_lines.length);
    }
  }





  // Volume scans: reading .OCT files
  if (volume_file_lines.length > 0) {
    // Loop through each line
    for (i = 0; i < volume_file_lines.length; i++) {
      elements = split(volume_file_lines[i], ",");    // Split the line by comma to get individual elements

      // Extract the first element and remove the surrounding quotes
      fileName = replace(elements[0], "[", "");
      fileName = replace(fileName, "'", "");

      // Add the extracted file name to the volume_file_names list
      volume_file_names = Array.concat(volume_file_names, fileName);
    }

    // Running through the list of files
    for (i = 0; i < volume_file_names.length; i++) {
      oct_file = directory + volume_file_names[i];

      run("OCT Reader", "select=[" + oct_file +"]");

      // Transforming and changing contrast
      run("Scale...", "x=- y=1.54 z=1.0 width=640 height=1577 interpolation=Bilinear average process create");
      run("Flip Vertically", "stack");
      setMinAndMax(min_contrast, max_contrast);
      run("Apply LUT", "stack");
      print("\\Update7:Enhancing contrast of volume scans: " + i+1 + "/" + volume_file_names.length);

      
      // Cropping the volume scan
      total_min = 1577;
      total_max = 0;
      for (a=1; a <= nSlices; a++) {
          setSlice(a);
          slice_mins = newArray();
          slice_maxes = newArray();

          for (j=50; j<630; j+=50) {
              find_retina_boundary(j);
          }

          // Replacing total_min with lower min from slice, if within standard deviation of other mins
          Array.getStatistics(slice_mins, _, _, slice_min_mean, slice_min_std);
          for (k=0; k < slice_mins.length; k++) {
              if (slice_mins[k] > slice_min_mean - slice_min_std){
                  if (slice_mins[k] < total_min) {
                      total_min = slice_mins[k];
                  }
              }
          }
          
          // Replacing total_max with lower max from slice, if within standard deviation of other maxes
          Array.getStatistics(slice_maxes, _, _, slice_max_mean, slice_max_std);
          for (k=0; k < slice_maxes.length; k++) {
              if (slice_maxes[k] < slice_max_mean + slice_max_std){
                  if (slice_maxes[k] > total_max) {
                      total_max = slice_maxes[k];
                  }
              }
          }
      }
      height = total_max - total_min;
      if (height < crop_amount) {
          middle_of_crop_image = total_min + (height / 2);
          total_min = middle_of_crop_image - (crop_amount / 2);
          height = crop_amount;
      }

      makeRectangle(0, total_min, 640, height);
      run("Crop");
      print("\\Update6:Cropping volume scans: " + i+1 + "/" + volume_file_names.length);


      //Saving the images as avi files
      avi_file_name = replace(volume_file_names[i], ".OCT", ".avi");
      save_location = initial_avi_directory + File.separator + avi_file_name;

      run("AVI... ", "compression=JPEG frame=7 save=[" + save_location + "]");
      close("*");
      
      print("\\Update5:Converting OCT volume scans to AVI files: " + i+1 + "/" + volume_file_lines.length);
    }

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

    // Extract the common part of the file_names and count unique occurrences
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

  settings_file = directory + "ImageJ_settings.txt";
  settings_content = File.openAsString(settings_file);
  settings = split(settings_content, "\n");
  min_contrast = settings[1]; //Recommend 25
  max_contrast = settings[2];  //Recommend 215

  for (i = 0; i < averaged_images.length; i++) {
    open(averaged_directory + File.separator + averaged_images[i]);
    setMinAndMax(min_contrast, max_contrast);
    run("Apply LUT");
    run("Save");
    close();
    print("\\Update3:Enhancing contrast of TIF files: " + i+1 + "/" + averaged_images.length);
  }
  setBatchMode(false);
}





// Function to find the retina boundary:

function find_retina_boundary(line_x_axis) {
  makeLine(line_x_axis, 0, line_x_axis, 1577);
  profile = getProfile();
  Array.getStatistics(profile, _, _, mean, std);
  cutoff = 1.5*std + mean;  // cutoff is defining the minimum brightness to be considered relevant
  if (cutoff < 50) {
      cutoff = 50;    // If the cutoff is less than 50, then there likely isn't any signal to pick up
  }
  start_point = 50;   // Ignore the top 50 pixels
  top_intensities = newArray();
  for (j = 50; j < profile.length; j++) {
      if (profile[j] > cutoff) {
          top_intensities = Array.concat(top_intensities, j);
      }
  }
  
  if (top_intensities.length > 0) {
      //Finding the middle of the retina
      middle_number = top_intensities.length / 2;   //This gives the median value, which works better than the mean
      middle_of_retina = top_intensities[middle_number];


      //Making the box around the retina
      initial_crop_amount = 480;
      half_of_crop_amount = initial_crop_amount / 2;
      top_of_crop = middle_of_retina - half_of_crop_amount - 10;
      if (top_of_crop < 0) {
          top_of_crop = 0;
      }

      makeLine(line_x_axis, top_of_crop, line_x_axis, top_of_crop + initial_crop_amount);


      shortened_profile = getProfile();
      Array.getStatistics(shortened_profile, _, _, shortened_mean, shortened_std);
      shortened_cutoff = 1.5*shortened_std + shortened_mean;
      if (shortened_cutoff < 50) {
          shortened_cutoff = 50;    // If the cutoff is less than 50, then there likely isn't any signal to pick up
      }

      shortened_top_intensities = newArray();
      for (j = 0; j < shortened_profile.length; j++) {
          if (shortened_profile[j] > cutoff) {
              shortened_top_intensities = Array.concat(shortened_top_intensities, j);
          }
      }


      Array.getStatistics(shortened_top_intensities, shortened_min, shortened_max, _, _);
      shortened_min = shortened_min + top_of_crop;
      shortened_max = shortened_max + top_of_crop;
      slice_mins = Array.concat(slice_mins, shortened_min);
      slice_maxes = Array.concat(slice_maxes, shortened_max);


  }
}
