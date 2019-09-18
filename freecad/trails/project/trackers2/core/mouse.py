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
Provides mouse callbacks for Tracker classes
"""

from ...support.view_state import ViewState

class Mouse():
    """
    Provides mouse callbacks for Tracker classes
    """

    def __init__(self):
        """
        Constructor
        """

        self.callbacks = {
            'SoLocation2Event':
                ViewState().view.addEventCallback(
                    'SoLocation2Event', self.mouse_event),

            'SoMouseButtonEvent':
                ViewState().view.addEventCallback(
                    'SoMouseButtonEvent', self.button_event)
        }

    def mouse_event(self, arg):
        """
        Base mouse event implementation
        """

        pass

    def button_event(self, arg):
        """
        Base button event implementation
        """

        pass