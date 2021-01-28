from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import Qt,QtCore
import os
import sys
import model



class ClusterDisplay(QLabel):
	def __init__(self, imageLoc, title,imgSize=600):
		super(ClusterDisplay, self).__init__()
		self.len = len(imageLoc)
		self.widthSize = imgSize
		self.index = 0
		self.title = title
		self.imageLocList = imageLoc
		self.__display__()
		self.__timerSetup__()
	def __display__(self):
		self.layout = QVBoxLayout()
		self.ImageLabel = QLabel()
		self.setImg()
		self.layout.addWidget(self.ImageLabel)
		self.layout.addWidget(QPushButton("Cluster: " +  self.title))
		self.setLayout(self.layout)
	def setImg(self):
		image = QPixmap(self.imageLocList[self.index]).scaledToWidth(self.widthSize)
		self.ImageLabel.setPixmap(image)
		self.index = (self.index + 1) % self.len
	def __timerSetup__(self):
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.setImg)
		self.timer.start(5000)

class MainWindow(QWidget):
	def __init__(self, width, height, title, pos = [0,0]):
		super(MainWindow, self).__init__()
		self.setWindowTitle(title)
		self.setWindowIcon(QIcon('icon.png')) 
		self.setGeometry(pos[0],pos[1],width,height)
		self.model = model.modelImage()
		self.__setupUI__()

	def __setupUI__(self):
		self.mainLayout = QVBoxLayout()
		self.mainLayoutClusterList = QVBoxLayout()
		self.topLayout = QHBoxLayout()
		self.clusterDisplayLayout = QVBoxLayout()
		###### TAB ########
		self.windowTab = QTabWidget(self)
		self.clusterListTab = QWidget()
		self.clusterProfileTab = QWidget()
		self.windowTab.addTab(self.clusterListTab, "Cluster location")
		self.windowTab.addTab(self.clusterProfileTab, "Cluster profile")
		##################
		#contruct layout
		self.mainLayoutClusterList.addLayout(self.topLayout)
		self.mainLayoutClusterList.addLayout(self.clusterDisplayLayout)
		#add widget
			#Top layout
		self.locationLineEdit = QLineEdit("") 
		self.locSearchButton = QPushButton("Search")
		self.configButton = QPushButton("Config")
		self.locSearchButton.clicked.connect(self.requestClusterDisply)
		self.topLayout.addWidget(self.locationLineEdit)
		self.topLayout.addWidget(self.locSearchButton)
		self.topLayout.addWidget(self.configButton)
			#Cluster
		scrollArea = QScrollArea()
		self.contentInScroll = QWidget(scrollArea)
		self.imageLayout = QGridLayout()
		self.contentInScroll.setLayout(self.imageLayout)
		scrollArea.setWidget(self.contentInScroll)
		scrollArea.setWidgetResizable(True)
		scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
		scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
		self.clusterDisplayLayout.addWidget(scrollArea)
		#set main layout 
		self.clusterListTab.setLayout(self.mainLayoutClusterList)
		self.mainLayout.addWidget(self.windowTab)
		self.setLayout(self.mainLayout)

	def clearLayout(self, layout):
		#Code reference [ https://www.semicolonworld.com/question/58072/clear-all-widgets-in-a-layout-in-pyqt ]
		for i in reversed(range(layout.count())): 
			layout.itemAt(i).widget().setParent(None)

	def requestClusterDisply(self):
		COLAMT = 3
		location = self.locationLineEdit.text()
		if(location):
			self.clearLayout(self.imageLayout)
			images = self.model.requestClusterImages(location, amount=10)
			SIZE = 600
			if(len(images) < 3):
				SIZE = 1920//len(images)
			for i,img in enumerate(images):
				row = i//COLAMT
				col = i%COLAMT
				img = ClusterDisplay(imageLoc=images[img], title=img, imgSize=SIZE)
				self.imageLayout.addWidget(img,row,col)
				self.imageLayout.setColumnMinimumWidth(col,500)
				self.imageLayout.setRowMinimumHeight(row,500)
				self.locationLineEdit.setText("")



if (__name__ == "__main__"):
	app = QApplication(sys.argv)
	window = MainWindow(width=1920, height=1080, title="Cluster assistant")
	window.show()
	sys.exit(app.exec_())