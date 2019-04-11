# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2018 Joel Graff <monograff76@gmail.com>                 *
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
Cell feature generates a 3D cell, consisting of a sketch swept along a baseline
"""
__title__ = "Cell.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import FreeCAD as App
import Draft
import Part
import transportationwb
import math
import Corridor.qt_dialog as qtd

OBJECT_TYPE = "Cell"

if App.Gui:
    import FreeCADGui as Gui
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

class _CommandCell:
    """
    The Corridor Cell command definition
    """
    def GetResources(self):
        return {'Pixmap'  : '../../icons/new_alignment.svg',
                'MenuText': QT_TRANSLATE_NOOP("Corridor_Cell", "Cell"),
                'Accel'   : "C, A",
                'ToolTip' : QT_TRANSLATE_NOOP("Corridor_Cell",
                "Creates a new cell object using a selected objects")
                }

    def IsActive(self):
        return not App.ActiveDocument is None

    def Activated(self):
        pass

def destroyCell(cell_name):
    """
    Destroys the specified cell
    """

    cel = App.ActiveDocument.getObject(cell_name)

    if cel is None:
        return

    for obj in cel.Group:
        App.ActiveDocument.removeObject(obj.Name)

    App.ActiveDocument.removeObject(cell_name)

    App.ActiveDocument.recompute()

def createCell(names, data):
    """
    Creates the cell object structure and
    builds the initial cell
    """

    template = App.ActiveDocument.getObject(names["sketch"])
    sweep_object = App.ActiveDocument.getObject(names["edge_obj"])

    if template is None:
        print("No valid template sketch selected")
        return None

    if sweep_object is None:
        print("No valid sweep object selected")
        return None

    fpo = App.ActiveDocument.addObject("PartDesign::FeaturePython", names["cell"] + "_Parameters")

    cel = _Cell(fpo)

    _ViewProviderCell(fpo.ViewObject)

    #create the body object and add this FPO as a child
    body = cel.createBody(names["cell"])

    #set initial property links
    cel.setPath(sweep_object)
    cel.setTemplate(template)
    cel.Object.Source_Edge = names["edge"]

    cel.Object.Start_Station = data["start"]
    cel.Object.End_Station = data["end"]
    cel.Object.Resolution = data["resolution"]

    print(data["start"], data["end"], data["resolution"])
    body.recompute()
    App.ActiveDocument.recompute()

    return body

def showSweepPicker():
    """
    Displays the non-modal dialog for cell creation
    """

    picker = qtd.SweepPicker(App.ActiveDocument)
    picker.createCallback = createCell
    picker.destroyCallback = destroyCell

class _Cell():

    def __init__(self, obj):
        """
        Default Constructor
        """
        obj.Proxy = self
        self.Type = OBJECT_TYPE + "_Parameters"
        self.Object = obj

        self.add_property("App::PropertyLength", "Start_Station", "Starting station for the cell", "Parameters").Start_Station = 0.00
        self.add_property("App::PropertyLength", "End_Station", "Ending station for the cell", "Parameters").End_Station = 0.00
        self.add_property("App::PropertyLength", "Resolution", "Resolution of sweep paths", "Parameters").Resolution = 0.00
        self.add_property("App::PropertyLength", "Length", "Length of cell along baseline", "Parameters", True).Length = 0.00
        self.add_property("App::PropertyLink", "Source_Path", "Source object for sweep path", "Links", True).Source_Path = None
        self.add_property("App::PropertyString", "Source_Edge", "Edge name", "Links", True).Source_Edge = ""
        self.add_property("App::PropertyLink", "Sweep_Path", "Sweep path for the cell sweep", "Links", True).Sweep_Path = None
        self.add_property("App::PropertyLink", "Template", "Template geometry for the sweep", "Links", True).Template = None
        self.add_property("App::PropertyLink", "Sweep", "Sweep geometry", "Links", True).Sweep = None

        self.init = True

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    @staticmethod
    def _copy_sketch(doc, sketch, target_name, empty_copy = False):
        """
        Copy sketch as a new SketchObjectPython
        doc - document object which receives the sketch
        sketch - the sketch object to copy
        target_name - string representing the name of the new sketch
        empty_copy - 
            True = create an empty sketch (only placement is duplicated)
            False = create a full copy of the original sketch
        """
        doc = App.ActiveDocument

        target = doc.addObject('Sketcher::SketchObject', target_name)

        #_ViewProvider(target.ViewObject)

        if not empty_copy:

            for geo in sketch.Geometry:
                index = target.addGeometry(geo)
                target.setConstruction(index, geo.Construction)

            for constraint in sketch.Constraints:
                target.addConstraint(constraint)

        target.Placement = sketch.Placement

        target.solve()
        target.recompute()

        return target

    def _update_length(self):
        """
        Sets the length of the cell path based on the starting and ending station properties
        """

        new_length = self.Object.End_Station - self.Object.Start_Station

        if new_length < 0.0:
            new_length = 0.0

        if self.Object.Length == new_length:
            return False

        self.Object.Length = new_length

        return True

    def _delete_objects(self):
        """
        Deletes existing cell objects in preparation for a rebuild
        """

        sweep_obj = self.Object.Sweep
        path_obj = self.Object.Sweep_Path

        if not sweep_obj is None:
            App.ActiveDocument.removeObject(sweep_obj.Name)

        if not path_obj is None:
            App.ActiveDocument.removeObject(path_obj.Name)

        return

    @staticmethod
    def _discretize_edge(edge, start_pt = 0.0, end_pt = 0.0, number = 3):
        """
        Discretizes an edge, returning two points for a line and three points for an arc
        """

        segmentize = start_pt <= 0.0 and end_pt <= 0.0
        points = []

        if not segmentize:

            if start_pt <= 0.0:
                start_pt = 0.0

            if end_pt <= 0.0:
                end_pt = edge.Length


        if isinstance(edge.Curve, Part.Line):

            if segmentize:
                points = [edge.Vertexes[0].Point, edge.Vertexes[1].Point]

            else:
                tmp = edge.discretize(Distance=(end_pt - start_pt))
                points = [tmp[0], tmp[1]]

        else:

            if segmentize:
                points = edge.discretize(3)

            else:
                start_prm = edge.Curve.parameterAtDistance(start_pt, edge.FirstParameter)
                end_prm = edge.Curve.parameterAtDistance(end_pt, edge.FirstParameter)

                points.extend(edge.discretize(Number=int(number), First=start_prm, Last=end_prm))

        return points

    @staticmethod
    def _get_edge_points(stations, spline, resolution):
        """
        USED
        Returns a list of point sublists which describe the final sweep path
        stations - list of starting and ending stations
        geometry - list of geometry elements which form a continuous path and
                   whose list order and vertices are sorted from beginning to end
        """
        length = stations[1] - stations[0]

        #if no resolution is defined, provide a minimum
        if resolution == 0.0:
            resolution = length / 3.0

        point_count = math.ceil(length / resolution)

        pts = _Cell._discretize_edge(number=point_count, start_pt=stations[0], end_pt=stations[1], edge=spline)

        return pts

    @staticmethod
    def _build_sweep(body, template, path):
        """
        Sweep the provided template along the provided path
        """

        template.MapMode = "NormalToEdge"
        template.Support = (path, ["Edge1"])

        add_pipe = body.getObject("Sweep")

        if not add_pipe is None:
            body.removeObject(add_pipe)

        add_pipe = body.newObject("PartDesign::AdditivePipe", "Sweep")

        add_pipe.Profile = template
        add_pipe.Spine = (path, ['Edge1'])
        add_pipe.Sections = template

        return add_pipe

    @staticmethod
    def _build_sweep_spline(points):
        """
        Build a spline for the sweep path based on the passed points
        """

        obj_type = "BSpline"

        pt_count = len(points)

        if pt_count < 2:
            return None

        elif len(points) == 2: 
            obj_type = "Line"

        obj = App.ActiveDocument.addObject("Part::Part2DObjectPython", obj_type)

        Draft._BSpline(obj)

        obj.Closed = False
        obj.Points = points
        obj.Support = None
        obj.Label = "SweepPath"

        Draft._ViewProviderWire(obj.ViewObject)

        return obj

    def add_property(self, prop_type, prop_name, prop_desc, group_name=OBJECT_TYPE, isReadOnly=False):

        prop = self.Object.addProperty(prop_type, prop_name, group_name, QT_TRANSLATE_NOOP("App::Property", prop_desc))

        if isReadOnly:
            prop.setEditorMode(prop_name, 1)

        return prop

    def createBody(self, cell_name):

        body = App.ActiveDocument.addObject("PartDesign::Body", cell_name)

        body.addObject(self.Object)

        Gui.activeView().setActiveObject('pdbody', body)

        return body

    def setPath(self, source_path):

        self.Object.Source_Path = source_path
        self.Object.End_Station = source_path.Shape.Length
    
    def setTemplate(self, template):

        cpy_temp = self._copy_sketch(App.ActiveDocument, template, "Template")

        self.Object.Template = cpy_temp
        self.Object.InList[0].addObject(cpy_temp)

    def onChanged(self, obj, prop):

        #dodge onChanged calls during initialization
        if not hasattr(self, 'init'):
            return

        if not hasattr(self, "Object"):
            self.Object = obj

        if prop=="Resolution":

            #change the length so it doesn't skip the next execution loop
            self.Object.Length.Value = self.Object.Length.Value + 1.0

    def execute(self, fpy):
        print("Executing...")

        if not self._update_length():
            return

        stations = [self.Object.Start_Station.Value, self.Object.End_Station.Value]

        self._delete_objects()

        points = self._get_edge_points(stations,
        self.Object.Source_Path.Shape.getElement(self.Object.Source_Edge),
        float(self.Object.Resolution.Value))

        spline = self._build_sweep_spline(points)

        if spline is None:
            return

        self.Object.InList[0].addObject(spline)
        self.Object.Sweep_Path = spline

        self.Object.Sweep = self._build_sweep(self.Object.InList[0], self.Object.Template, spline)

        return

    def removeObject(self, child):

        if hasattr(self, "Object"):
            grp = self.Object.Group

            if child in grp:
                grp.remove(child)
                self.Object.Group = grp

class _ViewProviderCell:

    def __init__(self, obj):
        """
        Initialize the view provider
        """
        obj.Proxy = self

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def attach(self, obj):
        """
        View provider scene graph initialization
        """
        self.Object = obj.Object

    def claimChildren(self):

        #if hasattr(self, "Object"):
        #    if self.Object:
        #        return self.Object.Group
        return []

    def updateData(self, fp, prop):
        """
        Property update handler
        """
        pass

    def getDisplayMode(self, obj):
        """
        Valid display modes
        """
        return ["Wireframe"]

    def getDefaultDisplayMode(self):
        """
        Return default display mode
        """
        return "Wireframe"

    def setDisplayMode(self, mode):
        """
        Set mode - wireframe only
        """
        return "Wireframe"

    def onChanged(self, vp, prop):
        """
        Handle individual property changes
        """
        pass

    def getIcon(self):
        return """

/* XPM */
static char * new_cell_xpm[] = {
"64 64 213 2",
"  	c None",
". 	c #000000",
"+ 	c #090909",
"@ 	c #373836",
"# 	c #333432",
"$ 	c #040404",
"% 	c #4B4C4A",
"& 	c #E4E5E3",
"* 	c #D8D9D5",
"= 	c #BABDB6",
"- 	c #9EA19B",
"; 	c #161615",
"> 	c #EFF0EF",
", 	c #FFFFFF",
"' 	c #C3C6C0",
") 	c #7E807B",
"! 	c #999A98",
"~ 	c #FBFBFA",
"{ 	c #BEC0BA",
"] 	c #A8ABA5",
"^ 	c #181918",
"/ 	c #F8F8F7",
"( 	c #D9DBD7",
"_ 	c #92948F",
": 	c #B9BAB8",
"< 	c #F6F6F6",
"[ 	c #BCBFB8",
"} 	c #3E3F3D",
"| 	c #373736",
"1 	c #FDFDFD",
"2 	c #D1D3CE",
"3 	c #90938D",
"4 	c #010101",
"5 	c #D4D4D2",
"6 	c #F0F1EF",
"7 	c #B9BCB5",
"8 	c #272726",
"9 	c #5B5C5A",
"0 	c #CACCC7",
"a 	c #767874",
"b 	c #030303",
"c 	c #E8E9E7",
"d 	c #E8E9E6",
"e 	c #B3B6B0",
"f 	c #919291",
"g 	c #5D5F5B",
"h 	c #1C1C1C",
"i 	c #F7F7F7",
"j 	c #DDDFDB",
"k 	c #A7AAA3",
"l 	c #080808",
"m 	c #BFC0BE",
"n 	c #F7F8F7",
"o 	c #BDC0B9",
"p 	c #434442",
"q 	c #454544",
"r 	c #D2D4CF",
"s 	c #8F918C",
"t 	c #E0E0DE",
"u 	c #EFF0EE",
"v 	c #B8BBB4",
"w 	c #232422",
"x 	c #888987",
"y 	c #FEFEFE",
"z 	c #C8CAC5",
"A 	c #6C6E6A",
"B 	c #282827",
"C 	c #F8F8F8",
"D 	c #E3E4E1",
"E 	c #ADB0A9",
"F 	c #0E0E0E",
"G 	c #D5D5D4",
"H 	c #BEC1BB",
"I 	c #4A4B48",
"J 	c #80817F",
"K 	c #CED0CB",
"L 	c #93958F",
"M 	c #222221",
"N 	c #E5E6E4",
"O 	c #B5B8B1",
"P 	c #20211F",
"Q 	c #D4D4D3",
"R 	c #F8F9F8",
"S 	c #BFC1BB",
"T 	c #585A56",
"U 	c #9B9D9A",
"V 	c #D0D2CD",
"W 	c #969993",
"X 	c #595959",
"Y 	c #F3F3F2",
"Z 	c #595A57",
"` 	c #2C2C2C",
" .	c #F1F1F0",
"..	c #FAFAFA",
"+.	c #C4C7C1",
"@.	c #90928D",
"#.	c #424241",
"$.	c #F4F4F4",
"%.	c #CACDC7",
"&.	c #AAADA6",
"*.	c #141413",
"=.	c #020202",
"-.	c #919190",
";.	c #FCFCFC",
">.	c #B7BAB3",
",.	c #313230",
"'.	c #151515",
").	c #868786",
"!.	c #EDEDEC",
"~.	c #FBFCFB",
"{.	c #CCCEC9",
"].	c #494A47",
"^.	c #2E2E2E",
"/.	c #646463",
"(.	c #8D8D8C",
"_.	c #AAAAA9",
":.	c #B0B0AE",
"<.	c #BABBB9",
"[.	c #BCBDBB",
"}.	c #BDBEBC",
"|.	c #CACAC8",
"1.	c #EBEBEA",
"2.	c #F2F3F2",
"3.	c #C6C8C2",
"4.	c #313131",
"5.	c #B8B8B7",
"6.	c #FBFBFB",
"7.	c #DCDDDA",
"8.	c #0F0F0F",
"9.	c #B6B7B5",
"0.	c #D8DAD6",
"a.	c #B4B7B0",
"b.	c #474946",
"c.	c #2A2B2A",
"d.	c #EBECEB",
"e.	c #E6E7E5",
"f.	c #DFE0DD",
"g.	c #DBDDD9",
"h.	c #DADCD8",
"i.	c #D6D8D3",
"j.	c #D3D5D0",
"k.	c #9A9C97",
"l.	c #2D2D2C",
"m.	c #EDEEEC",
"n.	c #CDCFCA",
"o.	c #BBBEB7",
"p.	c #A8AAA4",
"q.	c #4E4F4C",
"r.	c #141414",
"s.	c #E9E9E8",
"t.	c #A9ACA6",
"u.	c #7D7F7A",
"v.	c #3C3D3B",
"w.	c #050505",
"x.	c #C5C6C4",
"y.	c #CFD1CC",
"z.	c #757773",
"A.	c #5E605C",
"B.	c #4F504D",
"C.	c #4A4C49",
"D.	c #484947",
"E.	c #2C2C2B",
"F.	c #6F6F6E",
"G.	c #7B7D79",
"H.	c #1B1B1A",
"I.	c #090A09",
"J.	c #ECECEB",
"K.	c #ECEDEB",
"L.	c #555754",
"M.	c #919290",
"N.	c #C2C5BF",
"O.	c #676965",
"P.	c #131413",
"Q.	c #979994",
"R.	c #A7A9A6",
"S.	c #FAFBFA",
"T.	c #292A28",
"U.	c #131313",
"V.	c #F5F5F4",
"W.	c #949592",
"X.	c #F9FAF9",
"Y.	c #BCBFB9",
"Z.	c #1F1F1E",
"`.	c #ECEDEC",
" +	c #DCDEDA",
".+	c #757772",
"++	c #727371",
"@+	c #C0C3BD",
"#+	c #DDDEDC",
"$+	c #E3E4E2",
"%+	c #898B86",
"&+	c #3D3E3C",
"*+	c #C5C7C1",
"=+	c #B8B9B8",
"-+	c #A0A29C",
";+	c #0C0C0C",
">+	c #858684",
",+	c #B6B9B2",
"'+	c #111110",
")+	c #DCDCDB",
"!+	c #DDDEDB",
"~+	c #7D7F7B",
"{+	c #DFE0DE",
"]+	c #FDFDFC",
"^+	c #C1C4BD",
"/+	c #353533",
"(+	c #70726E",
"_+	c #D9DAD6",
":+	c #C9CBC6",
"<+	c #838580",
"[+	c #A3A59F",
"}+	c #222322",
"|+	c #1A1A19",
"                                                                                                                                ",
"                                                                                                                                ",
"                                                                                                            . . . .             ",
"                                                                                                        . . . . . . . .         ",
"                                                                                                      . . . . . . . . . .       ",
"                                                                                                    . . . . + @ # $ . . . .     ",
"                                                                                                    . . . % & * = - ; . . .     ",
"                                                                                                  . . . + > , , ' = ) . . .     ",
"                                                                                                . . . . ! , , ~ { = ] . . . .   ",
"                                                                                                . . . ^ / , , ( = = _ . . . .   ",
"                                                                                              . . . . : , , < [ = = } . . .     ",
"                                                                                              . . . | 1 , , 2 = = 3 4 . . .     ",
"                                                                                            . . . . 5 , , 6 = = 7 8 . . .       ",
"                                                                                            . . . 9 , , , 0 = = a . . . .       ",
"                                                                                          . . . b c , , d = = e ; . . .         ",
"                                                                                        . . . . f , , 1 ' = = g . . . .         ",
"                                                                                        . . . h i , , j = = k l . . .           ",
"                                                                                      . . . . m , , n o = = p . . . .           ",
"                                                                                      . . . q 1 , , r = = s 4 . . .             ",
"                                                                                    . . . 4 t , , u = = v w . . .               ",
"                                                                                  . . . . x , , y z = = A . . . .               ",
"                                                                                  . . . B C , , D = = E F . . .                 ",
"                                                                                . . . 4 G , , / H = = I . . . .                 ",
"                                                                              . . . . J , , , K = = L 4 . . .                   ",
"                                                                              . . . M < , , N = = O P . . .                     ",
"                                                                            . . . 4 Q , , R S = = T . . . .                     ",
"                                                                          . . . . U , , , V = = W $ . . .                       ",
"                                                                        . . . . X 1 , , & = = O P . . . .                       ",
"                                                                      . . . . | i , , Y o = = Z . . . .                         ",
"                                                                  . . . . . `  ., , ..+.= = @.b . . .                           ",
"                                          . . . . . . . . . . . . . . . . #.$., , 1 %.= = &.*.. . . .                           ",
"                                    . . . . . . . . . . . . . . . . . =.-.;., , 1 V = = >.,.. . . .                             ",
"                                  . . . . . . . . . . . . . . . . '.).!., , , ~.{.= = = ].. . . .                               ",
"                              . . . . . . . ^./.(._.:.<.[.}.|.Q 1.y , , , , 2.3.= = = g . . . .                                 ",
"                            . . . . . 4.5.Y , , , , , , , , , , , , , , 6.7.[ = = 7 Z . . . .                                   ",
"                          . . . . 8.9.y , , , , , , , , , , , , , y  .0.S = = = a.b.. . . . .                                   ",
"                        . . . . c.d., , , , 6.u e.f.f.g.h.h.i.j.0 o = = = = = k.M . . . . .                                     ",
"                      . . . . l.2., , , m.n.o.= = = = = = = = = = = = = = p.q.$ . . . . .                                       ",
"                      . . . r.s., , y i.= = = = = = = = = = = = = = t.u.v.w.. . . . .                                           ",
"                    . . . . x., , y y.= = = 7 W z.A.B.C.C.D.} } E.; . . . . . . . .                                             ",
"                    . . . F.y , , 0.= = = G.H.. . . . . . . . . . . . . . . . .                                                 ",
"                  . . . I.J., , K.= = = L.. . . . . . . . . . . . . . . . .                                                     ",
"                . . . . M., , 1 N.= = O.. . . . . . . . . . . . . . .                                                           ",
"                . . . P.2., , f.= = Q.$ . . . .                                                                                 ",
"              . . . . R., , S.S = 7 T.. . . .                                                                                   ",
"              . . . U.V., , ( = = ) . . . .                                                                                     ",
"              . . . W., , X.Y.= v Z.. . .                                                                                       ",
"            . . . w.`., ,  += = .+. . . .                                                                                       ",
"            . . . ++, , 1 @+= = M . . .                                                                                         ",
"          . . . . #+, , $+= = %+. . . .                                                                                         ",
"          . . . &+y , , *+= = @ . . .                                                                                           ",
"          . . . =+, , K.= = -+4 . . .                                                                                           ",
"        . . . ;+i , , V = = L.. . .                                                                                             ",
"        . . . >+, , R o.= ,+'+. . .                                                                                             ",
"        . . . )+, , !+= = ~+. . . .                                                                                             ",
"        . . . {+, ]+^+= = /+. . .                                                                                               ",
"        . . . (+_+:+= = - 4 . . .                                                                                               ",
"        . . . l <+= = [+}+. . .                                                                                                 ",
"        . . . . . |+}+$ . . . .                                                                                                 ",
"          . . . . . . . . . .                                                                                                   ",
"            . . . . . . . .                                                                                                     ",
"                . . . .                                                                                                         ",
"                                                                                                                                ",
"                                                                                                                                "};
"""
if App.GuiUp:
    Gui.addCommand(OBJECT_TYPE, _CommandCell())
