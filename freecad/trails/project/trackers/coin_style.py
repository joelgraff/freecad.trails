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
Support class for managing Coin3D node styles
"""

from pivy import coin

from ..support.const import Const

class CoinStyle(Const):
    """
    Useful math constants
    """

    DEFAULT = {
        'id': 'default',
        'shape': 'default',
        'line width': None,
        'line style': coin.SoDrawStyle.LINES,
        'line weight': 3,
        'line pattern': None,
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
    

    ERROR = {
        'id': 'error',
        'shape': 'default',
        'size': 9,
        'color': (1.0, 0.0, 0.0),
        'select': True
    }
