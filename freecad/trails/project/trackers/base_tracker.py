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

from DraftGui import todo

class BaseTracker:
    """
    A custom base Draft Tracker
    """

    def __init__(self, names, children=None, select=True, group=False):
        """
        Constructor
        """
        self.visible = False
        self.select = select
        self.color = coin.SoBaseColor()
        self.draw_style = coin.SoDrawStyle()
        self.names = names
        self.node = coin.SoSeparator()

        if not children:
            children = []

        if group:
            self.node = coin.SoGroup()

        if self.select:

            self.node = \
                coin.SoType.fromName("SoFCSelection").createInstance()

            self.node.documentName.setValue(self.names[0])
            self.node.objectName.setValue(self.names[1])
            self.node.subElementName.setValue(self.names[2])

        for child in [self.draw_style, self.color] + children:
            self.node.addChild(child)

    def finalize(self, node):
        """
        Node destruction / cleanup
        """

        self.remove_node(node)

    def on(self, switch, which_child=0):
        """
        Make node visible
        """

        switch.whichChild = which_child
        self.visible = True

    def off(self, switch):
        """
        Make node invisible
        """

        switch.whichChild = -1
        self.visible = False

    def insert_node(self, node):
        """
        Convenince wrapper for _insert_node
        """

        todo.delay(Draft.get3DView().getSceneGraph().addChild, node)

    def remove_node(self, node):
        """
        Convenience wrapper for _remove_node
        """

        if Draft.get3DView().getSceneGraph().findChild(node) >= 0:
            todo.delay(Draft.get3DView().getSceneGraph().removeChild, node)

    def insert_child(self, node):
        """
        Convenience wrapper for _insert_child
        """

        todo.delay(self.node.addChild, node)

    def remove_child(self, node):
        """
        Convenience wrapper for _remove_child
        """

        if self.node.findChild(node) >= 0:
            todo.delay(self.node.removeChild, node)

    def _insert_node(self, node, parent, ontop=False):
        """
        Insert node into the scene graph.
        Must not be called from an event handler (or other scene graph
        traversal).
        """

        if ontop:
            parent.insertChild(node, 0)
        else:
            parent.addChild(node)

    def _remove_node(self, parent, node):
        """
        Remove self.switch from the scene graph.
        Must not be called during scene graph traversal).
        """

        if parent.findChild(node) >= 0:
            parent.removeChild(node)

    def adjustTracker(self, node=None, to_top=True):
        """
        Raises the tracker to the top or lowers it to the bottom based
        on the passed boolean
        """

        if not node:
            node = self.node

        if not node:
            return

        _sg = Draft.get3DView().getSceneGraph()
        _sg.removeChild(node)

        if to_top:
            _sg.insertChild(node)

        else:
            _sg.addChild(node)
