# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2021 Hakan Seven <hakanseven12@gmail.com>             *
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

'''
Create a Table Object from FPO.
'''

import FreeCAD
from pivy import coin
from freecad.trails import ICONPATH, geo_origin
import copy



def create(pos, volume, name='Table'):
    obj=FreeCAD.ActiveDocument.addObject(
        "App::FeaturePython", "Table")

    obj.Label = name
    Table(obj)
    obj.Position = pos
    obj.VolumeAreas = volume
    ViewProviderTable(obj.ViewObject)

    FreeCAD.ActiveDocument.recompute()

    return obj


class Table:
    """
    This class is about Table Object data features.
    """

    def __init__(self, obj):
        '''
        Set data properties.
        '''

        self.Type = 'Trails::Table'

        obj.addProperty(
            'App::PropertyString', "TableTitle", "Base",
            "Table title").TableTitle = "Volume Table"

        obj.addProperty(
            'App::PropertyVector', "Position", "Base",
            "Section creation origin").Position = FreeCAD.Vector()

        obj.addProperty(
            'App::PropertyLink', "VolumeAreas", "Base",
            "Volume Areas").VolumeAreas = None

        obj.Proxy = self

    def onChanged(self, obj, prop):
        '''
        Do something when a data property has changed.
        '''
        return

    def execute(self, obj):
        '''
        Do something when doing a recomputation. 
        '''
        return


class ViewProviderTable:
    """
    This class is about Table Object view features.
    """

    def __init__(self, vobj):
        '''
        Set view properties.
        '''
        vobj.Proxy = self

    def attach(self, vobj):
        '''
        Create Object visuals in 3D view.
        '''
        # GeoCoord Node.
        self.geo_coords = coin.SoGeoCoordinate()
        self.table_borders = coin.SoLineSet()
        self.table_columns = coin.SoSeparator()

        # Highlight for selection.
        highlight = coin.SoType.fromName('SoFCSelection').createInstance()
        highlight.style = 'EMISSIVE_DIFFUSE'
        highlight.addChild(self.table_borders)
        highlight.addChild(self.table_columns)

        # Point group root.
        table_root = coin.SoSeparator()
        table_root.addChild(highlight)
        vobj.addDisplayMode(table_root,"Table")

    def onChanged(self, vobj, prop):
        '''
        Update Object visuals when a view property changed.
        '''
        return

    def updateData(self, obj, prop):
        '''
        Update Object visuals when a data property changed.
        '''
        tables = obj.getParentGroup()
        region = tables.getParentGroup()
        volume_areas = obj.getPropertyByName("VolumeAreas")

        if volume_areas:
            pos = obj.getPropertyByName("Position")
            if prop == "VolumeAreas" or prop == "TableTitle":
                self.table_columns.removeAllChildren()
                origin = geo_origin.get()
                base = copy.deepcopy(origin.Origin)
                base.z = 0

                column_titles = ["KM", "Area", "Volume", "Cumulative Volume"]

                table_title = obj.getPropertyByName("TableTitle")
                offset = 50000
                font = coin.SoFont()
                font.size = 10000

                # Table title
                title = coin.SoSeparator()
                location = coin.SoTranslation()
                text = coin.SoAsciiText()

                location.translation = pos + FreeCAD.Vector(0, font.size.getValue(), 0)
                text.string.setValues([table_title])

                title.addChild(font)
                title.addChild(location)
                title.addChild(text)

                # Stations column
                sta_list = [str(round(i,2)) for i in region.StationList]
                sta_list.insert(0,column_titles[0])

                sta_column = coin.SoSeparator()
                location = coin.SoTranslation()
                text = coin.SoAsciiText()

                location.translation = pos
                text.string.setValues(sta_list)

                sta_column.addChild(font)
                sta_column.addChild(location)
                sta_column.addChild(text)

                # Area column
                face_areas = []
                for sub in obj.VolumeAreas.Shape.SubShapes:
                    face_areas.append(sub.Area)

                area_list = [str(round(i/1000000,3)) for i in face_areas]
                area_list.insert(0,column_titles[1])

                area_column = coin.SoSeparator()
                location = coin.SoTranslation()
                text = coin.SoAsciiText()

                location.translation = pos.add(FreeCAD.Vector(offset, 0, 0))
                text.string.setValues(area_list)

                area_column.addChild(font)
                area_column.addChild(location)
                area_column.addChild(text)

                # Volume column
                volumes = []
                volumes.append(0)
                for count in range(1,len(face_areas)):
                    prev_area = float(face_areas[count-1])
                    next_area = float(face_areas[count])

                    prev_km = float(sta_list[count])
                    next_km = float(sta_list[count+1])

                    volume = ((next_area + prev_area)/2)*(next_km-prev_km)
                    volumes.append(volume)

                volume_list = [str(round(i/1000000,3)) for i in volumes]
                volume_list.insert(0,column_titles[2])

                volume_column = coin.SoSeparator()
                location = coin.SoTranslation()
                text = coin.SoAsciiText()

                location.translation = pos.add(FreeCAD.Vector(offset*2, 0, 0))
                text.string.setValues(volume_list)

                volume_column.addChild(font)
                volume_column.addChild(location)
                volume_column.addChild(text)

                # Cumulative volume column
                cum_vols = []
                cum_vols.append(0)

                for count in range(1,len(volumes)):
                    prev_cumvol = float(cum_vols[-1])
                    next_vol = float(volumes[count])

                    cum_vol = prev_cumvol + next_vol
                    cum_vols.append(cum_vol)

                cumvol_list = [str(round(i/1000000,3)) for i in cum_vols]
                cumvol_list.insert(0,column_titles[3])

                cumvol_column = coin.SoSeparator()
                location = coin.SoTranslation()
                text = coin.SoAsciiText()

                location.translation = pos.add(FreeCAD.Vector(offset*3, 0, 0))
                text.string.setValues(cumvol_list)

                cumvol_column.addChild(font)
                cumvol_column.addChild(location)
                cumvol_column.addChild(text)

                self.table_columns.addChild(title)
                self.table_columns.addChild(sta_column)
                self.table_columns.addChild(area_column)
                self.table_columns.addChild(volume_column)
                self.table_columns.addChild(cumvol_column)

    def getDisplayModes(self, vobj):
        '''
        Return a list of display modes.
        '''
        modes=[]
        modes.append("Table")

        return modes

    def getDefaultDisplayMode(self):
        '''
        Return the name of the default display mode.
        '''
        return "Table"

    def setDisplayMode(self,mode):
        '''
        Map the display mode defined in attach with 
        those defined in getDisplayModes.
        '''
        return mode

    def getIcon(self):
        '''
        Return object treeview icon.
        '''
        return ICONPATH + '/icons/table.svg'

    def __getstate__(self):
        """
        Save variables to file.
        """
        return None
 
    def __setstate__(self,state):
        """
        Get variables from file.
        """
        return None
