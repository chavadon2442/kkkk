from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import Qt,QtCore

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
		self.button = QPushButton("Cluster: " +  self.title)
		self.setImg()
		self.layout.addWidget(self.ImageLabel)
		self.layout.addWidget(self.button)
		self.setLayout(self.layout)
	def setImg(self):
		image = QPixmap(self.imageLocList[self.index]).scaledToWidth(self.widthSize)
		self.ImageLabel.setPixmap(image)
		self.index = (self.index + 1) % self.len
	def __timerSetup__(self):
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.setImg)
		self.timer.start(5000)