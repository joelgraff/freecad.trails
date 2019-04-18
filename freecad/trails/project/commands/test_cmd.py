# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2019 Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  This program is free software; you can redistribute it and/or modify  *
# *  it under the terms of the GNU Lesser General Public License (LGPL)    *
# *  as published by the Free Software Foundation; either version 2 of     *
# *  the License, or (at your option) any later version.                   *
# *  for detail see the LICENCE text file.                                 *
# *                                                                        *
# *  This program is distributed in the hope that it will be useful,       *
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *  GNU Library General Public License for more details.                  *
# *                                                                        *
# *  You should have received a copy of the GNU Library General Public     *
# *  License along with this program; if not, write to the Free Software   *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *  USA                                                                   *
# *                                                                        *
# **************************************************************************

import os
import FreeCAD as App
import FreeCADGui as Gui
import random
import timeit


class Command():
    """
    Command Description
    """
    def __init__(self):
        pass

    def GetResources(self):
        """
        Icon resources.
        """

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "../../../icons/new_alignment.svg"

        return {'Pixmap'  : icon_path,
                'Accel'   : '',
                'MenuText': '',
                'ToolTip' : '',
                'CmdType' : 'ForEdit'}


    def f(self):

        for _i in self.indices:
            j = hash((self._list[_i], self._list[_i+1]))

    def g(self):

        for _i in self._list:
            j = self._dict[_i]
            
    def Activated(self):
        """
        Command activation method
        """

        self._list = random.sample(range(-10000, 10000), 10000)
        self._dict = dict((_i, 0) for _i in self._list)

        random.shuffle(self._list)

        self.indices = list(range(0, 2,2))
        #random.shuffle(self.indices)

        itr = 100000
        print(timeit.timeit(self.f, number=itr) / float(itr))
        return

Gui.addCommand('Command', Command())
