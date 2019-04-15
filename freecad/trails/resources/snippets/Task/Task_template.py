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
DESCRIPTION
"""

import sys
from PySide import QtGui, QtCore
#from transportationwb.XXX.TaskModel import TaskModel as Model
#from transportationwb.XXX.TaskViewDelegate import TaskViewDelegate as Delegate

class CLASS_NAME:
    def __init__(self, update_callback):

        path = sys.path[0] + '/../freecad-transportation-wb/transportationwb/corridor/task_panel.ui'
        self.ui = path
        self.form = None
        self.update_callback = update_callback

    def accept(self):
        self.update_callback(self)
        return True

    def reject(self):
        return True

    def clicked(self, index):
        pass

    def open(self):
        pass

    def needsFullSpace(self):
        return False

    def isAllowedAlterSelection(self):
        return True

    def isAllowedAlterView(self):
        return True

    def isAllowedAlterDocument(self):
        return True

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok)

    def helpRequested(self):
        pass

    def add_item(self):

        indices = self.form.table_view.selectionModel().selectedIndexes()
        index = 0

        if not indices:
            row = self.form.table_view.model().rowCount()
            self.form.table_view.model().insertRows(row, 1)
            index = self.form.table_view.model().index(row, 0)

        else:
            for index in indices:

                if not index.isValid():
                    continue

                self.form.table_view.model().insertRows(index.row(), 1)

            index = indices[0]

        self.form.table_view.setCurrentIndex(index)
        self.form.table_view.edit(index)

    def remove_item(self):

        indices = self.form.table_view.selectionModel().selectedIndexes()

        for index in indices:

            if not index.isValid():
                continue

            self.form.table_view.model().removeRows(index.row(), 1)

    def build_model(self, data):
        """
        Construct the table model from the loft object property data
        """
        model_data = []

        for _i in range(0, len(data), 3):
            model_data.append([Model.fixup_station(data[_i]), data[_i + 1], data[_i]])

        return model_data

    def setup(self, data):

        #convert the data to lists of lists

        _mw = self.getMainWindow()

        form = _mw.findChild(QtGui.QWidget, 'TaskPanel')

        form.add_button = form.findChild(QtGui.QPushButton, 'add_button')
        form.remove_button = form.findChild(QtGui.QPushButton, 'remove_button')
        form.table_view = form.findChild(QtGui.QTableView, 'table_view')

        model_data = self.build_model(data)

        form.table_view.setModel(Model(form.table_view, model_data))
        form.table_view.setColumnHidden(2, True)
        form.table_view.setItemDelegate(ViewDelegate())
        form.table_view.clicked.connect(lambda: form.table_view.model().sort(2))

        self.form = form

        QtCore.QObject.connect(form.add_button, QtCore.SIGNAL('clicked()'), self.add_item)
        QtCore.QObject.connect(form.remove_button, QtCore.SIGNAL('clicked()'), self.remove_item)

    def getMainWindow(self):

        top = QtGui.QApplication.topLevelWidgets()

        for item in top:
            if item.metaObject().className() == 'Gui::MainWindow':
                return item

        raise RuntimeError('No main window found')

    def addItem(self):
        pass

    def get_model(self):
        """
        Returns the model data set with every element converted to string to external Loft object
        """

        return self.form.table_view.model().dataset
