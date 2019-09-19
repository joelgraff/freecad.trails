# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#* Copyright (c) 2018 Joel Graff <monograff76@gmail.com>               *
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
Subscriber base class
"""

class Subscriber:
    """
    Base Subscriber class
    """

    counter = 0
    name = 'Subscriber'

    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.sub_id = Subscriber.counter
        Subscriber.counter += 1

    def notify(self, event_type, message, verbose=False):
        """
        Default message update method
        """

        if verbose:
            print('{} (#{}) got event {} message "{}"'\
                .format(self.name, self.sub_id, event_type, message))
