from types import SimpleNamespace

from FreeCAD import Vector

from . import alignment_validator as validate
from ..geometry import arc, line, spiral, support
from ..project.support import units
from freecad_python_support.tuple_math import TupleMath

class AlignmentModel:

    def __init__(self, geometry, zero_reference):
        """
        Constructor
        """

        self.data = []
        self.errors = []
        self.set_geometry(geometry, zero_reference)

    def validate_geometry(self, geometry, datum=False, zero_ref=False):
        """
        Validate a list of geometric elements
        geometry - a list of geometric elements
        datum - boolean, True - update datum in metadata
        """

        _meta = geometry['meta']
        _geo = geometry['geometry']

        print('\n\tvalidate geometry 1\n', _geo)

        _geo = validate.geometry(_geo)

        print('\n\tvalidate geometry 2\n', _geo)
        #if datum:
        #    validate.datum(_meta, _geo[0])

        if not validate.bearings(_geo):
            return False

        validate.stationing(_meta, _geo)
        
        self.update_internal_station(geometry)

        print('\n\tvalidate geometry 4\n', _geo)



        validate.coordinates(_meta, _geo, zero_ref)

        print(_meta)
        if not validate.alignment(_meta, _geo):
            return False

        validate.stationing(_meta, _geo)

        self.update_internal_station(geometry)

        if zero_ref:
            self.zero_reference_coordinates()

        return True

    def set_geometry(self, geometry, zero_reference):
        """
        Set the data model to an existing dictionary of geometry
        """

        #validate the individual geometry
        if not self.validate_geometry(
            geometry, datum=True, zero_ref=zero_reference):

            print("Unable to validate alignment geometry")
            return

        self.data = geometry

    def add_geometry(self, geometry, zero_reference):
        """
        Add geometry to the alignment object in a supplied dict
        """

        if not self.data:
            self.data = geometry

        _geo = None

        for _k, _g in enumerate(geometry['geometry']):
            
            _g = self.validate((_g,))[0]

            if not _geo:
                self.errors.append(f'Invalid geometry:\n{str(geometry)}')

            else:
                self.data['geometry'].append(_geo)

    def update_internal_station(self, geometry):
        """
        Update the internal stationing on the geometry
        """

        for _geo in geometry['geometry']:

            _geo_sta = _geo['StartStation']
            _int_sta = self.get_internal_station(_geo_sta, geometry)

            _geo['InternalStation'] = (_int_sta, _int_sta + _geo['Length'])

    def get_internal_station(self, station, geometry=None):
        """
        Using the station equations, determine the internal station
        (position) along the alignment, scaled to the document units
        """

        if not geometry:
            geometry = self.data

        print ('\n\t=--=-=-=-=',geometry)

        start_sta = geometry.get('meta').get('StartStation')

        if not start_sta:
            start_sta = 0.0

        eqs = geometry.get('station')

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

    def validate_stationing(meta, geometry):
        """
        Iterate the geometry list, calculating the internal start station
        based on the actual station and storing it in an
        'InternalStation' parameter tuple for the start
        and end of the curve
        """

        prev_station = meta['StartStation']
        prev_coord = meta['Start']

        if (prev_coord is None) or (prev_station is None):
            return

        for _geo in geometry:

            if not _geo:
                continue

            _geo['InternalStation'] = None

            geo_station = _geo['StartStation']
            geo_coord = _geo['Start']

            #if no station is provided, try to infer it from the start
            #coordinate and the previous station
            if geo_station is None:

                geo_station = prev_station

                if geo_coord is None:
                    geo_coord = prev_coord

                delta = TupleMath.length(
                    TupleMath.subtract(tuple(geo_coord), tuple(prev_coord)))

                if not support.within_tolerance(delta):
                    geo_station += delta / units.scale_factor()

                if _geo.get('Type') == 'Line':
                    _geo.start_station = geo_station
                else:
                    _geo['StartStation'] = geo_station

            prev_coord = _geo['End']
            prev_station = _geo['StartStation'] \
                + _geo['Length'] / units.scale_factor()

    def _validate_stationing(self):
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

    def _validate_bearings(self):
        """
        Validate the bearings between geometric elements, ensuring they match
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

    def _validate_coordinates(self, zero_reference):
            """
            Iterate the geometry, testing for incomplete / incorrect station /
            coordinate values. Fix them where possible, error otherwise
            """

            #calculate distance between curve start and end using
            #internal station and coordinate vectors

            _datum = self.data.get('meta')
            _geo_data = self.data.get('geometry')

            print ('VALIDATE COORDINATE GEOMETRY\n', self.data)

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

    def _validate_alignment(self):
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

    def _zero_reference_coordinates(self):
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
