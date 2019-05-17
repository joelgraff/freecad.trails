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
import FreeCADGui as Gui

from .base_tracker import BaseTracker
from ..support.const import Const

class NodeTracker(BaseTracker):
    """
    A custom edit tracker
    """


    class STYLE(Const):
        """
        Style constants for nodes
        """

        DEFAULT = {
            'id': 'default',
            'shape': 'default',
            'size': 9,
            'color': (0.8, 0.8, 0.8),
            'select': True
        }

        ROLL_OUTER = {
            'id': 'roll_outer',
            'shape': 'circle',
            'size': 9,
            'color': (0.4, 0.8, 0.4),
            'select': True
        }

        ROLL_INNER = {
            'id': 'roll_inner',
            'shape': 'cross',
            'size': 5,
            'color': (0.4, 0.8, 0.4),
            'select': True
        }

        SELECTED = {
            'id': 'selected',
            'shape': 'default',
            'size': 9,
            'color': (1.0, 0.9, 0.0),
            'select': True
        }

    def __init__(self, names, point, nodes=None):
        """
        Constructor
        """

        self.type = 'NODE'
        if not nodes:
            nodes = []

        elif not isinstance(nodes, list):
            nodes = [nodes]

        self.groups = {
            'default': [],
            'rollover': []
        }

        self.switch = coin.SoSwitch() # this is the on/off switch
        self.coord = coin.SoCoordinate3()
        self.name = names[2]

        self.switch.setName(self.name)

        self.switch.addChild(self.create_default(names))
        self.switch.addChild(self.create_rollover(names))

        super().__init__(names=names, children=nodes + [self.switch],
                         select=False, group=True)

        self.on(self.switch, 0)

    def create_rollover(self, names):
        """
        Create the rollover node tracker
        """

        group = coin.SoGroup()

        for style in [self.STYLE.ROLL_INNER, self.STYLE.ROLL_OUTER]:

            marker = coin.SoMarkerSet()

            marker.markerIndex = \
                Gui.getMarkerIndex(style['shape'], style['size'])

            nam = names[:]
            nam[2] += '.' +style['id']

            child = BaseTracker(nam, [self.coord, marker], style['select'])
            child.color.rgb = style['color']

            group.addChild(child.node)

            self.groups['rollover'].append(child)

        return group

    def create_default(self, names):
        """
        Create the default node tracker
        """

        style = self.STYLE.DEFAULT

        marker = coin.SoMarkerSet()

        marker.markerIndex = Gui.getMarkerIndex(style['shape'], style['size'])

        nam = names[:]
        nam[2] += '.' +style['id']

        child = BaseTracker(nam, [self.coord, marker], style['select'])
        child.color.rgb = style['color']

        group = coin.SoGroup()
        group.addChild(child.node)

        self.groups['default'].append(child)

        return group

    def default(self):
        """
        Set node to default style
        """

        for _child in self.groups['default']:
            _child.color.rgb = self.STYLE.DEFAULT['color']

        if self.switch.whichChild:
            self.switch.whichChild = 0

    def selected(self):
        """
        Set node to select style
        """

        for _child in self.groups['default']:
            _child.color.rgb = self.STYLE.SELECTED['color']

        if self.switch.whichChild:
            self.switch.whichChild = 0

    def update(self, coord):
        """
        Update the coordinate position
        """

        _c = coord

        if not isinstance(coord, tuple):
            _c = tuple(_c)

        self.coord.point.setValue(_c)

    def get(self):
        """
        Get method
        """

        return Vector(self.coord.point.getValues()[0].getValue())

    def finalize(self):
        """
        Cleanup
        """

        self.remove_node(self.node)
