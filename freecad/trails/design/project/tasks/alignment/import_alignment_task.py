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
Task to import alignments from various file formats
"""
import FreeCAD, FreeCADGui
import Mesh
from PySide import QtGui, QtCore

from freecad.trails import resources, geo_origin
from .import_xml_subtask import ImportXmlSubtask
from ...support import utils
from ....alignment import horizontal_alignment
from .....geomatics.surface import surface
from .....geomatics.point import point_group

import os



class ImportAlignmentTask:
    """
    Import horizontal alignments from various file formats
    """
    def __init__(self):
        """
        Constructor
        """
        ui_path = resources.__path__[0] + '/ui/import_landxml_panel.ui'
        self.form = FreeCADGui.PySideUic.loadUi(ui_path)
        self.form.tb_browse.clicked.connect(self.choose_file)
        self.form.le_filename.textChanged.connect(self.examine_file)

    def choose_file(self):
        """
        Open the file picker dialog and open the file that the user chooses
        """
        parameter = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/General")
        path = parameter.GetString("FileOpenSavePath")
        filters = self.form.tr('LandXML files (*.xml)')

        file_name = QtGui.QFileDialog.getOpenFileName(
                        self.form, 'Select a LandXML File',
                        path, 'LandXML files (*.xml)', filters)

        self.form.le_filename.setText(file_name[0])

    def examine_file(self):
        """
        Examine the file path indicated in the QLineEdit, determine the type,
        and pass parsing on to the appropriate module
        """
        filename = 'import_alignment_task_xml_subpanel.ui'
        filepath = self.form.le_filename.text()
        subpanel = FreeCADGui.PySideUic.loadUi(resources.__path__[0] + '/ui/' + filename, None)
        self.subtask = ImportXmlSubtask(subpanel, filepath)

        try:
            self.data = self.subtask.parser.import_file(filepath)
            if self.subtask.parser.errors:
                for error in self.subtask.parser.errors:
                    print(error)

            model = QtGui.QStandardItemModel()
            self.form.tv_items.setModel(model)

            for name, group in self.data.items():
                group_widget = QtGui.QStandardItem(name)
                group_widget.setCheckable(True)
                group_widget.setCheckState(QtCore.Qt.Checked)
                model.appendRow(group_widget)

                for i in group:
                    item_widget = QtGui.QStandardItem(i)
                    item_widget.setCheckable(True)
                    item_widget.setCheckState(QtCore.Qt.Checked)
                    group_widget.appendRow(item_widget)

        except OSError:
            dialog = QtGui.QMessageBox(
                QtGui.QMessageBox.Critical, 'Unable to open file ', filepath)

            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.exec_()
            return

    def accept(self):
        """
        Accept the task parameters
        """
        data = self.subtask.import_model()

        if self.subtask.errors:

            print('Errors encountered during import:\n')
            for err in self.subtask.errors:
                print(err)

        if not data:
            return None

        errors = []

        #create a new document if one does not exist
        if not FreeCAD.ActiveDocument:
            FreeCAD.newDocument()
            FreeCADGui.activeDocument().activeView().viewDefaultOrientation()

        for name, s in data['PointClusters'].items():
            points = list(s[0].values())

            if not points:
                source = list(data['PointClusters'].values())[0]
                for i in  s[1]:
                    points.append(source[0][i])

            point_group.create(points, name)

        for name, s in data['Surfaces'].items():
            points = list(s['Points'].values())
            surf = surface.create(points, name)

            indexes = []
            for i in s['Faces']:
                key_list = list(s['Points'].keys())
                c1 = key_list.index(i[0])
                c2 = key_list.index(i[1])
                c3 = key_list.index(i[2])
                indexes.extend([c1, c2, c3])

            surf.Delaunay = indexes

        for align in data['Alignments'].values():

            result = horizontal_alignment.create(
                align, align['meta']['ID']).Proxy

            if result.errors:
                errors += result.errors
                result.errors = []

        if errors:
            print('Errors encountered during alignment creation:\n')

            for err in errors:
                print(err)

        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.SendMsgToActiveView("ViewFit")

        return True

    def reject(self):
        """
        Reject the task
        """
        return True

    def clicked(self, index):
        """
        Clicked callback
        """
        pass
