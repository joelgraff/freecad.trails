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
Class for managing 2D Horizontal Alignment data
"""

from FreeCAD import Vector

from ..project.support import units
from ..geometry import arc, line, spiral, support
from freecad_python_support.tuple_math import TupleMath

_CLASS_NAME = 'AlignmentModel'
_TYPE = 'AlignmentModel'

__title__ = 'alignment_model.py'
__author__ = 'Joel Graff'
__url__ = "https://www.freecadweb.org"

#Construction order:
#Calc arc parameters
#Sort arcs
#calculate arc start coordinates by internal position and apply to arcs

class AlignmentModel:
    """
    Alignment model for the alignment FeaturePython class
    """
    def __init__(self, geometry=None, zero_reference=False):
        """
        Default Constructor
        """
        self.errors = []
        self.data = []

        if geometry:
            if not self.construct_geometry(geometry, zero_reference):
                print('Errors encountered generating alignment model')

    def get_datum(self):
        """
        Return the alignment datum
        """

        return self.data.get('meta').get('Start')

    def get_pi_coords(self):
        """
        Return the coordinates of the alignment Points of Intersection(PIs)
        as a list of vectors
        """

        result = [Vector()]
        result += [
            _v.get('PI') for _v in self.data.get('geometry') if _v.get('PI')]

        result.append(self.data.get('meta').get('End'))

        return result

    def construct_geometry(self, geometry, zero_reference=True):
        """
        Assign geometry to the alignment object
        """

        self.data = geometry
        _geometry = []

        for _i, _geo in enumerate(self.data.get('geometry')):

            if _geo.get('Type') == 'Curve':
                _geo = arc.get_parameters(_geo)

            #skip serialized lines unless it begins the alignment.
            #In that case, set the tangent's start coordinate as
            #alignment datum before continuing
            elif _geo.get('Type') == 'Line':

                if _i == 0:

                    if not self.data.get('meta').get('Start'):
                        self.data.get('meta')['Start'] = _geo.get('Start')

                    #if only one line is defined, make sure it gets added to
                    #the geometry model
                    if len(self.data.get('geometry')) == 1:
                        _geometry.append(_geo)

                continue

            elif _geo.get('Type') == 'Spiral':
                _geo = spiral.get_parameters(_geo)

            else:
                self.errors.append('Undefined geometry: ' + str(_geo))
                continue

            _geometry.append(_geo)

        self.data['geometry'] = _geometry
        self.validate_datum()
        self.validate_stationing()

        if not self.validate_bearings():
            return False

        self.validate_coordinates(zero_reference)

        if not self.validate_alignment():
            return False

        #call once more to catch geometry added by validate_alignment()
        self.validate_stationing()

        if zero_reference:
            self.zero_reference_coordinates()

        #run discretization to force coordinate transformation updates

        return True

    def zero_reference_coordinates(self):
        """
        Reference the coordinates to the start point
        by adjustuing by the datum
        """

        datum = self.get_datum()

        for _geo in self.data.get('geometry'):

            for _key in ['Start', 'End', 'Center', 'PI']:

                if _geo.get(_key) is None:
                    continue

                _geo[_key] = TupleMath.subtract(_geo[_key], datum)

        if self.data.get('meta').get('End'):
            self.data.get('meta')['End'] = \
                TupleMath.subtract(self.data.get('meta').get('End'), datum)

    def validate_alignment(self):
        """
        Ensure the alignment geometry is continuous.
        Any discontinuities (gaps between end / start coordinates)
        must be filled by a completely defined line
        """

        _prev_sta = 0.0
        _prev_coord = self.data['meta']['Start']
        _geo_list = []

        #iterate through all geometry, looking for coordinate gaps
        #and filling them with line segments.
        for _geo in self.data.get('geometry'):

            if not _geo:
                continue

            _coord = _geo.get('Start')

            _d = abs(TupleMath.length(TupleMath.subtract(
                tuple(_coord), tuple(_prev_coord))))

            #test for gap at start of geometry and end of previous geometry
            if not support.within_tolerance(_d, tolerance=0.01):

                #build the line using the provided parameters and add it
                _geo_list.append(
                    line.get_parameters({
                        'Start': Vector(_prev_coord),
                        'End': Vector(_coord),
                        'StartStation': self.get_alignment_station(_prev_sta),
                        'Bearing': _geo.get('BearingIn'),
                    }).to_dict()
                )

            _geo_list.append(_geo)
            _prev_coord = _geo.get('End')
            _prev_sta = _geo.get('InternalStation')[1]

        _length = 0.0

        #fill in the alignment length.  If the end of the alignment falls short
        #of the calculated length, append a line to complete it.
        if not self.data.get('meta').get('Length'):

            _end = self.data.get('meta').get('End')

            #abort - no overall length or end coordinate specified
            if not _end:
                return False

            _prev = _geo_list[-1]

            if TupleMath.length(
                TupleMath.subtract(_end, _prev.get('End'))) > 0.0:

                _geo_list.append(
                    line.get_parameters({
                        'Start': _prev.get('End'),
                        'End': _end,
                        'StartStation': self.get_alignment_station(
                            _prev['InternalStation'][0]),
                        'Bearing': _prev.get('BearingOut')
                    }).to_dict()
                )

            self.data.get('meta')['Length'] = 0.0

        #accumulate length across individual geometry and test against
        #total alignment length
        for _geo in _geo_list:
            _length += _geo.get('Length')

        align_length = self.data.get('meta').get('Length')

        if not support.within_tolerance(_length, align_length):

            if  _length > align_length:
                self.data.get('meta')['Length'] = align_length

            else:
                _start = _geo_list[-1].get('End')
                bearing = _geo_list[-1].get('BearingOut')

                _end = line.get_coordinate(
                    _start, bearing, align_length - _length
                    )

                _geo_list.append(
                    line.get_parameters({
                        'Start': _start,
                        'End': _end,
                        'StartStation': self.get_alignment_station(
                            _geo['InternalStation'][1]),
                        'BearingOut': bearing
                    }).to_dict()
                )

        self.data['geometry'] = _geo_list

        return True

    def validate_datum(self):
        """
        Ensure the datum is valid, assuming 0+00 / (0,0,0)
        for station and coordinate where none is suplpied and it
        cannot be inferred fromt the starting geometry
        """
        _datum = self.data.get('meta')
        _geo = self.data.get('geometry')[0]

        if not _geo or not _datum:
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

        #----------------------------
        #Parameter Initialization
        #----------------------------
        _geo_station = 0
        _geo_start = Vector()

        if _geo_truth[0]:
            _geo_station = _geo.get('StartStation')

        if _geo_truth[1]:
            _geo_start = _geo.get('Start')

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

        if _datum_truth[0]:

            _datum['Start'] = _geo_start

            #assume geometry start if no geometry station
            if not _geo_truth[0]:
                return

            #scale the distance to the system units
            delta = _geo_station - _datum['StartStation']

            #cutoff if error is below tolerance
            if not support.within_tolerance(delta):
                delta *= units.scale_factor()
            else:
                delta = 0.0

            #assume geometry start if station delta is zero
            if delta:

                #calculate the start based on station delta
                _datum['Start'] =\
                    TupleMath.subtract(_datum.get('Start'),
                    TupleMath.scale(
                        TupleMath.bearing_vector(_geo.get('BearingIn')),
                        delta)
                        #_geo.get('BearingIn')).multiply(delta)
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
            delta = TupleMath.length(
                TupleMath.subtract(_geo_start, _datum.get('Start'))
            ) / units.scale_factor()

            _datum['StartStation'] -= delta

    def validate_coordinates(self, zero_reference):
        """
        Iterate the geometry, testing for incomplete / incorrect station /
        coordinate values. Fix them where possible, error otherwise
        """

        #calculate distance between curve start and end using
        #internal station and coordinate vectors

        _datum = self.data.get('meta')
        _geo_data = self.data.get('geometry')

        _prev_geo = {'End': _datum.get('Start'), 'InternalStation': (0.0, 0.0),
                     'StartStation': _datum.get('StartStation'), 'Length': 0.0
                    }

        if zero_reference:
            _prev_geo['End'] = Vector()

        for _geo in _geo_data:

            if not _geo:
                continue

            #get the vector between the two geometries
            #and the station distance
            _vector = TupleMath.subtract(
                tuple(_geo.get('Start')), tuple(_prev_geo.get('End')))

            _sta_len = abs(
                _geo.get('InternalStation')[0] \
                    - _prev_geo.get('InternalStation')[1]
            )

            #calculate the difference between the vector length
            #and station distance in document units
            _delta = \
                (TupleMath.length(_vector) - _sta_len) / units.scale_factor()

            #if the stationing / coordinates are out of tolerance,
            #the error is with the coordinate vector or station
            if not support.within_tolerance(_delta):
                bearing_angle = TupleMath.bearing(_vector)

                #fix station if coordinate vector bearings match
                if support.within_tolerance(
                        bearing_angle, _geo.get('BearingIn')):


                    _int_sta = (
                        _prev_geo.get('InternalStation')[1] \
                            + TupleMath.length(_vector),
                        _geo.get('InternalStation')[0]
                        )

                    _start_sta = _prev_geo.get('StartStation') + \
                                    _prev_geo.get('Length') / \
                                        units.scale_factor() + \
                                           TupleMath.length(_vector) / \
                                               units.scale_factor()

                    _geo['InternalStation'] = _int_sta
                    _geo['StartStation'] = _start_sta

                #otherwise, fix the coordinate
                else:
                    _bearing_vector = TupleMath.multiply(
                        TupleMath.bearing_vector(_geo.get('BearingIn')),
                        _sta_len)

                    _start_pt = TupleMath.add(tuple(_prev_geo.get('End')),tuple(_bearing_vector))
                    _geo['Start'] = _start_pt

            _prev_geo = _geo

    def validate_bearings(self):
        """
        Validate the bearings between geometry, ensuring they are equal
        """

        geo_data = self.data.get('geometry')

        if len(geo_data) < 2:
            return True

        if geo_data[0] is None:
            self.errors.append('Undefined geometry in bearing validation')
            return False

        prev_bearing = geo_data[0].get('BearingOut')

        for _geo in geo_data[1:]:

            if not _geo:
                continue

            #don't validate bearings on a zero-radius arc
            if _geo.get('Type') == 'Curve' and not _geo.get('Radius'):
                continue

            _b = _geo.get('BearingIn')

            #if bearings are missing or not within tolerance of the
            #previous geometry bearings, reduce to zero-radius arc
            _err = [_b is None, not support.within_tolerance(_b, prev_bearing)]

            _err_msg = '({0:.4f}, {1:.4f}) at curve {2}'\
                .format(prev_bearing, _b, _geo)

            if any(_err):

                if _geo.get('Type') == 'Curve':
                    _geo['Radius'] = 0.0

                if _err[0]:
                    _err_msg = 'Invalid bearings ' + _err_msg
                else:
                    _err_msg = 'Bearing mismatch ' + _err_msg

                self.errors.append(_err_msg)

            prev_bearing = _geo.get('BearingOut')

        return True

    def validate_stationing(self):
        """
        Iterate the geometry, calculating the internal start station
        based on the actual station and storing it in an
        'InternalStation' parameter tuple for the start
        and end of the curve
        """

        prev_station = self.data.get('meta').get('StartStation')
        prev_coord = self.data.get('meta').get('Start')

        if (prev_coord is None) or (prev_station is None):
            return

        for _geo in self.data.get('geometry'):

            if not _geo:
                continue

            _geo['InternalStation'] = None

            geo_station = _geo.get('StartStation')
            geo_coord = _geo.get('Start')

            #if no station is provided, try to infer it from the start
            #coordinate and the previous station
            if geo_station is None:

                geo_station = prev_station

                if not geo_coord:
                    geo_coord = prev_coord

                print(geo_coord, prev_coord)
                delta = TupleMath.length(
                    TupleMath.subtract(tuple(geo_coord), tuple(prev_coord)))

                if not support.within_tolerance(delta):
                    geo_station += delta / units.scale_factor()

                if _geo.get('Type') == 'Line':
                    _geo.start_station = geo_station
                else:
                    _geo['StartStation'] = geo_station

            prev_coord = _geo.get('End')
            prev_station = _geo.get('StartStation') \
                + _geo.get('Length')/units.scale_factor()

            int_sta = self.get_internal_station(geo_station)

            _geo['InternalStation'] = (int_sta, int_sta + _geo.get('Length'))

    def get_internal_station(self, station):
        """
        Using the station equations, determine the internal station
        (position) along the alignment, scaled to the document units
        """
        start_sta = self.data.get('meta').get('StartStation')

        if not start_sta:
            start_sta = 0.0

        eqs = self.data.get('station')

        #default to distance from starting station
        position = 0.0

        for _eq in eqs[1:]:

            #if station falls within equation, quit
            if start_sta < station < _eq['Back']:
                break

            #increment the position by the equaion length and
            #set the starting station to the next equation
            position += _eq['Back'] - start_sta
            start_sta = _eq['Ahead']

        #add final distance to position
        position += station - start_sta

        if support.within_tolerance(position):
            position = 0.0

        return position * units.scale_factor()

    def get_alignment_station(self, internal_station=None, coordinate=None):
        """
        Return the alignment station given an internal station or coordinate
        Coordinate overrides internal station
        """

        if coordinate is not None:
            internal_station = self.get_station_offset(coordinate)[0]

        if internal_station is None:
            return None

        _start_sta = self.data.get('meta').get('StartStation')
        _dist = internal_station

        for _eq in self.data.get('station'):

            #station equation adjustments should be limited to equations
            #on the same alignment
            if _eq['Description'] != _eq['Alignment']:
                continue

            #if the raw station exceeds the end of the first station
            #deduct the length of the first equation
            if _eq['Back'] >= _start_sta + _dist:
                break

            _dist -= _eq['Back'] - _start_sta
            _start_sta = _eq['Ahead']

        #start station represents beginning of enclosing equation
        #and raw station represents distance within equation to point
        return _start_sta + (_dist / units.scale_factor())

    def get_station_offset(self, coordinate):
        """
        Locate the provided coordinate along the alignment, returning
        the internal station or None if not within tolerance.
        """

        _matches = []
        _classes = {'Line': line, 'Curve': arc, 'Spiral': spiral}

        #iterate the geometry, creating a list of potential matches
        for _i, _v in enumerate(self.data.get('geometry')):

            _class = _classes[_v.get('Type')]

            _pos, _dist, _b = _class.get_position_offset(_v, coordinate)

            #if position is before geometry, quit
            if _b < 0:
                break

            #if position is after geometry, skip to next
            if _b > 0:
                continue

            #save result
            _matches.append((_pos, _dist, _i))

        if not _matches:
            return None, None

        #get the distances
        _dists = [_v[1] for _v in _matches]

        #return the closest match
        return _matches[_dists.index(min(_dists))]

    def locate_curve(self, station):
        """
        Retrieve the curve at the specified station
        """

        int_station = self.get_internal_station(station)

        if int_station is None:
            return None

        prev_geo = None

        for _geo in self.data.get('geometry'):

            if _geo.get('InternalStation')[0] > int_station:
                break

            prev_geo = _geo

        return prev_geo

    def get_orthogonal(self, station, side):
        """
        Return the orthogonal vector to a station along the alignment
        """

        curve = self.locate_curve(station)
        int_sta = self.get_internal_station(station)

        if (curve is None) or (int_sta is None):
            print('unable to locate station ', station, 'on curve ', curve)
            return None

        distance = int_sta - curve.get('InternalStation')[0]

        _fn = {
            'Line': line,
            'Curve': arc,
            'Spiral': spiral,
        }

        #return orthogonal for valid curve types
        if curve.get('Type') in _fn:
            return _fn[curve.get('Type')].get_ortho_vector(
                curve, distance, side)

        return None

    def get_tangent(self, station):
        """
        Return the tangent vector to a station along the alignment,
        directed in the direction of the curve
        """

        curve = self.locate_curve(station)
        int_sta = self.get_internal_station(station)

        if (curve is None) or (int_sta is None):
            return None

        distance = int_sta - curve.get('InternalStation')[0]

        _fn = {
            'Line': line,
            'Curve': arc,
            'Spiral': spiral,
        }

        if curve.get('Type') in _fn:
            return _fn[curve.get('Type')].get_tangent_vector(curve, distance)

        return None

    def discretize_geometry(self, interval=None, method='Segment', delta=10.0):
        """
        Discretizes the alignment geometry to a series of vector points
        interval - the starting internal station and length of curve
        method - method of discretization
        delta - discretization interval parameter
        """

        geometry = self.data.get('geometry')

        points = []
        last_curve = None

        #undefined = entire length
        if not interval:
            interval = [0.0, self.data.get('meta').get('Length')]

        #only one element = starting position
        if len(interval) == 1:
            interval.append(self.data.get('meta').get('Length'))

        #discretize each arc in the geometry list,
        #store each point set as a sublist in the main points list
        for curve in geometry:

            if not curve:
                continue

            _sta = curve.get('InternalStation')

            #skip if curve end precedes start of interval
            if _sta[1] < interval[0]:
                continue

            #skip if curve start exceeds end of interval
            if _sta[0] > interval[1]:
                continue

            _start = _sta[0]

            #if curve starts before interval, use start of interval
            if _sta[0] < interval[0]:
                _start = interval[0]

            _end = _sta[1]

            #if curve ends past the interval, stop at end of interval
            if _sta[1] > interval[1]:
                _end = interval[1]

            #calculate start position on arc and length to discretize
            _arc_int = [_start - _sta[0], _end - _start]

            #just in case, skip for zero or negative lengths
            if _arc_int[1] <= 0.0:
                continue

            if curve.get('Type') == 'Curve':

                _pts = arc.get_points(
                    curve, size=delta, method=method, interval=_arc_int
                )

                if _pts:
                    points.append(_pts)

            elif curve.get('Type') == 'Spiral':

                _pts = spiral.get_points(curve, size=delta, method=method)

                if _pts:
                    points.append(_pts)

            else:

                _start_coord = line.get_coordinate(
                    curve.get('Start'), curve.get('BearingIn'), _arc_int[0]
                )

                points.append(
                    [
                        _start_coord,
                        line.get_coordinate(
                            _start_coord, curve.get('BearingIn'), _arc_int[1])
                    ]
                )

            last_curve = curve

        #store the last point of the first geometry for the next iteration
        _prev = points[0][-1]
        result = points[0]

        if not (_prev and result):
            return None

        #iterate the point sets, adding them to the result set
        #and eliminating any duplicate points
        for item in points[1:]:

            _v = item

            #duplicate points are within a hundredth of a foot of each other
            if TupleMath.length(
                TupleMath.subtract(tuple(_prev), tuple(item[0]))) < 0.01:

                _v = item[1:]

            result.extend(_v)
            _prev = item[-1]

        #add a line segment for the last tangent if it exists
        last_tangent = abs(
            self.data.get('meta').get('Length') \
                - last_curve.get('InternalStation')[1]
        )

        if not support.within_tolerance(last_tangent):
            _vec = TupleMath.bearing_vector(
                last_curve.get('BearingOut') * last_tangent)

#            _vec = support.vector_from_angle(last_curve.get('BearingOut'))\
#                .multiply(last_tangent)

            last_point = tuple(result[-1])

            result.append(TupleMath.add(last_point, _vec))

        #set the end point
        if not self.data.get('meta').get('End'):
            self.data.get('meta')['End'] = result[-1]

        return result
