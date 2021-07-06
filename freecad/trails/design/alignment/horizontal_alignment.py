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
from math import inf
import Draft
import Part

from freecad.trails import ICONPATH, geo_origin
from pivy import coin

from ..project.support import properties, units
from ..geometry import support
from . import alignment_group
from .alignment_model import AlignmentModel
from .alignment import Alignment
from .alignment_registrar import AlignmentRegistrar

from ...geomatics.guideline import gl_clusters

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
    print('\n\t\t-=-=-=-=-= HORIZONTAL ALIGNMENT GEOMETRY -=-=-=-=-=\n', geometry)
    _obj.ModelKeeper = str(geometry)
    _obj.Proxy.set_geometry(geometry, zero_reference)
    ViewProviderHorizontalAlignment(_obj.ViewObject)

    clusters = gl_clusters.create()
    _obj.addObject(clusters)

    App.ActiveDocument.recompute()

    return _obj

class HorizontalAlignment(Alignment):
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
        obj.Label = label

        self.init_class_members(obj)

        #create property to indicate object is fully initialized
        #done to prevent premature event excution
        obj.addProperty('App::PropertyBool', 'Initialized', 'Base', 'Is Initialized').Initialized = True

    def init_class_members(self, obj):
        """
        Separate function for initialization on creation / reload
        """

        obj.Proxy = self

        self.errors = []

        self.curve_edges = None

        self.model = None
        self.meta = {}
        self.hashes = None

        self.Type = 'Trails::HorizontalAlignment'
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
        super().__init__()

        self.init_class_members(obj)
        self.set_geometry(eval(obj.ModelKeeper))


    def initialize_model(self, model, obj):
        """
        Callback triggered from the parent group to force model update
        model - the alignment model
        obj - the alignment object
        """

        if isinstance(model, AlignmentModel):
            model = model.data

        self.model = AlignmentModel(model)
        self.build_curve_edge_dict(obj)

    def _plot_vectors(self, stations, interval=1.0, is_ortho=True):
        """
        Testing function to plot coordinates and vectors between specified
        stations.

        stations - tuple / list of starting / ending stations
        is_ortho - bool, False plots tangent, True plots orthogonal
        """

        if not stations:
            stations = [
                self.model.data.get('meta').get('StartStation'),
                self.model.data.get('meta').get('StartStation') \
                    + self.model.data.get('meta').get('Length') / 1000.0
            ]

        _pos = stations[0]
        _items = []

        while _pos < stations[1]:

            if is_ortho:
                _items.append(tuple(self.model.get_orthogonal(_pos, 'Left')))

            else:
                _items.append(tuple(self.model.get_tangent(_pos)))

            _pos += interval

        for _v in _items:

            _start = _v[0]
            _end = _start + _v[1] * 100000.0

            _pt = [self.model.data.get('meta').get('Start')]*2
            _pt[0] = _pt[0].add(_start)
            _pt[1] = _pt[1].add(_end)

            line = Draft.makeWire(_pt, closed=False, face=False, support=None)

            Draft.autogroup(line)

        App.ActiveDocument.recompute()


    def build_curve_edge_dict(self, obj):
        """
        Build the dictionary which correlates edges to their corresponding
        curves for quick lookup when curve editing
        """

        curve_dict = {}
        curves = self.model.data.get('geometry')

        print('\n\t[][][][[] CURVES!!! [][][][][]\n\t',curves)
        #iterate the curves, creating the dictionary for each curve
        #that lists it's wire edges keyed by it's Edge index
        for _i, curve in enumerate(curves):

            #curve.set('ObjectID', f'{curve.get('Type')}{str(_i)}')

            if curve.get('Type') == 'Line':
                continue

            curve_edges = obj.Shape.Edges
            curve_pts = [curve.get('Start'), curve.get('End')]
            edge_dict = {}

            #iterate edge list, add edges that fall within curve limits
            for _i, edge in enumerate(curve_edges):

                edge_pts = [edge.Vertexes[0].Point, edge.Vertexes[1].Point]

                #empty list means we haven't found the start yet
                if not edge_dict:

                    if not support.within_tolerance(curve_pts[0], edge_pts[0]):
                        continue

                #still here?  then we're within the geometry
                edge_dict['Edge' + str(_i + 1)] = edge

                #if this edge fits the end, we're done
                if support.within_tolerance(curve_pts[1], edge_pts[1]):
                    break

            #calculate a unique hash based on the curve start and end points
            #and save the edge list to it

            curve_dict[curve['Hash']] = edge_dict

        self.curve_edges = curve_dict

    def get_pi_coords(self):
        """
        Convenience function to get PI coordinates from the model
        """

        return self.model.get_pi_coords()

    def get_edges(self):
        """
        Return the dictionary of curve edges
        """

        return self.curve_edges

    def get_data(self):
        """
        Return the complete dataset for the alignment
        """

        return self.model.data

    def get_data_copy(self):
        """
        Returns a deep copy of the alignment dataset
        """

        return deepcopy(self.model.data)

    def get_length(self):
        """
        Return the alignment length
        """

        return self.model.data.get('meta').get('Length')

    def get_curves(self):
        """
        Return a list of only the curves
        """

        return [_v for _v in self.model.data.get('geometry') \
            if _v.get('Type') != 'Line']

    def get_geometry(self, curve_hash=None):
        """
        Return the geometry of the curve matching the specified hash
        value.  If no match, return all of the geometry
        """

        if not curve_hash:
            return self.model.data.get('geometry')

        for _geo in self.model.data.get('geometry'):

            if _geo['Hash'] == curve_hash:
                return _geo

        return None

    def update_curves(self, curves, pi_list, zero_reference=False):
        """
        Assign updated alignment curves to the model.
        """

        _model = {
            'meta': {
                'Start': pi_list[0],
                'StartStation':
                    self.model.data.get('meta').get('StartStation'),
                'End': pi_list[-1],
            },
            'geometry': curves,
            'station': self.model.data.get('station')
        }

        self.set_geometry(_model, zero_reference)

    def set_geometry(self, geometry, zero_reference=False):
        """
        Assign geometry to the alignment object
        """
        print('CREATE ALIGNMENT MODEL')
        self.model = AlignmentModel(geometry, zero_reference)

        print ('MODEL DATA=',self.model.data)

        if self.model.errors:
            for _err in self.model.errors:
                print('Error in alignment {0}: {1}'\
                    .format(self.Object.Label, _err)
                     )

            self.model.errors.clear()

        self.assign_meta_data()

        return self.model.errors

    def assign_meta_data(self, model=None):
        """
        Extract the meta data for the alignment from the data set
        Check it for errors
        Assign properties
        """

        obj = self.Object

        meta = self.model.data.get('meta')

        if meta.get('ID'):
            obj.ID = meta.get('ID')

        if meta.get('Description'):
            obj.Description = meta.get('Description')

        if meta.get('ObjectID'):
            obj.ObjectID = meta.get('ObjectID')

        if meta.get('Length'):
            obj.Length = meta.get('Length')

        if meta.get('Status'):
            obj.Status = meta.get('Status')

        if meta.get('StartStation'):
            obj.Start_Station = str(meta.get('StartStation')) + ' ft'

    def onChanged(self, obj, prop):
        """
        Property change callback
        """

        #if not super().onChanged(obj, prop):
        #    return

        #dodge onChanged calls during initialization
        #if hasattr(self, 'no_execute'):
        #    return

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

        #if not super().execute(obj):
        #    return

        points = None

        if hasattr(self.model, 'discretize_geometry'):
            points = self.model.discretize_geometry(
                [0.0], self.Object.Method, self.Object.Seg_Value)

        if not points:
            return

        _wires = []
        _prev = App.Vector(points[0])

        for _p in points[1:]:
            _q = App.Vector(_p)

            _wires.append(Part.LineSegment(_prev, _q))
            _prev = _q

        _shape = Part.Shape(_wires)
        _wire = Part.Wire(_shape.Edges)

        obj.Shape = Part.makeCompound(_wire)

class ViewProviderHorizontalAlignment():

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

        # Lines root.
        self.line_coords = coin.SoGeoCoordinate()
        self.lines = coin.SoLineSet()

        # Line style.
        line_color = coin.SoBaseColor()
        line_color.rgb = (1.0, 0.0, 0.0)
        line_style = coin.SoDrawStyle()
        line_style.style = coin.SoDrawStyle.LINES
        line_style.lineWidth = 2

        # Labels root.
        self.tick_coords = coin.SoGeoCoordinate()
        self.ticks = coin.SoLineSet()
        self.labels = coin.SoSeparator()

        # Highlight for selection.
        highlight = coin.SoType.fromName('SoFCSelection').createInstance()
        highlight.style = 'EMISSIVE_DIFFUSE'
        highlight.addChild(line_style)
        highlight.addChild(self.line_coords)
        highlight.addChild(self.lines)
        highlight.addChild(self.tick_coords)
        highlight.addChild(self.ticks)

        # Alignment root.
        lines_root = coin.SoSeparator()
        lines_root.addChild(line_color)
        lines_root.addChild(self.labels)
        lines_root.addChild(highlight)
        vobj.addDisplayMode(lines_root,"Wireframe")

    def onChanged(self, vobj, prop):
        """
        Handle individual property changes
        """

        if prop == "Labels":

            self.labels.removeAllChildren()
            labels = vobj.getPropertyByName("Labels")

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
            shape = obj.getPropertyByName("Shape")

            if shape.Vertexes:
                points = []

                for vertex in shape.Vertexes:
                    points.append(vertex.Point)

                # Get GeoOrigin.
                origin = geo_origin.get(points[0])
                base = deepcopy(origin.Origin)
                base.z = 0

                # Set GeoCoords.
                geo_system = ["UTM", origin.UtmZone, "FLAT"]
                self.line_coords.geoSystem.setValues(geo_system)
                self.line_coords.point.values = points

    def get_stations(self, obj):
        """
        Retrieve the coordinates of the start and end points of the station
        tick mark orthogonal to the alignment
        """

        start = obj.Proxy.model.data['meta']['StartStation']
        length = obj.Proxy.model.data['meta']['Length']
        end = start + length/1000

        stations = {}

        for sta in range(int(start), int(end)):

            if sta % 10 == 0:

                tuple_coord, tuple_vec =\
                    obj.Proxy.model.get_orthogonal( sta, "Left", True)

                coord = App.Vector(tuple_coord)
                vec = App.Vector(tuple_vec)

                left_vec = deepcopy(vec)
                right_vec = deepcopy(vec)

                left_side = coord.add(left_vec.multiply(1500))
                right_side = coord.add(right_vec.negative().multiply(1500))

                stations[sta] = [left_side, right_side]

        return stations

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
