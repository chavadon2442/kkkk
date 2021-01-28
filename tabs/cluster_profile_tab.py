from PyQt5.QtWidgets import *
from PyQt5 import Qt,QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap, QFont
from functools import partial
from widgets.image_display import imageDisplay
import model
import os

class ClusterProfileTab(QWidget):
	def __init__(self,parent, threadpool, db):
		super(ClusterProfileTab, self).__init__(parent)
		self.parent = parent
		self.clusterName = ""
		self.type = ""
		self.model = model.modelImage(db)
		self.chosenView = None
		self.threadpool = threadpool
		self.__UIsetup__()
		self.__datasetup__()
	def __UIsetup__(self):
		#Layout
		self.mainLayout = QHBoxLayout()
		self.imageLayout = QVBoxLayout()
		self.infoLayout = QVBoxLayout()
		#Set Layout
		self.mainLayout.addLayout(self.imageLayout)
		self.mainLayout.addLayout(self.infoLayout)
		#Info layout
		self.errPopupWidget = QMessageBox()
		self.clusterInfoFrame = QFrame()
		self.photoInfoFrame = QFrame()
		self.updateDataButton = QPushButton("Update data")
		self.updateDataButton.clicked.connect(self.__datasetup__)
		self.clusterInfoFrame.setMaximumWidth(525)
		self.photoInfoFrame.setMaximumWidth(525)
		self.clusterInfoFrame.setMaximumHeight(200)
		self.photoInfoFrame.setMaximumHeight(400)
		self.photoInfoFrame.setFrameStyle(QFrame.Panel)
		self.clusterInfoFrame.setFrameStyle(QFrame.Panel)
		self.clusterInfoFrame.setStyleSheet("QFrame {border : 2px solid rgba(220,220,200,1); background-color: rgba(220,220,220,0.1)}")
		self.photoInfoFrame.setStyleSheet("QFrame {border : 2px solid rgba(220,220,200,1); background-color: rgba(220,220,220,0.1)}")
		self.infoLayout.addWidget(self.updateDataButton)
		self.infoLayout.addWidget(self.clusterInfoFrame)
		self.infoLayout.addWidget(self.photoInfoFrame)
		#Image 
		self.imageDisplay = imageDisplay() 
		self.imageLayout.addWidget(self.imageDisplay)
		#Cluster info
		self.clusterInfoLayout = QGridLayout()
		self.viewList = QComboBox()
		self.clusterList = QComboBox()
		self.imageLabel = QLabel("Image Label: ")
		self.filterLabelInfo = QLabel("")
		self.paramLabelInfo = QLabel("")
		self.clusterLocationWidget = QLineEdit("")
		self.clusterLocationWidget.setStyleSheet("color: black; background-color: rgba(0,0,0,0.15);")
		self.browseClusterButton = QPushButton("Browse")
		self.clusterLocationWidget.setReadOnly(True)
		self.browseClusterButton.clicked.connect(self.getDirectoryLocation)
		self.viewList.activated.connect(self.setupClusterList)
		self.clusterList.activated.connect(self.getPhoto)
		self.clusterInfoLayout.addWidget(self.clusterLocationWidget,0,0)
		self.clusterInfoLayout.addWidget(self.browseClusterButton,0,1)
		self.clusterInfoLayout.addWidget(QLabel("View"), 1,0)
		self.clusterInfoLayout.addWidget(self.viewList, 1,1)
		self.clusterInfoLayout.addWidget(QLabel("Cluster"), 2,0)
		self.clusterInfoLayout.addWidget(self.clusterList, 2,1)
		self.clusterInfoLayout.addWidget(self.imageLabel, 3,0,1,2)
		self.clusterInfoLayout.addWidget(QLabel("Filter:"), 4,0)
		self.clusterInfoLayout.addWidget(self.filterLabelInfo, 4,1)
		self.clusterInfoLayout.addWidget(QLabel("Param used:"), 5,0)
		self.clusterInfoLayout.addWidget(self.paramLabelInfo, 5,1)
		self.clusterInfoFrame.setLayout(self.clusterInfoLayout)

		#Photo info
		self.tagButton = QPushButton("tag complete cluster")
		self.tagPhotoButton = QPushButton("tag current image")
		self.RecomButton = QLabel("Recommend Tags : Focus Tag")
		#self.RecomButton.clicked.connect(self.recomTag)
		self.tagButton.clicked.connect(self.tagCluster)
		self.tagPhotoButton.clicked.connect(self.tagSelctedImage)
		#self.tagButton.setEnabled(False)
		self.photoInfoLayout = QGridLayout()
		self.getNextPhotoButton = QPushButton("Next photo") 
		self.photoInfoLayout.addWidget(self.getNextPhotoButton, 0,0,1,2)
		self.photoDropDown = QListWidget()
		self.photoDropDown1 = QListWidget()
		#self.photoDropDown.setSelectionMode(QListWidget.MultiSelection)
		self.photoInfoLayout.addWidget(self.photoDropDown, 1,0,1,2)
		self.photoInfoLayout.addWidget(self.RecomButton, 2,0,1,2)
		self.photoInfoLayout.addWidget(self.photoDropDown1, 3,0,1,2)
		self.photoInfoLayout.addWidget(self.tagButton, 4,0,1,2)
		self.photoInfoLayout.addWidget(self.tagPhotoButton, 5,0,1,2)
		
		tags  = self.model.DB.query_alltag()
		for tg in tags:
			self.photoDropDown.addItem(tg)
			
		tags1  = self.model.DB.query_alltag1()
		for tg in tags1:
			self.photoDropDown1.addItem(tg)
		self.photoDropDown.setCurrentRow(0)
		self.photoDropDown1.setCurrentRow(0)
		self.photoInfoFrame.setLayout(self.photoInfoLayout)
		##buttonsetup
		self.getNextPhotoButton.clicked.connect(self.getPhoto)
		#setup
		self.setLayout(self.mainLayout)


	def __datasetup__(self):
		newLocal = self.clusterLocationWidget.text()
		if(os.path.exists(newLocal) == True):
			self.viewList.clear()
			self.mainData = self.model.get_views_clusters(newLocal)
			[self.viewList.addItem(views) for views in self.mainData]
			self.setupClusterList()


	def setupClusterList(self):
		self.clusterList.clear()
		currentView, _ = self.getCurrentClusterAndView()
		clusters = self.mainData[currentView]
		[self.clusterList.addItem(cluster) for cluster in clusters]
		self.imgIndex = -1
		self.getPhoto()

	def getPhoto(self):
		currentView, currentCluster = self.getCurrentClusterAndView()
		curCluster = self.mainData[currentView][currentCluster]
		self.imgIndex = (self.imgIndex + 1) % curCluster.imgAmt
		currentImgPath = curCluster.images[self.imgIndex]
		self.imageLabel.setText(os.path.split(currentImgPath)[-1])
		self.imageDisplay.setPhotoPath(currentImgPath)
		self.tagPhotoButton.setEnabled(True)

	def tagCluster(self):
		currentView, currentCluster = self.getCurrentClusterAndView()
		tag = [item.text() for item in self.photoDropDown.selectedItems()]
		self.model.tagCluster(currentView, self.mainData[currentView][currentCluster].paths, tag)
		del self.mainData[currentView][currentCluster]
		self.setupClusterList()

	def tagSelctedImage(self):
		self.tagPhotoButton.setEnabled(False)
		imgname =self.getimgname()
		currentView, currentCluster = self.getCurrentClusterAndView()
		curCluster = self.mainData[currentView][currentCluster]
		tag = [item.text() for item in self.photoDropDown.selectedItems()][0]
		if(self.filterInfo != None):
			if(currentCluster not in self.filterClassDict):
				self.filterClassDict[currentCluster] = dict({})
			if(tag not in self.filterClassDict[currentCluster]):
				self.filterClassDict[currentCluster][tag] = 1
			else:
				self.filterClassDict[currentCluster][tag] += 1
		self.model.tag_image_trivial(curCluster.images[self.imgIndex], tag)
		curCluster.removeImages(self.imgIndex)
		if(curCluster.getClusterLen() == 0 and self.filterInfo != None):
			#Add the tag information to DB
			filterName, view, params = self.filterInfo
			totalTagged = sum(self.filterClassDict[currentCluster].values())
			for tags in self.filterClassDict[currentCluster]:
				#Please change this method !! --> tagID = self.model.DB.query("SELECT Tag_No from DETAILS WHERE Description=?", (tags,))[0]
				tagTotal = self.filterClassDict[currentCluster][tags]
				recallRate = tagTotal / totalTagged
				result = self.model.DB.query("""
				SELECT performance, ses_amt, detectedImage from Filter_tag 
				WHERE filter_name=? AND
					  Params=? AND
					  View=? AND
					  tag_alias=? AND
					  tag_name=?""", (filterName, params, view, str(currentCluster), tags))
				
				result1 = self.model.DB.query("""
				SELECT image_name, View, detail from Image_tag
				WHERE image_name=? AND
					  View=? AND
					  detail=?
				""",(str(imgname),view,tags)

				)
				if(result1 != []):
					self.model.DB.modifyTable("""UPDATE Image_tag SET image_name=? AND
					  View=? AND
					  detail=?
					
					""",(str(imgname),view,tags))

				if(result != []):
					performance, ses_amt, detectedImage = result[0]
					newAvgPerformance = (performance*ses_amt + recallRate) / (ses_amt + 1)
					newDetectedImage = tagTotal + detectedImage
					new_ses = ses_amt + 1
					print(newAvgPerformance, newDetectedImage, new_ses)
					self.model.DB.modifyTable("""UPDATE Filter_tag 
					   SET performance=?,ses_amt=?,detectedImage=?
					   WHERE filter_name=? AND Params=? AND View=? AND tag_alias=? AND tag_name=?""", (newAvgPerformance, new_ses, newDetectedImage, filterName, params, view, str(currentCluster), tags))
				else:
					self.model.DB.modifyTable("""INSERT INTO FIlter_tag VALUES (?,?,?,?,?,?,?,?)""", (filterName, params, view, str(currentCluster), tags, recallRate, 1, tagTotal))
			del self.mainData[currentView][currentCluster]
			self.setupClusterList()
		else:
			self.getPhoto()
		# if(self.model.tagImage(currentView, curCluster.images[self.imgIndex], tag) == True):
		# 	curCluster.removeImages(self.imgIndex)
		# 	self.getPhoto()
		# else:
		# 	print("Moving images failed!")

	def getimgname(self):
		currentView, currentCluster = self.getCurrentClusterAndView()
		curCluster = self.mainData[currentView][currentCluster]
		self.imgIndex = (self.imgIndex + 1) % curCluster.imgAmt
		currentImgPath = curCluster.images[self.imgIndex]
		return self.imageLabel.setText(os.path.split(currentImgPath)[-1])
		

	def getCurrentClusterAndView(self):
		return self.viewList.itemText(self.viewList.currentIndex()), self.clusterList.itemText(self.clusterList.currentIndex())

	def getDirectoryLocation(self):
		fileLocal = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
		if(fileLocal != None and fileLocal != ""):
			self.setDirectoryLocation(fileLocal)
	
	def setDirectoryLocation(self, fileLocal):
		if(fileLocal != None and fileLocal != ""):
			self.clusterLocationWidget.setText(fileLocal)
			filePath = os.path.join(fileLocal, ".cainfo")
			self.filterInfo = None
			self.filterClassDict = dict({})
			if(os.path.exists(filePath) == False):
				self.errPopupWidget.setWindowTitle("Warning!")
				self.errPopupWidget.setText("No .cainfo file in directory!:\nThis location was not filtered; The performance of each class will not be tracked!")
				self.errPopupWidget.setIcon(QMessageBox.Warning)
				self.errPopupWidget.setStandardButtons(QMessageBox.Ok)
				self.errPopupWidget.exec_()
			else:
				self.filterInfo = self.model.getSesInformation(filePath)
				self.filterLabelInfo.setText(self.filterInfo[0])
				self.paramLabelInfo.setText(self.filterInfo[2])
			self.__datasetup__()
	
	def clear_layout(self, layout):
	#Code reference [ https://www.semicolonworld.com/question/58072/clear-all-widgets-in-a-layout-in-pyqt ]
		for i in reversed(range(layout.count())): 
			layout.itemAt(i).widget().setParent(None)