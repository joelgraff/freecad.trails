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

"""
Class for managing 2D Horizontal Alignments
"""
from copy import deepcopy

import FreeCAD as App
from FreeCAD import Vector
import Part

from freecad.trails import ICONPATH, geo_origin
from ...geomatics.region import regions
from ..project.support import properties, units
from .alignment_functions import DataFunctions, ViewFunctions

from pivy import coin
from math import inf

__title__ = 'horizontal_alignment.py'
__author__ = 'Joel Graff'
__url__ = "https://www.freecadweb.org"


def create(geometry, object_name='', parent=None, no_visual=False, zero_reference=False):
    """
    Class construction method
    object_name - Optional. Name of new object.  Defaults to class name.
    no_visual - If true, generates the object without a ViewProvider.
    """

    if not geometry:
        print('No curve geometry supplied')
        return

    _name = "Alignment FeaturePython Object"

    if object_name:
        _name = object_name

    _obj = None

    if not parent:
        _obj = App.ActiveDocument.addObject("App::DocumentObjectGroupPython", _name)

    else:
        _obj = parent.newObject("App::DocumentObjectGroupPython", _name)

    HorizontalAlignment(_obj, _name)
    _obj.Label = _name
    _obj.ModelKeeper = str(geometry)
    _obj.Proxy.set_geometry(geometry, zero_reference)
    ViewProviderHorizontalAlignment(_obj.ViewObject)

    regs = regions.create()
    _obj.addObject(regs)

    App.ActiveDocument.recompute()

    return _obj

class HorizontalAlignment(DataFunctions):
    """
    FeaturePython Alignment class
    """

    def __init__(self, obj, label=''):
        """
        Default Constructor
        """

        #metadata
        properties.add(obj, 'String', 'ID', 'ID of alignment', label)
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

        obj.addProperty("Part::PropertyPartShape", "Shape", "Base",
            "Alignment Shape").Shape = Part.Shape()

        properties.add(
            obj, 'Vector', 'Datum', 'Datum value as Northing / Easting',
            App.Vector(0.0, 0.0, 0.0)
        )

        properties.add(
            obj, 'FloatList', 'Hashes', 'Coordiante hashes', []
        )

        #geometry
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

        obj.addProperty(
            'App::PropertyString', 'ModelKeeper', 'Base', "ModelKeeper"
        ).ModelKeeper = ''

        properties.add(obj, 'Float', 'Segment.Seg_Value',
                       'Set the curve segments to control accuracy',
                       int(1000.0 / units.scale_factor()) / 100.0
                      )

        #add class members
        self.init_class_members(obj)

    def init_class_members(self, obj):
        """
        Separate function for initialization on creation / reload
        """

        obj.Proxy = self
        self.Type = 'Trails::HorizontalAlignment'

        self.errors = []

        self.curve_edges = None

        self.model = None
        self.meta = {}
        self.hashes = None

        self.Object = obj

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onDocumentRestored(self, obj):
        """
        Restore object references on reload
        """
        self.init_class_members(obj)
        self.set_geometry(eval(obj.ModelKeeper))

    def onChanged(self, obj, prop):
        """
        Property change callback
        """
        if prop == "Method":

            _prop = obj.getPropertyByName(prop)

            if _prop == 'Interval':
                self.Object.Seg_Value = int(3000.0 / units.scale_factor())

            elif _prop == 'Segment':
                self.Object.Seg_Value = 200.0

            elif _prop == 'Tolerance':
                self.Object.Seg_Value = \
                    int(1000.0 / units.scale_factor()) / 100.0

    def execute(self, obj):
        """
        Recompute callback
        """
        if hasattr(self.model, 'discretize_geometry'):
            curves, spirals, lines, points = obj.Proxy.model.discretize_geometry(
                [0.0], obj.Method, obj.Seg_Value, types=True)

            # Get GeoOrigin.
            origin = geo_origin.get(points[0])
            base = deepcopy(origin.Origin)
            base.z = 0

            obj.Shape = self.get_shape(lines, curves, spirals, base)


class ViewProviderHorizontalAlignment(ViewFunctions):

    def __init__(self, vobj):
        """
        Initialize the view provider
        """

        vobj.addProperty(
            "App::PropertyBool", "Labels", "Base",
            "Show/hide labels").Labels = False

        vobj.Proxy = self

    def attach(self, vobj):
        """
        View provider scene graph initialization
        """

        self.Object = vobj.Object

        # Line style.
        line_style = coin.SoDrawStyle()
        line_style.style = coin.SoDrawStyle.LINES
        line_style.lineWidth = 2

        # Line geometry keepers.
        line_color = coin.SoBaseColor()
        line_color.rgb = (1.0, 0.0, 0.0)
        self.lines = coin.SoSeparator()
        self.lines.addChild(line_style)
        self.lines.addChild(line_color)

        # Line geometry keepers.
        curve_color = coin.SoBaseColor()
        curve_color.rgb = (0.0, 0.5, 0.0)
        self.curves = coin.SoSeparator()
        self.curves.addChild(line_style)
        self.curves.addChild(curve_color)

        # Line geometry keepers.
        spiral_color = coin.SoBaseColor()
        spiral_color.rgb = (0.0, 0.33, 1.0)
        self.spirals = coin.SoSeparator()
        self.spirals.addChild(line_style)
        self.spirals.addChild(spiral_color)

        # Labels root.
        self.tick_coords = coin.SoGeoCoordinate()
        self.ticks = coin.SoLineSet()
        self.labels = coin.SoSeparator()

        # Alignment root.
        lines_root = coin.SoSeparator()
        lines_root.addChild(self.lines)
        lines_root.addChild(self.curves)
        lines_root.addChild(self.spirals)
        lines_root.addChild(self.ticks)
        lines_root.addChild(self.labels)
        vobj.addDisplayMode(lines_root,"Wireframe")

    def onChanged(self, vobj, prop):
        """
        Handle individual property changes
        """

        if prop == "Labels":

            self.labels.removeAllChildren()
            labels = vobj.getPropertyByName(prop)

            if labels:
                # Get GeoOrigin.
                origin = geo_origin.get()
                base = deepcopy(origin.Origin)
                base.z = 0

                geo_system = ["UTM", origin.UtmZone, "FLAT"]

                points = []
                line_vert = []
                stations = self.get_stations(vobj.Object)

                for label, tick in stations.items():
                    font = coin.SoFont()
                    font.size = 3000
                    sta_label = coin.SoSeparator()
                    location = coin.SoTranslation()
                    text = coin.SoAsciiText()

                    location.translation = deepcopy(tick[1]).sub(base)
                    text.string.setValues([str(label)])

                    sta_label.addChild(font)
                    sta_label.addChild(location)
                    sta_label.addChild(text)
                    self.labels.addChild(sta_label)

                    points.extend(tick)
                    line_vert.append(len(tick))

                self.tick_coords.geoSystem.setValues(geo_system)
                self.tick_coords.point.values = points
                self.ticks.numVertices.values = line_vert

    def updateData(self, obj, prop):
        '''
        Update Object visuals when a data property changed.
        '''
        if prop == "Shape":
            shape = obj.getPropertyByName(prop)
            if not shape.SubShapes: return

            # Get GeoOrigin.
            origin = geo_origin.get()
            geo_system = ["UTM", origin.UtmZone, "FLAT"]
            base = deepcopy(origin.Origin)
            base.z = 0

            copy_shape = shape.copy()
            copy_shape.Placement.move(base)

            lines = copy_shape.SubShapes[0]
            for wire in lines.Wires:
                points = []
                for vertex in wire.OrderedVertexes:
                    points.append(vertex.Point)

                line = coin.SoType.fromName('SoFCSelection').createInstance()
                line.style = 'EMISSIVE_DIFFUSE'

                line_coords = coin.SoGeoCoordinate()
                line_coords.geoSystem.setValues(geo_system)
                line_coords.point.values = points
                line_set = coin.SoLineSet()

                line.addChild(line_coords)
                line.addChild(line_set)
                self.lines.addChild(line)

            curves = copy_shape.SubShapes[1]
            for wire in curves.Wires:
                points = []
                for vertex in wire.OrderedVertexes:
                    points.append(vertex.Point)

                curve = coin.SoType.fromName('SoFCSelection').createInstance()
                curve.style = 'EMISSIVE_DIFFUSE'

                curve_coords = coin.SoGeoCoordinate()
                curve_coords.geoSystem.setValues(geo_system)
                curve_coords.point.values = points
                curve_set = coin.SoLineSet()

                curve.addChild(curve_coords)
                curve.addChild(curve_set)
                self.curves.addChild(curve)

            spirals = copy_shape.SubShapes[2]
            for wire in spirals.Wires:
                points = []
                for vertex in wire.OrderedVertexes:
                    points.append(vertex.Point)

                spiral = coin.SoType.fromName('SoFCSelection').createInstance()
                spiral.style = 'EMISSIVE_DIFFUSE'

                spiral_coords = coin.SoGeoCoordinate()
                spiral_coords.geoSystem.setValues(geo_system)
                spiral_coords.point.values = points
                spiral_set = coin.SoLineSet()

                spiral.addChild(spiral_coords)
                spiral.addChild(spiral_set)
                self.spirals.addChild(spiral)

    def getDisplayMode(self, obj):
        """
        Valid display modes
        """
        return ["Wireframe"]

    def getDefaultDisplayMode(self):
        """
        Return default display mode
        """
        return "Wireframe"

    def setDisplayMode(self, mode):
        """
        Set mode - wireframe only
        """
        return "Wireframe"

    def getIcon(self):
        '''
        Return object treeview icon.
        '''
        return ICONPATH + '/icons/Alignment.svg'

    def claimChildren(self):
        """
        Provides object grouping
        """
        return self.Object.Group

    def setEdit(self, vobj, mode=0):
        """
        Enable edit
        """
        return True

    def unsetEdit(self, vobj, mode=0):
        """
        Disable edit
        """
        return False

    def doubleClicked(self, vobj):
        """
        Detect double click
        """
        pass

    def setupContextMenu(self, obj, menu):
        """
        Context menu construction
        """
        pass

    def edit(self):
        """
        Edit callback
        """
        pass
    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
