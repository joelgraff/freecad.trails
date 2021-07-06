from FreeCAD import Vector

from freecad_python_support.tuple_math import TupleMath
from ..project.support import units
from ..geometry import arc, spiral, line, support

def geometry(geometry):
    """
    Validate the individual geometric elements in a list of geometry
    """

    print('validate.geometry=', geometry)
    _geo = []

    for _g in geometry:

        if _g['Type'] == 'Curve':
            _geo.append(arc.get_parameters(_g))

        elif _g['Type'] == 'Spiral':
            _geo.append(spiral.get_parameters(_g))

        else:
            print (f'Undefined geometry:\n\t{str(_g)}')

    return _geo

         
def bearings(geometry):
    """
    Validate the bearings between geometry, ensuring they are equal
    """

    if len(geometry) < 2:
        return True

    if geometry[0] is None:
        print('Undefined geometry in bearing validation')
        return False

    prev_bearing = geometry[0]['BearingOut']

    for _geo in geometry[1:]:

        if not _geo:
            continue

        #don't validate bearings on a zero-radius arc
        if _geo['Type'] == 'Curve' and not _geo['Radius']:
            continue

        _b = _geo['BearingIn']

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

            print (_err_msg)

        prev_bearing = _geo['BearingOut']

    return True

def internal_station(geometry):
    """
    Ensure consistent internal stationing across the elements
    """

    _last_sta = 0.0

    for _geo in geometry:

        _next_sta = _last_sta + _geo['Length']
        _geo['InternalStation'] = (_last_sta, _next_sta)
        _last_Sta = _next_sta

def coordinates(meta, geometry):
    """
    Ensure coordinates are valid
    """

    #get the metadata starting position
    _start = meta['Start']

    #iterate the geometry
    for _geo in geometry:

        #get the geometry starting and ending coordinates
        _coord = (geometry['Start'], geometry['End'])

        #if the metadata starting position doesn't match the geometry start,
        #calc the delta, and update the geoemtry coordinates
        if _start != _coord[0]:
            _delta = TupleMath.subtract(_start, _coord[0])
            geometry['Start'] = _start
            geometry['End'] = TupleMath.add(_coord[1], _delta)

        #preseve the end of this geometry for the next iteration
        _start = _geo['End']

def stationing(meta, geometry):
    """
    Apply stationing with appropriate equations across geometry
    """

    _eqs = meta['station']

    for _eq in _eqs:

        #if the raw station exceeds the end of the first station
        #deduct the length of the first equation
        if _eq['Back'] >= _start_sta + _dist:
            break

        _dist -= _eq['Back'] - _start_sta
        _start_sta = _eq['Ahead']

    #start station represents beginning of enclosing equation
    #and raw station represents distance within equation to point
    return _start_sta + (_dist / units.scale_factor())

def _coordinates(meta, geometry, zero_reference):
    """
    Iterate the geometry, testing for incomplete / incorrect station /
    coordinate values. Fix them where possible, error otherwise
    """

    #calculate distance between curve start and end using
    #internal station and coordinate vectors

    _prev_geo = {
        'End': meta['Start'], 'InternalStation': (0.0, 0.0),
        'StartStation': meta['StartStation'], 'Length': 0.0
    }

    if zero_reference or not _prev_geo['End']:
        _prev_geo['End'] = Vector()

    for _geo in geometry:

        if not _geo:
            continue

        print ('\n\t_geo=',_geo,'\n\t_prev_geo=', _prev_geo)

        #get the vector between the two geometries
        #and the station distance
        _vector = \
            TupleMath.subtract(tuple(_geo['Start']), tuple(_prev_geo['End']))

        _vals = [_geo['InternalStation'], _prev_geo['InternalStation']]
        
        if not _geo['InternalStation']:
            _geo['InternalStation'] = (0,0)

        if not _prev_geo['InternalStation']:
            _prev_geo['InternalStation'] = (0,0)
            
        _sta_len = abs(_geo['InternalStation'][0] \
            - _prev_geo['InternalStation'][1])

        #calculate the difference between the vector length
        #and station distance in document units
        _delta = \
            (TupleMath.length(_vector) - _sta_len) / units.scale_factor()

        #if the stationing / coordinates are out of tolerance,
        #the error is with the coordinate vector or station
        if not support.within_tolerance(_delta):
            _angle = TupleMath.bearing(_vector)

            #fix station if coordinate vector bearings match
            if support.within_tolerance(_angle, _geo['BearingIn']):

                _int_sta = (
                    _prev_geo['InternalStation'][1] + TupleMath.length(_vector),
                    _geo['InternalStation'][0]
                )

                _start_sta = _prev_geo['StartStation'] + _prev_geo['Length'] / \
                                units.scale_factor() + \
                                    TupleMath.length(_vector) / \
                                        units.scale_factor()

                _geo['InternalStation'] = _int_sta
                _geo['StartStation'] = _start_sta

            #otherwise, fix the coordinate
            else:
                _vector = TupleMath.multiply(
                    TupleMath.bearing_vector(_geo['BearingIn']), _sta_len)

                _start_pt =\
                     TupleMath.add(tuple(_prev_geo['End']),tuple(_vector))

                _geo['Start'] = _start_pt

        _prev_geo = _geo

def datum(meta, geometry):
    """
    Validate the datum in the metadata against the passed geometric element
    """

    #both datum station and coordinate defined - quit
    if all((meta['Start'], meta['StartStation'])):
        return

    #neither datum station nor coordinate defined - assign geo values
    if not any ((meta['Start'], meta['StartStation'])):
        meta['Start'] = geometry['Start']
        meta['StartStation'] = geometry['StartStation']
        
        if not any ((meta['Start'], meta['StartStation'])):
            return

        #run datum on the changed metadata to ensure it is complete
        datum(meta, geometry)
        return

    #no start coordinate?
    #Use geo coordinate and station delta to project
    if not meta['Start']:
    
        meta['Start'] = geometry['Start']

        #invalid definition.  Abort.
        if not meta['Start']:
            meta['Start'] = (0.0, 0.0, 0.0)
            return

        _delta = geometry['StartStation'] - meta['StartStation']

        #if zero delta, quit
        if support.within_tolerance(_delta):
            return

        meta['Start'] =\
            TupleMath.subtract(meta['Start'],
                TupleMath.scale(
                    TupleMath.bearing_vector(geometry['BearingIn']),
                    _delta * units.scale_factor()
                )
            )

        return

    #no start station?  project from coordinates
    meta['StartStation'] = geometry['StartStation']

    if meta['StartStation']:

        _delta = TupleMath.length(
            TupleMath.subtract(geometry['Start'], meta['Start'])
        ) / units.scale_factor()

        meta['StartStation'] = _delta

def alignment(meta, geometry):
    """
    Ensure the alignment geometry is continuous.
    Any discontinuities (gaps between end / start coordinates)
    must be filled by a completely defined line
    """

    _prev_sta = 0.0
    _prev_coord = meta['Start']
    _geo_list = []

    #iterate through all geometry, looking for coordinate gaps
    #and filling them with line segments.
    for _geo in geometry:

        if not _geo:
            continue

        _coord = _geo['Start']

        print(_coord, _prev_coord)

        _d = TupleMath.subtract(tuple(_coord), tuple(_prev_coord))
        _d = abs(TupleMath.length(_d))

        #test for gap at start of geometry and end of previous geometry
        if not support.within_tolerance(_d, tolerance=0.01):

            #build the line using the provided parameters and add it
            _geo_list.append(
                line.get_parameters({
                    'Start': Vector(_prev_coord),
                    'End': Vector(_coord),
                    'StartStation': get_alignment_station(_prev_sta),
                    'Bearing': _geo['BearingIn'],
                }).to_dict()
            )

        _geo_list.append(_geo)
        _prev_coord = _geo['End']
        _prev_sta = _geo['InternalStation'][1]

    _length = 0.0

    #fill in the alignment length.  If the end of the alignment falls short
    #of the calculated length, append a line to complete it.
    if not meta['Length']:

        _end = meta['End']

        #abort - no overall length or end coordinate specified
        if not _end:
            return False

        _prev = _geo_list[-1]

        if TupleMath.length(
            TupleMath.subtract(_end, _prev['End'])) > 0.0:

            _geo_list.append(
                line.get_parameters({
                    'Start': _prev['End'],
                    'End': _end,
                    'StartStation': get_alignment_station(
                        _prev['InternalStation'][0]),
                    'Bearing': _prev['BearingOut']
                }).to_dict()
            )

        meta['Length'] = 0.0

    #accumulate length across individual geometry and test against
    #total alignment length
    for _geo in _geo_list:
        _length += _geo['Length']

    align_length = meta['Length']

    if not support.within_tolerance(_length, align_length):

        if  _length > align_length:
            meta['Length'] = align_length

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
                    'StartStation': get_alignment_station(
                        _geo['InternalStation'][1]),
                    'BearingOut': bearing
                }).to_dict()
            )

    geometry = _geo_list

    return True