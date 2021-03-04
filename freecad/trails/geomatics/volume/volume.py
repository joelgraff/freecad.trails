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
Create a Volume Object from FPO.
'''

import FreeCAD
import Part
from pivy import coin
#from . import volumes
from .volume_func import VolumeFunc
from freecad.trails import ICONPATH, geo_origin
import random, copy



def create(sections, name='Volume'):
    #group = volumes.get()
    obj=FreeCAD.ActiveDocument.addObject("App::FeaturePython", "Volume")
    obj.Label = name
    Volume(obj)
    obj.TopSections = sections[0]
    obj.BottomSections = sections[1]
    ViewProviderVolume(obj.ViewObject)
    #group.addObject(obj)
    FreeCAD.ActiveDocument.recompute()

    return obj


class Volume(VolumeFunc):
    """
    This class is about Volume Object data features.
    """

    def __init__(self, obj):
        '''
        Set data properties.
        '''
        self.Type = 'Trails::Volume'

        obj.addProperty(
            'App::PropertyLinkList', "TopSections", "Base",
            "Top section list").TopSections = []

        obj.addProperty(
            'App::PropertyLinkList', "BottomSections", "Base",
            "Bottom section list").BottomSections = []

        obj.addProperty(
            "Part::PropertyPartShape", "Shape", "Base",
            "Volume areas shape").Shape = Part.Shape()

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
        top = obj.getPropertyByName("TopSections")
        bottom = obj.getPropertyByName("BottomSections")

        if top and bottom:
            obj.Shape = self.get_areas([top[0], bottom[0]])

class ViewProviderVolume:
    """
    This class is about Volume Object view features.
    """

    def __init__(self, vobj):
        '''
        Set view properties.
        '''
        (r, g, b) = (random.random(), random.random(), random.random())

        vobj.addProperty(
            "App::PropertyColor", "AreaColor", "Base",
            "Color of the volume areas").AreaColor = (r, g, b)

        vobj.Proxy = self

    def attach(self, vobj):
        '''
        Create Object visuals in 3D view.
        '''
        # Face root.
        self.face_coords = coin.SoGeoCoordinate()
        self.faces = coin.SoIndexedFaceSet()
        self.line_color = coin.SoBaseColor()

        # Highlight for selection.
        highlight = coin.SoType.fromName('SoFCSelection').createInstance()
        highlight.style = 'EMISSIVE_DIFFUSE'
        highlight.addChild(self.face_coords)
        highlight.addChild(self.faces)

        # Volume root.
        volume_root = coin.SoSeparator()
        volume_root.addChild(self.line_color)
        volume_root.addChild(highlight)
        vobj.addDisplayMode(volume_root,"Volume")

        # Take features from properties.
        self.onChanged(vobj,"AreaColor")

    def onChanged(self, vobj, prop):
        '''
        Update Object visuals when a view property changed.
        '''
        try:
            if prop == "AreaColor":
                color = vobj.getPropertyByName("TriangleColor")
                self.mat_color.diffuseColor = (color[0],color[1],color[2])
        except Exception: pass

    def updateData(self, obj, prop):
        '''
        Update Object visuals when a data property changed.
        '''
        if prop == "Shape":
            shape = obj.getPropertyByName("Shape")

            points = []
            faces = []

            # Get GeoOrigin.
            origin = geo_origin.get()
            base = copy.deepcopy(origin.Origin)
            base.z = 0

            # Set GeoCoords.
            geo_system = ["UTM", origin.UtmZone, "FLAT"]
            self.face_coords.geoSystem.setValues(geo_system)

            points = []
            face_vert = []
            prev = 0
            for i, face in enumerate(shape.Faces):
                for vertex in face.Vertexes:
                    points.append(vertex.Point.add(base))

                face_vert.extend(range(prev, len(points)))
                face_vert.append(-1)

                prev = len(points)

            #Set contour system.
            self.face_coords.point.values = points
            self.faces.coordIndex.values = face_vert

    def getDisplayModes(self,vobj):
        '''
        Return a list of display modes.
        '''
        modes=[]
        modes.append("Volume")

        return modes

    def getDefaultDisplayMode(self):
        '''
        Return the name of the default display mode.
        '''
        return "Volume"

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
        return ICONPATH + '/icons/volume.svg'

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
