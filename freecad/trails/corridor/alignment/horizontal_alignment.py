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
import FreeCAD as App
import Draft

from freecad.trails.project.support import Properties, Units, Utils
from freecad.trails.geometry import Arc, Line, Support
from freecad.trails.corridor.alignment import alignment_group

_CLASS_NAME = 'HorizontalAlignment'
_TYPE = 'Part::Part2DObjectPython'

__title__ = 'horizontal_alignment.py'
__author__ = 'Joel Graff'
__url__ = "https://www.freecadweb.org"


def create(geometry, object_name=''):
    """
    Class construction method
    object_name - Optional. Name of new object.  Defaults to class name.
    parent - Optional.  Reference to existing DocumentObjectGroup.
             Defaults to ActiveDocument
    data - a list of the curve data in tuple('label', 'value') format
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

    result = _HorizontalAlignment(_obj, _name)
    result.set_geometry(geometry)

    Draft._ViewProviderWire(_obj.ViewObject)

    App.ActiveDocument.recompute()
    return result

#Construction order:
#Calc arc parameters
#Sort arcs
#calculate arc start coordinates by internal position and apply to arcs

class _HorizontalAlignment(Draft._Wire):

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

        self.geometry = []
        self.meta = {}

        obj.Label = label
        obj.Closed = False

        if not label:
            obj.Label = obj.Name

        #add class properties

        #metadata
        Properties.add(obj, 'String', 'ID', 'ID of alignment', '')
        Properties.add(obj, 'String', 'oID', 'Object ID', '')

        Properties.add(
            obj, 'Length', 'Length', 'Alignment length', 0.0, is_read_only=True
        )

        Properties.add(
            obj, 'String', 'Description', 'Alignment description', ''
        )

        Properties.add(
            obj, 'Length', 'Start Station',
            'Starting station of the alignment', 0.0
        )

        obj.addProperty(
            'App::PropertyEnumeration', 'Status', 'Base', 'Alignment status'
        ).Status = ['existing', 'proposed', 'abandoned', 'destroyed']

        Properties.add(obj, 'VectorList', 'Station Equations',
                       'Station equation along the alignment', [])
        Properties.add(
            obj, 'Vector', 'Datum', 'Datum value as Northing / Easting',
            App.Vector(0.0, 0.0, 0.0)
        )



        #geometry
        Properties.add(
            obj, 'VectorList', 'PIs', """
            Discretization of Points of Intersection (PIs) as a list of
            vectors""", []
            )

        Properties.add(
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

        Properties.add(obj, 'Float', 'Segment.Seg_Value',
                       'Set the curve segments to control accuracy', 1.0)

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

    def get_geometry(self):
        """
        Return the geometry dictionary of the alignment,
        reflecting any changes to the data
        """

        return self.geometry

    def set_geometry(self, geometry):
        """
        Assign geometry to the alignment object
        """

        self.geometry = geometry

        self.assign_meta_data()
        self.assign_station_data()

        for _i, _geo in enumerate(self.geometry['geometry']):

            if _geo['Type'] == 'Curve':
                _geo = Arc.get_parameters(_geo)

            elif _geo['Type'] == 'Line':
                _geo = Line.get_parameters(_geo)

            else:
                self.errors.append('Undefined geometry: ' + _geo)
                continue

            self.geometry['geometry'][_i] = _geo

        self.validate_datum()

        self.validate_stationing()

        if not self.validate_bearings():
            return False

        self.validate_coordinates()

        self.validate_alignment()

        #call once more to catch geometry added by validate_alignment()
        self.validate_stationing()

        return True

    def validate_alignment(self):
        """
        Ensure the alignment geometry is continuous.
        Any discontinuities (gaps between end / start coordinates)
        must be filled by a completely defined line
        """

        _prev_coord = self.geometry['meta']['Start']
        _geo_list = []

        for _geo in self.geometry['geometry']:

            if not _geo:
                continue

            _coord = _geo['Start']

            if not Support.within_tolerance(_coord.Length, _prev_coord.Length):

                #build the line using the provided parameters and add it
                _geo_list.append(
                    Line.get_parameters({'Start': App.Vector(_prev_coord),
                                         'End': App.Vector(_coord),
                                         'BearingIn': _geo['BearingIn'],
                                         'BearingOut': _geo['BearingOut'],
                                         })
                )

            _geo_list.append(_geo)
            _prev_coord = _geo['End']

        self.geometry['geometry'] = _geo_list

    def validate_datum(self):
        """
        Ensure the datum is valid, assuming 0+00 / (0,0,0)
        for station and coordinate where none is suplpied and it
        cannot be inferred fromt the starting geometry
        """
        _datum = self.geometry['meta']
        _geo = self.geometry['geometry'][0]

        if not _geo or not _datum:
            print('Unable to validate alignment datum')
            return

        _datum_truth = [not _datum.get('StartStation') is None,
                        not _datum.get('Start') is None]

        _geo_truth = [not _geo.get('StartStation') is None,
                      not _geo.get('Start') is None]

        #----------------------------
        #CASE 0
        #----------------------------
        #both defined?  nothing to do
        if all(_datum_truth):
            return

        _geo_station = 0
        _geo_start = App.Vector()

        if _geo_truth[0]:
            _geo_station = _geo['StartStation']

        if _geo_truth[1]:
            _geo_start = _geo['Start']

        #---------------------
        #CASE 1
        #---------------------
        #no datum defined?  use initial geometry or zero defaults
        if not any(_datum_truth):

            _datum['StartStation'] = _geo_station
            _datum['Start'] = _geo_start
            return

        #--------------------
        #CASE 2
        #--------------------
        #station defined?
        #if the geometry has a station and coordinate,
        #project the start coordinate

        if _datum['StartStation']:

            _datum['Start'] = _geo_start

            #assume geometry start if no geometry station
            if not _geo_truth[0]:
                return

            #scale the distance to the system units
            delta = _geo_station - _datum['StartStation']

            #cutoff if error is below tolerance
            if not Support.within_tolerance(delta):
                delta *= Units.scale_factor()
            else:
                delta = 0.0

            #assume geometry start if station delta is zero
            if delta:

                #calcualte the start based on station delta
                _datum['Start'] = _datum['Start'].sub(
                    Support.vector_from_angle(
                        _geo['BearingIn']).multiply(delta)
                )

            return

        #---------------------
        #CASE 3
        #---------------------
        #datum start coordinate is defined
        #if the geometry has station and coordinate,
        #project the start station
        _datum['StartStation'] = _geo_station

        #assume geometry station if no geometry start
        if _geo_truth[1]:

            #scale the length to the document units
            delta = _geo_start.sub(_datum['Start']).Length/Units.scale_factor()

            _datum['StartStation'] -= delta

    def validate_coordinates(self):
        """
        Iterate the geometry, testing for incomplete / incorrect station /
        coordinate values. Fix them where possible, error otherwise
        """

        #calculate distance bewteen curve start and end using
        #internal station and coordinate vectors

        _datum = self.geometry['meta']
        _geo_data = self.geometry['geometry']

        _prev_geo = {'End': _datum['Start'], 'InternalStation': (0.0, 0.0),
                     'StartStation': _datum['StartStation'], 'Length': 0.0
                    }

        for _geo in _geo_data:

            if not _geo:
                continue

            #get the vector between the two gemetries
            #and the station distance
            _vector = _geo['Start'].sub(_prev_geo['End'])
            _sta_len = abs(
                _geo['InternalStation'][0] - _prev_geo['InternalStation'][1]
            )

            #calculate the difference between the vector length
            #and station distance in document units
            _delta = (_vector.Length - _sta_len) / Units.scale_factor()

            #if the stationing / coordinates are out of tolerance,
            #the error is with the coordinate vector or station
            if not Support.within_tolerance(_delta):
                bearing_angle = Support.get_bearing(_vector)

                #fix station if coordinate vector bearings match
                if Support.within_tolerance(bearing_angle, _geo['BearingIn']):

                    _geo['InternalStation'] = (
                        _prev_geo['InternalStation'][1] \
                        + _vector.Length, _geo['InternalStation'][0]
                        )

                    _geo['StartStation'] = _prev_geo['StartStation'] + \
                                           _prev_geo['Length'] / \
                                           Units.scale_factor() + \
                                           _vector.Length/Units.scale_factor()

                #otherwise, fix the coordinate
                else:
                    _bearing_vector = Support.vector_from_angle(
                        _geo['BearingIn']
                    ).multiply(_sta_len)

                    _geo['Start'] = _prev_geo['End'].add(_bearing_vector)

            _prev_geo = _geo

    def validate_bearings(self):
        """
        Validate the bearings between geometry, ensuring they are equal
        """

        geo_data = self.geometry['geometry']

        if len(geo_data) < 2:
            return True

        if geo_data[0] is None:
            return False

        prev_bearing = geo_data[0]['BearingOut']

        for _geo in geo_data[1:]:

            if not _geo:
                continue

            _b = _geo.get('BearingIn')

            if _b is None:
                self.errors.append(
                    'Invalid bearings ({0:.4f}, {1:.4f}) at curve {2}'\
                        .format(prev_bearing, _b, _geo)
                )
                return False

            if not Support.within_tolerance(_b, prev_bearing):
                self.errors.append(
                    'Bearing mismatch ({0:.4f}, {1:.4f}) at curve {2}'\
                        .format(prev_bearing, _b, _geo)
                )
                return False

            prev_bearing = _geo.get('BearingOut')

        return True

    def validate_stationing(self):
        """
        Iterate the geometry, calculating the internal start station
        based on the actual station and storing it in an
        'InternalStation' parameter tuple for the start
        and end of the curve
        """

        prev_station = self.geometry['meta'].get('StartStation')
        prev_coord = self.geometry['meta'].get('Start')

        if not prev_coord or not prev_station:
            print('Unable to validate alignment stationing')
            return

        for _geo in self.geometry['geometry']:

            if not _geo:
                continue

            _geo['InternalStation'] = None
            geo_station = _geo.get('StartStation')
            geo_coord = _geo['Start']

            #if no station is provided, try to infer it from the start
            #coordinate and the previous station
            if geo_station is None:
                geo_station = prev_station

                if not geo_coord:
                    geo_coord = prev_coord

                delta = geo_coord.sub(prev_coord).Length

                if not Support.within_tolerance(delta):
                    geo_station += delta / Units.scale_factor()

                _geo['StartStation'] = geo_station

            prev_coord = _geo['End']
            prev_station = _geo['StartStation'] \
                + _geo['Length']/Units.scale_factor()

            int_sta = self._get_internal_station(geo_station)

            _geo['InternalStation'] = (int_sta, int_sta + _geo['Length'])

    def _get_internal_station(self, station):
        """
        Using the station equations, determine the internal station
        (position) along the alingment, scaled to the document units
        """
        start_sta = self.Object.Station_Equations[0].y
        eqs = self.Object.Station_Equations

        #default to distance from starting station
        position = 0.0

        for _eq in eqs[1:]:

            #if station falls within equation, quit
            if start_sta < station < _eq.x:
                break

            #increment the position by the equaion length and
            #set the starting station to the next equation
            position += _eq.x - start_sta
            start_sta = _eq.y

        #add final distance to position
        position += station - start_sta

        return position * Units.scale_factor()

    def assign_meta_data(self):
        """
        Extract the meta data for the alignment from the data set
        Check it for errors
        Assign properties
        """

        obj = self.Object

        meta = self.geometry['meta']

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

    def assign_station_data(self):
        """
        Assign the station and intersection equation data
        """

        obj = self.Object

        _eqs = self.geometry['station']
        _meta = self.geometry['meta']

        _eqn_list = []
        _start_sta = Utils.to_float(_meta.get('StartStation'))

        if _start_sta:
            _eqn_list.append(App.Vector(0.0, _start_sta, 0.0))
        else:
            self.errors.append('Unable to convert starting station %s'
                               % _meta.get('StartStation')
                              )

        for _eqn in _eqs:

            eq_vec = None

            #default to increasing station if unspecified
            if not _eqn['Direction']:
                _eqn['Direction'] = 1.0

            try:
                eq_vec = App.Vector(
                    float(_eqn['Back']),
                    float(_eqn['Ahead']),
                    float(_eqn['Direction'])
                    )

            except ValueError:
                self.errors.append(
                    'Unable to convert station equation (%s)' % (_eqn)
                )
                continue

            _eqn_list.append(eq_vec)

        obj.Station_Equations = _eqn_list

    def discretize_geometry(self):
        """
        Discretizes the alignment geometry to a series of vector points
        """

        interval = self.Object.Seg_Value
        interval_type = self.Object.Method
        geometry = self.geometry['geometry']
        points = [[self.geometry['meta']['Start']]]
        last_curve = None

        #discretize each arc in the geometry list,
        #store each point set as a sublist in the main points list
        for curve in geometry:

            if not curve:
                continue

            if curve['Type'] == 'arc':
                points.append(Arc.get_points(curve, interval, interval_type))

            #if curve['Type'] == 'line':
            #    points.append([curve['Start'], curve['End']])

            last_curve = curve

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
            self.geometry['meta']['Length'] - last_curve['InternalStation'][1]
            )

        if not Support.within_tolerance(last_tangent):
            _vec = Support.vector_from_angle(last_curve['BearingOut'])\
                .multiply(last_tangent)

            last_point = result[-1]

            result.append(last_point.add(_vec))

        #print('\n<><><><><>\n', result)
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
                self.Object.Seg_Value = 100.0

            elif _prop == 'Segment':
                self.Object.Seg_Value = 10.0

            elif _prop == 'Tolerance':
                self.Object.Seg_Value = 1.0

    def execute(self, obj):
        """
        Recompute callback
        """
        if hasattr(self, 'no_execute'):
            return

        points = self.discretize_geometry()

        if not points:
            return

        self.Object.Points = self.discretize_geometry()

        super(_HorizontalAlignment, self).execute(obj)
        #self.Object.Placement.Base = self.Object.Placement.Base.add
        #(self.get_intersection_delta())
        #super(_HorizontalAlignment, self).execute(obj)

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
