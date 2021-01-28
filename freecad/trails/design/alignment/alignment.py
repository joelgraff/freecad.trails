# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#* Copyright (c) 2019, Joel Graff <monograff76@gmail.com               *
#*                                                                     *
#* This program is free software; you can redistribute it and/or modify*
#* it under the terms of the GNU Lesser General Public License (LGPL)  *
#* as published by the Free Software Foundation; either version 2 of   *
#* the License, or (at your option) any later version.                 *
#* for detail see the LICENCE text file.                               *
#*                                                                     *
#* This program is distributed in the hope that it will be useful,     *
#* but WITHOUT ANY WARRANTY; without even the implied warranty of      *
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
#* GNU Library General Public License for more details.                *
#*                                                                     *
#* You should have received a copy of the GNU Library General Public   *
#* License along with this program; if not, write to the Free Software *
#* Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
#* USA                                                                 *
#*                                                                     *
#***********************************************************************


__title__ = 'alignment.py'
__author__ = 'Joel Graff'
__url__ = "https://www.freecadweb.org"

"""
Class for managing 2D Horizontal Alignments
"""

import FreeCAD as App
from pivy import coin

from freecad.trails import ICONPATH, geo_origin
from ..project.support import properties, units
from ..geometry import support
from . import alignment_group, alignment_model
from .alignment_func import AlignmentFunc

from copy import deepcopy



def create(geometry, object_name='', parent = None, no_visual=False, zero_reference=False):
    """
    Class construction method
    object_name - Optional. Name of new object.  Defaults to class name.
    no_visual - If true, generates the object without a ViewProvider.
    """

    if not geometry:
        print('No curve geometry supplied')
        return

    alignments = alignment_group.get()
    obj = App.ActiveDocument.addObject("App::FeaturePython", "Alignment")
    if object_name: obj.Label = object_name
    alignments.addObject(obj)

    HorizontalAlignment(obj)
    obj.Proxy.set_geometry(geometry, zero_reference)
    ViewProviderHorizontalAlignment(obj.ViewObject)
    App.ActiveDocument.recompute()

    return obj

class HorizontalAlignment(AlignmentFunc):
    """
    This class is about Alignment Object data features.
    """

    def __init__(self, obj):
        '''
        Set data properties.
        '''

        obj.Proxy = self

        self.Type = 'Trails::Alignment'
        self.Object = obj
        self.errors = []

        self.curve_edges = None

        self.model = None
        self.meta = {}
        self.hashes = None

        #add class properties

        #metadata
        properties.add(obj, 'String', 'ID', 'ID of alignment', '')
        properties.add(obj, 'String', 'oID', 'Object ID', '')

        properties.add(
            obj, 'Length', 'Length', 'Alignment length', 0.0, is_read_only=True
        )

        properties.add(
            obj, 'String', 'Description', 'Alignment description', ''
        )

        properties.add(
            obj, 'Length', 'Start Station',
            'Starting station of the alignment', 0.0
        )

        obj.addProperty(
            'App::PropertyEnumeration', 'Status', 'Base', 'Alignment status'
        ).Status = ['existing', 'proposed', 'abandoned', 'destroyed']

        properties.add(
            obj, 'Vector', 'Datum', 'Datum value as Northing / Easting',
            App.Vector(0.0, 0.0, 0.0)
        )

        properties.add(
            obj, 'FloatList', 'Hashes', 'Coordiante hashes', []
        )

        #geometry
        properties.add(
            obj, 'VectorList', 'Points', """
            Discretization of Points of Intersection (PIs) as a list of
            vectors""", []
            )

        properties.add(
            obj, 'VectorList', 'PIs', """
            Discretization of Points of Intersection (PIs) as a list of
            vectors""", []
            )

        properties.add(
            obj, 'Link', 'Parent Alignment',
            'Links to parent alignment object', None
        )

        subdivision_desc = """
            Method of Curve Subdivision\n
            \nTolerance - ensure error between segments and curve is (n)
            \nInterval - Subdivide curve into segments of fixed length
            \nSegment - Subdivide curve into equal-length segments
            """

        obj.addProperty(
            'App::PropertyEnumeration', 'Method', 'Segment', subdivision_desc
        ).Method = ['Tolerance', 'Interval', 'Segment']

        properties.add(obj, 'Float', 'Segment.Seg_Value',
                       'Set the curve segments to control accuracy',
                       int(1000.0 / units.scale_factor()) / 100.0
                      )

    def onDocumentRestored(self, obj):
        """
        Restore object references on reload
        """

        self.Object = obj
        group = obj.InList[0]

        self.model = alignment_model.AlignmentModel(
            self.Object.InList[0].Proxy.get_alignment_data(group, obj.ID)
        )

        #self.build_curve_edge_dict()

    def onChanged(self, obj, prop):
        '''
        Do something when a data property has changed.
        '''
        #dodge onChanged calls during initialization
        if prop == "Method" and hasattr(obj, 'Seg_Value'):
            method = obj.getPropertyByName(prop)

            if method == 'Interval':
                obj.Seg_Value = int(3000.0 / units.scale_factor())

            elif method == 'Segment':
                obj.Seg_Value = 200.0

            elif method == 'Tolerance':
                obj.Seg_Value = \
                    int(1000.0 / units.scale_factor()) / 100.0

    def execute(self, obj):
        '''
        Do something when doing a recomputation.
        '''
        if hasattr(self.model, 'discretize_geometry'):
            obj.Points = self.model.discretize_geometry(
                [0.0], self.Object.Method, self.Object.Seg_Value)

    def __getstate__(self):
        """
        Save variables to file.
        """
        return self.Type

    def __setstate__(self, state):
        """
        Get variables from file.
        """
        if state:
            self.Type = state


class ViewProviderHorizontalAlignment:
    """
    This class is about Point Group Object view features.
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
        # Lines root.
        self.line_coords = coin.SoGeoCoordinate()
        self.lines = coin.SoLineSet()

        # Line style.
        line_color = coin.SoBaseColor()
        line_color.rgb = (1.0, 0.0, 0.0)
        line_style = coin.SoDrawStyle()
        line_style.style = coin.SoDrawStyle.LINES
        line_style.lineWidth = 2

        # Highlight for selection.
        highlight = coin.SoType.fromName('SoFCSelection').createInstance()
        #highlight.documentName.setValue(FreeCAD.ActiveDocument.Name)
        #highlight.objectName.setValue(vobj.Object.Name)
        #highlight.subElementName.setValue("Main")
        highlight.addChild(line_style)
        highlight.addChild(self.line_coords)
        highlight.addChild(self.lines)

        # Surface root.
        lines_root = coin.SoSeparator()
        lines_root.addChild(line_color)
        lines_root.addChild(highlight)
        vobj.addDisplayMode(lines_root,"Wireframe")

    def onChanged(self, vobj, prop):
        '''
        Update Object visuals when a view property changed.
        '''
        pass

    def updateData(self, obj, prop):
        '''
        Update Object visuals when a data property changed.
        '''
        if prop == "Points":
            points = obj.getPropertyByName("Points")
            if points:
                # Get GeoOrigin.
                origin = geo_origin.get(points[0])
                base = deepcopy(origin.Origin)
                base.z = 0

                # Set GeoCoords.
                geo_system = ["UTM", origin.UtmZone, "FLAT"]
                self.line_coords.geoSystem.setValues(geo_system)
                self.line_coords.point.values = points

    def getDisplayMode(self, vobj):
        '''
        Return a list of display modes.
        '''
        return ["Wireframe"]

    def getDefaultDisplayMode(self):
        '''
        Return the name of the default display mode.
        '''
        return "Wireframe"

    def setDisplayMode(self, mode):
        '''
        Map the display mode defined in attach with
        those defined in getDisplayModes.
        '''
        return "Wireframe"

    def getIcon(self):
        '''
        Return object treeview icon.
        '''
        return ICONPATH + '/icons/Alignment.svg'

    def __getstate__(self):
        """
        Save variables to file.
        """
        return None

    def __setstate__(self, state):
        """
        Get variables from file.
        """
        return None
