# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2019 Joel Graff <monograff76@gmail.com>                         *
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

"""
QItemStyledDelegate class for Task QTableView
"""

from PySide import QtGui, QtCore

class TaskViewDelegate(QtGui.QStyledItemDelegate):

    def __init__(self, parent=None):

        QtGui.QStyledItemDelegate.__init__(self, parent)
        self._is_editing = False

    def createEditor(self, parent, option, index):

        return super(TaskViewDelegate, self).createEditor(parent, option, index)

    def setEditorData(self, editor, index):

        self._is_editing = True

        value = index.data(QtCore.Qt.EditRole) or index.data(QtCore.Qt.DisplayRole)

        if editor.metaObject().className() in ['QSpinBox', 'QDoubleSpinBox']:
            editor.setValue(value)
        else:
            editor.setText(value)

    def setModelData(self, editor, model, index):

        super(TaskViewDelegate, self).setModelData(editor, model, index)

        self._is_editing = False

    def isEditing(self):

        return self._is_editing