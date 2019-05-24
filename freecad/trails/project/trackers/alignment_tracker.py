# -*- coding: utf-8 -*-
#**************************************************************************
#*                                                                     *
#* Copyright (c) 2019 Joel Graff <monograff76@gmail.com>               *
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
Tracker for alignment drafting
"""

from pivy import coin

from FreeCAD import Vector

from ...geometry import support, arc
from .base_tracker import BaseTracker

class AlignmentTracker(BaseTracker):
    """
    Tracker class for alignment design
    """

    def __init__(self, doc, view, object_name, model):
        """
        Constructor
        """

        self.model = model
        self.pi_list = []
        self.curve_list = []
        self.start_pi = -1
        self.coord_group = coin.SoGroup()
        self.coord3 = coin.SoCoordinate3()
        self.start_path = None
        self.drag_start = Vector()

        self.viewport = \
            view.getViewer().getSoRenderManager().getViewportRegion()

        _names = [doc.Name, object_name, 'ALIGNMENT_TRACKER']
        super().__init__(names=_names, select=False, group=True)

    def get_selection_group(self, pi_coords):
        """
        Return a node of coordinates and lines which represents the
        discretized alignment from the end of the curve at the specified
        PI coordinate to the end of the alignment
        pi-coords = SoCoordinate3 of selected PI's
        """

        if len(pi_coords.point.getValues()) < 2:
            return coin.SoGroup()

        pi_coord = pi_coords.point.getValues()[0]

        _start_sta = 0.0

        for _curve in self.model.data['geometry']:

            _pi = _curve.get('PI')

            if not _pi:
                continue

            if support.within_tolerance(_pi, pi_coord, 0.1):
                _start_sta = _curve['InternalStation'][1]

        _geo = self.model.discretize_geometry([_start_sta])

        _group = coin.SoGroup()
        _group.setName('ALIGNMENT_TRACKER')

        _coord = coin.SoCoordinate3()
        _coord.point.setValues(0, len(_geo), [list(_v) for _v in _geo])

        _line = coin.SoLineSet()

        _group.addChild(_coord)
        _group.addChild(_line)

        return _group

    def get_connection_group(self, selected):
        """
        Build the connection group based on passed selected PI's
        """

        #abort for empty selection
        if not selected:
            return coin.SoGroup()

        _pi_list = self.model.get_pi_coords()
        _sel = -1

        sel_vec = Vector(selected.point.getValues()[0].getValue())

        #find selected pi index
        for _i, _pi in enumerate(_pi_list):

            if support.within_tolerance(_pi, sel_vec, 0.1):
                _sel = _i
                break

        #abort if not found
        if _sel == -1:
            return coin.SoGroup()

        sel_len = len(selected.point.getValues())

        #get list of PI's
        #first PI is the second PI preceding the selected one
        #last PI is the seoncd PI following the selected,
        #unless multiple PI's are selected, then only one
        pi_range = [_sel-2, _sel + int(sel_len == 1) +  2]

        if pi_range[0] < 0:
            pi_range[0] = 0

        if pi_range[1] > len(_pi_list):
            pi_range[1] = len(_pi_list)

        self.pi_list = [_v for _v in _pi_list[pi_range[0]: pi_range[1]]]

        #get the index of the first selected PI w.r.t. the reduced list
        for _i, _v in enumerate(self.pi_list):

            if support.within_tolerance(_v, sel_vec, 0.1):
                self.start_pi = _i
                break

        _curves = []
        _sta = []

        #get list of curves
        for _pi in self.pi_list[0:self.start_pi + 1]:

            _c = None

            for _curve in self.model.data['geometry']:

                if _curve['Type'] != 'Curve':
                    continue

                if support.within_tolerance(_pi, _curve['PI'], 0.1):
                    _c = _curve
                    break

            _curves.append(_c)

            #store valid stations for discretization range
            if _c:
                _sta.append(_c['InternalStation'])

        #build scenegraph nodes
        _coords = self.model.discretize_geometry([_sta[0][0], _sta[-1][1]])

        self.coord_group.setName('ALIGNMENT_TRACKER')

        self.coord3.point.setValues(
            0, len(_coords), [list(_v) for _v in _coords]
        )

        _line = coin.SoLineSet()
        _line.numVertices.setValue(len(_coords))

        self.coord_group.addChild(self.coord3)
        self.coord_group.addChild(coin.SoMarkerSet())
        self.coord_group.addChild(_line)

        self.curve_list = _curves

        return self.coord_group

    def drag_callback(self, xform, pos):
        """
        Callback for drag operations
        """

        #iterate the list of PI's, getting the updated bearings
        #and the updated start pi
        #and recalculating the corresponding curves

        _prev = None
        _coords = []

        #self.get_transformed_coordinates()

        #self.curve_list[self.start_pi]['PI'] = \
        #    self.curve_list[self.start_pi]['PI'].add(xform)

        for _i, _v in enumerate(self.curve_list):

            if _v is None:
                continue

            _b_in = support.get_bearing(_v['PI'].sub(self.pi_list[_i - 1]))
            _b_out = support.get_bearing(self.pi_list[_i + 1].sub(_v['PI']))

            curve = {
                'PI': _v['PI'],
                'BearingIn': _b_in,
                'BearingOut': _b_out,
                'Radius': self.curve_list[_i]['Radius']
            }

            _parms = arc.get_parameters(curve)
            _pts = arc.get_points(_parms, _dtype=tuple)[0]

            _coords.extend(_pts)

        print(_coords)
        self.coord3.point.setValues(0, len(_coords), _coords)

    def update(self, points):
        """
        Update the tracker points and recompute
        """

        pass

    def finalize(self, node=None):
        """
        Override of the parent method
        """

        self.model = None

        if not node:
            node = self.node

        super().finalize(node)

    def get_transformed_coordinates(self):
        """
        Return the transformed coordinates of the selected nodes based on the
        transformations applied by the drag tracker
        """

        #define the search path if not defined
        if not self.start_path:

            _search = coin.SoSearchAction()
            _search.setNode(self.coord3)
            _search.apply(self.coord_group)

            self.start_path = _search.getPath()

        #get the matrix for the transformation
        _matrix = coin.SoGetMatrixAction(self.viewport)
        _matrix.apply(self.start_path)

        _xf = _matrix.getMatrix()

        #create the 4D vectors for the transformation
        _vecs = [coin.SbVec4f(tuple(_v) + (1.0,)) for _v in self.pi_list]

        #multiply each coordinate by the transformation matrix and return
        #a list of the transformed coordinates, omitting the fourth value
        self.pi_list = [
            Vector(_xf.multVecMatrix(_v).getValue()[:3]) for _v in _vecs
        ]