###Search and Rescue Simulation using OpenCV###
-----------------------------------------------

Overview
--------
This project simulates a search-and-rescue operation using image processing in OpenCV. 
It detects casualties and rescue pads in drone images, calculates casualty priority scores, assigns casualties to pads based on distance and priority, and visualizes the results.

Features:-
----------
- Detects casualties of different shapes (star, triangle, square) and rescue pads (circle).  
- Computes priority scores for each casualty.  
- Assigns casualties to rescue pads while considering pad capacity and distance.  
- Generates two types of outputs:
  - Output1: casualties with priority scores.  
  - Output2: final assignments with lines connecting casualties to pads.  
- Visualizes land and ocean using colored masks to avoid interference with other objects.  
- Calculates a “rescue ratio” for each image.

How to Use
----------
1. Place input images in the 'images' folder.  
2. Ensure 'output1' and 'output2' folders exist.  
3. Run the script:
   python main.py
4. The processed images will appear sequentially:
   - Output1: images with priority scores.
   - Output2: images with assigned lines.
5. Press any key to move to the next image.  
6. All output images are deleted automatically after viewing.

File Structure
--------------
project/
├── images/          # Input images
├── output1/         # Casualties with scores
├── output2/         # Final assignments
├── main.py          # Main processing script
└── README.md        # Project documentation

How it Works
------------
1. Convert image to HSV and create masks for land and ocean.  
2. Detect contours in the image to identify casualties and pads.  
3. Determine shape and color of each contour.  
4. Calculate casualty priority score (priority * emergency factor).  
5. Assign each casualty to the best available rescue pad based on distance and priority, respecting pad capacity.  
6. Draw lines from casualties to pads and display images.

Rescue_Ratio
------------
Rescue Ratio = Average of Best_score for all assigned casualties in an image.
Best_score for each casualty is calculated by [priority_score/(distance+1)] . I have used +1 to avoid divisin by zero in any case.
It indicates the efficiency of casualty assignment in the image.

Areas of Improvement
--------------------
- Extend to handle video streams or real-time drone footage.  
- Add more shapes/colors for casualties and pads.  
- More Robust identification of shapes and colors.


Acknowledgement
---------------
I wish to thank UAS-DTU for giving me this project to work upon which made me learn so much. Although I approached it as a part of recruitment process but it offered much more..

Also i request the mentor to please pardon if my rescue_ratio doesn't resonate with what you asked for. I am a bit confused about what you mean by that and will improve once you provide the feedback....






