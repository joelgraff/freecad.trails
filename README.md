# FreeCAD Trails Workbench (Transportation and Geomatics)

Hakan Seven is a Geomatics Engineer and Joel_graff is a Transportation Engineer. We decide to create a workbench for our own needs. So this workbench is being developed to provide functionality specific to Transportation and Geomatics engineering.

## Features

* Geodata Tools
* Import Survey Data Files
* Export Point Groups to File
* Create Surface
* Edit Surface  
* Create Regions
* Create Sections
* Calculate Volume Areas
* Create Volume Tables
* Create Building Pads
* Import Alignment LandXML files.

## Usage & Screenshots

![](https://community.osarch.org/uploads/editor/ii/jmi2oo80pbt8.png "")
![](https://community.osarch.org/uploads/editor/9l/01m40i4on158.png "")
![](https://community.osarch.org/uploads/editor/n3/gqbzauel9gnz.png "")
![](https://community.osarch.org/uploads/editor/mq/t3fkzt6q51nr.png "")
![](https://community.osarch.org/uploads/editor/hn/66wuqmutn9o7.png "")
![](https://community.osarch.org/uploads/editor/z6/b3hupo69epaw.png "")
![](https://community.osarch.org/uploads/editor/sv/epkb70fifwg2.png "")
![](https://community.osarch.org/uploads/editor/8m/y4n02o7kdep4.png "")
![](https://community.osarch.org/uploads/editor/kp/pxsgaezkvhhg.png "")
![](https://community.osarch.org/uploads/editor/5g/t7b741rit6fy.gif "")
![](https://community.osarch.org/uploads/editor/mg/92t6nyg6vst0.png "")
![](https://community.osarch.org/uploads/editor/fm/zogcrzsmfe4y.png "")
![](https://community.osarch.org/uploads/editor/qx/zdqum123doe4.png "")

## Installation

### Easy
Go to releases: https://github.com/joelgraff/freecad.trails/releases

Download and extract the ZIP file into the `.FreeCAD/Mod` folder.

**Note:** This releases are not up to date. So maybe you can't find the newly added features.

### Hard
FreeCAD-Trails depends on the [pivy_trackers 2D geometry library] https://github.com/joelgraff/pivy_trackers and my own [FreeCAD_python_support] https://github.com/joelgraff/freecad_python_support repo to run.  Pivy_trackers provides low-level 2D rendering support through Python for FreeCAD.  FreeCAD_python_support is a collection of python support functions.  Both are included in the FreeCAD Trails project as submodules.

In order to clone the repo with the complete supporting submodules, invoke git from the /Mod folder at the commandline as follows:

`git clone --recursive https://github.com/joelgraff/freecad.trails.git`

## Feedback 
Get help: [FreeCAD Trails Workbench (Transportation and Geomatics)](https://forum.freecadweb.org/viewtopic.php?f=8&t=34371)

Discuss this Workbench on the FreeCAD forum thread dedicated to this topic: 
[Civil engineering feature implementation (Transportation Engineering)](https://forum.freecadweb.org/viewtopic.php?f=8&t=22277). 

FYI, this thread was born of a parent thread: 
[Civil Engineering Design functions](https://forum.freecadweb.org/viewtopic.php?f=8&t=6973)

## Developer 
Joel Graff ([@joelgraff](https://github.com/joelgraff)) and Hakan Seven ([@HakanSeven12](https://github.com/HakanSeven12)) with inspiration and help from the FreeCAD community
