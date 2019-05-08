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
Customized wire tracker from DraftTrackers.wireTracker
"""

from pivy import coin

import Draft

from DraftTrackers import Tracker
from DraftGui import todo

class BaseTracker:
    """
    A custom base Draft Tracker
    """

    def __init__(self, names, children=[], select=True, group=False):
        """
        Constructor
        """
        self.visible = False
        self.select = select
        self.color = coin.SoBaseColor()
        self.draw_style = coin.SoDrawStyle()
        self.names = names
        self.node = coin.SoSeparator()

        if group:
            self.node = coin.SoGroup()

        if self.select:

            self.node = \
                coin.SoType.fromName("SoFCSelection").createInstance()

            self.node.documentName.setValue(self.names[0])
            self.node.objectName.setValue(self.names[1])
            self.node.subElementName.setValue(self.names[2])

        for c in [self.draw_style, self.color] + children:
            self.node.addChild(c)

    def finalize(self, node):
        self.remove_node(node)

    def on(self, switch, which_child=0):
        switch.whichChild = which_child
        self.visible = True

    def off(self, switch):
        switch.whichChild = -1
        self.visible = False

    def insert_node(self, node):
        """
        Convenince wrapper for _insert_node
        """

        todo.delay(self._insert_node, node)

    def remove_node(self, node):
        """
        Convenience wrapper for _remove_node
        """

        todo.delay(self._remove_node, node)

    def _insert_node(self, node, ontop=False):
        """
        Insert node into the scene graph.
        Must not be called from an event handler (or other scene graph
        traversal).
        """

        _sg = Draft.get3DView().getSceneGraph()

        if ontop:
            _sg.insertChild(node, 0)
        else:
            _sg.addChild(node)

    def _remove_node(self, node):
        """
        Remove self.switch from the scene graph.
        Must not be called during scene graph traversal).
        """

        _sg = Draft.get3DView().getSceneGraph()

        print('try remove node ', node, '\n\t', _sg.findChild(node))

        if _sg.findChild(node) >= 0:
            print('remove node ', node)
            _sg.removeChild(node)

    def adjustTracker(self, toTop=True):
        """
        Raises the tracker to the top or lowers it to the bottom based
        on the passed boolean
        """

        if self.switch:

            sg = Draft.get3DView().getSceneGraph()
            sg.removeChild(self.switch)

            if toTop:
                sg.insertChild(self.switch)
            else:
                sg.addChild(self.switch)
