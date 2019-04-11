import FreeCAD as App
import math

def discretize_spiral(start_coord, bearing, radius, angle, length, interval, interval_type):
    """
    Discretizes a spiral curve using the length parameter.  
    """

    #generate inbound spiral
    #generate circular arc
    #generate outbound spiral

    points = []

    length_mm = length * 304.80
    radius_mm = radius * 304.80

    bearing_in = App.Vector(math.sin(bearing), math.cos(bearing))

    curve_dir = 1.0

    if angle < 0.0:
        curve_dir = -1.0
        angle = abs(angle)

    _Xc = ((length_mm**2) / (6.0 * radius_mm))
    _Yc = (length_mm - ((length_mm**3) / (40 * radius_mm**2)))

    _dY = App.Vector(bearing_in).multiply(_Yc)
    _dX = App.Vector(bearing_in.y, -bearing_in.x, 0.0).multiply(curve_dir).multiply(_Xc)

    theta_spiral = length_mm/(2 * radius_mm)
    arc_start = start_coord.add(_dX.add(_dY))
    arc_coords = [arc_start]
    #arc_coords.extend(_HorizontalAlignment.discretize_arc(arc_start, bearing + (theta_spiral * curve_dir), radius, curve_dir * (angle - (2 * theta_spiral)), interval, interval_type))

    if len(arc_coords) < 2:
        print('Invalid central arc defined for spiral')
        return None

    segment_length = arc_coords[0].distanceToPoint(arc_coords[1])
    segments = int(length_mm / segment_length) + 1

    for _i in range(0, segments):

        _len = float(_i) * segment_length

        _x = (_len ** 3) / (6.0 * radius_mm * length_mm)
        _y = _len - ((_len**5) / (40 * (radius_mm ** 2) * (length_mm**2)))

        _dY = App.Vector(bearing_in).multiply(_y)
        _dX = App.Vector(bearing_in.y, -bearing_in.x, 0.0).multiply(curve_dir).multiply(_x)

        points.append(start_coord.add(_dY.add(_dX)))

    points.extend(arc_coords)

    exit_bearing = bearing + (angle * curve_dir)
    bearing_out = App.Vector(math.sin(exit_bearing), math.cos(exit_bearing), 0.0)

    _dY = App.Vector(bearing_out).multiply(_Yc)
    _dX = App.Vector(-bearing_out.y, bearing_out.x, 0.0).multiply(curve_dir).multiply(_Xc)

    end_coord = points[-1].add(_dY.add(_dX))

    temp = [end_coord]

    for _i in range(1, segments):

        _len = float(_i) * segment_length

        if _len > length_mm:
            _len = length_mm

        _x = (_len ** 3) / (6.0 * radius_mm * length_mm)
        _y = _len - ((_len ** 5) / (40 * (radius_mm ** 2) * (length_mm**2)))

        _dY = App.Vector(-bearing_out).multiply(_y)
        _dX = App.Vector(bearing_out.y, -bearing_out.x, 0.0).multiply(curve_dir).multiply(_x)

        temp.append(end_coord.add(_dY.add(_dX)))

    points.extend(temp[::-1])

    return points