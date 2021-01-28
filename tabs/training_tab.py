from PyQt5.QtWidgets import *
from widgets.cluster_display import ClusterDisplay
from PyQt5 import Qt,QtCore, QtGui
import model
from functools import partial
import json
import os
        
class TrainTab(QWidget):
    def __init__(self,parent, threadpool):
        super(TrainTab, self).__init__(parent)
        self.model = model.modelImage()
        self.parent = parent
        self.threadpool = threadpool
        self.__UIsetup__()
    def __UIsetup__(self):
        self.mainLayoutClusterList = QVBoxLayout()
        self.mainLayoutClusterList.setAlignment(QtCore.Qt.AlignCenter)
        self.trainGroupBox = QGroupBox("Training")
        self.trainGroupBox.setMaximumWidth(1000)
        self.trainGroupBox.setMaximumHeight(1000)
        self.resultGroupBox = QGroupBox("Result")
        self.resultGroupBox.setMaximumWidth(1000)
        self.resultGroupBox.setMaximumHeight(1000)
        
        #Train group box
        trainGroupBoxLayout = QGridLayout()
        trainGroupBoxLayout.addWidget(QLabel("Model (pipeline): "), 0,0)
        trainGroupBoxLayout.addWidget(QLabel("Tags: "), 1,0)
        trainGroupBoxLayout.addWidget(QLabel("Amount: "), 2,0)
        self.modelListWidget = QComboBox()
        trainGroupBoxLayout.addWidget(self.modelListWidget, 0, 1)
        self.tagOptionsWidget = QListWidget()
        self.tagOptionsWidget.setSelectionMode(QListWidget.MultiSelection)
        self.tagOptionsWidget.setMaximumHeight(100)
        trainGroupBoxLayout.addWidget(self.tagOptionsWidget, 1, 1)
        self.tagImgAmountWidget = QComboBox()
        trainGroupBoxLayout.addWidget(self.tagImgAmountWidget, 2, 1)
        self.initLearningButton = QPushButton("Start")
        self.initLearningButton.clicked.connect(self.startPipeProcess)
        trainGroupBoxLayout.addWidget(self.initLearningButton, 3, 0)

        self.fillImgAmtBox()
        self.getAllPipeConfig()
        self.getAllUsedTags()
        self.trainGroupBox.setLayout(trainGroupBoxLayout)
        #Result group box
        resultLayout = QVBoxLayout()
        self.consoleLabel = QLabel("Results will be here......")
        self.consoleLabel.setWordWrap(True)
        resultLayout.addWidget(self.consoleLabel)
        self.resultGroupBox.setLayout(resultLayout)

        self.mainLayoutClusterList.addWidget(self.trainGroupBox)
        self.mainLayoutClusterList.addWidget(self.resultGroupBox)
        self.setLayout(self.mainLayoutClusterList)

    def fillImgAmtBox(self):
        for x in range(50, 500, 50):
            self.tagImgAmountWidget.addItem(str(x))

    def getAllPipeConfig(self):
        for items in self.model.getAllPipeConfig():
            self.modelListWidget.addItem(items)

    def getAllUsedTags(self):
        for tags in self.model.DB.used_tag():
            self.tagOptionsWidget.addItem(tags)
    
    def startPipeProcess(self):
        selectedTag = [item.text() for item in self.tagOptionsWidget.selectedItems()]
        X = []
        y = []
        for tags in selectedTag:
            imgs_list = self.model.DB.image_with_tag([tags])
            X = X + [self.model.findImageAbs(imgs) for imgs in imgs_list]
            y = y + [tags] * len(imgs_list)
        selectedPipeline = self.modelListWidget.itemText(self.modelListWidget.currentIndex())
        selectedPipeline = self.model.getPipeLine(selectedPipeline)
        clusterThread = model.TrainingThread(X, y, selectedPipeline)
        self.threadpool.start(clusterThread)
        clusterThread.signals.performanceOutput.connect(self.updateConsole)
    
    def updateConsole(self, results):
        self.consoleLabel.setText(results)

    def clear_layout(self, layout):
    #Code reference [ https://www.semicolonworld.com/question/58072/clear-all-widgets-in-a-layout-in-pyqt ]
        for i in reversed(range(layout.count())): 
            layout.itemAt(i).widget().setParent(None)
