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

    def __init__(self, doc, children=[], ontop=False, name=None, insert=False):

        self.top_node = insert
        self.ontop = ontop

        self.color = coin.SoBaseColor()
        self.draw_style = coin.SoDrawStyle()

        node = coin.SoSeparator()

        for c in [self.draw_style, self.color] + children:
            print(c)
            node.addChild(c)

        self.switch = coin.SoSwitch() # this is the on/off switch

        if name:
            self.switch.setName(name)

        self.switch.addChild(node)
        self.off()

        if self.top_node:
            todo.delay(self._insertSwitch, self.switch)

    def finalize(self):

        if not self.top_node:
            return

        todo.delay(self._removeSwitch, self.switch)
        self.switch = None

    def _insertSwitch(self, switch):
        """
        Insert self.switch into the scene graph.
        Must not be called from an event handler (or other scene graph
        traversal).
        """

        sg=Draft.get3DView().getSceneGraph()

        if self.ontop:
            sg.insertChild(switch, 0)
        else:
            sg.addChild(switch)

    def _removeSwitch(self, switch):
        """
        Remove self.switch from the scene graph.
        Must not be called during scene graph traversal).
        """

        sg=Draft.get3DView().getSceneGraph()

        if sg.findChild(switch) >= 0:
            sg.removeChild(switch)

    def on(self):
        self.switch.whichChild = 0
        self.Visible = True

    def off(self):
        self.switch.whichChild = -1
        self.Visible = False

    def adjustTracker(self, toTop = True):
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
