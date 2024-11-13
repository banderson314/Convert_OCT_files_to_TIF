//Converting OCT files to tif files
//Made by Brandon Anderson, University of Pennsylvania
//Last updated on April 5, 2023

//For this macro to work, you need the OCT reader plugin and the OCT averager plugin



macro "Close all images [e]" {
  close("*");
}


macro "Enhance contrast and brightness [s]" {
  fileLocation = getDir("Choose which folder of images to change contrast");
  fileList = getFileList(fileLocation);

  Dialog.create("Contrast numbers");

  Dialog.addMessage("Min and max pixel values. \n0 and 255 are original values. 25 and 215 are recommended.");
  min = 25; max = 215; type = "tif";
  Dialog.addNumber("Min: ", min);
  Dialog.addNumber("Max: ", max);
  Dialog.addString("File type: ", type);

  Dialog.show();

  minContrast = Dialog.getNumber();
  maxContrast = Dialog.getNumber();
  imageType = Dialog.getString();

  for (i = 0; i < fileList.length; i++) {
    if (indexOf(fileList[i], imageType) >= 0) {
      open(fileLocation + File.separator + fileList[i]);
      setMinAndMax(minContrast, maxContrast);
      run("Apply LUT");
      run("Save");
      close();
    }
  }

}




function savingFilesAsSeparateImages() {
  fileName = "Temp";
  parentDirectory = File.getParent(File.directory);
  tempFilePath = parentDirectory + File.separator + "Temporary files" + File.separator;

  File.makeDirectory(tempFilePath);

  fileDirName = tempFilePath + fileName + ".tif";
  saveAs("Tiff", fileDirName);
  run("Image Sequence... ", "dir=&tempFilePath format=TIFF digits=2");
  ok = File.delete(fileDirName);
  close("*");
  return tempFilePath;
}



function averaging(location) {
  //****************Using the averaging macro****************
  list = getFileList(tempFilePath);
  for (i = 0; i < list.length; i++) {
    tempFile = tempFilePath + list[i];
    open(tempFile);
  }
  run("Register and Average Image Stacks");
  close("Temp*");

  selectWindow("rotatedRegAvgImg");
  close();
  selectWindow("regAvgImg");


  //****************Figuring out final name of file****************
  if (location == "tnsi") {
    i = saveTheI;
    for (j = 0; j < revisedFileList.length; j++) {
      if (indexOf(revisedFileList[j], fileList[i]) >= 0) {

        endOfFinalName = indexOf(revisedFileList[j], "depth") + 5;
        finalName = File.separator + "Peripheral images" + File.separator + substring(revisedFileList[j], 0, endOfFinalName);
      }
    }
  }

  if (location == "vertical") {
    i = saveTheI;
    for (j = 0; j < revisedFileList.length; j++) {
      if (indexOf(revisedFileList[j], fileList[i]) >= 0) {

        endOfFinalName = indexOf(revisedFileList[j], "depth") + 5;
        finalName = substring(revisedFileList[j], 0, endOfFinalName);
        finalName = replace(finalName, "central", "vertical");
      }
    }
  }

  if (location == "horizontal") {
    i = saveTheI;
    for (j = 0; j < revisedFileList.length; j++) {
      if (indexOf(revisedFileList[j], fileList[i]) >= 0) {

        endOfFinalName = indexOf(revisedFileList[j], "depth") + 5;
        finalName = substring(revisedFileList[j], 0, endOfFinalName);
        finalName = replace(finalName, "central", "horizontal");
      }
    }
  }



  //****************Enhancing the contrast****************
  setMinAndMax(minContrast, maxContrast);
  run("Apply LUT");


  //****************Saving the final file****************
  saveAs("Tiff", finishedFileLocation + File.separator + finalName + ".tif");
  close();


  //****************Saving one of the unaveraged files****************

  list = getFileList(tempFilePath);

  tempFileWithPath = tempFilePath + list[0];
  open(tempFileWithPath);
  setMinAndMax(minContrast, maxContrast);
  run("Apply LUT");
  saveAs("Tiff", finishedFileLocation + File.separator + "Unaveraged images" + File.separator + finalName + ".tif");
  close();

  //****************Deleting the temporary files****************

  for (a = 0; a < list.length; a++) {
    ok = File.delete(tempFilePath + list[a]);
    }
  ok = File.delete(tempFilePath);

} //end of the function



function previouslyAveragedFiles(location) {

  if (location == "temporalOrNasal") {
    i = saveTheI;
    for (j = 0; j < revisedFileList.length; j++) {  // Figuring out the final name of the file
      if (indexOf(revisedFileList[j], fileList[i]) >= 0) {
        endOfFinalName = indexOf(revisedFileList[j], "depth") + 5;
        finalName = File.separator + "Peripheral images" + File.separator + substring(revisedFileList[j], 0, endOfFinalName);
      }
    }
    setMinAndMax(minContrast, maxContrast);  //Enhancing the contrast
    run("Apply LUT");

    saveAs("Tiff", finishedFileLocation + File.separator + finalName + ".tif"); //saving the final file
    close();
  }



  if (location == "central") {
    i = saveTheI;
    for (j = 0; j < revisedFileList.length; j++) {  // Figuring out the final name of the file
      if (indexOf(revisedFileList[j], fileList[i]) >= 0) {
        endOfFinalName = indexOf(revisedFileList[j], "depth") + 5;
        finalName = substring(revisedFileList[j], 0, endOfFinalName);
      }
    }

    tempFilePath = savingFilesAsSeparateImages(); //Saving each of the two files into separate files

    list = getFileList(tempFilePath);
    open(tempFilePath + File.separator + list[0]);   // Opening up the horizontal image
    finalName = replace(finalName, "central", "horizontal");
    setMinAndMax(minContrast, maxContrast);
    run("Apply LUT");
    saveAs("Tiff", finishedFileLocation + File.separator + finalName + ".tif");
    close();

    open(tempFilePath + File.separator + list[1]);   // Opening up the vertical image
    finalName = replace(finalName, "horizontal", "vertical");
    setMinAndMax(minContrast, maxContrast);
    run("Apply LUT");
    saveAs("Tiff", finishedFileLocation + File.separator + finalName + ".tif");
    close();

    for (a = 0; a < list.length; a++) {     //Deleting the temporary files
      ok = File.delete(tempFilePath + list[a]);
      }
    ok = File.delete(tempFilePath);
  }



  if (location == "superiorOrInferior") {
  i = saveTheI;
  for (j = 0; j < revisedFileList.length; j++) {  // Figuring out the final name of the file
    if (indexOf(revisedFileList[j], fileList[i]) >= 0) {
      endOfFinalName = indexOf(revisedFileList[j], "depth") + 5;
      finalName = substring(revisedFileList[j], 0, endOfFinalName);
    }
  }

  tempFilePath = savingFilesAsSeparateImages(); //Saving each of the two files into separate files

  list = getFileList(tempFilePath);
  open(tempFilePath + File.separator + list[1]);   // Opening up the vertical image
  setMinAndMax(minContrast, maxContrast);
  run("Apply LUT");
  saveAs("Tiff", finishedFileLocation + File.separator + finalName + ".tif");
  close();

  for (a = 0; a < list.length; a++) {     //Deleting the temporary files
    ok = File.delete(tempFilePath + list[a]);
    }
  ok = File.delete(tempFilePath);
  }
}







macro "Open OCT files [a]" {

  //****************Selecting a directory to work from****************

  OCTFileLocation = getDir("Choose a directory with your OCT files");
  finishedFileLocation = getDir("Choose a directory for processed files");
  File.makeDirectory(finishedFileLocation + File.separator + "Peripheral images");
  File.makeDirectory(finishedFileLocation + File.separator + "Unaveraged images");
  File.makeDirectory(finishedFileLocation + File.separator + "Unaveraged images" + File.separator + "Peripheral images");
  fileList = getFileList(OCTFileLocation);
  parentDirectory = File.getParent(File.directory);


  //****************Removing files from fileList if its averaged file is present****************
  noRepeatFileList = fileList;
  for (i = 0; i < fileList.length; i++) {
    startOfIDNumber = indexOf(fileList[i], "000");
    endOfIDNumber = indexOf(fileList[i], ".OCT");
    IDNumber = substring(fileList[i], startOfIDNumber, endOfIDNumber);

    for (j = 0; j < fileList.length; j++) {
      if(indexOf(fileList[j], IDNumber) >= 0 && j != i && indexOf(fileList[j], "RegAvg") < 0) {
        noRepeatFileList = Array.deleteValue(noRepeatFileList, fileList[j]);
      }
    }
  }
  fileList = noRepeatFileList;


  //****************Rename OCT file names****************

  orderedFileList = newArray();

  //****************Putting the ordered number in the front of the file****************
  for (i = 0; i < fileList.length; i++) {
    startOfIDNumber = indexOf(fileList[i], "000");
    endOfIDNumber = indexOf(fileList[i], ".OCT");
    IDNumber = substring(fileList[i], startOfIDNumber, endOfIDNumber);
    rearrangedName = IDNumber + "_" + fileList[i];
    orderedFileList = Array.concat(orderedFileList, rearrangedName);
  }

  //Ordering the array in numerical order
  orderedFileList = Array.sort(orderedFileList);


  //****************Determining number of mice****************
  count = 1
  previousEye = substring(orderedFileList[0], indexOf(orderedFileList[0], "_O") + 1, indexOf(orderedFileList[0], "_O") + 3);

  for (i = 0; i < orderedFileList.length; i++) {
    eye = substring(orderedFileList[i], indexOf(orderedFileList[i], "_O") + 1, indexOf(orderedFileList[i], "_O") + 3);

    if (eye != previousEye && previousEye == "OS") {
      count = count + 1;
    }
    previousEye = eye;
  }

  //****************Having the user input the mouse names/numbers****************
  Dialog.create("Mice");
  Dialog.addMessage("Fill in the mouse numbers in the order they were taken with the OCT camera.");
  Dialog.addMessage("Number of mice found: " + count);
  for (i = 0; i < count; i++) {
    Dialog.addString("Mouse " + i+1, "");
  }
  Dialog.addMessage("Min and max pixel values. \n0 and 255 are original values. 25 and 215 are recommended.");
  min = 25; max = 215;
  Dialog.addNumber("Min: ", min);
  Dialog.addNumber("Max: ", max);

  Dialog.show();

  mouseNumbers = newArray();
  for (i = 0; i < count; i++) {
    mouseNumbers = Array.concat(mouseNumbers, Dialog.getString());
  }

  minContrast = Dialog.getNumber();
  maxContrast = Dialog.getNumber();


  //****************Adding mouse numbers to the file names****************
  //****************Creating a revised file list****************
  j = 0   // j represents the mouse number, from 0 to whatever, in order of mice imaged by the OCT
  radialScanCount = 0
  linearScanCount = 0
  revisedFileList = newArray();
  previousEye = substring(orderedFileList[0], indexOf(orderedFileList[0], "_O") + 1, indexOf(orderedFileList[0], "_O") + 3);

  for (i = 0; i < orderedFileList.length; i++) {
    eye = substring(orderedFileList[i], indexOf(orderedFileList[i], "_O") + 1, indexOf(orderedFileList[i], "_O") + 3);

    //****Determining if a new mouse happens and changing variable when it does****
    if (eye != previousEye && previousEye == "OS") {
      j = j + 1;
    }

    //****Determining if a new eye happens and changing variable when it does****
    if (eye != previousEye) {
      radialScanCount = 0;
      linearScanCount = 0;
    }

    //****Assigning orientation****
    if(indexOf(orderedFileList[i], "_R_") >=0 && radialScanCount == 2) {
      orientation = "inferior";
      radialScanCount = radialScanCount + 1;
    }
    if(indexOf(orderedFileList[i], "_R_") >=0 && radialScanCount == 1) {
      orientation = "superior";
      radialScanCount = radialScanCount + 1;
    }
    if(indexOf(orderedFileList[i], "_R_") >=0 && radialScanCount == 0) {
      orientation = "central";
      radialScanCount = radialScanCount + 1;
    }
    if(indexOf(orderedFileList[i], "_L_") >=0 && linearScanCount == 1) {
      orientation = "nasal";
      linearScanCount = linearScanCount + 1;
    }
    if(indexOf(orderedFileList[i], "_L_") >=0 && linearScanCount == 0) {
      orientation = "temporal";
      linearScanCount = linearScanCount + 1;
    }

    //****Putting the file names in an array called revisedFileList****
    revisedFileList = Array.concat(revisedFileList, mouseNumbers[j] + "_" + eye + "_" + orientation + "_" + "0.48mmdepth_" + orderedFileList[i]);
    previousEye = eye;
  }



  //****************Reporting how many files are going to be processed****************

  trueLength = 0
  for (i=0; i < fileList.length; i++) {
    if (indexOf(fileList[i], "_V_") >= 0 || indexOf(fileList[i], ".OCT") < 0) {
      continue;
    }
    trueLength = trueLength + 1;
  }

  for (i=0; i < revisedFileList.length; i++) {
    if (indexOf(revisedFileList[i], "central") >= 0) {
      trueLength = trueLength + 1;
      }
  }

  print("\\Clear");
  if (trueLength == 0) {
    print("No valid files found");
  } else {
    print("Beginning to process " + trueLength + " files");
  }

  startTime = getTime();
  trueFileNumber = 0; //this is i, but doesn't include the volume scans or non .OCT files. This variable is just for progress updates.


  //****************Running through each file in the directory - this is the bulk of the macro****************

  for (i = 0; i < fileList.length; i++) {

    saveTheI = i; //This is used because i is  part of the loop currently underway but I want to use it for loops within this loop

    if (indexOf(fileList[i], "RegAvg") >= 0) {
      isItRegAvg = "yes";
    } else {
      isItRegAvg = "no";
    }

    //****************Skipping over the volume scans and non OCT files****************

    if (indexOf(fileList[i], "_V_") >= 0 || indexOf(fileList[i], ".OCT") < 0) {
      continue;
    }


    //****************Reporting progress****************

    if (trueFileNumber > 0) {
      newerTime = getTime();
      estimate = round(((newerTime - olderTime)/1000)*(trueLength - trueFileNumber));
      if (estimate < 61) {
        print("\\Update0:" + trueFileNumber + "/" + trueLength + " files complete");
        print("\\Update1:Estimated time to completion: " + estimate + " s");
      } else {
        minuteEstimate = floor(estimate/60);
        remainderEstimate = round((estimate/60 - minuteEstimate) * 60);
        print("\\Update0:" + trueFileNumber + "/" + trueLength + " files complete");
        print("\\Update1:Estimated time to completion: " + minuteEstimate + " m " + remainderEstimate + " s");
      }
    }
    currentTime = getTime();
    totalTime = (currentTime - startTime)/1000;
    totalMinute = floor(totalTime/60);
    totalSecondRemainder = round((totalTime/60 - totalMinute)*60);
    if (totalMinute > 0) {
      print("\\Update2:Elapsed time so far: " + totalMinute + " m " + totalSecondRemainder + " s");
    } else {
      print("\\Update2:Elapsed time so far: " + totalSecondRemainder + " s");
    }
    olderTime = getTime();


    //****************Opening up the file and putting it in proper orientation****************

    currentFile = fileList[i];
    run("OCT Reader", "select=[" + OCTFileLocation + currentFile + "]");

    run("Flip Vertically", "stack");
    run("Scale...", "x=- y=1.54 z=- width=640 height=1577 interpolation=Bilinear average process create");
    close("Oct Intensity Stack");


    //****************START OF FIGURING OUT WHERE THE RETINA IS****************
    //****************Getting the grey values from once vertical slice of the image****************
    makeLine(200, 0, 200, 1577);
    profile = getProfile();


    //****************Figuring out where the top intensities are****************
    Array.getStatistics(profile, min, max, mean, std);
    cutoff = 1.5*std + mean;

    topIntensities = newArray();
    for (i = 0; i < profile.length; i++) {
      if (profile[i] > cutoff) {
        topIntensities = Array.concat(topIntensities, i);
      }
    }

    //****************Finding the middle of the retina****************
    middleNumber = topIntensities.length / 2;   //This gives the median value, which works better than the mean
    middleOfRetina = topIntensities[middleNumber];
    //Array.getStatistics(topIntensities, min, max, mean, std);  //This way would take the mean, but I don't think that works as well
    //middleOfRetina = round(mean);

    //****************STOP OF FIGURING OUT WHERE THE RETINA IS****************

    //****************Making the box around the retina****************
    y = middleOfRetina - 250;
    makeRectangle(0, y, 640, 480);



    //****************Cropping the file to just have the retina****************
    run("Crop");


    //****************Saving the files as separate images****************
    if (isItRegAvg == "no") {  //it will only do this if the image isn't already averaged
      tempFilePath = savingFilesAsSeparateImages();
    }

    //****************Deleting the unnecessary temporary files from superior and inferior image stacks, and then calling the averaging function****************
    i = saveTheI;
    for (j = 0; j < revisedFileList.length; j++) {    //running through my array that has the annotated files (i.e. has the files with 'superior' etc.)
      if (indexOf(revisedFileList[j], fileList[i]) >= 0) {    //figuring out which of the annotated files matches my current file

          if(indexOf(revisedFileList[j], "superior") >= 0 || indexOf(revisedFileList[j], "inferior") >= 0) {   //determining if the file is superior or inferior

            if(isItRegAvg == "yes") {   //directing it to the previouslyAveragedFiles function if it has already been averaged
              previouslyAveragedFiles("superiorOrInferior");

            } else {
              tempFileList = getFileList(tempFilePath);
              for (k = 0; k < tempFileList.length / 2; k++) {
                ok = File.delete(tempFilePath + tempFileList[k]);
              }
              averaging("tnsi");
            }
          }

        if(indexOf(revisedFileList[j], "central") >= 0) {

            trueFileNumber = trueFileNumber + 1;
            if(isItRegAvg == "yes") {   //directing it to the previouslyAveragedFiles function if it has already been averaged
              previouslyAveragedFiles("central");
            } else {
              tempFilePath2 = parentDirectory + File.separator + "Temporary files - horizontal images" + File.separator;
              File.makeDirectory(tempFilePath2);
              tempFileList = getFileList(tempFilePath);
              for (k = 0; k < tempFileList.length / 2; k++) {   //moving the horizontal images to a different temporary folder
                if (k != floor(tempFileList.length / 2)) {   //skipping the last horizontal image because it is actually a combined horizontal/vertical image
                  ok = File.rename(tempFilePath + tempFileList[k], tempFilePath2 + tempFileList[k]);
                  }
                ok = File.delete(tempFilePath + tempFileList[k]);
              }
              averaging("vertical");

              File.makeDirectory(tempFilePath);
              tempFileList2 = getFileList(tempFilePath2);
              for (k = 0; k < tempFileList2.length; k++) {
                ok = File.rename(tempFilePath2 + tempFileList2[k], tempFilePath + tempFileList2[k]);
                ok = File.delete(tempFilePath2 + tempFileList2[k]);
              }
              ok = File.delete(tempFilePath2);
              averaging("horizontal");
            }
            olderTime = getTime();  //this is to keep the time estimate more accurate
        }

        if(indexOf(revisedFileList[j], "temporal") >= 0 || indexOf(revisedFileList[j], "nasal") >= 0) {

            if(isItRegAvg == "yes") {   //directing it to the previouslyAveragedFiles function if it has already been averaged
              previouslyAveragedFiles("temporalOrNasal");
            } else {
              averaging("tnsi");
            }
        }
      }
    }

    //****************Reporting that the process is finished****************

    if (trueFileNumber+1 == trueLength) {
      print("\\Update2:");
      print("\\Update0:" + trueFileNumber+1 + "/" + trueLength + " files complete");
      endTime = getTime();
      totalTime = (endTime - startTime)/1000;
      totalMinute = floor(totalTime/60);
      totalSecondRemainder = round((totalTime/60 - totalMinute)*60);
      if (totalMinute > 0) {
        print("\\Update1:Total time to completion: " + totalMinute + " m " + totalSecondRemainder + " s");
      } else {
        print("\\Update1:Total time to completion: " + totalSecondRemainder + " s");
      }
    }

    trueFileNumber = trueFileNumber + 1;
    i = saveTheI; //restoring the i to the original value

    } //end of the major loop that goes between each file
 } //end of macro




function deleteCreatedFiles (path) {
  if (File.exists(path)) {
    list = getFileList(path);
      for (b = 0; b < list.length; b++) {
        ok = File.delete(path + list[b]);
      }
      ok = File.delete(path);
  }
}

macro "Delete created files [r]" {
  deleteCreatedFiles("C:/Users/bran314/Desktop/124 OCT images/Temporary files/");
  deleteCreatedFiles("C:/Users/bran314/Desktop/124 OCT images/Finished files/Peripheral images/");
  deleteCreatedFiles("C:/Users/bran314/Desktop/124 OCT images/Finished files/Unaveraged images/");
  deleteCreatedFiles("C:/Users/bran314/Desktop/124 OCT images/Finished files/");
  deleteCreatedFiles("C:/Users/bran314/Desktop/124 OCT images/Temporary files - horizontal images/");
  File.makeDirectory("C:/Users/bran314/Desktop/124 OCT images/Finished files/");
}
