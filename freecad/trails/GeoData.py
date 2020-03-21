# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2019 Hakan Seven <hakanseven12@gmail.com>             *
# *                                                                     *
# * This program is free software; you can redistribute it and/or modify*
# * it under the terms of the GNU Lesser General Public License (LGPL)  *
# * as published by the Free Software Foundation; either version 2 of   *
# * the License, or (at your option) any later version.                 *
# * for detail see the LICENCE text file.                               *
# *                                                                     *
# * This program is distributed in the hope that it will be useful,     *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of      *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
# * GNU Library General Public License for more details.                *
# *                                                                     *
# * You should have received a copy of the GNU Library General Public   *
# * License along with this program; if not, write to the Free Software *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
# * USA                                                                 *
# *                                                                     *
# ***********************************************************************

import FreeCAD
import FreeCADGui


class import_csv:

    def Activated(self):
        import GeoDataWB.import_csv
        GeoDataWB.import_csv.mydialog()

    def GetResources(self):
        return {
            'Pixmap': 'Std_Tool3',
            'MenuText': 'Import CSV',
            'ToolTip': 'Import CSV'
        }


class import_emir:

    def Activated(self):
        import GeoDataWB.import_emir
        from importlib import reload

        reload(GeoDataWB.import_emir)
        GeoDataWB.import_emir.mydialog()

    def GetResources(self):
        return {
            'Pixmap': 'Std_Tool3',
            'MenuText': 'Import EMIR',
            'ToolTip': 'Import EMIR'
        }


class import_xyz:

    def Activated(self):
        import GeoDataWB.import_xyz
        from importlib import reload

        reload(GeoDataWB.import_xyz)
        GeoDataWB.import_xyz.mydialog(False)

    def GetResources(self):
        return {
            'Pixmap': 'Std_Tool3',
            'MenuText': 'Import XYZ',
            'ToolTip': 'Import XYZ'
        }


class import_image:

    def Activated(self):
        import GeoDataWB.import_image
        from importlib import reload

        reload(GeoDataWB.import_image)
        GeoDataWB.import_image.mydialog(False)

    def GetResources(self):
        return {
            'Pixmap': 'Std_Tool3',
            'MenuText': 'Import Image',
            'ToolTip': 'Import Image'
        }


class import_gpx:

    def Activated(self):
        import GeoDataWB.import_gpx

        GeoDataWB.import_gpx.mydialog()

    def GetResources(self):
        return {
            'Pixmap': 'Std_Tool3',
            'MenuText': 'Import GPX',
            'ToolTip': 'Import GPX'
        }


class import_latlony:

    def Activated(self):
        import GeoDataWB.import_latlony
        from importlib import reload
        reload(GeoDataWB.import_latlony)
        GeoDataWB.import_latlony.mydialog()
        # GeoDataWB.import_latlony.run()

    def GetResources(self):
        return {
            'Pixmap': 'Std_Tool3',
            'MenuText': 'Import Lat/Long Height',
            'ToolTip': 'Import Latitude/Longitude Height'
        }


class import_aster:

    def Activated(self):
        import GeoDataWB.import_aster
        from importlib import reload

        reload(GeoDataWB.import_aster)
        GeoDataWB.import_aster.mydialog()

    def GetResources(self):
        return {
            'Pixmap': 'Std_Tool3',
            'MenuText': 'Import ASTER',
            'ToolTip': 'Import ASTER'
        }


class import_lidar:

    def Activated(self):
        import GeoDataWB.import_lidar
        from importlib import reload

        reload(GeoDataWB.import_lidar)
        GeoDataWB.import_lidar.mydialog()

    def GetResources(self):
        return {
            'Pixmap': 'Std_Tool3',
            'MenuText': 'Import LIDAR',
            'ToolTip': 'Import LIDAR'
        }


class navigator:

    def Activated(self):
        import GeoDataWB.navigator
        FreeCADGui.activeDocument().activeView().setCameraType("Perspective")
        FreeCADGui.updateGui()
        GeoDataWB.navigator.navi()

    def GetResources(self):
        return {
            'Pixmap': 'Std_Tool2',
            'MenuText': 'Navigator',
            'ToolTip': 'Navigator'
        }


class import_osm:

    def Activated(self):
        import GeoDataWB.import_osm
        from importlib import reload
        reload(GeoDataWB.import_osm)
        GeoDataWB.import_osm.mydialog()

    def GetResources(self):
        return {
            'Pixmap': 'Std_Tool1',
            'MenuText': 'Import OSM Map',
            'ToolTip': 'Import OSM Map'
        }


class importheights:

    def Activated(self):
        import GeoDataWB.import_heights
        from importlib import reload

        reload(GeoDataWB.import_heights)
        GeoDataWB.import_heights.mydialog()

    def GetResources(self):
        return {
            'Pixmap': 'Std_Tool1',
            'MenuText': 'Import OSM Heights',
            'ToolTip': 'Import OSM Heights'
        }


class importsrtm:

    def Activated(self):
        import GeoDataWB.import_srtm
        from importlib import reload

        reload(GeoDataWB.import_srtm)
        GeoDataWB.import_srtm.mydialog()

    def GetResources(self):
        return {
            'Pixmap': 'Std_Tool1',
            'MenuText': 'Import SRTM Heights',
            'ToolTip': 'Import SRTM Heights'
        }


class createHouse:

    def Activated(self):
        import GeoDataWB.createhouse
        from importlib import reload

        reload(GeoDataWB.createhouse)
        FreeCAD.rc = GeoDataWB.createhouse.mydialog()

    def GetResources(self):
        return {
            'Pixmap': 'Std_Tool1',
            'MenuText': 'Create Houses',
            'ToolTip': 'Create House '
        }


class ElevationGrid:

    def Activated(self):

        import GeoDataWB.elevationgrid
        from importlib import reload

        reload(GeoDataWB.elevationgrid)
        GeoDataWB.elevationgrid.run()
        # FreeCAD.rc=GeoDataWB.createhouse.mydialog()

    def GetResources(self):
        return {
            'Pixmap': 'Std_Tool1',
            'MenuText': 'Elevation Grid',
            'ToolTip': 'Create Elevation Grid '
        }


FreeCADGui.addCommand('Import OSM Map', import_osm())
FreeCADGui.addCommand('Import CSV', import_csv())
FreeCADGui.addCommand('Import GPX', import_gpx())
FreeCADGui.addCommand('Import Heights', importheights())
FreeCADGui.addCommand('Import SRTM', importsrtm())
FreeCADGui.addCommand('Import XYZ', import_xyz())
FreeCADGui.addCommand('Import LatLonZ', import_latlony())
FreeCADGui.addCommand('Import Image', import_image())
FreeCADGui.addCommand('Import ASTER', import_aster())
FreeCADGui.addCommand('Import LIDAR', import_lidar())
FreeCADGui.addCommand('Create House', createHouse())
FreeCADGui.addCommand('Navigator', navigator())
FreeCADGui.addCommand('ElevationGrid', ElevationGrid())
FreeCADGui.addCommand('Import EMIR', import_emir())
