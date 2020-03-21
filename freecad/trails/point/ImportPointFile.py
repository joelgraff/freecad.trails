
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
from PySide import QtCore, QtGui
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

        # TODO : replace with  FreeCAD.getUserAppDataDir()
        # Get file path.
        self.Path = os.path.dirname(__file__)

        # Get *.ui files.
        self.IPFui = FreeCADGui.PySideUic.loadUi(
            self.Path + "/ImportPointFile.ui")
        self.CPGui = FreeCADGui.PySideUic.loadUi(
            self.Path + "/CreatePointGroup.ui")

        # Set icon,  menu text and tooltip.
        self.Resources = {
            'Pixmap': self.Path + '/../Resources/Icons/ImportPointFile.svg',
            'MenuText': "Import Point File",
            'ToolTip': "Import point file which includes survey data."
        }

        # To do.
        UI = self.IPFui
        UI.AddB.clicked.connect(self.AddFile)
        UI.RemoveB.clicked.connect(self.RemoveFile)
        UI.SelectedFilesLW.itemSelectionChanged.connect(self.Preview)
        UI.PointGroupChB.stateChanged.connect(self.ActivatePointGroups)
        UI.CreateGroupB.clicked.connect(self.LoadCPGui)
        UI.ImportB.clicked.connect(self.ImportFile)
        UI.CancelB.clicked.connect(UI.close)

        # Create empty point group names list.
        self.GroupList = []

    def GetResources(self):
        """
        Return the command resources dictionary.
        """

        return self.Resources

    def IsActive(self):
        if FreeCAD.ActiveDocument is None:
            return False
        return True

    def Activated(self):
        """
        Command activation method
        """

        if FreeCAD.ActiveDocument is None:
            return

        # Get or create "Point_Groups".
        try:
            PointGroups = FreeCAD.ActiveDocument.Point_Groups
        except:
            PointGroups = FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'Point_Groups')
            PointGroups.Label = "Point Groups"

        # Get or create "Points".
        try:
            FreeCAD.ActiveDocument.Points
        except:
            Points = FreeCAD.ActiveDocument.addObject(
                'Points::Feature', "Points")
            PointGroups.addObject(Points)

        # Show UI.
        UI = self.IPFui
        UI.setParent(FreeCADGui.getMainWindow())
        UI.setWindowFlags(QtCore.Qt.Window)
        UI.show()

        # Clear previous operation.
        UI.FileNameL.setText("")
        UI.SubGroupListCB.clear()
        UI.SelectedFilesLW.clear()
        UI.PreviewTW.setRowCount(0)
        UI.PointGroupChB.setChecked(False)

        # Add point groups to combo box.
        PointGroups = FreeCAD.ActiveDocument.Point_Groups.Group

        for Item in PointGroups:
            if Item.TypeId == 'Points::Feature':
                self.GroupList.append(Item.Name)
                UI.SubGroupListCB.addItem(Item.Label)

    def AddFile(self):
        """
        Add selected point files to the list view.
        """

        UI = self.IPFui

        FileList = QtGui.QFileDialog.getOpenFileNames(
                        None, "Select one or more files to open",
                        os.getenv("HOME"), 'All Files (*.*)')
        UI.SelectedFilesLW.addItems(FileList[0])

    def RemoveFile(self):
        """
        Remove selected point file from list view.
        """

        UI = self.IPFui

        for item in UI.SelectedFilesLW.selectedItems():
            UI.SelectedFilesLW.takeItem(UI.SelectedFilesLW.row(item))

    def ActivatePointGroups(self):
        """
        If check box status changed, enable or disable combo box and 
        push button.
        """

        UI = self.IPFui

        if UI.PointGroupChB.isChecked():
            UI.SubGroupListCB.setEnabled(True)
            UI.CreateGroupB.setEnabled(True)

        else:
            UI.SubGroupListCB.setEnabled(False)
            UI.CreateGroupB.setEnabled(False)

    def LoadCPGui(self):
        """
        Load Create Point Group UI.
        """

        UI = self.IPFui
        CPG = self.CPGui

        # Show UI.
        CPG.setParent(UI)
        CPG.setWindowFlags(QtCore.Qt.Window)
        CPG.show()

        # To do.
        CPG.OkB.clicked.connect(self.CreatePointGroup)
        CPG.CancelB.clicked.connect(CPG.close)

    def CreatePointGroup(self):
        """
        When Ok button clicked, create new point group.
        """

        UI = self.IPFui
        CPG = self.CPGui

        NewGroupName = CPG.PointGroupNameLE.text()
        NewGroup = FreeCAD.ActiveDocument.addObject(
            'Points::Feature', "Point_Group")
        FreeCAD.ActiveDocument.Point_Groups.addObject(NewGroup)
        UI.SubGroupListCB.addItem(NewGroupName)
        self.GroupList.append(NewGroup.Name)
        NewGroup.Label = NewGroupName
        CPG.close()

    def FileReader(self, File, Operation):
        """
        Read selected files point name, x, y, z and description.
        """

        UI = self.IPFui
        self.PointList = []
        Counter = 1

        # Get *.ui variables.
        PointName = UI.PointNameLE.text()
        Northing = UI.NorthingLE.text()
        Easting = UI.EastingLE.text()
        Elevation = UI.ElevationLE.text()
        Description = UI.DescriptionLE.text()

        # Set delimiter.
        if UI.DelimiterCB.currentText() == "Space":
            reader = csv.reader(File, delimiter=' ')

        if UI.DelimiterCB.currentText() == "Comma":
            reader = csv.reader(File, delimiter=',')

        if UI.DelimiterCB.currentText() == "Tab":
            reader = csv.reader(File, delimiter='\t')

        # Read files.
        for row in reader:
            PN = int(PointName) - 1
            N = int(Northing) - 1
            E = int(Easting) - 1
            Z = int(Elevation) - 1
            D = int(Description) - 1

            if Operation == "Preview":
                numRows = UI.PreviewTW.rowCount()
                UI.PreviewTW.insertRow(numRows)

                UI.PreviewTW.setItem(
                    numRows, 0, QtGui.QTableWidgetItem(row[PN]))
                UI.PreviewTW.setItem(
                    numRows, 1, QtGui.QTableWidgetItem(row[N]))
                UI.PreviewTW.setItem(
                    numRows, 2, QtGui.QTableWidgetItem(row[E]))
                UI.PreviewTW.setItem(
                    numRows, 3, QtGui.QTableWidgetItem(row[Z]))

                try:
                    UI.PreviewTW.setItem(
                        numRows, 4, QtGui.QTableWidgetItem(row[D]))
                except:
                    pass

                if Counter == 500:
                    break
                else:
                    Counter += 1

            elif Operation == "Import":
                self.PointList.append((float(row[E]) * 1000,
                                       float(row[N]) * 1000,
                                       float(row[Z]) * 1000))

    def Preview(self):
        """
        Show a preview for selected point file in list view.
        """

        UI = self.IPFui

        # Get selected file.
        listItems = UI.SelectedFilesLW.selectedItems()

        # Separate path and file name.
        if listItems:
            head, tail = os.path.split(listItems[0].text())
            UI.FileNameL.setText(tail)
            UI.PreviewTW.setRowCount(0)

            # Show selected point file preview in table view.
            File = open(listItems[0].text(), 'r')
            self.FileReader(File, "Preview")

    def ImportFile(self):
        """
        When Import button clicked, create new point group.
        """

        UI = self.IPFui

        # Get *.ui variables.
        Index = UI.SubGroupListCB.currentIndex()

        # If check box is checked get selected item in combo box.
        if UI.PointGroupChB.isChecked():
            SPG = self.GroupList[Index]
            PointGroup = FreeCAD.ActiveDocument.getObject(SPG)
        else:
            PointGroup = FreeCAD.ActiveDocument.Points

        # Read Points from file.
        if UI.SelectedFilesLW.count() < 1:
            FreeCAD.Console.PrintMessage("No Files selected")
            return

        Items = []
        for i in range(UI.SelectedFilesLW.count()):
            Items.append(UI.SelectedFilesLW.item(i))
        Labels = [i.text() for i in Items]
        for FilePath in Labels:
            File = open(FilePath, 'r')
            self.FileReader(File, "Import")

        List = []
        Base = self.PointList[0]
        for Point in self.PointList:
            Point = (Point[0]-Base[0], Point[1]-Base[1], Point[2]-Base[2])
            List.append(Point)

        PointObject = PointGroup.Points.copy()
        PointObject.addPoints(List)
        PointGroup.Points = PointObject
        PointGroup.Placement.Base = Base
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.SendMsgToActiveView("ViewFit")
        UI.close()

FreeCADGui.addCommand('Import Point File', ImportPointFile())
