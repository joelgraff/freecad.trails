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

    def __init__(self, names, children=None, group=False):
        """
        Constructor
        """
        self.visible = False
        self.color = coin.SoBaseColor()
        self.draw_style = coin.SoDrawStyle()
        self.names = names
        self.node = coin.SoSeparator()
        self.parent = None
        self.picker = coin.SoPickStyle()

        if not children:
            children = []

        if group:
            self.node = coin.SoGroup()

        self.sel_node = \
            coin.SoType.fromName("SoFCSelection").createInstance()

        self.sel_node.documentName.setValue(self.names[0])
        self.sel_node.objectName.setValue(self.names[1])
        self.sel_node.subElementName.setValue(self.names[2])

        for child in [
            self.sel_node, self.picker, self.draw_style, self.color
            ] + children:

            self.node.addChild(child)

    def is_selectable(self):
        """
        Return the selectability of the node based on the picker state
        """

        return self.picker.style.getValue() != coin.SoPickStyle.UNPICKABLE

    def set_selectability(self, is_selectable):
        """
        Set the selectability of the node using the SoPickStyle node
        """
        _state = coin.SoPickStyle.UNPICKABLE

        if is_selectable:
            _state = coin.SoPickStyle.SHAPE

        self.picker.style.setValue(_state)

    def finalize(self, node, parent=None):
        """
        Node destruction / cleanup
        """

        self.remove_node(node, parent)

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

    def copy(self, node=None):
        """
        Return a copy of the tracker node
        """

        if not node:
            node = self.node

        return node.copy()

    def get_search_path(self, node):
        """
        Return the search path for the specified node
        """

        #define the search path if not defined
        #if not self.start_path:
        _search = coin.SoSearchAction()
        _search.setNode(node)
        _search.apply(self.node)

        return _search.getPath()

    def _insert_sg(self, node):
        """
        Insert a node into the scenegraph at the top
        """

        Draft.get3DView().getSceneGraph().insertChild(node, 0)

    def insert_node(self, node, parent=None):
        """
        Insert a node as a child of the passed node
        """

        _fn = self._insert_sg

        if parent:
            _fn = parent.addChild

        todo.delay(_fn, node)

    def remove_node(self, node, parent=None):
        """
        Convenience wrapper for _remove_node
        """

        if not parent:
            parent = Draft.get3DView().getSceneGraph()

        if parent.findChild(node) >= 0:
            todo.delay(parent.removeChild, node)

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
