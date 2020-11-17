# -------------------------------------------------
# -- heights importer, gui miki string
# --
# -- microelly 2016 v 0.4
# -- Bernd Hahnebach <bernd@bimstatik.org> 2020
# --
# -- GNU Lesser General Public License (LGPL)
# -------------------------------------------------
"""the dialog layout as miki string"""

 
sdialog = '''
MainWindow:
	VerticalLayout:
		id:'main'
#		setFixedHeight: 600
		setFixedWidth: 300
#		move:  QtCore.QPoint(3000,100)

		QtGui.QLabel:
			setText:"C O N F I G U R A T I O N"
		QtGui.QLabel:

		QtGui.QLineEdit:
			setText:"50.3377879,11.2104096"
#			setText:"50.3736049,11.191643"
			id: 'bl'

		QtGui.QPushButton:
			setText: "Run values"
			clicked.connect: app.runbl

#
'''
