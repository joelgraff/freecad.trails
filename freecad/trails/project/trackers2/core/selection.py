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
Provides SoFCSelection support for Tracker classes
"""

from pivy import coin

from .coin_styles import CoinStyles

from .mouse import Mouse
from .signal import Signal

from .selection_state import SelectionState
from .selection_state import SelectionStateEnum as Enum

from .publisher_events import PublisherEvents as Events

class Selection(Mouse, Signal):
    """
    Provides SoFCSelection support for Tracker classes
    """

    #members provided by Base and Style
    name = []
    base_node = None
    coin_style = None

    def set_style(self, style=None, draw=None, color=None): pass

    #class static for global selection
    sel_state = SelectionState()

    def __init__(self):
        """
        Constructor
        """

        if not self.name:
            return

        self.do_select_highlight = True

        self.sel_node = coin.SoType.fromName("SoFCSelection").createInstance()

        self.sel_node.documentName.setValue(self.name[2])
        self.sel_node.objectName.setValue(self.name[1])
        self.sel_node.subElementName.setValue(self.name[0])

        self.base_node.addChild(self.sel_node)

        super().__init__()

    def is_selected(self):
        """
        Return whether or not the node is selected at all
        """

        return self.sel_state.is_selected(self) > Enum.NONE

    def mouse_event(self, arg):
        """
        Mouse override
        """

        if self.do_select_highlight:
            self.highlight()

        Mouse.mouse_event(self, arg)

    def button_event(self, arg):
        """
        Mouse override
        """

        if self.mouse_state.button1.state == 'DOWN':
            self.sel_state.select(self)

            if self.is_selected():
                self.notify(Events.NODE.SELECTED)

        elif self.do_select_highlight and not self.is_selected():
            self.highlight()

        Mouse.button_event(self, arg)

    def highlight(self):
        """
        Test for highlight conditions and changes
        """

        _style = self.coin_style

        #test to see if this node is under the cursor
        if self.name[0] == self.mouse_state.component:
            _style = CoinStyles.SELECTED

        self.set_style(_style)
