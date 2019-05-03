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

import FreeCAD as App
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

        OUTER = {
            'id': 'outer',
            'shape': 'circle',
            'size': 9,
            'color': (0.4, 0.8, 0.4),
            'select': True
        }

        INNER = {
            'id': 'inner',
            'shape': 'cross',
            'size': 5,
            'color': (0.4, 0.8, 0.4),
            'select': False
        }

    def __init__(self, names, point, nodes=None):

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
        
        if names[2]:
            self.switch.setName(names[2])

        self.switch.addChild(self.create_default(names))
        self.switch.addChild(self.create_rollover(names))

        super().__init__(names=names, children=nodes + [self.switch],
                         select=False)

        self.on(self.switch, 0)

    def create_rollover(self, names):
        """
        Create the rollover node tracker
        """

        group = coin.SoGroup()

        for style in [self.STYLE.INNER, self.STYLE.OUTER]:

            marker = coin.SoMarkerSet()

            marker.markerIndex = \
                Gui.getMarkerIndex(style['shape'], style['size'])

            nam = names[:]
            nam[2] += '_' +style['id']

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
        nam[2] += '_' +style['id']

        child = BaseTracker(nam, [self.coord, marker], style['select'])
        child.color.rgb = style['color']

        group = coin.SoGroup()
        group.addChild(child.node)

        self.groups['default'].append(child)

        return group

    def switch_node(self, state='default'):
        """
        Switch to default node
        """

        idx = 0

        if state == 'rollover':
            idx = 1

        elif state == 'select':
            for _child in self.groups['rollover']:
                _child.node.color.rgb = (0.8, 0.8, 0.4)

        elif state == 'deselect':
            for _child in self.groups['rollover']:
                _child.node.color.rgb = (0.8, 0.8, 0.8)

        self.switch.whichChild = idx

    def update(self, coord):
        """
        Update the coordinate position
        """

        self.coord.point.setValue(tuple(coord))

    def get(self):
        """
        Get method
        """
        _pt = self.coord.point.getValues()[0]

        return App.Vector(_pt)

    def finalize(self):
        """
        Cleanup
        """

        self._removeSwitch(self.switch)
