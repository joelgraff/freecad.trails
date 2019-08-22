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
Grid tracker
"""

from pivy import coin

from FreeCAD import Vector

from .base_tracker import BaseTracker

class GridTracker(BaseTracker):
    """
    GridTracker Class

    self.points - list of Vectors
    self.selction_nodes -
        list of point indices which correspond to node trackers
    """

    def __init__(self, names, nodes=None):
        """
        Constructor
        """

        self.line = coin.SoLineSet()

        self.coord = coin.SoCoordinate3()
        self.points = None
        self.selection_nodes = None
        self.selection_indices = []
        self.names = names

        self.group = coin.SoSeparator()
        self.drag_coord = None
        self.drag_idx = None
        self.drag_start = []

        self.grid_dimension = Vector()
        self.grid_size = Vector()
        self.grid_border = Vector()
        self.grid_pad = Vector()

        self.grid_cells = []

        if not nodes:
            nodes = []

        elif not isinstance(nodes, list):
            nodes = list(nodes)

        nodes += [self.coord, self.line]

        self._build_grid_cells()

        super().__init__(names=names, children=nodes)

    def _build_grid_cells(self):

        pass
        #_names = self.names[:]

        #_names[2] = 'GRID'
        #_wt = WireTracker(_names)

        #_dim = Vector()

        #_dim = self.grid_size.add(self.grid_pad.)


    def mouse_event(self, arg):
        """
        Override of base function
        """

        pass

    def update(self):
        """
        Update the grid cells
        """

        pass

    def update_dimension(self, horizontal=None, vertical=None):
        """
        Update the grid overall dimensions
        """

        if horizontal:
            self.grid_dimension.x = horizontal

        if vertical:
            self.grid_dimension.y = vertical

        self.update()

    def update_size(self, horizontal=None, vertical=None):
        """
        Update the grid cell size
        """

        if horizontal:
            self.grid_size.x = horizontal

        if vertical:
            self.grid_size.y = vertical

        self.update()

    def update_border(self, horizontal=None, vertical=None):
        """
        Update the grid border padding
        """

        if horizontal is not None:
            self.grid_border.x = horizontal

        if vertical is not None:
            self.grid_border.y = vertical

        self.update()

    def update_pad(self, horizontal=None, vertical=None):
        """
        Update the grid cell padding
        """

        if horizontal is not None:
            self.grid_pad.x = horizontal

        if vertical is not None:
            self.grid_pad.y = vertical

        self.update()
