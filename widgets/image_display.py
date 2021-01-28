from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import Qt,QtCore, QtGui
import model
import qimage2ndarray

class imageDisplay(QLabel):
	def __init__(self):
		super(imageDisplay, self).__init__()
		#self.model = model.modelImage()
		self.widthSize = 1300
		self.__display__()
		self.__setupFuncs__()
	def __display__(self):
		self.mainLayout = QVBoxLayout()
		self.imageLayout = QVBoxLayout()
		self.buttonLayout = QHBoxLayout()
		#Setting layout
		self.mainLayout.addLayout(self.imageLayout)
		self.mainLayout.addLayout(self.buttonLayout)
		#Creation images 
		self.ImageLabel = QLabel()
		#Control
		
		#self.quantizeButton = QPushButton("Quantize")
		#self.brightnessPlus = QPushButton("Brightness +")
		#self.brightnessMinus = QPushButton("Brightness -")
		
		#Adding widgets to layout
		self.imageLayout.addWidget(self.ImageLabel)	
		#self.buttonLayout.addWidget(self.quantizeButton)
		#self.buttonLayout.addWidget(self.brightnessMinus)
		#self.buttonLayout.addWidget(self.brightnessPlus)	
		
		#set the main layout
		self.setLayout(self.mainLayout)
	def __setupFuncs__(self):
		pass
		#self.quantizeButton.clicked.connect(self.quantizeReq)
		#self.brightnessPlus.clicked.connect(lambda: self.brightness(10))
		#self.brightnessMinus.clicked.connect(lambda: self.brightness(-10))
	def setPhotoPath(self, newimage):
		self.imgPath = newimage
		self.imgData = QtGui.QImage(self.imgPath, "tiff")
		self.setImg()
	def setImg(self):
		image = QPixmap(self.imgData).scaledToWidth(self.widthSize)
		self.ImageLabel.setPixmap(image)
	# def brightness(self, amt):
	# 	QImageInArr = qimage2ndarray.rgb_view(self.imgData)
	# 	image = self.model.brightness(QImageInArr,isArr=True, beta=amt)
	# 	self.imgData = qimage2ndarray.array2qimage(image)
	# 	self.setImg()
	# def quantizeReq(self):
	# 	QImageInArr = qimage2ndarray.rgb_view(self.imgData)
	# 	image = self.model.quant(QImageInArr,cluster=4,isArr=True)
	# 	self.imgData = qimage2ndarray.array2qimage(image)
	# 	self.setImg()
		