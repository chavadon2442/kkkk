from PyQt5.QtWidgets import *
from widgets.cluster_display import ClusterDisplay
from PyQt5 import Qt,QtCore, QtGui, QtWidgets
import model
from functools import partial
import json
"""
QUESTION : Why importing widgets module work in this case!
"""
class RowInformtionWidget(QWidget):
	def __init__(self, parent, setSize=1000):
		super(RowInformtionWidget, self).__init__(parent)
		self._setup(setSize)
	def _setup(self,setSize=1000):
		if(setSize != None):
			self.setMaximumWidth(setSize)
		self.layout = QHBoxLayout()
		self.setLayout(self.layout)


class ClusterListTab(QWidget):
	def __init__(self,parent, threadpool, db):
		super(ClusterListTab, self).__init__(parent)
		self.model = model.modelImage(db)
		self.parent = parent
		self.threadpool = threadpool
		self.__UIsetup__()		
		self.setConfigOptions()

	def __UIsetup__(self):
		self.mainLayoutClusterList = QGridLayout()
		#Location [row]
		self.locationInputUI = RowInformtionWidget(self)
		self.selectLocationButton = QPushButton("Browse location")
		self.locationInputField = QLineEdit()
		self.locationInputField.setReadOnly(True)
		self.locationInputField.setStyleSheet("color: black; background-color: rgba(0,0,0,0.15);")
		self.selectLocationButton.clicked.connect(self.getDirectoryLocation)
		self.locationInputUI.layout.addWidget(QLabel("Location:- "))
		self.locationInputUI.layout.addWidget(self.locationInputField)
		self.locationInputUI.layout.addWidget(self.selectLocationButton)
		#Create structure [row]
		self.creteStructureInputUI = RowInformtionWidget(self)
		self.createStructureYes = QRadioButton("Yes")
		self.createStructureNo  = QRadioButton("No")
		self.creteStructureInputUI.layout.addWidget(QLabel("Structure Directory before cluster?"))
		self.creteStructureInputUI.layout.addWidget(self.createStructureYes)
		self.creteStructureInputUI.layout.addWidget(self.createStructureNo)
		#Choose config [row]
		self.configInputUI = RowInformtionWidget(self)
		self.configInputSelection = QComboBox()	
		self.configInputSelection.setMinimumWidth(300)
		self.configInputSelection.activated.connect(self.displayConfigSummary)
		self.configInputSummary = QTableWidget()
		self.configInputSummary.setMaximumHeight(250)
		self.updateConfigOptions = QPushButton("Update")
		self.updateConfigOptions.clicked.connect(self.setConfigOptions)
		self.configInputUI.layout.addWidget(QLabel("Config :- "))
		self.configInputUI.layout.addWidget(self.configInputSelection)
		self.configInputUI.layout.addWidget(self.configInputSummary)
		self.configInputUI.layout.addWidget(self.updateConfigOptions)
		self.initiateClusterButton = QPushButton("Start clustering")
		self.initiateClusterButton.clicked.connect(self.startClusteringProcess)
		#Console output text area [row]
		self.consoleOutputUI = RowInformtionWidget(self)
		self.consoleOutputArea = QTextEdit()
		self.consoleOutputArea.setReadOnly(True)
		self.consoleOutputArea.setMinimumWidth(500)
		self.consoleOutputArea.setMaximumHeight(500)
		self.consoleOutputUI.layout.addWidget(self.consoleOutputArea)
		#Set main layout
		self.mainLayoutClusterList.addWidget(self.locationInputUI, 0,0)
		self.mainLayoutClusterList.addWidget(self.creteStructureInputUI,1,0)
		self.mainLayoutClusterList.addWidget(self.configInputUI,2,0)
		self.mainLayoutClusterList.addWidget(self.initiateClusterButton,3,0)
		self.mainLayoutClusterList.addWidget(self.consoleOutputUI,4,0)
		self.setLayout(self.mainLayoutClusterList)


	def setConfigOptions(self):
		self.configValue = self.model.getAllConfigs() #Give List of config names and thier contents
		try:
			self.configInputSelection.clear()
		except:
			pass
		self.configInputSelection.addItems([keys for keys in self.configValue])
		self.displayConfigSummary()
	
	def displayConfigSummary(self):
		jsonVal = self.configValue[self.configInputSelection.itemText(self.configInputSelection.currentIndex())] 
		configkeys = list(jsonVal.keys())
		self.configInputSummary.setColumnCount(len(jsonVal)+1)
		self.configInputSummary.setRowCount(len(jsonVal[configkeys[0]]) + 1)
		for i,keys in enumerate(jsonVal[configkeys[0]]):
			self.configInputSummary.setItem(0,i+1, QTableWidgetItem(keys))
		for x, keys in enumerate(configkeys):
			self.configInputSummary.setItem(x+1,0, QTableWidgetItem(keys))
			for y, subinfo in enumerate(jsonVal[keys]):
				cell = QTableWidgetItem(str(jsonVal[keys][subinfo]))
				cell.setFlags(QtCore.Qt.ItemIsEnabled)
				self.configInputSummary.setItem(x+1,y+1,cell)
		# self.configInputSummary.setText(json.dumps(jsonVal, indent=4))

	def startClusteringProcess(self):
		path = self.locationInputField.text().strip()
		if(self.model.validLocationCheck(path) == False):
			print("Location given is not valid, please try again!")
			return None
		structure = self.createStructureYes.isChecked()
		configFile = self.configInputSelection.itemText(self.configInputSelection.currentIndex())
		clusterThread = model.ClusteringThread(path, structure, configFile)
		self.threadpool.start(clusterThread)
		clusterThread.signals.finished.connect(self.ClusteringCompleted)
		clusterThread.signals.updateInfo.connect(self.updateConsole)
		self.blockUntilClusterFinish()

	def updateConsole(self, update):
		self.consoleOutputArea.append(update)

	def blockUntilClusterFinish(self):
		self.initiateClusterButton.setEnabled(False)

	def ClusteringCompleted(self):
		self.initiateClusterButton.setEnabled(True)

	def getDirectoryLocation(self):
		fileLocal = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
		if(fileLocal != None and fileLocal != ""):
			self.locationInputField.setText(fileLocal)

	def clear_layout(self, layout):
	#Code reference [ https://www.semicolonworld.com/question/58072/clear-all-widgets-in-a-layout-in-pyqt ]
		for i in reversed(range(layout.count())): 
			layout.itemAt(i).widget().setParent(None)
