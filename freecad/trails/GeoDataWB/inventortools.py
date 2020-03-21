import pivy
from pivy import coin


def setcolorlights(obj):
	''' monochromes licht auf objekt legen '''

	obj.ViewObject.ShapeColor = (1.00,1.00,1.00)
	obj.ViewObject.LineColor = (1.00,1.00,.00)
	obj.ViewObject.LineWidth = 1.00

	viewprovider = obj.ViewObject
	root=viewprovider.RootNode

	l=coin.SoDirectionalLight()
	l.direction.setValue(coin.SbVec3f(0,1,0))
	l.color.setValue(coin.SbColor(0,1,0))
	root.insertChild(l, 0)

	l=coin.SoDirectionalLight()
	l.direction.setValue(coin.SbVec3f(1,0,0))
	l.color.setValue(coin.SbColor(0,1,0))
	root.insertChild(l, 0)

	l=coin.SoDirectionalLight()
	l.direction.setValue(coin.SbVec3f(0,-1,0))
	l.color.setValue(coin.SbColor(0,1,0))
	root.insertChild(l, 0)
	
	l=coin.SoDirectionalLight()
	l.direction.setValue(coin.SbVec3f(-1,0,0))
	l.color.setValue(coin.SbColor(0,1,0))
	root.insertChild(l, 0)

	l=coin.SoDirectionalLight()
	l.direction.setValue(coin.SbVec3f(0,0,1))
	l.color.setValue(coin.SbColor(0,1,0))
	root.insertChild(l, 0)
	
	l=coin.SoDirectionalLight()
	l.direction.setValue(coin.SbVec3f(0,0,-1))
	l.color.setValue(coin.SbColor(0,1,0))
	root.insertChild(l, 0)


def setcolors2(obj):
	''' unterschiedliches licht aus allen richtungen '''

	viewprovider = obj.ViewObject
	root=viewprovider.RootNode

	l=coin.SoDirectionalLight()
	l.direction.setValue(coin.SbVec3f(0,1,0))
	l.color.setValue(coin.SbColor(0,0,1))
	root.insertChild(l, 0)

	l=coin.SoDirectionalLight()
	l.direction.setValue(coin.SbVec3f(1,0,0))
	l.color.setValue(coin.SbColor(0,1,0))
	root.insertChild(l, 0)

	l=coin.SoDirectionalLight()
	l.direction.setValue(coin.SbVec3f(0,-1,0))
	l.color.setValue(coin.SbColor(1,0,1))
	root.insertChild(l, 0)
	
	l=coin.SoDirectionalLight()
	l.direction.setValue(coin.SbVec3f(-1,0,0))
	l.color.setValue(coin.SbColor(0,1,1))
	root.insertChild(l, 0)

	l=coin.SoDirectionalLight()
	l.direction.setValue(coin.SbVec3f(0,0,1))
	l.color.setValue(coin.SbColor(1,0,0))
	root.insertChild(l, 0)
	
	l=coin.SoDirectionalLight()
	l.direction.setValue(coin.SbVec3f(0,0,-1))
	l.color.setValue(coin.SbColor(1,1,0))
	root.insertChild(l, 0)

