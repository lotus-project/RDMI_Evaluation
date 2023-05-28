# **Using Google Earth Engine**

#### The following instructions will help you download NDVI and night light data using Google Earth Engine Code

---

## Prequisites

- Sign up to Google Earth Engine Code with your Google account. This **needs to be done first** otherwise it will fail to download the images.
- Depending on the spatial resolution used (set to 1000 m by default), downloading images for the entire globe will **require several GBs of free space in your Google Drive**.

---

## Instructions

1. Go to [Google Earth Engine Code](https://code.earthengine.google.com).
2. Copy and paste the code from the entire JavaScript file for the required dataset (NDVI or night light) into the Script Editor.

<img src="./guide_images/script_editor.png" alt="Script Editor" width="800"/>

3. At this point, you can save the script to your Google Earth Engine account by clicking **'Save'** at the top of the Script Editor to allow for easier execution of the script should you wish to run it again at a later date.
4. Before running the script, make sure to check all parameters:
    - The default dates used to query the satellite image datasets produced the best resulting image data as of the time of initial publication (August 2020). However, these dates can be updated as required. For NDVI, using a span of several years (> 3) and taking the median, which is done to negate cloud cover and ground shadows, seems to produce the best final image. Again, feel free to experiment 
    - Cloud cover is set to less than 5% -- it is not recommended to increase this.
    - Region parameter is set to the first geometry shape (geometry1) by default. The script is designed to be run using all 4 geometry shapes. This will be covered in more detail in the next steps.
    - Scale lets you set the spatial resolution of the downloaded images in metres per pixel. Night light data can resolve down to approx. 460 metres per pixel, whereas NDVI data can resolve down to 10-30 metres per pixel depending on the satellite imagery used (*i.e.* Landsat, Sentinel-2). The scale is set to 1000 by default to match the population density data being used.
    - maxPixels has been set very high in the script to allow for the download high resolution images.
5. Once you are happy with the parameters, click **'Run'**.
6. Go to the **Tasks** tab in the upper-right corner and click **Run** on the file to begin the process of downloading to your Google Drive.

<img src="./guide_images/task_run.png" alt="Task" width="700"/>

7. After you see a tick appear next to the task, the download will be complete and you will be able to see the file in your Google Drive.
8. Run the script again with each geometry shape. Simply change the **region** parameter to geometry2, geometry3, or geometry4, as well as the accompanying **description** each time before clicking **Run**.

<img src="./guide_images/parameters.png" alt="Parameters" width="350"/>

9. Once all images have been added to your Google Drive, transfer them to a folder for use with the **tif_stitch** module to create global tif files. Make sure you only put the images of one type in the folder (i.e. create one folder for NDVI and another folder for night light).