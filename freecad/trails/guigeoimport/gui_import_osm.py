# -------------------------------------------------
# -- osm map importer gui
# --
# -- microelly 2016 v 0.4
# -- Bernd Hahnebach <bernd@bimstatik.org> 2020
# --
# -- GNU Lesser General Public License (LGPL)
# -------------------------------------------------
"""gui for import data from openstreetmap"""


import WebGui
from PySide import QtGui

# import FreeCAD
# import FreeCADGui

from freecad.trails.geoimport import import_osm
from freecad.trails.geoimport import miki
from freecad.trails.geoimport.say import say


# the gui backend
class MyApp(object):
    """execution layer of the Gui"""

    def run(self, lat, lon):
        """
        run(self,lat,lon) imports area
        with center coordinates latitude lat, longitude lon
        """
        s = self.root.ids["s"].value()
        key = "%0.7f" % (lat) + "," + "%0.7f" % (lon)
        self.root.ids["bl"].setText(key)
        import_osm.import_osm2(
            lat,
            lon,
            float(s)/10,
            self.root.ids["progb"],
            self.root.ids["status"],
            False
        )

    def run_alex(self):
        """imports Berlin Aleancderplatz"""
        self.run(52.52128, lon=13.41646)

    def run_paris(self):
        """imports Paris"""
        self.run(48.85167, 2.33669)

    def run_tokyo(self):
        """imports Tokyo near tower"""
        self.run(35.65905, 139.74991)

    def run_spandau(self):
        """imports Berlin Spandau"""
        self.run(52.508, 13.18)

    def run_co2(self):
        """imports  Coburg Univerity and School"""
        self.run(50.2631171, 10.9483)

    def run_sternwarte(self):
        """imports Sonneberg Neufang observatorium"""
        self.run(50.3736049, 11.191643)

    def showHelpBox(self):

        msg = QtGui.QMessageBox()
        msg.setText("<b>Help</b>")
        msg.setInformativeText(
            "Import_osm map dialogue box can also accept links "
            "from following sites in addition to "
            "(latitude, longitude)<ul><li>OpenStreetMap</li><br>"
            "e.g. https://www.openstreetmap.org/#map=15/30.8611/75.8610<br><li>Google Maps</li><br>"
            "e.g. https://www.google.co.in/maps/@30.8611,75.8610,5z<br><li>Bing Map</li><br>"
            "e.g. https://www.bing.com/maps?osid=339f4dc6-92ea-4f25-b25c-f98d8ef9bc45&cp=30.8611~75.8610&lvl=17&v=2&sV=2&form=S00027<br><li>Here Map</li><br>"
            "e.g. https://wego.here.com/?map=30.8611,75.8610,15,normal<br><li>(latitude,longitude)</li><br>"
            "e.g. 30.8611,75.8610</ul><br>"
            "If in any case, the latitude & longitudes are estimated incorrectly, "
            "you can use different separators in separator box "
            "or can put latitude & longitude directly into their respective boxes."
        )
        msg.exec_()

    def showHelpBoxY(self):
        # self.run_sternwarte()
        say("showHelpBox called")

    def getSeparator(self):
        bl = self.root.ids["bl"].text()
        if bl.find("openstreetmap.org") != -1:
            self.root.ids["sep"].setText("/")
        elif bl.find("google.co") != -1:
            self.root.ids["sep"].setText("@|,")
        elif bl.find("bing.com") != -1:
            self.root.ids["sep"].setText("=|~|&")
        elif bl.find("wego.here.com") != -1:
            self.root.ids["sep"].setText("=|,")
        elif bl.find(",") != -1:
            self.root.ids["sep"].setText(",")
        elif bl.find(":") != -1:
            self.root.ids["sep"].setText(":")
        elif bl.find("/") != -1:
            self.root.ids["sep"].setText("/")

    def getCoordinate(self):
        sep = self.root.ids["sep"].text()
        bl = self.root.ids["bl"].text()
        import re
        spli = re.split(sep, bl)
        flag = "0"
        for x in spli:
            try:
                float(x)
                if x.find(".") != -1:
                    if flag == "0":
                        self.root.ids["lat"].setText(x)
                        flag = "1"
                    elif flag == "1":
                        self.root.ids["long"].setText(x)
                        flag = "2"
            except:
                flag = flag

    def swap(self):
        tmp1 = self.root.ids["lat"].text()
        tmp2 = self.root.ids["long"].text()
        self.root.ids["long"].setText(tmp1)
        self.root.ids["lat"].setText(tmp2)

    def downloadData(self):
        """download data from osm"""
        button = self.root.ids["runbl1"]
        button.hide()
        br = self.root.ids["running"]
        br.show()

        bl_disp = self.root.ids["lat"].text()
        lat = float(bl_disp)
        bl_disp = self.root.ids["long"].text()
        lon = float(bl_disp)

        s = self.root.ids["s"].value()
        elevation = self.root.ids["elevation"].isChecked()

        rc = import_osm.import_osm2(
            float(lat),
            float(lon),
            float(s)/10,
            self.root.ids["progb"],
            self.root.ids["status"],
            elevation
        )
        if not rc:
            button = self.root.ids["runbl2"]
            button.show()
        else:
            button = self.root.ids["runbl1"]
            button.show()
        br.hide()

    def applyData(self):
        """apply downloaded or cached data to create the FreeCAD models"""
        button = self.root.ids["runbl2"]
        button.hide()
        br = self.root.ids["running"]
        br.show()

        bl_disp = self.root.ids["lat"].text()
        lat = float(bl_disp)
        bl_disp = self.root.ids["long"].text()
        lon = float(bl_disp)

        s = self.root.ids["s"].value()
        elevation = self.root.ids["elevation"].isChecked()

        import_osm.import_osm2(
            float(lat),
            float(lon),
            float(s)/10,
            self.root.ids["progb"],
            self.root.ids["status"],
            elevation
        )
        button = self.root.ids["runbl1"]
        button.show()
        br.hide()

    def showMap(self):
        """
        open a webbrowser window and display
        the openstreetmap presentation of the area
        """

        bl_disp = self.root.ids["lat"].text()
        lat = float(bl_disp)
        bl_disp = self.root.ids["long"].text()
        lon = float(bl_disp)

        # s = self.root.ids["s"].value()
        WebGui.openBrowser(
            "http://www.openstreetmap.org/#map=16/{}/{}".format(lat, lon)
        )

    def showDistanceOnLabel(self):
        distance = self.root.ids["s"].value()
        showDistanceLabel = self.root.ids["showDistanceLabel"]
        showDistanceLabel.setText(
            "Distance is {} km.".format(float(distance)/10)
        )


# the gui startup
def mydialog():
    """ starts the gui dialog """
    print("OSM gui startup")
    app = MyApp()

    my_miki = miki.Miki()
    my_miki.app = app
    app.root = my_miki

    from .miki_import_osm import s6
    my_miki.parse2(s6)
    my_miki.run(s6)
    return my_miki


def importOSM():
    mydialog()


"""
#-----------------
# verarbeiten

import xml.etree.ElementTree as ET

fn="/home/thomas/.FreeCAD//geodat3/50.340722-11.232647-0.015"
#tree = ET.parse(fn)

data_as_string=''<?xml version="1.0"?><data>
    <country name="Liechtenstein">
        <rank>1</rank>
        <year>2008</year>
        <gdppc>141100</gdppc>
        <neighbor name="Austria" direction="E"/>
        <neighbor name="Switzerland" direction="W"/>
    </country>
    <country name="Singapore">
        <rank>4</rank>
        <year>2011</year>
        <gdppc>59900</gdppc>
        <neighbor name="Malaysia" direction="N"/>
    </country>
    <country name="Panama">
        <rank>68</rank>
        <year>2011</year>
        <gdppc>13600</gdppc>
        <neighbor name="Costa Rica" direction="W"/>
        <neighbor name="Colombia" direction="E"/>
    </country>
</data>
''

root = ET.fromstring(data_as_string)


for element in tree.getiterator("node"):
    print(element.attrib)


root = tree.getroot()
ET.dump(root)

for elem in root:
    print (elem.tag,elem.attrib)
#----------------
"""
