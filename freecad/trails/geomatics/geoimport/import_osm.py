# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2016 microelly <>                                       *
# *  Copyright (c) 2020 Bernd Hahnebach <bernd@bimstatik.org               *
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
Import data from OpenStreetMap
"""

import os
import time
import urllib.request

import FreeCAD
import FreeCADGui
import Part

from . import inventortools
from . import my_xmlparser
from . import transversmercator

from .get_elevation import getHeight as get_height_single
from .get_elevation import getHeights as get_height_list
from .say import say
from .say import sayErr
from .say import sayexc
# from .say import sayW


# TODO: test run osm import method in on non gui
debug = False


def import_osm2(b, l, bk, progressbar=False, status=False, elevation=False):

    bk = 0.5 * bk
    if elevation:
        say("get height for {}, {}".format(b, l))
        baseheight = get_height_single(b, l)
        say("baseheight: {}".format(baseheight))
    else:
        baseheight = 0.0

    say("The importer of trails is used to import osm data.")
    say("This one does support elevations.")
    say(b, l, bk, progressbar, status, elevation)

    # *************************************************************************
    # get and parse osm data
    if progressbar and FreeCAD.GuiUp:
        progressbar.setValue(0)
    if status and FreeCAD.GuiUp:
        status.setText(
            "get data from openstreetmap.org and parse it for later usage ..."
        )
        FreeCADGui.updateGui()
    tree = get_osmdata(b, l, bk)
    if tree is None:
        sayErr("Something went wrong on retrieving OSM data.")
        return False

    # say("nodes")
    # for element in tree.getiterator("node"):
    #     say(element.params)
    # say("ways")
    # for element in tree.getiterator("way"):
    #     say(element.params)
    # say("relations")
    # for element in tree.getiterator("relation"):
    #     say(element.params)

    # *************************************************************************
    if status and FreeCAD.GuiUp:
        status.setText("transform data ...")
        FreeCADGui.updateGui()

    # relations = tree.getiterator("relation")
    nodes = tree.getiterator("node")
    ways = tree.getiterator("way")
    bounds = tree.getiterator("bounds")[0]

    # get base area size and map nodes data to the area on coordinate origin
    tm, size, corner_min, points, nodesbyid = map_data(nodes, bounds)
    # say(tm)
    # say(size)
    # say(corner_min)
    # say(len(points))
    # say(len(nodesbyid))

    # *************************************************************************
    if status and FreeCAD.GuiUp:
        status.setText("create visualizations  ...")
        FreeCADGui.updateGui()

    # new document
    # TODO, if a document exists or was passed use this one
    # it makes sense to use the doc as return value
    doc = FreeCAD.newDocument("OSM Map")
    say("New FreeCAD document created.")

    # base area
    area = doc.addObject("Part::Plane", "area")
    area.Length = size[0] * 2
    area.Width = size[1] * 2
    placement_for_area = FreeCAD.Placement(
        FreeCAD.Vector(-size[0], -size[1], 0.00),
        FreeCAD.Rotation(0.00, 0.00, 0.00, 1.00)
    )
    area.Placement = placement_for_area
    if FreeCAD.GuiUp:
        # set camera
        set_cam(area, bk)
        area.ViewObject.Document.activeView().viewAxonometric()
        FreeCADGui.updateGui()
    say("Base area created.")

    # *************************************************************************
    # ways
    say("Ways")
    wn = -1
    count_ways = len(ways)
    starttime = time.time()
    refresh = 1000

    for way in ways:
        wid = way.params["id"]
        wn += 1

        # say(way.params)
        # say("way content")
        # for c in way.content:
        #     say(c)
        # for debugging, break after some of the ways have been processed
        # if wn == 6:
        #     say("Waycount restricted to {} by dev".format(wn - 1))
        #     break

        nowtime = time.time()
        # if wn != 0 and (nowtime - starttime) / wn > 0.5:  # had problems
        if wn != 0:
            say(
                "way ---- # {}/{} time per house: {}"
                .format(wn, count_ways, round((nowtime-starttime)/wn, 2))
            )

        if progressbar:
            progressbar.setValue(int(0 + 100.0 * wn / count_ways))

        # get a name for the way
        name, way_type, nr, building_height = get_way_information(way)

        # generate way polygon points
        say("get nodes", way)
        polygon_points = []
        if not elevation:
            for n in way.getiterator("nd"):
                wpt = points[str(n.params["ref"])]
                # say(wpt)
                polygon_points.append(wpt)
        else:
            # get heights for lat lon way polygon points
            say("get heights for " + str(len(llpoints)))
            heights = get_height_list(llpoints)
            for n in w.getiterator("nd"):
                wpt = points[str(n.params["ref"])]
                if building and elevation:
                    if not height:
                        try:
                            key_for_height = m.params["lat"]+" "+m.params["lon"]
                            height = heights[key_for_height] * 1000 - baseheight
                        except Exception:
                            sayErr(
                                "---no height available for {} {}"
                                .format(m.params["lat"], m.params["lon"])
                            )
                            height = 0
                    wpt.z = height
                polygon_points.append(wpt)

        # create document object out of the way polygon points
        # for p in polygon_points:
        #    say(p)

        # a wire for each way polygon
        polygon_shape = Part.makePolygon(polygon_points)
        polygon_obj = doc.addObject("Part::Feature", "w_" + wid)
        polygon_obj.Shape = polygon_shape
        # polygon_obj.Label = "w_" + wid

        if name == " ":
            g = doc.addObject("Part::Extrusion", name)
            g.Base = polygon_obj
            g.ViewObject.ShapeColor = (1.0, 1.0, 0.0)
            g.Dir = (0, 0, 10)
            g.Solid = True
            g.Label = "way ex "

        if way_type == "building":
            g = doc.addObject("Part::Extrusion", name)
            g.Base = polygon_obj
            g.ViewObject.ShapeColor = (1.0, 1.0, 1.0)
            if building_height == 0:
                building_height = 10000
            g.Dir = (0, 0, building_height)
            g.Solid = True
            g.Label = name
            inventortools.setcolors2(g)  # what does this do?

        if way_type == "highway":
            g = doc.addObject("Part::Extrusion", "highway")
            g.Base = polygon_obj
            g.ViewObject.LineColor = (0.0, 0.0, 1.0)
            g.ViewObject.LineWidth = 10
            g.Dir = (0, 0, 0.2)
            g.Label = name

        if way_type == "landuse":
            g = doc.addObject("Part::Extrusion", name)
            g.Base = polygon_obj
            if nr == "residential":
                g.ViewObject.ShapeColor = (1.0, 0.6, 0.6)
            elif nr == "meadow":
                g.ViewObject.ShapeColor = (0.0, 1.0, 0.0)
            elif nr == "farmland":
                g.ViewObject.ShapeColor = (0.8, 0.8, 0.0)
            elif nr == "forest":
                g.ViewObject.ShapeColor = (1.0, 0.4, 0.4)
            g.Dir = (0, 0, 0.1)
            g.Label = name
            g.Solid = True


        refresh += 1
        if refresh > 3 and FreeCAD.GuiUp:
            FreeCADGui.updateGui()
            # FreeCADGui.SendMsgToActiveView("ViewFit")
            refresh = 0

    # *************************************************************************
    doc.recompute()
    if progressbar and FreeCAD.GuiUp:
        progressbar.setValue(100)
    if status and FreeCAD.GuiUp:
        status.setText("import finished.")
        FreeCADGui.updateGui()

    organize_doc(doc)
    doc.recompute()

    endtime = time.time()
    say(("running time ", int(endtime-starttime),  " count ways ", count_ways))

    return True


def organize_doc(doc):
    """
    Create groups for the different object types
    GRP_highways, GRP_building, GRP_landuse
    """
    highways = doc.addObject(
        "App::DocumentObjectGroup",
        "GRP_highways"
    )
    landuse = doc.addObject(
        "App::DocumentObjectGroup",
        "GRP_landuse"
    )
    buildings = doc.addObject(
        "App::DocumentObjectGroup",
        "GRP_building"
    )
    pathes = doc.addObject(
        "App::DocumentObjectGroup",
        "GRP_pathes"
    )

    for obj in doc.Objects:
        if obj.Label.startswith("building"):
            buildings.addObject(obj)
            # obj.ViewObject.Visibility=False
        if obj.Label.startswith("highway") or obj.Label.startswith("way"):
            highways.addObject(obj)
            # obj.ViewObject.Visibility = False
        if obj.Label.startswith("landuse"):
            landuse.addObject(obj)
            # obj.ViewObject.Visibility = False
        if obj.Label.startswith("w_"):
            pathes.addObject(obj)
            obj.ViewObject.Visibility = False


def map_data(nodes, bounds):
    # center of the scene
    minlat = float(bounds.params["minlat"])
    minlon = float(bounds.params["minlon"])
    maxlat = float(bounds.params["maxlat"])
    maxlon = float(bounds.params["maxlon"])
    # print(minlat)
    # print(minlon)
    # print(maxlat)
    # print(maxlon)

    tm = transversmercator.TransverseMercator()
    # print("Center vorh: {}".format(tm.fromGeographic(b,l)))
    tm.lat = 0.5 * (minlat + maxlat)
    tm.lon = 0.5 * (minlon + maxlon)
    # setting values changes the result, see transversmerctor module
    # print("Center nach: {}".format(center))

    center = tm.fromGeographic(tm.lat, tm.lon)
    coord_corner_min = tm.fromGeographic(minlat, minlon)
    coord_corner_max = tm.fromGeographic(maxlat, maxlon)
    # print("Corner lu: {}".format(coord_corner_min))
    # print("Corner ro: {}".format(coord_corner_max))
    corner_min = FreeCAD.Vector(
        coord_corner_min[0],
        coord_corner_min[1],
        0
    )
    corner_max = FreeCAD.Vector(
        coord_corner_max[0],
        coord_corner_max[1],
        0
    )
    print("Corner lu: {}".format(corner_min))
    print("Corner ro: {}".format(corner_max))
    size = [center[0] - corner_min[0], center[1] - corner_min[1]]

    # map all points to xy-plane
    points = {}
    nodesbyid = {}
    for n in nodes:
        nodesbyid[n.params["id"]] = n
        ll = tm.fromGeographic(
            float(n.params["lat"]),
            float(n.params["lon"])
        )
        points[str(n.params["id"])] = FreeCAD.Vector(
            ll[0] - center[0],
            ll[1] - center[1],
            0.0
        )

    return (tm, size, corner_min, points, nodesbyid)


def get_osmdata(b, l, bk):

    dn = os.path.join(FreeCAD.ConfigGet("UserAppData"), "geodat_osm")
    if not os.path.isdir(dn):
        os.makedirs(dn)
    fn = os.path.join(dn, "{}-{}-{}".format(b, l, bk))
    say("Local osm data file:")
    say("{}".format(fn))

    # TODO: do much less in try/except
    # use os for file existense etc.
    tree = None
    try:
        say("Try to read data from a former existing osm data file ... ")
        f = open(fn, "r")
        content = f.read()  # try to read it
        False if content else True  # get pylint and LGTM silent
        # really read fn before skipping new internet upload
        # because fn might be empty or does have wrong encoding
        tree = my_xmlparser.getData(fn)
    except Exception:
        say(
            "No former existing osm data file, "
            "connecting to openstreetmap.org ..."
        )
        lk = bk
        b1 = b - bk / 1113 * 10
        l1 = l - lk / 713 * 10
        b2 = b + bk / 1113 * 10
        l2 = l + lk / 713 * 10
        koord_str = "{},{},{},{}".format(l1, b1, l2, b2)
        source = "http://api.openstreetmap.org/api/0.6/map?bbox=" + koord_str
        say(source)

        response = urllib.request.urlopen(source)

        # the file we write into needs uft8 encoding
        f = open(fn, "w", encoding="utf-8")
        # decode makes a string out of the bytesstring
        f.write(response.read().decode("utf8"))
        f.close()

        # writing the file is only for later usage
        # thus may be first parse the data and afterwards write it ... ?
        tree = my_xmlparser.getData(fn)

    if tree is not None:
        return tree
    else:
        return None


def set_cam(area, bk):

    # does this makes a difference ?

    from pivy import coin
    try:
        root = area.ViewObject.RootNode
        myLight = coin.SoDirectionalLight()
        myLight.color.setValue(coin.SbColor(0, 1, 0))
        root.insertChild(myLight, 0)
        say("Lighting on base area activated.")
    except Exception:
        sayexc("Lighting 272")

    mycam = """#Inventor V2.1 ascii
    OrthographicCamera {
      viewportMapping ADJUST_CAMERA
      orientation 0 0 -1.0001  0.001
      nearDistance 0
      farDistance 10000000000
      aspectRatio 100
      focalDistance 1
    """
    x = 0
    y = 0
    cam_height = 200 * bk * 10000 / 0.6
    mycam += "\nposition " + str(x) + " " + str(y) + " 999\n "
    mycam += "\nheight " + str(cam_height) + "\n}\n\n"

    area.ViewObject.Document.activeView().setCamera(mycam)
    say("Camera was set.")


def get_way_information(w):
    st = ""
    st2 = ""
    nr = ""
    building_height = 0
    # ci is never used
    # ci = ""
    way_type = ""

    for t in w.getiterator("tag"):
        try:
            if debug:
                say(t)
                # say(t.params["k"])
                # say(t.params["v"])

            if str(t.params["k"]) == "building":
                way_type = "building"
                if st == "":
                    st = "building"

            if str(t.params["k"]) == "landuse":
                way_type = "landuse"
                st = t.params["k"]
                nr = t.params["v"]

            if str(t.params["k"]) == "highway":
                way_type = "highway"
                st = t.params["k"]

            if str(t.params["k"]) == "addr:city":
                pass
                # ci is never used
                # ci = t.params["v"]

            if str(t.params["k"]) == "name":
                nr = t.params["v"]

            if str(t.params["k"]) == "ref":
                nr = t.params["v"]+" /"

            if str(t.params["k"]) == "addr:street":
                st2 = " "+t.params["v"]

            if str(t.params["k"]) == "addr:housenumber":
                nr = str(t.params["v"])

            if str(t.params["k"]) == "building:levels":
                if building_height == 0:
                    building_height = int(str(t.params["v"]))*1000*3

            if str(t.params["k"]) == "building:height":
                building_height = int(str(t.params["v"]))*1000

        except Exception:
            sayErr("unexpected error {}".format(50*"#"))

    name = "{}{} {}".format(st, st2, nr)
    if name == " ":
        name = "landuse xyz"
    if debug:
        say("name {}".format(name))

    return (name, way_type, nr, building_height)
