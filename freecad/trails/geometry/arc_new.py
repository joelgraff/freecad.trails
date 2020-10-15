import math

from types import SimpleNamespace

from freecad_python_support.tuple_math import TupleMath

class ArcLambdas(Const):
    """
    Arc lambdas
    """
    delta = [],
    radius = [],
    tangent = lambda r,d: r * math.tan(d / 2.0),
    external = lambda r,d: r * (1/(math.cos(d/2.0))-1),
    middle = lambda r,d: r * (1-math.cos(d/2.0)),
    length = lambda r,d: r * d * math.pi / 180.0,
    chord = lambda r,d: 2 * r * math.sin(d/2.0),
    start = [],
    end = [],
    center = [],
    pi = [],
    bearings = []

def get_parameters(source_arc):
    """
    Given a partially-defined source arc, return a completely defined arc
    """

    _points = (
        source_arc.start, source_arc.end, source_arc.pi, source_arc.center)

    #no points defined - abort
    _arc_fail('No points defined', source_arc)

    _pt_count = sum((1 if _v else 0 for _v in _points))

    #need at least one angle, one length and one point
    if (_pt_count == 1):

        if not (source_arc.bearing_in or source_arc.bearing_out\
            or source_arc.delta):

            _arc_fail('No angles defined.', source_arc)

        if not (source_arc.radius and source_arc.delta):

            print('Insufficient definition for arc:\n\t{}'\
                .format(str(source_arc)))

            return None



    assert source_arc.radius or source_arc.delta

    _truth = (1 if _v else 0 for _v in _points)

    #missing radius and/or delta and have only one point - abort
    if not sum() == 3:
        return None



    #still here - we have three points and either a radius or a delta

def get_bearings(pc, pt, pi, ctr, terminate_early = False):
    """
    Return the bearings of the vectors associated with the points
    """

    _fv = lambda x, y: TupleMath.subtract(x, y) if x and y else None

    _vecs = [
        _fv(pi, pc),
        _fv(pt, pi),
        _fv(pc, ctr),
        _fv(pt, ctr),
        _fv(pi, ctr),
        _fv(pt, pc)
    ]

    _fa = lambda x, y: TupleMath.angle_between(x, y) if x and y else 0.0

    _ang = [
        _fa(_vecs[0], _vecs[1]),
        _fa(_vecs[2], _vecs[3]),
        _fa(_vecs[4], _vecs[3]) * 2,
        _fa(_vecs[4], _vecs[2]) * 2,
        _fa(_vecs[5], _vecs)
    ]
    _pts = []

    _fvec = lambda x, y: TupleMath.subtract(x, y) if x and y else None

    _vecs = [
        _fvec(pi, pc), _fvec(pt, pi),
        _fvec(pc, ctr), _fvec(pt, ctr),
        _fvec(pi, ctr)
    ]

    _fang = lambda x, y: TupleMath.angle_between(x, y) if x and y else None

    _deltas = [
        _fang(_vecs[0], _vecs[1]),
        _fang(_vecs[2], _vecs[3]),
        _fang(_vecs[4], _vecs[3]),
        _fang(_vecs[4], _vecs[2])
    ]

def _arc_fail(message, arc):
    """
    Assert fail subroutine
    """

    assert(False), '\nArc: {}\n\t{}'.format(message, str(arc))
