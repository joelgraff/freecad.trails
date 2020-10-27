# -*- coding: utf-8 -*-
#***********************************************************************
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
QItemStyledDelegate class for Task QTableView
"""

import PySide.QtGui as QtGui
import PySide.QtCore as QtCore


class ImportAlignmentViewDelegate(QtGui.QStyledItemDelegate):
    """
    View delegate for import alignment task UI
    """

    def __init__(self, model, parent=None):
        """
        Constructor
        """

        QtGui.QStyledItemDelegate.__init__(self, parent)

        self._is_editing = False
        self.combo_box = None
        self.model = ['']
        self.model.extend(model)

    def paint(self, painter, option, index):
        """
        Canvas painting
        """

        painter.save()

        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        painter.setBrush(QtGui.QColor(215, 215, 215))
        painter.drawRect(option.rect)

        if index.isValid():
            painter.setPen(QtGui.QPen(QtGui.QColor(128, 128, 128)))
            value = index.data(QtCore.Qt.DisplayRole)
            painter.drawText(option.rect, QtCore.Qt.AlignCenter, value)

        painter.restore()

    def createEditor(self, parent, option, index):
        """
        Editor for items in model view
        """

        if index.row() > 0:
            return super(ImportAlignmentViewDelegate, self) \
                .createEditor(parent, option, index)

        self.combo_box = QtGui.QComboBox(parent)

        self.combo_box.addItems(self.model)

        value = index.data(QtCore.Qt.DisplayRole)

        self.combo_box.setCurrentIndex(self.combo_box.findText(value))

        return self.combo_box

    def setEditorData(self, editor, index):
        """
        Write model data to editor widget
        """

        self._is_editing = True

        value = index.data(QtCore.Qt.EditRole) \
                or index.data(QtCore.Qt.DisplayRole)

        editor_class = editor.metaObject().className()

        if editor_class == 'QComboBox':
            return

        if editor_class in ['QSpinBox', 'QDoubleSpinBox']:
            editor.setValue(value)

        elif editor_class == 'QComboBox':
            editor.setCurrentIndex()

        else:
            editor.setText(value)

    def setModelData(self, editor, model, index):
        """
        Write edited data to model
        """

        QtGui.QStyledItemDelegate(self).setModelData(editor, model, index)

        self._is_editing = False

    def isEditing(self):
        """
        Return edit status
        """

        return self._is_editing
