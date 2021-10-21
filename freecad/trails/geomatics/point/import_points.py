
# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2019 Hakan Seven <hakanseven12@gmail.com>             *
# *                                                                     *
# * This program is free software; you can redistribute it and/or modify*
# * it under the terms of the GNU Lesser General Public License (LGPL)  *
# * as published by the Free Software Foundation; either version 2 of   *
# * the License, or (at your option) any later version.                 *
# * for detail see the LICENCE text file.                               *
# *                                                                     *
# * This program is distributed in the hope that it will be useful,     *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of      *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
# * GNU Library General Public License for more details.                *
# *                                                                     *
# * You should have received a copy of the GNU Library General Public   *
# * License along with this program; if not, write to the Free Software *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
# * USA                                                                 *
# *                                                                     *
# ***********************************************************************

import FreeCAD
import FreeCADGui
from PySide2 import QtCore, QtGui, QtWidgets
from freecad.trails import ICONPATH
from . import point_group, point_groups
import csv
import os



class ImportPointFile:
    """
    Command to import point file which includes survey data.
    """

    def __init__(self):
        """
        Constructor
        """

        # Get file path
        self.ui_path = os.path.dirname(__file__)

        # Get *.ui file(s)
        ui = FreeCADGui.PySideUic.loadUi(
            self.ui_path + "/import_points.ui")

        # UI connections
        ui.AddB.clicked.connect(self.add_file)
        ui.RemoveB.clicked.connect(self.remove_file)
        ui.SelectedFilesLW.itemSelectionChanged.connect(self.preview)
        ui.PointGroupChB.stateChanged.connect(self.pg_selection)
        ui.CreateGroupB.clicked.connect(self.load_newpg_ui)
        ui.ImportB.clicked.connect(self.import_file)
        ui.CancelB.clicked.connect(ui.close)
        self.ui = ui

    def GetResources(self):
        """
        Return the command resources dictionary.
        """

        return {
            'Pixmap': ICONPATH + '/icons/ImportPointFile.svg',
            'MenuText': "Import Point File",
            'ToolTip': "Import point file which includes survey data."
            }

    def IsActive(self):
        """
        Define tool button activation situation
        """
        # Check for document
        if FreeCAD.ActiveDocument:
            return True
        return False

    def Activated(self):
        """
        Command activation method
        """
        # Get or create 'Point Groups'.
        groups = point_groups.get()

        # Set and show UI
        self.ui.setParent(FreeCADGui.getMainWindow())
        self.ui.setWindowFlags(QtCore.Qt.Window)
        self.ui.show()

        # Clear previous operation
        self.ui.FileNameL.setText("")
        self.ui.SubGroupListCB.clear()
        self.ui.SelectedFilesLW.clear()
        self.ui.PreviewTW.setRowCount(0)
        self.ui.PointGroupChB.setChecked(False)

        # Add point groups to QComboBox
        self.group_dict = {}
        for child in groups.Group:
            if child.Proxy.Type == 'Trails::PointGroup':
                self.group_dict[child.Label] = child
                self.ui.SubGroupListCB.addItem(child.Label)

    def add_file(self):
        """
        Add point files to importer
        """
        # Get selected point file(s) and add them to QListWidget
        parameter = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/General")
        path = parameter.GetString("FileOpenSavePath")
        file_name = QtWidgets.QFileDialog.getOpenFileNames(
                        None, "Select one or more files to open",
                        path, 'All Files (*.*)')
        self.ui.SelectedFilesLW.addItems(file_name[0])

    def remove_file(self):
        """
        Remove point files from importer
        """
        # Get selected point file(s) and remove them from QListWidget
        for item in self.ui.SelectedFilesLW.selectedItems():
            self.ui.SelectedFilesLW.takeItem(self.ui.SelectedFilesLW.row(item))

    def pg_selection(self):
        """
        Enable or disable 'Create Point Group' feature
        """
        #If check box status changed, enable or disable combo box and push button.
        if self.ui.PointGroupChB.isChecked():
            self.ui.SubGroupListCB.setEnabled(True)
            self.ui.CreateGroupB.setEnabled(True)
        else:
            self.ui.SubGroupListCB.setEnabled(False)
            self.ui.CreateGroupB.setEnabled(False)

    def load_newpg_ui(self):
        """
        Load 'Create Point Group' UI.
        """
        # Set and show 'Create Point Group' UI
        subpanel = FreeCADGui.PySideUic.loadUi(
            self.ui_path + "/create_pg.ui")
        subpanel.setParent(self.ui)
        subpanel.setWindowFlags(QtCore.Qt.Window)
        subpanel.show()

        # UI connections
        self.subpanel = subpanel
        subpanel.OkB.clicked.connect(self.create_pg)
        subpanel.CancelB.clicked.connect(subpanel.close)

    def create_pg(self):
        """
        Create new point group
        """
        # Create new point group and add it to QComboBox
        group_name = self.subpanel.PointGroupNameLE.text()
        new_group = point_group.create(name=group_name)
        self.group_dict[new_group.Label] = new_group
        self.ui.SubGroupListCB.addItem(new_group.Label)
        self.subpanel.close()

    def file_reader(self, file, operation):
        """
        Read file points and show them to user or add them to point group
        """
        # Get user inputs
        names = []
        vectors = []
        descriptions = []

        counter = 1
        point_name = self.ui.PointNameLE.text()
        northing = self.ui.NorthingLE.text()
        easting = self.ui.EastingLE.text()
        elevation = self.ui.ElevationLE.text()
        description = self.ui.DescriptionLE.text()

        # Set delimiter
        combobox = self.ui.DelimiterCB

        if combobox.currentText() == "Space":
            reader = csv.reader(file, delimiter=' ',
                skipinitialspace=True)

        if combobox.currentText() == "Comma":
            reader = csv.reader(file, delimiter=',')

        if combobox.currentText() == "Tab":
            reader = csv.reader(file, delimiter='\t')

        table_widget = self.ui.PreviewTW

        # Read files
        for row in reader:
            pn = int(point_name) - 1
            n = int(northing) - 1
            e = int(easting) - 1
            z = int(elevation) - 1
            d = int(description) - 1

            # Show point file data in QTableView
            if operation == "Preview":
                numRows = table_widget.rowCount()
                table_widget.insertRow(numRows)

                try:
                    table_widget.setItem(
                        numRows, 0, QtWidgets.QTableWidgetItem(row[pn]))
                except Exception:
                    pass

                try:
                    table_widget.setItem(
                        numRows, 1, QtWidgets.QTableWidgetItem(row[n]))
                except Exception:
                    pass

                try:
                    table_widget.setItem(
                        numRows, 2, QtWidgets.QTableWidgetItem(row[e]))
                except Exception:
                    pass

                try:
                    table_widget.setItem(
                        numRows, 3, QtWidgets.QTableWidgetItem(row[z]))
                except Exception:
                    pass

                try:
                    table_widget.setItem(
                        numRows, 4, QtWidgets.QTableWidgetItem(row[d]))
                except Exception:
                    pass

                if counter == 500:
                    break
                else:
                    counter += 1

            # Add points to point group
            elif operation == "Import":
                try: name = row[pn]
                except Exception: name = ""

                try: des = row[d]
                except Exception: des = ""

                names.append(name)
                descriptions.append(des)
                vector = FreeCAD.Vector(float(row[e]), float(row[n]), float(row[z]))
                vectors.append(vector.multiply(1000))

        return names, vectors, descriptions

    def preview(self):
        """
        Show a preview for selected point file
        """
        # Get selected file
        selected_file = self.ui.SelectedFilesLW.selectedItems()

        # Separate path and file name
        if selected_file:
            head, tail = os.path.split(selected_file[0].text())
            self.ui.FileNameL.setText(tail)
            self.ui.PreviewTW.setRowCount(0)

            # Send selected point file to preview
            file = open(selected_file[0].text(), 'r')
            self.file_reader(file, "Preview")

    def import_file(self):
        """
        Import added files to selected point group
        """
        # Get user inputs
        text = self.ui.SubGroupListCB.currentText()

        # If check box is checked get selected item in QComboBox
        if self.ui.PointGroupChB.isChecked():
            group = self.group_dict[text]
        else:
            # Get or create 'Points'.
            group = point_group.get_points()

        # Read Points from file
        list_widget = self.ui.SelectedFilesLW
        if list_widget.count() < 1:
            FreeCAD.Console.PrintMessage("No Files selected")
            return

        items = []
        for i in range(list_widget.count()):
            items.append(list_widget.item(i))
        file_paths = [i.text() for i in items]
        names = group.PointNames.copy()
        points = group.Vectors.copy()
        descriptions = group.Descriptions.copy()

        for path in file_paths:
            file = open(path, 'r')
            names, vectors, descriptions =self.file_reader(file, "Import")
            names.extend(names)
            points.extend(vectors)
            descriptions.extend(descriptions)

        group.PointNames = names
        group.Vectors = points
        group.Descriptions = descriptions
        group.recompute()

FreeCADGui.addCommand('Import Point File', ImportPointFile())
