from PyQt5.QtWidgets import *
from widgets.cluster_display import ClusterDisplay
from PyQt5 import Qt,QtCore, QtGui, QtWidgets
import model
from functools import partial
import json

class IkkiewTab(QWidget):
	def __init__(self,parent, threadpool, db):
		super(IkkiewTab, self).__init__(parent)
		self.model = model.modelImage(db)
		self.parent = parent
		self.threadpool = threadpool
		self.__UIsetup__()

	def __UIsetup__(self):
		self.mainLayoutClusterList = QGridLayout()
		#Set main layout
		self.mainLayoutClusterList.addWidget(QLabel("Ikkiew"), 0,0)
		self.mainLayoutClusterList.addWidget(QLabel("Balls"),1,0)
		self.mainLayoutClusterList.addWidget(QPushButton("poposusu"),2,0)
		self.mainLayoutClusterList.addWidget(QLabel("Lorem"),3,0)
		self.mainLayoutClusterList.addWidget(QPushButton("Ipsum"),4,0)
		self.setLayout(self.mainLayoutClusterList)

	def clear_layout(self, layout):
	#Code reference [ https://www.semicolonworld.com/question/58072/clear-all-widgets-in-a-layout-in-pyqt ]
		for i in reversed(range(layout.count())): 
			layout.itemAt(i).widget().setParent(None)
