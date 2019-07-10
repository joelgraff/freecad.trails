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
    def __init__(self, geometry=None, zero_reference=True):
        """
        Default Constructor
        """
        self.errors = []
        self.data = []

        if geometry:
            if not self.construct_geometry(geometry, zero_reference):
                print('Errors encounterd generating alignment model')

    def get_datum(self):
        """
        Return the alignment datum
        """

        return self.data['meta']['Start']

    def get_pi_coords(self):
        """
        Return the coordinates of the alignment Points of Intersection(PIs)
        as a list of vectors
        """

        result = [Vector()]
        result += [_v['PI'] for _v in self.data['geometry'] if _v.get('PI')]

        result.append(self.data['meta']['End'])

        return result

    def construct_geometry(self, geometry, zero_reference=True):
        """
        Assign geometry to the alignment object
        """

        self.data = geometry
        _geometry = []

        for _i, _geo in enumerate(self.data['geometry']):

            if _geo['Type'] == 'Curve':
                _geo = arc.get_parameters(_geo)

            #skip serialized lines unless it begins the alignment.
            #In that case, set the tangent's start coordiante as
            #alignment datum before continuing
            elif _geo['Type'] == 'Line':

                if _i == 0:

                    if not self.data['meta']['Start']:
                        self.data['meta']['Start'] = _geo['Start']

                continue

            elif _geo['Type'] == 'Spiral':
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
        #self.discretize_geometry()

        return True

    def zero_reference_coordinates(self):
        """
        Reference the coordinates to the start point
        by adjustuing by the datum
        """

        datum = self.get_datum()

        for _geo in self.data['geometry']:

            for _key in ['Start', 'End', 'Center', 'PI']:

                if _geo.get(_key) is None:
                    continue

                _geo[_key] = _geo[_key].sub(datum)

        if self.data['meta'].get('End'):
            self.data['meta']['End'] = self.data['meta']['End'].sub(datum)

    def validate_alignment(self):
        """
        Ensure the alignment geometry is continuous.
        Any discontinuities (gaps between end / start coordinates)
        must be filled by a completely defined line
        """

        _prev_coord = self.get_datum()
        _geo_list = []

        for _geo in self.data['geometry']:

            if not _geo:
                continue

            _coord = _geo['Start']
            _d = abs(_coord.Length - _prev_coord.Length)

            if not support.within_tolerance(_d, tolerance=0.01):

                #build the line using the provided parameters and add it
                _geo_list.append(
                    line.get_parameters({
                        'Start': Vector(_prev_coord),
                        'End': Vector(_coord),
                        'BearingIn': _geo['BearingIn'],
                        'BearingOut': _geo['BearingOut'],
                    })
                )

            _geo_list.append(_geo)
            _prev_coord = _geo['End']

        _length = 0.0

        if not self.data['meta'].get('Length'):

            _end = self.data['meta']['End']

            if not _end:
                return False

            _prev = _geo_list[-1]

            if _prev['End'].distanceToPoint(_end) > 0.0:

                _geo_list.append(
                    line.get_parameters({
                        'Start': _prev['End'],
                        'End': _end,
                        'BearingIn': _prev['BearingOut'],
                        'BearingOut': _prev['BearingOut']
                    })
                )

            self.data['meta']['Length'] = 0.0

        for _geo in _geo_list:
            _length += _geo['Length']

        align_length = self.data['meta']['Length']

        if not support.within_tolerance(_length, align_length):

            if  _length > align_length:
                self.data['meta']['Length'] = align_length

            else:
                _start = _geo_list[-1]['End']
                bearing = _geo_list[-1]['BearingOut']

                _end = line.get_coordinate(
                    _start, bearing, align_length - _length
                    )

                _geo_list.append(
                    line.get_parameters({
                        'Start': _start,
                        'End': _end,
                        'BearingIn': bearing,
                        'BearingOut': bearing
                    })
                )

        self.data['geometry'] = _geo_list

        return True

    def validate_datum(self):
        """
        Ensure the datum is valid, assuming 0+00 / (0,0,0)
        for station and coordinate where none is suplpied and it
        cannot be inferred fromt the starting geometry
        """
        _datum = self.data['meta']
        _geo = self.data['geometry'][0]

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

        #----------------------------
        #Parameter Initialization
        #----------------------------
        _geo_station = 0
        _geo_start = Vector()

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
                _datum['Start'] = _datum['Start'].sub(
                    support.vector_from_angle(
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
            delta = _geo_start.sub(_datum['Start']).Length/units.scale_factor()

            _datum['StartStation'] -= delta

    def validate_coordinates(self, zero_reference):
        """
        Iterate the geometry, testing for incomplete / incorrect station /
        coordinate values. Fix them where possible, error otherwise
        """

        #calculate distance between curve start and end using
        #internal station and coordinate vectors

        _datum = self.data['meta']
        _geo_data = self.data['geometry']

        _prev_geo = {'End': _datum['Start'], 'InternalStation': (0.0, 0.0),
                     'StartStation': _datum['StartStation'], 'Length': 0.0
                    }

        if not zero_reference:
            _prev_geo['End'] = Vector()

        for _geo in _geo_data:

            if not _geo:
                continue

            #get the vector between the two geometries
            #and the station distance
            _vector = _geo['Start'].sub(_prev_geo['End'])
            _sta_len = abs(
                _geo['InternalStation'][0] - _prev_geo['InternalStation'][1]
            )

            #calculate the difference between the vector length
            #and station distance in document units
            _delta = (_vector.Length - _sta_len) / units.scale_factor()

            #if the stationing / coordinates are out of tolerance,
            #the error is with the coordinate vector or station
            if not support.within_tolerance(_delta):
                bearing_angle = support.get_bearing(_vector)

                #fix station if coordinate vector bearings match
                if support.within_tolerance(bearing_angle, _geo['BearingIn']):

                    _geo['InternalStation'] = (
                        _prev_geo['InternalStation'][1] \
                        + _vector.Length, _geo['InternalStation'][0]
                        )

                    _geo['StartStation'] = _prev_geo['StartStation'] + \
                                           _prev_geo['Length'] / \
                                           units.scale_factor() + \
                                           _vector.Length/units.scale_factor()

                #otherwise, fix the coordinate
                else:
                    _bearing_vector = support.vector_from_angle(
                        _geo['BearingIn']
                    ).multiply(_sta_len)

                    _geo['Start'] = _prev_geo['End'].add(_bearing_vector)

            _prev_geo = _geo

    def validate_bearings(self):
        """
        Validate the bearings between geometry, ensuring they are equal
        """

        geo_data = self.data['geometry']

        if len(geo_data) < 2:
            return True

        if geo_data[0] is None:
            self.errors.append('Undefined geometry in bearing validation')
            return False

        prev_bearing = geo_data[0]['BearingOut']

        for _geo in geo_data[1:]:

            if not _geo:
                continue

            #don't validate bearings on a zero-radius arc
            if _geo['Type'] == 'Curve' and not _geo['Radius']:
                continue

            _b = _geo.get('BearingIn')

            #if bearings are missing or not within tolerance of the
            #previous geometry bearings, reduce to zero-radius arc
            _err = [_b is None, not support.within_tolerance(_b, prev_bearing)]

            _err_msg = '({0:.4f}, {1:.4f}) at curve {2}'\
                .format(prev_bearing, _b, _geo)

            if any(_err):

                if _geo['Type'] == 'Curve':
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

        prev_station = self.data['meta'].get('StartStation')
        prev_coord = self.data['meta'].get('Start')

        if (prev_coord is None) or (prev_station is None):
            print('Unable to validate alignment stationing')
            return

        for _geo in self.data['geometry']:

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

                if not support.within_tolerance(delta):
                    geo_station += delta / units.scale_factor()

                _geo['StartStation'] = geo_station

            prev_coord = _geo['End']
            prev_station = _geo['StartStation'] \
                + _geo['Length']/units.scale_factor()

            int_sta = self.get_internal_station(geo_station)

            _geo['InternalStation'] = (int_sta, int_sta + _geo['Length'])

    def get_internal_station(self, station):
        """
        Using the station equations, determine the internal station
        (position) along the alignment, scaled to the document units
        """
        start_sta = self.data['meta'].get('StartStation')

        if not start_sta:
            start_sta = 0.0

        eqs = self.data['station']

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

        if support.within_tolerance(position):
            position = 0.0

        return position * units.scale_factor()

    def get_station_offset(self, coordinate):
        """
        Locate the provided coordinate along the alignment, returning
        the internal station or None if not within tolerance.
        """

        _matches = []
        _classes = {'Line': line, 'Curve': arc, 'Spiral': spiral}

        #iterate the geometry, creating a list of potential matches
        for _i, _v in enumerate(self.data['geometry']):

            _class = _classes[_v['Type']]

            _p, _d, _b = _class.get_position_offset(_v, coordinate)

            if _b < 0:
                break

            if _b > 0:
                continue

            _matches.append((_p, _d, _i))

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

        for _geo in self.data['geometry']:

            if _geo['InternalStation'][0] > int_station:
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

        distance = int_sta - curve['InternalStation'][0]

        _fn = {
            'Line': line,
            'Curve': arc,
            'Spiral': spiral,
        }

        if curve['Type'] in _fn:
            return _fn[curve['Type']].get_ortho_vector(curve, distance, side)

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

        distance = int_sta - curve['InternalStation'][0]

        _fn = {
            'Line': line,
            'Curve': arc,
            'Spiral': spiral,
        }

        if curve['Type'] in _fn:
            return _fn[curve['Type']].get_tangent_vector(curve, distance)

        return None

    def discretize_geometry(self, interval=None, method='Segment', delta=10.0):
        """
        Discretizes the alignment geometry to a series of vector points
        interval - the starting internal station and length of curve
        method - method of discretization
        delta - discretization interval parameter
        """

        geometry = self.data['geometry']
        points = []
        last_curve = None

        #undefined = entire length
        if not interval:
            interval = [0.0, self.data['meta']['Length']]

        #only one element = starting position
        if len(interval) == 1:
            interval.append(self.data['meta']['Length'])

        #discretize each arc in the geometry list,
        #store each point set as a sublist in the main points list
        for curve in geometry:

            if not curve:
                continue

            _sta = curve['InternalStation']

            #skip if curve end precedes start of interval
            if _sta[1] < interval[0]:
                continue

            #skip if curve start exceeds end of interval
            if _sta[0] > interval[1]:
                continue

            _start = _sta[0]

            #if curve starts bfore interval, use start of interval
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

            if curve['Type'] == 'Curve':

                _pts, _hsh = arc.get_points(
                    curve, size=delta, method=method, interval=_arc_int
                )

                if _pts:
                    points.append(_pts)

            elif curve['Type'] == 'Spiral':
                _pts = spiral.get_points(curve, size=delta, method=method)

                if _pts:
                    points.append(_pts)
            else:
                _start_coord = line.get_coordinate(
                    curve['Start'], curve['BearingIn'], _arc_int[0]
                )

                points.append(
                    [
                        _start_coord,
                        line.get_coordinate(
                            _start_coord, curve['BearingIn'], _arc_int[1])
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
            if _prev.sub(item[0]).Length < 0.01:
                _v = item[1:]

            result.extend(_v)
            _prev = item[-1]

        #add a line segment for the last tangent if it exists
        last_tangent = abs(
            self.data['meta']['Length'] - last_curve['InternalStation'][1]
        )

        if not support.within_tolerance(last_tangent):
            _vec = support.vector_from_angle(last_curve['BearingOut'])\
                .multiply(last_tangent)

            last_point = result[-1]

            result.append(last_point.add(_vec))

        #set the end point
        if not self.data['meta'].get('End'):
            self.data['meta']['End'] = result[-1]

        return result
