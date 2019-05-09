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
Tracker for dragging operations
"""

from pivy import coin

from FreeCAD import Vector

from DraftGui import todo

from .base_tracker import BaseTracker

class DragTracker(BaseTracker):
    """
    Tracker for dragging operations
    """

    def __init__(self, names, children, parent, node_tracker):
        """
        Constructor
        """

        self.parent = parent
        self.switch = coin.SoSwitch()
        self.datum = Vector(node_tracker.coord.point.getValues()[0].getValue())
        self.transform = coin.SoTransform()
        self.transform.translation.setValue([0.0, 0.0, 0.0])

        self.marker_coords = coin.SoCoordinate3()

        coords = []

        for child in children:
            coords.append(child.get())

        #assign all coords to self.marker_coords
        #...

        self.marker_set = coin.SoMarkerSet()

        if len(coords) > 1:
            self.line_set = coin.SoLineSet()
            self.line_set.numVertices.setValue(len(coords))

        child_nodes = \
            [self.transform, self.marker_coords, self.marker_set, self.line_set] + [_v.node for _v in children]

        super().__init__(names, child_nodes, False)


    def _init_(self, names, children, parent, node_tracker):
        """
        Deprecated Constructor
        """

        self.parent = parent
        self.switch = coin.SoSwitch()
        self.separator = coin.SoSeparator()
        self.datum = \
            Vector(node_tracker.coord.point.getValues()[0].getValue())

        self.transform = coin.SoTransform()
        self.transform.translation.setValue([0.0, 0.0, 0.0])

        super().__init__(names,
                         [self.transform] + [_v.node for _v in children], False, True
                        )

        coord = coin.SoCoordinate3()
        coord.point.setValue((tuple(children[0].get())))
        self.node.addChild(coord)
        coord = coin.SoCoordinate3()
        coord.point.setValue((tuple(children[1].get())))
        self.node.addChild(coord)
        line = coin.SoLineSet()
        line.numVertices.setValue((1,1))

        self.node.addChild(line)

        self.separator.addChild(self.node)
        self.switch.addChild(self.separator)
        self.parent.addChild(self.switch)

        self.on(self.switch)

    def update(self, position):
        """
        Update the transform with the passed position
        """

        self.transform.translation.setValue(tuple(position))

    def update_placement(self, position):
        """
        Update the placement
        """

        _pos = tuple(list(position.sub(self.datum)))
        self.transform.translation.setValue(_pos)

    def get_placement(self):
        """
        Return the placement of the tracker
        """

        return Vector(self.transform.translation.getValue())

    def finalize(self, node=None):
        """
        Shutdown
        """

        if not node:
            node = self.switch

        todo.delay(self.parent.removeChild, node)
