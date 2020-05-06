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
Box tracker

PRESERVED FOR FUTURE REFERENCE AS POSSIBLE RUBBERBAND SELECTION TOOL
"""
"""
from pivy import coin

from FreeCAD import Vector

#from .base_tracker import BaseTracker
#from .wire_tracker import WireTracker
from .trait.coin.coin_styles import CoinStyles

from ..support.drag_state import DragState
from ..support.mouse_state import MouseState

class BoxTracker(BaseTracker):
    #"#""
    BoxTracker Class

    self.points - list of Vectors
    self.selction_nodes -
        list of point indices which correspond to node trackers
    #"#""

    def __init__(self, names, nodes=None):
        #"#""
        Constructor
        #"#""

        self.face = coin.SoFaceSet()

        self.coord = coin.SoCoordinate3()
        self.points = None
        self.selection_nodes = None
        self.selection_indices = []
        self.names = names

        self.group = coin.SoSeparator()
        self.drag_coord = None
        self.drag_idx = None
        self.drag_start = []

        self.trackers = []
        self.start = Vector()
        self.size = Vector()

        self.transparency = coin.SoTransparencyType()

        if not nodes:
            nodes = []

        elif not isinstance(nodes, list):
            nodes = list(nodes)

        nodes += [self.coord, self.transparency, self.face]

        super().__init__(names, nodes)

        self._build_trackers()

        for _t in self.trackers:
            self.node.addChild(_t.switch)

    def _build_trackers(self):

        _names = self.names[:]

        _names[2] = 'BOX'

        for _i in range(0, 4):
            _wt = WireTracker(_names)
            _wt.set_selectability(False)
            self.trackers.append(_wt)

    def mouse_event(self, arg):
        #"#""
        Override of base function
        #"#""

        pass

    def update(self, start_pt=None, end_pt=None):
        #"#""
        Update function
        #"#""

        if start_pt is None:
            start_pt = DragState().start

        if end_pt is None:
            end_pt = MouseState().coordinates

        dim = end_pt.sub(start_pt)

        self.size.x = abs(dim.x)
        self.size.y = abs(dim.y)

        self.points = [
            start_pt,
            Vector(end_pt.x, start_pt.y, 0.0),
            end_pt,
            Vector(start_pt.x, end_pt.y, 0.0),
        ]

        _points = [tuple(_v) for _v in self.points]

        self.coord.point.setValues(0, 4, _points)
        self.face.numVertices.setValue(4)
        self.coin_style = CoinStyles.DEFAULT

        super().refresh()
"""
