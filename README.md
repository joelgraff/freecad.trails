# FreeCAD-Trails Transportation Engineering Workbench

This workbench is being developed to provide functionality specific to Transportation engineering (road and rail) and Geomatics/Survey engineering.

## Functions

* Import Point Files  
* Export Points  
* GeoData Tools
* Create Surface  
* Edit Surface  
* Create Contours  
* Create Guide Lines
* Create Sections (WIP)
* Import Alignment LandXML files.

## Usage & Screenshots
![IPF](https://user-images.githubusercontent.com/3831435/59975941-f9e35800-95c6-11e9-9afc-05f5a5d0bf2d.gif)
![EP](https://user-images.githubusercontent.com/3831435/59975942-f9e35800-95c6-11e9-995d-4263f34f6f87.gif)
![CS](https://user-images.githubusercontent.com/3831435/59975943-f9e35800-95c6-11e9-99d3-65282669817b.gif)
![ES](https://user-images.githubusercontent.com/3831435/59975944-fa7bee80-95c6-11e9-8b47-a2f583fa25a6.gif)
![CC](https://user-images.githubusercontent.com/3831435/59975946-fa7bee80-95c6-11e9-8e2f-7bdffac13d01.gif)
![CGL](https://user-images.githubusercontent.com/3831435/58638005-76eb1c80-82fc-11e9-83bd-49dbb06d9202.png)
![GeoData](https://user-images.githubusercontent.com/3831435/59973802-212d2b80-95ad-11e9-919f-8cf3f75cb375.png)
![OSM](https://user-images.githubusercontent.com/3831435/59843173-ad96de80-9360-11e9-9c6a-153449516a7f.png)
![Surface](https://user-images.githubusercontent.com/3831435/59920075-fff40000-9431-11e9-8411-b13032364f28.gif)

## Installation

Download and extract the ZIP file into the `.FreeCAD/Mod` folder or use git to clone into `.FreeCAD/Mod`

### Dependencies
FreeCAD-Trails depends on the [pivy_trackers 2D geometry library] https://github.com/joelgraff/pivy_trackers to run.  This library provides low-level 2D rendering support through Python for FreeCAD.

### For GeoData Functions
* cv2
* gdal
* gdalconst
* requests (urllib, chardet, certifi, idna)

**Note:** `.FreeCAD/Ext` is also a valid file path and may eventually become the target path for external workbenches

## Feedback 
Discuss this Workbench on the FreeCAD forum thread dedicated to this topic: 
[Civil engineering feature implementation (Transportation Engineering)](https://forum.freecadweb.org/viewtopic.php?f=8&t=22277). 

FYI, this thread was born of a parent thread: 
[Civil Engineering Design functions](https://forum.freecadweb.org/viewtopic.php?f=8&t=6973)

## Developer 
Joel Graff ([@joelgraff](https://github.com/joelgraff)) and Hakan Seven ([@HakanSeven12](https://github.com/HakanSeven12)) with inspiration and help from the FreeCAD community
