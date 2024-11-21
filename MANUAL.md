# Authors of Software
Jannik Guckel, Daesung Park

# Short Manual of the Software

This is an internal repository containing the Iterative Scanner Software introduced in *Link*

## Dependencies

The Script is fully written in Python 3 (v 3.9), used of mostly using standard libraries and OpenCV (v 4.5)
it requires the following packages in order to be ran:

+ PIL
+ hyperspy
+ numpy
+ matplotlib
+ glob
+ scipy
+ ast
+ csv
+ os
+ shutil
+ openCV

## Installation and Using the program

Assuming Python3 and the above mentioned libraries are installed, the only installation step needed should be downloading the code provided by this repository without changing the local folder structure.
The program can then be executed in the terminal by using:

```
cd *local direction of this folder*
python3 find_particles.py
```

Basic is a version developed for dimers on a substrate. with_origami includes additional segmentation steps to segment background from origami and is used in the paper ...

## Guides and Explanation of Input Parameters

This program is a command line tool. Upon activation, it will ask if you want to read an existing input file. If yes is selected, it will ask you for its location. If no is selected, you enter "on the fly" mode, where the program asks you to provide all necessary input parameters. A sample input file for both modes is provided in the folder "Examples". You can download and edit the parameters to your needs in any text editor. The meaning of each input parameter is provided down below. In general, it is possible to analyze multiple images at once. However, all images will then use identical input parameters. Therefore, we recommend analyzing data with different imaging conditions separately from each other.

### File Management
+ Program Version: Miscellanous Information about the Version used.
+ Home Directory: File Location of the Data set you wish to analyze. Make sure that your directory ends on a separator (such as / for Linux). This applies to all instances asking for a path.
+ Relative Working Directory: Folder of a data Subset
+ Name of Results Folder: Name of the folder, where each analysis results is saved.
+ Pixel size and Pixel unit: Value and Unit of square pixel.
+ File Format: Format of your data for analysis. Our code can read the image formats "png", "jpeg", "tif" through PIL as well as raw data formats "dm4" and "hdf5" via hyperspy. Other formats can still be possible but have not been tested.

Our code assumes the following organization: 
```
Home Path/ 
    Data Set 1/  
        image1.ext
        image2.ext
        ...
    Data Set 2/
        image1.ext
        image2.ext
        ....
    ....
```
In this example, choosing Data Set 1 as Relative working directory will analyze all images within Data Set 1, assuming ext was chosen as File Format.
The analysis result can be found under

```
Home Path/ 
    Results Folder/
        Data Set 1/
            *Analysis Results*
```

### Pre-Processing Parameters

+ Standard Deviation of Gaussian Blurring: Optional Gaussian Blurring of Images for Despiking.
+ Data Bar Length: Some image format have a data bar the bottom, which belongs to the image. This parameter cuts the bottom rows from all images. Default value: 0
+ Use Bottom/ Top Thresholding: You can apply optional image intensity thresholding. Selecting 1 will enable it, 0 will disable it. These parameters have been replaced by the parameter "segmentation mode", which will automatically select 1 of 3 mode (background brightest, background darkest, background inbetween)
+ Top Threshold / Bottom Threshold: If any thresholding option is selected, the program will ask you to set its value. You can either insert a float value or an integer. If a float value is entered, the program will analyze the gray values of each image and selects the specific quantile, 0.975 means the threshold is set to the 97.5 % quantile. If an integer is entered, the value is treated as a flat gray value number. It is important to note, that our Software normalizes the images to 8 bit integer before applying any other pre-processing steps, as this format is required by OpenCV. Therefore you have to select integer values with this in mind. If the use of a specific threshold was not selected previously, the program will automatically set the values to 0.0 and 1.0 respectively.

The code executes its pre-processing in the following order:

```
Loading image
Save a Backup Copy of the Original Image
Cutting Data Bar (optional)
Gaussian Blurring (optional)
Conversion to 8-bit Integer (Maximum of current image: 255, Minimum of current image: 0)
Thresholding
```

### Detection Parameters

Our code uses the following detection Parameters:

+ Canny Edge Detection Threshold $`p_1`$: Upper Gradient Limit for Edge Detection. Necessary for Circular Hough Transform (CHT)
+ Voting threshold $`p_2`$: Voting threshold parameter for CHT. Lower Threshold allows for more particles at the risk of detecting false positives. 
+ rmin, rmax: minimum and maximum radius of the particles in pixel (only integers allowed)
+ Particle Overlap Factor P: This is a proportionality factor that controls how much the particles are allowed to overlap. The minimum neighbor distance is calculated by $`\Delta d = P \cdot r_{min}`$. Default: 1.5
+ monomer radius (dmax): maximum distance between 2 dimer particles. input in "real units". Program will automatically calculate convert this value into pixels!
+ agg_size: a parameter that controls how strict our algorithm filters out agglomerates. Values: Integers above 1. Default 2. Only available in "no origami mode".
+ cluster threshold: Critical size of a pixel cluster. Pixel clusters below this this threshold are considered noise and will be ignored in further analysis. only in"origami mode".
+ origami threshold: Critical size of a pixel cluster. Pixel clusters above this threshold are considered DNA origami (only used in "single particle vs monomer" decision). only in "origami mode"


## Output files

Our Program provides the following output files:

+ Canny Edge of each image. This way you can check the validity of the value of p1
+ Threshold image of each image: Image after thresholding. Allows to check your thresholding values (optional output in "no origami mode". mandatory in "origami mode")
+ Cluster image of each image: Pixel cluster identification (alternatively called 'Labeling')
+ Denoised cluster image (all images): removes small "noisy" clusters, which are too small to contain any particles - Saved as binary mask. allows you to check the validity of the cluster threshold
+ Masked image (for all images): The product of Threshold Image with its respective denoised cluster image. Final Segregation image that provides a visual feedback about the background segregation as a whole.
+ Hough overlay of each image: Overlay of Particles detected by CHT before classification - Allows to check the validity of other CHT parameters (p2, rmin, rmax)
+ Classification overlay of each image(*_mono_dimer.png): Provides visual feedback of the particle classification result by color code. Red = monomer, Orange = single particle, green = dimer, purple = agglomerate, blue = cannot be classified

+ A radius histogram, showing the distribution of particle radius across all analyzed images
+ A CSV file listing the position and radius of each detected circle and which image it was found in.
+ An inter-particle distance histogram across all analyzed images
+ A CSV file listing all dimer information (particle positions of both particles, distance, which image was it found in)
+ A text file saving all input parameters. Format is compatible input file for the mode you have used.

## Fix for potential Issue

The code was written in Linux. When you concat multiple path strings, our software assumes / as separator between different sub-folders by default. if you have a different separator (like \ for Windows), open the script iterative_scanner.py in an editor and change the / in line 30 to the separator of your local system.

## License

This program is available under the GPLv3.

## Citation

Please cite our software at https://onlinelibrary.wiley.com/doi/10.1111/jmi.13371, if you are using it in any publication. 

