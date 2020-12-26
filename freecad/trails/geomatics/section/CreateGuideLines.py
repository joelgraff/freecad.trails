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

import os
import math
import FreeCAD
import FreeCADGui
import Draft
from FreeCAD import Vector
from PySide import QtCore, QtGui
from freecad.trails import ICONPATH


class CreateGuideLines:

    def __init__(self):

        self.resources = {
            'Pixmap': ICONPATH + '/icons/CreateGuideLines.svg',
            'MenuText': "Create Guide Lines",
            'ToolTip': "Create guide lines for selected alignment"
                    }

        # Command to create guide lines for selected alignment.
        self.Path = os.path.dirname(__file__)

        self.IPFui = FreeCADGui.PySideUic.loadUi(
            self.Path + "/CreateGuideLines.ui")
        self.CPGui = FreeCADGui.PySideUic.loadUi(
            self.Path + "/CreateGuideLinesGroup.ui")

        # TODO List
        self.IPFui.CreateB.clicked.connect(self.CreateGuideLines)
        self.IPFui.CancelB.clicked.connect(self.IPFui.close)
        self.IPFui.AddGLGroupB.clicked.connect(self.LoadCGLGui)
        self.CPGui.OkB.clicked.connect(self.CreateNewGroup)
        self.CPGui.CancelB.clicked.connect(self.CPGui.close)
        self.IPFui.AlignmentCB.currentIndexChanged.connect(
            self.ListGuideLinesGroups)
        self.IPFui.FromAlgStartChB.stateChanged.connect(self.ActivateStations)
        self.IPFui.ToAlgEndChB.stateChanged.connect(self.ActivateStations)

    def GetResources(self):
        # Return the command resources dictionary
        return self.resources

    def IsActive(self):
        """
        Define tool button activation situation
        """
        # Check for document
        if FreeCAD.ActiveDocument:
            return True
        return False

    def Activated(self):
        Alignments = FreeCAD.ActiveDocument.getObject('Alignments')
        AlignmentGroup = FreeCAD.ActiveDocument.getObject('AlignmentGroup')
        if Alignments: alignment_group = Alignments
        elif AlignmentGroup: alignment_group = AlignmentGroup
        else:
            alignment_group = FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'AlignmentGroup')
            alignment_group.Label = "Alignment Group"

        GuideLineGroup = FreeCAD.ActiveDocument.getObject('GuideLines')
        if not GuideLineGroup:
            GuideLineGroup = FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'GuideLines')
            GuideLineGroup.Label = "Guide Lines"

        alignment_group.addObject(GuideLineGroup)

        self.IPFui.setParent(FreeCADGui.getMainWindow())
        self.IPFui.setWindowFlags(QtCore.Qt.Window)
        self.IPFui.show()

        # List Alignments
        self.IPFui.AlignmentCB.clear()
        self.alignment_list = []

        for Object in alignment_group.Group:
            if Object.TypeId == 'Part::Part2DObjectPython':
                self.alignment_list.append(Object.Name)
                self.IPFui.AlignmentCB.addItem(Object.Label)

        # Check that the Alignments Group has Wire objects
        if len(self.alignment_list) == 0:
            FreeCAD.Console.PrintMessage(
                "Please add a Wire Object to the Alignment Group")
            return

        self.ListGuideLinesGroups()

    def getAlignmentInfos(self):
        alignment_index = self.IPFui.AlignmentCB.currentIndex()

        if alignment_index < 0:
            FreeCAD.Console.PrintMessage(
                "Please add a Alignment object to the Alignment Group")
            return None, 0.0, 0.0

        alignment_name = self.alignment_list[alignment_index]

        Alignment = FreeCAD.ActiveDocument.getObject(alignment_name)
        if hasattr(Alignment.Proxy, 'model'):
            Start = Alignment.Proxy.model.data['meta']['StartStation']
            Length = Alignment.Proxy.model.data['meta']['Length']
            End = Start + Length/1000
        else:
            Start = 0.0
            Length = Alignment.Length.Value
            End = Start + Length/1000

        return Alignment, Start, End

    def ListGuideLinesGroups(self):

        # List Guide Lines Groups.
        self.IPFui.GLGroupCB.clear()
        GuideLines_group = FreeCAD.ActiveDocument.GuideLines.Group
        self.GLGList = []

        for Object in GuideLines_group:
            if Object.TypeId == 'App::DocumentObjectGroup':
                self.GLGList.append(Object.Name)
                self.IPFui.GLGroupCB.addItem(Object.Label)

        Alignment, Start, End = self.getAlignmentInfos()

        self.IPFui.StartStationLE.setText(str(round(Start, 3)))
        self.IPFui.EndStationLE.setText(str(round(End, 3)))

    def LoadCGLGui(self):

        # Load Create Guide Lines Group UI
        self.CPGui.setParent(self.IPFui)
        self.CPGui.setWindowFlags(QtCore.Qt.Window)
        self.CPGui.show()

    def CreateNewGroup(self):
        # Create new guide lines group
        NewGroupName = self.CPGui.GuideLinesGroupNameLE.text()
        NewGroup = FreeCAD.ActiveDocument.addObject(
            "App::DocumentObjectGroup", NewGroupName)
        NewGroup.Label = NewGroupName
        FreeCAD.ActiveDocument.GuideLines.addObject(NewGroup)
        self.IPFui.GLGroupCB.addItem(NewGroupName)
        self.GLGList.append(NewGroup.Name)
        NewGroup.Label = NewGroupName
        self.CPGui.close()

    def ActivateStations(self):
        # When QCheckBox status changed do the following options
        Alignment, Start, End = self.getAlignmentInfos()
        if self.IPFui.FromAlgStartChB.isChecked():
            self.IPFui.StartStationLE.setEnabled(False)
            self.IPFui.StartStationLE.setText(str(round(Start, 3)))
        else:
            self.IPFui.StartStationLE.setEnabled(True)

        if self.IPFui.ToAlgEndChB.isChecked():
            self.IPFui.EndStationLE.setEnabled(False)
            self.IPFui.EndStationLE.setText(str(round(End, 3)))
        else:
            self.IPFui.EndStationLE.setEnabled(True)

    def GetOrthoVector(self, line, distance, side=''):
        """
        Return the orthogonal vector pointing toward the indicated side at the
        provided position.  Defaults to left-hand side
        """

        _dir = 1.0

        _side = side.lower()

        if _side in ['r', 'rt', 'right']:
            _dir = -1.0

        start = line.Start
        end = line.End

        if (start is None) or (end is None):
            return None, None

        _delta = end.sub(start).normalize()
        _left = Vector(-_delta.y, _delta.x, 0.0)

        _coord = start.add(_delta.multiply(distance*1000))

        return _coord, _left.multiply(_dir)

    def CreateGuideLines(self):
        """
        Generates guidelines along a selected alignment
        """

        #get left and right offsets from centerline
        l = self.IPFui.LeftLengthLE.text()
        r = self.IPFui.RightLengthLE.text()

        #station limits
        FirstStation = self.IPFui.StartStationLE.text()
        LastStation = self.IPFui.EndStationLE.text()

        #target group
        glg_index = self.IPFui.GLGroupCB.currentIndex()

        if glg_index < 0:
            FreeCAD.Console.PrintMessage(
                "Please add a Guide Line Group")
            return

        GLGIndexName = self.GLGList[glg_index]

        #guideline intervals
        TangentIncrement = self.IPFui.TIncrementLE.text()
        CurveSpiralIncrement = self.IPFui.CSIncrementLE.text()

        #retrieve alignment data
        Alignment, Start, End = self.getAlignmentInfos()

        if Alignment is None :
            FreeCAD.Console.PrintMessage(
                "Please add a Alignment object to the Alignment Group")
            return

        #get 3D coordinate dataset and placement
        Stations = []
        if hasattr(Alignment.Proxy, 'model'):
            AlgPl = Alignment.Placement.Base
            Geometry = Alignment.Proxy.model.data['geometry']

            for Geo in Geometry:
                #compute starting and ending stations based on alignment
                StartStation = Geo.get('StartStation')
                EndStation = Geo.get('StartStation')+Geo.get('Length')/1000

                if StartStation != 0:
                    if self.IPFui.HorGeoPointsChB.isChecked():
                        Stations.append(StartStation)

                #generate line intervals
                if Geo.get('Type') == 'Line':

                    #Iterate the station range, rounding to the nearest whole
                    for i in range(
                        round(float(StartStation)), round(float(EndStation))):

                        #add stations which land on increments exactly
                        if i % int(TangentIncrement) == 0:
                            Stations.append(i)

                #generate curve intervals
                elif Geo.get('Type') == 'Curve' or Geo["Type"] == 'Spiral':

                    for i in range(round(float(StartStation)), round(float(EndStation))):
                        if i % int(CurveSpiralIncrement) == 0:
                            Stations.append(i)

        else:
            StartStation = Start
            EndStation = End
            AlgPl = FreeCAD.Vector(0, 0, 0)
            if StartStation != 0:
                if self.IPFui.HorGeoPointsChB.isChecked():
                    Stations.append(StartStation)

            for i in range(int(float(StartStation)), int(float(EndStation))):
                if i % int(TangentIncrement) == 0:
                    Stations.append(i)

        #add the end station, rounded to the nearest three decimals
        Stations.append(round(End,3))

        Result = []

        #iterate the stations, appending what falls in the specified limits
        for Station in Stations:

            if float(FirstStation) <= Station <= float(LastStation):
                Result.append(Station)

        Result.sort()

        #iterate the final list of stations,
        #computing coordinates and orthoginals for guidelines
        for Station in Result:
            if hasattr(Alignment.Proxy, 'model'):
                Coord, vec = Alignment.Proxy.model.get_orthogonal( Station, "Left")
            else:
                Coord, vec = self.GetOrthoVector(Alignment, Station, "Left")

            LeftEnd = Coord.add(FreeCAD.Vector(vec).multiply(int(l)*1000))
            RightEnd = Coord.add(vec.negative().multiply(int(r)*1000))

            #generate guide line object and add to document
            GuideLine = Draft.makeWire([LeftEnd, Coord, RightEnd])
            GuideLine.Placement.Base = AlgPl
            GuideLine.Label = str(round(Station, 3))

            FreeCAD.ActiveDocument.getObject(GLGIndexName).addObject(GuideLine)
            FreeCAD.ActiveDocument.recompute()

FreeCADGui.addCommand('Create Guide Lines', CreateGuideLines())
