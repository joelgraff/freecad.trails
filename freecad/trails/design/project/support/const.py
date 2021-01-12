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
Constant class definition
"""

__title__ = "Const.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

class MetaConst(type):
    """
    Metaclass to enforce constant-like behaviors
    """

    def __getattr__(cls, key):
        """
        Default getter
        """
        #pylint: disable=unsubscriptable-object
        return cls[key]

    def __setattr__(cls, key, value):
        """
        Default setter
        """
        raise TypeError

class Const(object, metaclass=MetaConst):
    """
    Const class for subclassing
    """

    def __getattr__(self, name):
        """
        Default getter
        """

        return self[name]

    def __setattr__(self, name, value):
        """
        Default setter
        """

        raise TypeError
