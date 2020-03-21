'''some testdata generators'''
import cv2,matplotlib
import FreeCAD 
App=FreeCAD
import Part,Points
import numpy as np


def elevationmatrix():
	'''a 12 x 20 matrix of heights'''
	matrix=np.zeros(12*20).reshape(12,20)
	matrix[5,4]=20
	matrix[7,6]=-10
	matrix[6:10,13:17]=40
	for i in range(3,16):
		matrix[2:4,i] += i*3
	return matrix


def pointarray(matrix=None):
	'''a point/vector array with 12 * 20 points '''
	d=10
	if matrix==None:
		matrix=elevationmatrix()
	matrix=np.array(matrix)
	cu,cv=matrix.shape
	pts=[]
	for u in range(cu):
		ptsu=[FreeCAD.Vector(d*u,d*v,matrix[u,v]) for v in range(cv)]
		pts.append(ptsu)
	return pts

def pointlist(matrix=None):
	'''a point/vector list with 12 * 20 points '''
	d=10
	if matrix==None:
		matrix=elevationmatrix()
	matrix=np.array(matrix)
	cu,cv=matrix.shape
	pts=[FreeCAD.Vector(d*u,d*v,matrix[u,v]) for v in range(cv) for u in range(cu)]
	return pts


def pcl(pts=None):
	'''create a point cloud of points pts'''
	if pts==None:
		pts=pointlist()
	pcl=Points.Points(pts)
	Points.show(pcl)
	return App.ActiveDocument.ActiveObject


def bspline(pts=None):
	'''interpolate a bspline surface over the point matrix'''
	ffs=App.ActiveDocument.getObject("TestPCL")
	if ffs == None:
		bs=Part.BSplineSurface()
		if pts==None:
			pts=pointarray()
		bs.interpolate(pts)
		ffs=App.ActiveDocument.addObject("Part::Spline","TestBSF")
		ffs.Shape=bs.toShape()
	return ffs


def image(matrix=None,mode=1,mirroru=False,mirrorv=False,cmap='hsv'):
	'''transform the matrix to a colormap image
	return the filename of the temporary image file'''
	if matrix==None:
		matrix=elevationmatrix()
	matrix=np.array(matrix)
	cu,cv=matrix.shape
	matrix -= matrix.min()
	matrix /= matrix.max()

	img= np.zeros((cu,cv,3), np.uint8)

	#cmap = matplotlib.cm.get_cmap('jet')
	cmapd = matplotlib.cm.get_cmap(cmap)

	for ux in range(cu):
		for vx in range(cv):
			t=matrix[ux,vx]
			if mode == 1: (r,g,b,a)=cmapd(1-t)
			if mode == 2: (r,g,b,a)=cmapd(t)
			if mirroru:
				img[cu-1-ux,vx]=(255*r,255*g,255*b)
			else:
				img[ux,vx]=(255*r,255*g,255*b)
	

	import tempfile
	fn=tempfile.mkdtemp()
	size="12x20"
	fn +='_image_'+str(size)+'.png'
	cv2.imwrite(fn,img)
	return fn




def runtest():
	'''selftest'''
	nurbs=bspline()

	import geodat.postprocessor
	import geodat.geodat_lib
	fn=image(mirroru=True)

	geodat.geodat_lib.addImageTexture(nurbs,fn,scale=(1,2))
	Gui.updateGui()



if __name__ == '__main__':
	runtest()

