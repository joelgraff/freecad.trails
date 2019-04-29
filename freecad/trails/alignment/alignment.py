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
import Draft

from ..project.support import properties, units
from ..geometry import support, arc
from . import alignment_group, alignment_model

_CLASS_NAME = 'Alignment'
_TYPE = 'Part::Part2DObjectPython'

__title__ = 'alignment.py'
__author__ = 'Joel Graff'
__url__ = "https://www.freecadweb.org"


def create(geometry, object_name='', no_visual=False):
    """
    Class construction method
    object_name - Optional. Name of new object.  Defaults to class name.
    no_visual - If true, generates the object without a ViewProvider.
    """

    if not geometry:
        print('No curve geometry supplied')
        return

    _obj = None
    _name = _CLASS_NAME

    if object_name:
        _name = object_name

    parent = alignment_group.create()

    _obj = parent.Object.newObject(_TYPE, _name)

    result = Alignment(_obj, _name)
    result.set_geometry(geometry)

    if not no_visual:
        Draft._ViewProviderWire(_obj.ViewObject)

    App.ActiveDocument.recompute()
    return result

#Construction order:
#Calc arc parameters
#Sort arcs
#calculate arc start coordinates by internal position and apply to arcs

class Alignment(Draft._Wire):
    """
    FeaturePython Alignment class
    """

    def __init__(self, obj, label=''):
        """
        Default Constructor
        """

        super(Alignment, self).__init__(obj)

        self.no_execute = True

        obj.Proxy = self

        self.Type = _CLASS_NAME
        self.Object = obj
        self.errors = []

        self.curve_edges = None

        self.model = None
        self.meta = {}
        self.hashes = None

        obj.Label = label
        obj.Closed = False

        if not label:
            obj.Label = obj.Name

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

        delattr(self, 'no_execute')

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onDocumentRestored(self, obj):
        """
        Restore object references on reload
        """

        self.Object = obj

        self.model = alignment_model.AlignmentModel(
            self.Object.InList[0].Proxy.get_alignment_data(obj.ID)
        )

        self.build_curve_edge_dict()

    def build_curve_edge_dict(self):
        """
        Build the dictionary which correlates edges to their corresponding
        curves for quick lookup when curve editing
        """

        curve_dict = {}
        curves = self.model.data['geometry']

        #iterate the curves, creating the dictionary for each curve
        #that lists it's wire edges keyed by it's Edge index
        for curve in curves:

            if curve['Type'] == 'Line':
                continue

            curve_edges = self.Object.Shape.Edges
            curve_pts = [curve['Start'], curve['End']]
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

        coords = self.model.get_pi_coords()
        datum = self.model.get_datum()

        for _coord in coords:
            _coord.sub(datum)

        return coords

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

    def get_geometry(self, curve_hash=None):
        """
        Return the geometry of the curve matching the specified hash
        value.  If no match, return all of the geometry
        """

        if not curve_hash:
            return self.model.data['geometry']

        for _geo in self.model.data['geometry']:

            if _geo['Hash'] == curve_hash:
                return _geo

        return None

    def set_geometry(self, geometry):
        """
        Assign geometry to the alignment object
        """

        self.model = alignment_model.AlignmentModel(geometry)

        self.assign_meta_data()

        return self.model.errors

    def assign_meta_data(self):
        """
        Extract the meta data for the alignment from the data set
        Check it for errors
        Assign properties
        """

        obj = self.Object

        meta = self.model.data['meta']

        if meta.get('ID'):
            obj.ID = meta['ID']

        if meta.get('Description'):
            obj.Description = meta['Description']

        if meta.get('ObjectID'):
            obj.ObjectID = meta['ObjectID']

        if meta.get('Length'):
            obj.Length = meta['Length']

        if meta.get('Status'):
            obj.Status = meta['Status']

        if meta.get('StartStation'):
            obj.Start_Station = str(meta['StartStation']) + ' ft'

    def discretize_geometry(self, interval=10.0, interval_type='Segment'):
        """
        Discretizes the alignment geometry to a series of vector points
        """

        geometry = self.model.data['geometry']
        datum = self.model.data['meta']['Start']
        points = [[App.Vector()]]
        last_curve = None
        hashes = {}

        print('\n<<<--datum--->>>', datum)
        #discretize each arc in the geometry list,
        #store each point set as a sublist in the main points list
        for curve in geometry:

            if not curve:
                continue

            curve_hash = hash(tuple(curve['Start']) + tuple(curve['End']))

            if curve['Type'] == 'Curve':

                tmp_curve = deepcopy(curve)

                print('\n<<<--- curve --->>>', tmp_curve)
                for _coord in ['Start', 'PI', 'End', 'Center']:
                    tmp_curve[_coord] = tmp_curve[_coord].sub(datum)

                _pts, _hsh = arc.get_points(tmp_curve, interval, interval_type)

                points.append(_pts)
                hashes = {**hashes,
                          **dict.fromkeys(set(_hsh), curve_hash)}

            elif curve['Type'] == 'Line':
                points.append(
                    [curve['Start'].sub(datum), curve['End'].sub(datum)]
                )

            last_curve = curve

        self.hashes = hashes

        #store the last point of the first geometry for the next iteration
        _prev = points[0][-1]
        result = points[0]

        if not (_prev and result):
            return None

        #iterate the point sets, adding them to the result set
        #and eliminating any duplicate points
        for item in points[1:]:

            if _prev.sub(item[0]).Length < 0.0001:
                result.extend(item[1:])
            else:
                result.extend(item)

            _prev = item[-1]

        last_tangent = abs(
            self.model.data['meta']['Length'] \
                - last_curve['InternalStation'][1]
            )

        if not support.within_tolerance(last_tangent):
            _vec = support.vector_from_angle(last_curve['BearingOut'])\
                .multiply(last_tangent)

            last_point = result[-1]

            result.append(last_point.add(_vec))

        if not self.model.data['meta'].get('End'):
            self.model.data['meta']['End'] = result[-1]

        print('\n<<<--- result --->>>', result)
        return result

    def onChanged(self, obj, prop):
        """
        Property change callback
        """
        #dodge onChanged calls during initialization
        if hasattr(self, 'no_execute'):
            return

        if prop == "Method":

            _prop = obj.getPropertyByName(prop)

            if _prop == 'Interval':
                self.Object.Seg_Value = int(3000.0 / units.scale_factor())

            elif _prop == 'Segment':
                self.Object.Seg_Value = 200.0

            elif _prop == 'Tolerance':
                self.Object.Seg_Value = int(1000.0 / units.scale_factor()) / 100.0

    def execute(self, obj):
        """
        Recompute callback
        """
        if hasattr(self, 'no_execute'):
            return

        points = self.discretize_geometry(
            self.Object.Seg_Value, self.Object.Method)

        if not points:
            return

        self.Object.Points = points

        _pl = App.Placement()
        _pl.Base = self.model.data['meta']['Start']

        self.Object.Placement = _pl

        super(Alignment, self).execute(obj)


class _ViewProviderHorizontalAlignment:

    def __init__(self, obj):
        """
        Initialize the view provider
        """
        obj.Proxy = self
        self.Object = obj

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def attach(self, obj):
        """
        View provider scene graph initialization
        """
        self.Object = obj

    def updateData(self, obj, prop):
        """
        Property update handler
        """
        pass

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

    def onChanged(self, vobj, prop):
        """
        Handle individual property changes
        """
        pass
