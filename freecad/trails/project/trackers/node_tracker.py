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
Customized edit tracker from DraftTrackers.editTracker
"""

from pivy import coin

from FreeCAD import Vector

from ..support.drag_state import DragState
from ..support.view_state import ViewState
from ..support.mouse_state import MouseState

from ..support.publisher import PublisherEvents as Events

from .base_tracker import BaseTracker

class NodeTracker(BaseTracker):
    """
    Tracker object for nodes
    """

    def __init__(self, names, point, nodes=None):
        """
        Constructor
        """

        self.type = 'NODE'

        if not nodes:
            nodes = []

        elif not isinstance(nodes, list):
            nodes = [nodes]

        self.is_end_node = False
        self.point = tuple(point)
        self.ui_message = {}

        #build node structure for the node tracker
        self.coord = coin.SoCoordinate3()
        self.marker = coin.SoMarkerSet()
        self.drag_point = self.point

        super().__init__(
            names=names, children=[self.coord, self.marker] + nodes
        )

        self.update()

    def button_event(self, arg):
        """
        Override base implementation
        """

        super().button_event(arg)

        #if MouseState().button1.state == 'UP' and self.is_selected():
        #    self.dispatch(Events.NODE_EVENT,
        #    {'name': self.name, 'position': self.point})

    def start_drag(self):
        """
        Initialize drag ops
        """

        if not self.is_selected():
            return

        super().start_drag()

        self.drag_point = self.point

        if self == DragState().drag_node:
            MouseState().set_mouse_position(self.point)

        #self.ui_message = {
        #    'name': self.name,
        #    'position': self.drag_point,
        #    'translation': DragState().transform.translation,
        #    'rotation': DragState().transform.rotation,
        #    'center': DragState().transform.center
        #}

    def on_drag(self):
        """
        Override of base function
        """

        if not (self.drag_point and DragState().drag_node):
            return

        super().on_drag()

        self.update_drag_point()

        #self.ui_message['position'] = self.drag_point
        #self.dispatch(Events.NODE_EVENT, self.ui_message)

    def end_drag(self):
        """
        Override of base function
        """

        if self.drag_point and DragState().drag_node and not DragState().abort:
            self.update_drag_point()
            self.update(self.drag_point)

        #self.ui_message['position'] = self.point
        #self.dispatch(Events.NODE_EVENT, self.ui_message)

        super().end_drag()

    def notify(self, event_type, message):
        """
        Override of Subscriber method
        """

        if not self.is_selected():
            return

        if not event_type == Events.NODE_EVENT:
            return

        self.update(message)

    def update_drag_point(self):
        """
        Update the drag point based on the selection method
        """

        if self.select_state == 'MANUAL':
            self.drag_point = \
                self.drag_copy.getChild(3).point.getValues()[0].getValue()

        else:
            self.drag_point = tuple(ViewState().transform_points(
                [self.point], DragState().node_group)[0])

        self.drag_point = self.drag_point[0:3]

    def update(self, coord=None):
        """
        Update the coordinate position
        """

        #if we have a list of points, pick the first
        if isinstance(coord, list):
            coord = coord[0]

        if not coord:
            coord = self.point

        _c = coord

        if not isinstance(coord, tuple):
            _c = tuple(_c)

        self.coord.point.setValue(_c[:3])
        self.point = _c

        print('\n\t',self.name, 'node update...')
        self.dispatch(Events.NODE_EVENT, ('NODE_POSITION', self.point), True)

    def get(self):
        """
        Get method
        """

        return Vector(self.coord.point.getValues()[0].getValue())

    def finalize(self, node=None, parent=None):
        """
        Cleanup
        """

        super().finalize(self.get_node(), parent)
