# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2019 AUTHOR_NAME <AUTHOR_EMAIL>                         *
# *                                                                        *
# *  This program is free software; you can redistribute it and/or modify  *
# *  it under the terms of the GNU Lesser General Public License (LGPL)    *
# *  as published by the Free Software Foundation; either version 2 of     *
# *  the License, or (at your option) any later version.                   *
# *  for detail see the LICENCE text file.                                 *
# *                                                                        *
# *  This program is distributed in the hope that it will be useful,       *
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *  GNU Library General Public License for more details.                  *
# *                                                                        *
# *  You should have received a copy of the GNU Library General Public     *
# *  License along with this program; if not, write to the Free Software   *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *  USA                                                                   *
# *                                                                        *
# **************************************************************************

"""
Alignment object for managing 2D (Horizontal and Vertical) and 3D alignments
"""
import math

import FreeCAD as App
import FreeCADGui as Gui
import Draft
import numpy

from Project.Support import Properties, Units, Utils, DocumentProperties

_CLASS_NAME = 'HorizontalAlignment'
_TYPE = 'Part::Part2DObjectPython'

__title__ = _CLASS_NAME + '.py'
__author__ = "AUTHOR_NAME"
__url__ = "https://www.freecadweb.org"

meta_fields = ['ID', 'Northing', 'Easting']
data_fields = ['Northing', 'Easting', 'Bearing', 'Distance', 'Radius', 'Degree']
station_fields = ['Parent_ID', 'Back', 'Forward']

def create(data, object_name='', units='English', parent=None):
    """
    Class construction method
    object_name - Optional. Name of new object.  Defaults to class name.
    parent - Optional.  Reference to existing DocumentObjectGroup.  Defaults to ActiveDocument
    data - a list of the curve data in tuple('label', 'value') format
    """

    if not data:
        print('No curve data supplied')
        return

    _obj = None
    _name = _CLASS_NAME

    if object_name:
        _name = object_name

    if parent:
        _obj = parent.newObject(_TYPE, _name)
    else:
        _obj = App.ActiveDocument.addObject(_TYPE, _name)

    Draft._BSpline(_obj)

    result = _HorizontalAlignment(_obj)
    result.set_data(data)

    #if not units == 'English':
        #result.set_units(units)

    Draft._ViewProviderWire(_obj.ViewObject)

    App.ActiveDocument.recompute()
    return result

class _HorizontalAlignment(Draft._BSpline):

    def __init__(self, obj, label=''):
        """
        Default Constructor
        """

        super(_HorizontalAlignment, self).__init__(obj)

        self.no_execute = True

        obj.Proxy = self
        self.Type = _CLASS_NAME
        self.Object = obj
        self.errors = []

        obj.Label = label
        obj.Closed = False

        if not label:
            obj.Label = obj.Name

        #add class properties
        Properties.add(obj, 'String', 'ID', 'ID of alignment', '')
        Properties.add(obj, 'Vector', 'Intersection Equation', 'Station equation for intersections with parent alignment', App.Vector(0.0, 0.0, 0.0))
        Properties.add(obj, 'VectorList', 'Alignment Equations', 'Station equation along the alignment', [])
        Properties.add(obj, 'Vector', 'Datum', 'Datum value as Northing / Easting', App.Vector(0.0, 0.0, 0.0))
        Properties.add(obj, 'VectorList', 'Geometry', 'Geometry defining the alignment', [])
        Properties.add(obj, 'String', 'Units', 'Alignment units', 'English', is_read_only=True)
        Properties.add(obj, 'VectorList', 'PIs', 'Discretization of Points of Intersection (PIs) as a list of vectors', [])
        Properties.add(obj, 'Integer', 'Segments', 'Set the curve segments to control accuracy', 1)
        Properties.add(obj, 'Link', 'Parent Alignment', 'Links to parent alignment object', None)
        obj.addProperty('App::PropertyEnumeration', 'Draft Shape', '' ,'Represent the alignment as either a Spline or Wire shape').Draft_Shape = ['Wire', 'Spline']

        delattr(self, 'no_execute')

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def set_units(self, units):
        """
        Sets the units of the alignment
        Does not recompute values
        """

        self.Object.Units = units

    def assign_meta_data(self, data):
        """
        Extract the meta data for the alignment from the data set
        Check it for errors
        Assign properties
        """

        obj = self.Object

        if data['ID']:
            obj.ID = data['ID']

        if data['Northing'] and data['Easting']:
            obj.Datum = App.Vector(float(data['Easting']), float(data['Northing']), 0.0)

    def assign_station_data(self, data):
        """
        Assign the station and intersection equation data
        """

        print('processing station data: ', data)
        obj = self.Object

        for key in data.keys():

            if key == 'equations':

                for _eqn in data['equations']:

                    back = 0
                    forward = 0

                    try:

                        if _eqn[0]:
                            back = float(_eqn[0])

                        if _eqn[1]:
                            forward = float(_eqn[1])

                    except:
                        self.errors.append('Unable to convert station equation (Back: %s, Forward: %s)' % (_eqn[0], _eqn[1]))
                        continue

                    eqns = obj.Alignment_Equations
                    eqns.append(App.Vector(back, forward, 0.0))

                    obj.Alignment_Equations = eqns

            else:

                back = data[key][0]
                forward = data[key][1]

                try:
                    back = float(back)
                    forward = float(forward)

                except:
                    self.errors.append('Unable to convert intersection equation with parent %s: (Back: %s, Forward: %s' % (key, data[key][0], data[key][1]))

                objs = App.ActiveDocument.getObjectsByLabel(key + '_Horiz')

                if objs is None:
                    self.errors.append('Parent ID %s specified, but no object %s_Horiz exists' % key)
                    return

                obj.Parent_Alignment = objs[0]
                obj.Intersection_Equation = App.Vector(back, forward, 0.0)

    def assign_geometry_data(self, datum, data):
        """
        Iterate the dataset, extracting geometric data
        Validate data
        Create separate items for each curve / tangent
        Assign Northing / Easting datums
        """

        _points = [datum]
        _geometry = []

        for item in data:

            _ne = []
            _db = []
            _rd = []

            try:
                _ne = [item['Northing'], item['Easting']]
                _db = [item['Distance'], item['Bearing']]
                _rd = [item['Radius'], item['Degree']]

            except:
                self.errors.append('Inivalid geometric data: %s' % item)
                continue

            geo_vector = App.Vector(0.0, 0.0, 0.0)
            point_vector = App.Vector(0.0, 0.0, 0.0)

            #parse degree of curve / radius values
            if _rd[0]:
                try:
                    geo_vector.z = float(_rd[0])
                except:
                    self.errors.append('Invalid radius: %s' % _rd[0])

            elif _rd[1]:
                try:
                    geo_vector.z = Utils.doc_to_radius(float(_rd[1]))
                except:
                    self.errors.append('Invalid degree of curve: %s' % _rd[1])
            else:
                self.errors.append('Missing Radius / Degree of Curvature')

            #parse bearing / distance values
            if any(_db) and not all(_db):
                self.errors.append('(Distance, Bearing) Incomplete: (%s, %s)' % tuple(_db))
            
            elif all(_db):
                #get the last point in the geometry for the datum, unless empty
                datum = self.Object.Datum

                try:
                    _db[0] = float(_db[0])
                    _db[1] = float(_db[1])

                    #zero distance means coincident PI's.  Skip that.
                    if _db[0] > 0.0:

                        #set values to geo_vector, adding the previous position to the new one
                        point_vector = Utils.distance_bearing_to_coordinates(_db[0], _db[1])
                        geo_vector.x, geo_vector.y = _db

                        if not Units.is_metric_doc():
                            point_vector.multiply(304.8)

                        point_vector = _points[-1].add(point_vector)

                except:
                    self.errors.append('(Distance, Bearing) Invalid: (%s, %s)' % tuple(_db))

            #parse northing / easting values
            if any(_ne) and not all(_ne):
                self.errors.append('(Easting, Northing) Incomplete: ( %s, %s)' % tuple(_ne))

            elif all(_ne):

                try:
                    point_vector.y = float(_ne[0])
                    point_vector.x = float(_ne[1])

                except:
                    self.errors.append('(Easting, Northing) Invalid: (%s, %s)' % tuple(_ne))

                geo_vector.x, geo_vector.y = Utils.coordinates_to_distance_bearing(_points[-1], point_vector)

            #skip coincident PI's
            if geo_vector.x > 0.0:
                _points.append(point_vector)
                _geometry.append(geo_vector)

        self.Object.PIs = _points
        self.Object.Geometry = _geometry

    def get_intersection_delta(self):
        """
        Return the delta of the object intersection point with it's parent alignment
        """

        if not self.Object.Parent_Alignment:
            return App.Vector(0.0, 0.0, 0.0)

        if not self.Object.Intersection_Equation:
            return App.Vector(0.0, 0.0, 0.0)

        parent = self.Object.Parent_Alignment
        int_eq = self.Object.Intersection_Equation
        sta_eqs = self.Object.Alignment_Equations

        parent_coord = self._get_coordinate_at_station(int_eq[0], parent)

        start_sta = 0.0

        #if the first equation's Back is 0.0, the Forward is the starting station
        if sta_eqs:
            if sta_eqs[0][0] == 0.0:
                start_sta = sta_eqs[0][1]

        distance = (int_eq[1] - start_sta) * 304.80

        child_coord = self.Object.Points[0].add(self.Object.Placement.Base)

        if distance > 0.0:

            child_coord = self.Object.Shape.discretize(Distance=distance)[1]

        if not parent_coord or not child_coord:
            print('Unable to calculate geometry datum')
            return App.Vector(0.0, 0.0, 0.0)

        delta = parent_coord.sub(child_coord)

        print('Parent coordinate at %f: %f, %f' % (int_eq[0], parent_coord.x, parent_coord.y))
        print('Child coordinate at %f: %f, %f' % (int_eq[0], child_coord.x, child_coord.y))
        print('Delta at: %f, %f' % (delta.x, delta.y))

        #subtract the child coordinate's intersection point from the parent's
        return delta

    def set_data(self, data):
        """
        Assign curve data to object, parsing and converting to coordinate form
        """

        self.no_execute = True

        self.assign_meta_data(data['meta'])
        self.assign_station_data(data['station'])

        datum = App.Vector(0.0, 0.0, 0.0)

        self.assign_geometry_data(datum, data['data'])

        delattr(self, 'no_execute')

        self.Object.Points = self._discretize_geometry(self.Object.Segments)

    def _get_coordinate_at_station(self, station, parent):
        """
        Return the distance along an alignment from the passed station as a float
        """

        equations = parent.Alignment_Equations

        #default starting station unles otherwise specified
        start_sta = 0.0
        start_index = 0

        #if the first equation's back value is zero, it's forward value is the starting station
        if equations:
            if equations[0][0] == 0.0:
                start_sta = equations[0][1]
                start_index = 1

        distance = 0

        if len(equations) > 1:

            #iterate the equation list, locating the passed station
            for _eqn in equations[start_index:]:

                #does station fall between previous forward and current back?
                if start_sta <= station <= _eqn[0]:
                    break

                #otherwise, accumulate the total distance between the previous forward and current back
                distance += _eqn[0] - start_sta

                #set the starting station to the current forward
                start_sta = _eqn[1]

        distance += station - start_sta

        #station bound checks
        if distance > parent.Shape.Length or distance < 0.0:
            print('Station distance exceeds parent limits (%f not in [%f, %f]' % (station, start_sta, start_sta + parent.Shape.Length))
            return None

        #discretize valid distance
        result = parent.Shape.discretize(Distance=distance * 304.80)[1]

        if len(result) < 2:
            print('failed to discretize')
            return None

        return result

    def _discretize_geometry(self, segments):
        """
        Discretizes the alignment geometry to a series of vector points
        """

        print ('discretizing ', self.Object.Geometry)

        #alignment construction requires a 'look ahead' at the next element
        #This implementation does a 'look back' at the previous.
        #Thus, iteration starts at the second element and
        #the last element is duplicated to ensure it is constructed.
        geometry = self.Object.Geometry

        if not geometry:
            print('No geometry defined.  Unnable to discretize')
            return None

        prev_geo = geometry[0]

        #test in case we only have one geometric element
        if len(geometry) > 1:
            geometry = geometry[1:]
            geometry.append(geometry[-1])

        prev_coord = App.Vector(0.0, 0.0, 0.0)
        prev_curve_tangent = 0.0

        coords = [App.Vector(0.0, 0.0, 0.0)]

        for _geo in geometry:

            print('\n-----=======>>>>>', _geo)

            distance = prev_geo[0]
            bearing_in = math.radians(prev_geo[1])
            bearing_out = math.radians(_geo[1])

            in_tangent = Utils.vector_from_angle(bearing_in)
            out_tangent = Utils.vector_from_angle(bearing_out)

            curve_dir, central_angle = Utils.directed_angle(in_tangent, out_tangent)

            radius = prev_geo[2]

            #if both the current geometry and the look-back geometry have nno-zero radii,
            #we're between curves
            between_curves = radius > 0.0 and _geo[2] > 0.0

            curve_tangent = radius * math.tan(central_angle / 2.0)
            prev_tan_len = distance - curve_tangent - prev_curve_tangent
            _forward = App.Vector(math.sin(bearing_in), math.cos(bearing_in), 0.0)

            print('bearing in ', bearing_in)
            print('bearing_out ', bearing_out)
            print('distance ', distance)
            print('in-tangent ', in_tangent)
            print('out-tangent ', out_tangent)
            print('curve-dir ', curve_dir)
            print('central angle ', central_angle)
            print('radius ', radius)
            print('between curves? ', between_curves)
            print('prev_tan_len ', prev_tan_len)
            print('curve tangent ', curve_tangent)

            #skip if our tangent length is too short leadng up to a curve (likely a compound curve)
            if prev_tan_len >= 1: #DocumentProperties.MinimumTangentLength.get_value() or not between_curves:

                #append three coordinates:  
                #   one a millimeter away from the starting point
                #   one a millimeter away from the ending point
                #   one at the end point
                mm_tan_len = prev_tan_len * 304.80

                coords.append(prev_coord.add(_forward))
                coords.append(prev_coord.add(App.Vector(_forward).multiply(mm_tan_len - 1)))
                coords.append(prev_coord.add(App.Vector(_forward).multiply(mm_tan_len)))

            #zero radius or curve direction means no curve.  We're done
            if radius > 0.0:

                _left = App.Vector(_forward.y, -_forward.x, 0.0)
                seg_rad = central_angle / float(segments)

                prev_coord = coords[-1]

                radius_mm = radius * 304.80
                unit_delta = seg_rad * 0.01

                print('prev coord ', prev_coord)
                print('radius mm ', radius_mm)
                print('unit delta ', unit_delta)
                print('seg_rad ', seg_rad)
                print('segments ', segments)

                for _i in range(0, segments):
                    
                    delta = float(_i + 1) * seg_rad

                    _dfw = App.Vector(_forward).multiply(math.sin(delta))
                    _dlt = App.Vector(_left).multiply(curve_dir * (1 - math.cos(delta)))

                    coords.append(prev_coord.add(_dfw.add(_dlt).multiply(radius_mm)))

                    print('next coord ', coords[-1])

            prev_geo = _geo
            prev_coord = coords[-1]
            prev_curve_tangent = curve_tangent

        print ('COORDS: ', coords)
        return coords

    def onChanged(self, obj, prop):

        #dodge onChanged calls during initialization
        if hasattr(self, 'no_execute'):
            return

        if prop == "Segments":
            self.Object.Points = self._discretize_geometry(self.Object.Segments)
            self.wire.Points = self.Object.Points

    def execute(self, obj):

        if hasattr(self, 'no_execute'):
            return

        print('executing ', self.Object.Label)


        super(_HorizontalAlignment, self).execute(obj)
        self.Object.Placement.Base = self.Object.Placement.Base.add(self.get_intersection_delta())
        #wire = Draft.makeWire(self.Object.Points)
        #wire.Placement.Base = self.Object.Placement.Base
        super(_HorizontalAlignment, self).execute(obj)

class _ViewProviderHorizontalAlignment:

    def __init__(self, obj):
        """
        Initialize the view provider
        """
        obj.Proxy = self

    def __getstate__(self):
        return None
    
    def __setstate__(self, state):
        return None

    def attach(self, obj):
        """
        View provider scene graph initialization
        """
        self.Object = obj.Object

    def updateData(self, fp, prop):
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

    def onChanged(self, vp, prop):
        """
        Handle individual property changes
        """
        pass