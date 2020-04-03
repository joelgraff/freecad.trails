# Unit test for the Geodat module


import FreeCAD, os, unittest, FreeCADGui

App=FreeCAD
Gui=FreeCADGui

class GeodatTest(unittest.TestCase):

	def setUp(self):
		if FreeCAD.ActiveDocument:
			if FreeCAD.ActiveDocument.Name != "Test":
				FreeCAD.newDocument("Test")
		else:
			FreeCAD.newDocument("Test")
		FreeCAD.setActiveDocument("Test")


	def XtestPivy(self):
		FreeCAD.Console.PrintLog ('Checking Pivy...\n')
		from pivy import coin
		c = coin.SoCube()
		FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().addChild(c)
		self.failUnless(c,"Pivy is not working properly")

	def testInventortools(self):
		import geodat.inventortools
		obj=App.ActiveDocument.addObject("Part::Box","Box")
		geodat.inventortools.setcolorlights(obj)

	def testInventortools2(self):
		import geodat.inventortools
		obj=App.ActiveDocument.Box
		geodat.inventortools.setcolors2(obj)


	def tearDown(self):
		# FreeCAD.closeDocument("Test")
		pass



