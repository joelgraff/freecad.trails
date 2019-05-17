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
import copy

import FreeCAD as App

from ..project.support import units
from ..geometry import arc, line, support

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
    def __init__(self, geometry=None):
        """
        Default Constructor
        """
        self.errors = []
        self.data = []

        if geometry:
            self.construct_geometry(geometry)

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

        result = [App.Vector()]
        result += [_v['PI'] for _v in self.data['geometry'] if _v.get('PI')]
        result.append(self.data['meta']['End'])

        return result

    def get_alignment_wires(self):
        """
        Return wire (discrete) representations of the curves which
        comprise the alignment, subdivided by the method and interval parameters.  Returns a dict keyed to each PI internal station
        """

        pass

    def construct_geometry(self, geometry):
        """
        Assign geometry to the alignment object
        """

        self.data = geometry

        for _i, _geo in enumerate(self.data['geometry']):

            if _geo['Type'] == 'Curve':
                _geo = arc.get_parameters(_geo)

            elif _geo['Type'] == 'Line':
                _geo = line.get_parameters(_geo)

            else:
                self.errors.append('Undefined geometry: ' + str(_geo))
                continue

            self.data['geometry'][_i] = _geo

        self.validate_datum()

        self.validate_stationing()

        if not self.validate_bearings():
            return False

        self.validate_coordinates()

        self.validate_alignment()

        #call once more to catch geometry added by validate_alignment()
        self.validate_stationing()

        self.zero_reference_coordinates()

        return True

    def zero_reference_coordinates(self):
        """
        Reference the coordinates to the origin (0,0,0)
        by adjustuing by the datum
        """

        datum = self.get_datum()

        for _geo in self.data['geometry']:

            for _key in ['Start', 'End', 'Center', 'PI']:

                if _geo.get(_key) is None:
                    continue

                _geo[_key] = _geo[_key].sub(datum)

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

            if not support.within_tolerance(_coord.Length, _prev_coord.Length):

                #build the line using the provided parameters and add it
                _geo_list.append(
                    line.get_parameters({'Start': App.Vector(_prev_coord),
                                         'End': App.Vector(_coord),
                                         'BearingIn': _geo['BearingIn'],
                                         'BearingOut': _geo['BearingOut'],
                                         })
                )

            _geo_list.append(_geo)
            _prev_coord = _geo['End']

        _length = 0.0

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

                #calcualte the start based on station delta
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

    def validate_coordinates(self):
        """
        Iterate the geometry, testing for incomplete / incorrect station /
        coordinate values. Fix them where possible, error otherwise
        """

        #calculate distance bewteen curve start and end using
        #internal station and coordinate vectors

        _datum = self.data['meta']
        _geo_data = self.data['geometry']

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

            if not support.within_tolerance(_b, prev_bearing):
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

        return position * units.scale_factor()

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
            return None

        distance = int_sta - curve['InternalStation'][0]

        if curve['Type'] == 'Line':
            return line.get_ortho_vector(curve, distance, side)

        if curve['Type'] == 'Curve':
            return arc.get_ortho_vector(curve, distance, side)

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

        if curve['Type'] == 'Line':
            return line.get_tangent_vector(curve, distance)

        if curve['Type'] == 'Curve':
            return arc.get_tangent_vector(curve, distance)

        return None