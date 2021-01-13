# Unit test for the geodat module

from importlib import reload

import FreeCAD, os, unittest, FreeCADGui

class GeodatTest(unittest.TestCase):

	def setUp(self):
		if FreeCAD.ActiveDocument:
			if FreeCAD.ActiveDocument.Name != "geodatTest":
				FreeCAD.newDocument("geodatTest")
		else:
			FreeCAD.newDocument("geodatTest")
		FreeCAD.setActiveDocument("geodatTest")

	def tearDown(self):
		FreeCAD.closeDocument("geodatTest")



	def xtestPivy(self):
		FreeCAD.Console.PrintLog ('Checking Pivy...\n')
		from pivy import coin
		c = coin.SoCube()
		FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().addChild(c)
		self.failUnless(c,"Pivy is not working properly")


	def testDialog(self):
		FreeCAD.Console.PrintLog ('Checking sole alog...\n')
		import geodat
		import geodat.import_aster
		reload(geodat.import_aster)
		m=geodat.import_aster.mydialog()
		self.failUnless(len(m.objects)>4,"import_aster dialog")
		m.objects[0].hide()

	def testDialog2(self):
		import geodat.import_srtm
		reload(geodat.import_srtm)
		m=geodat.import_srtm.mydialog()
		self.failUnless(len(m.objects)>4,"import_srtm dialog")
		m.objects[0].hide()

	def testDialog3(self):
		import geodat.navigator
		reload(geodat.navigator)
		FreeCADGui.activeDocument().activeView().setCameraType("Perspective")
		FreeCADGui.updateGui() 
		ef=geodat.navigator.navi()
		self.failUnless(ef.navi,"navigator dialog dialog")
		ef.navi.hide()
		ef.output.hide()
		geodat.navigator.stop()



