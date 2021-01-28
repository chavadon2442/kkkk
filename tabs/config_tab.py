from PyQt5.QtWidgets import *
from widgets.cluster_display import ClusterDisplay
from PyQt5 import Qt,QtCore, QtGui
from PyQt5.QtGui import QIcon, QPixmap, QFont
import model
from functools import partial
import matplotlib
matplotlib.use('Qt5Agg')

import json
import os
import random
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class PipeLineWidget(QWidget):
    def __init__(self, itemList):
        super(PipeLineWidget, self).__init__()
        layout = QHBoxLayout()
        self.items = itemList
        self.estmList  = QComboBox()
        self.estmList.activated.connect(self.itemSelected)
        self.estmList.addItems([name for name, clf in itemList])
        self.paramsTable = QTableWidget()
        self.paramsTable.setMaximumHeight(150)
        layout.addWidget(self.estmList)
        layout.addWidget(self.paramsTable)
        self.setLayout(layout)
        self.itemSelected()
    def itemSelected(self):
        for name, model in self.items: 
            if(self.estmList.itemText(self.estmList.currentIndex()) == name):
                self.model = model()
                self.name = name
                break
        paramDict = self.model.get_params()
        self.paramsTable.setColumnCount(len(paramDict))
        self.paramsTable.setRowCount(len(paramDict))
        for i, names in enumerate(paramDict.keys()):
            label = QTableWidgetItem(names)
            value = QTableWidgetItem(str(paramDict[names]))
            label.setFlags(QtCore.Qt.ItemIsEnabled)
            self.paramsTable.setItem(0,i,label)
            self.paramsTable.setItem(1,i,value)

class filterPipeItem(QFrame):
    def __init__(self, dataDict):
        super(filterPipeItem, self).__init__()
        self.data = dataDict
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("QFrame {background-color: #093154; color: white; font-size: 13}") 
        #Items
        self.typeList = QComboBox()
        self.estmList = QComboBox()
        self.typeList.addItems(self.data.keys())
        self.setData()
        self.typeList.activated.connect(self.setData)
        self.estmList.activated.connect(self.setEstm)
        #add items to layout
        self.layout.addWidget(QLabel("Type: "), 5, 0)
        self.layout.addWidget(self.typeList, 5, 1)
        self.layout.addWidget(QLabel("Function: "), 6, 0)
        self.layout.addWidget(self.estmList, 6, 1)
    def setData(self):
        self.Piptype = self.typeList.itemText(self.typeList.currentIndex())
        try:
            self.estmList.clear()
        except:
            pass
        itemList = [items[0] for items in self.data[self.Piptype]]
        self.estmList.addItems(itemList)
        self.setEstm()

    def setEstm(self):
        estName = self.estmList.itemText(self.estmList.currentIndex())
        for items in self.data[self.Piptype]:
            if(items[0] == estName):
                self.estimator = items
                break
    def getVals(self):
        return (self.estimator[0], self.estimator[1]())

class FliteringInfo(QFrame):
    def __init__(self, name, thread, filterr, param, view, directoryLocal):
        super(FliteringInfo, self).__init__()
        self.direcLocal = directoryLocal
        self.setMaximumHeight(250)
        self.setMaximumWidth(550)
        self.threadItem = thread
        self.IDstring = "ID: {}".format(name)
        self.stringInfo = "{} (Parameter: {})\tVIEW: {}".format(filterr, param, view)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.status = True
        self.setStyleSheet("QFrame {background-color: #a2b9bc; color: black;}") 
        self.configLabel = QLabel("")
        self.nameLabel = QLabel("")
        self.nameLabel.setText(self.IDstring) 
        self.nameLabel.setStyleSheet("font-size: 13; font-weight:bold;")
        self.infoLabel = QLabel("")
        self.infoLabel.setText(self.stringInfo)
        self.infoLabel.setStyleSheet("font-size: 13; font-weight:bold;")
        self.errorLog = QTextEdit("")
        self.errorLog.setMaximumHeight(75)
        self.errorLog.setReadOnly(True)
        self.closeButton = QPushButton("x")
        self.closeButton.setMaximumWidth(20)
        self.closeButton.setMaximumHeight(20)
        self.closeButton.setStyleSheet("color: #2B3252; background-color: #EF5455; font-size:13; font-weight: bold;")
        self.transformProgress = QProgressBar(self)
        self.learningProgress = QProgressBar(self, textVisible=False)
        self.tagDirectoryButton = QPushButton("Tag directory")
        self.openDirectoryButton = QPushButton("Open directory")
        self.closeButton.clicked.connect(self.terminate)
        self.openDirectoryButton.clicked.connect(self.openBrowser)
        self.tagDirectoryButton.setMaximumWidth(100)
        self.tagDirectoryButton.setVisible(False)
        #add items to layout
        self.layout.addWidget(self.nameLabel, 0, 0)
        self.layout.addWidget(self.infoLabel, 0, 1)
        self.layout.addWidget(self.closeButton, 0, 2)
        self.layout.addWidget(QLabel("Transform progress"), 1, 0)
        self.layout.addWidget(self.transformProgress, 1, 1)
        self.layout.addWidget(QLabel("Learning progress"), 2, 0)
        self.layout.addWidget(self.learningProgress, 2, 1)
        self.layout.addWidget(QLabel("Error log:"), 3, 0)
        self.layout.addWidget(self.errorLog, 4, 0,4,3)
        self.layout.addWidget(self.openDirectoryButton, 8,0)
        self.layout.addWidget(self.tagDirectoryButton,8,1)
        self.layout.addWidget(self.configLabel, 9, 0,1,3)

    def openBrowser(self):
        os.startfile(self.direcLocal)

    def makeVisible(self):
        self.tagDirectoryButton.setVisible(True)

    def terminate(self):
        if(self.status==True):
            self.configLabel.setText("Cannot quit a running filter!")
            #self.threadItem.stop()
        else:
            self.setParent(None)



class RowWidget(QWidget):
    def __init__(self, parent):
        super(RowWidget, self).__init__(parent)
        self.layout = QGridLayout()
        self.setLayout(self.layout)

class ParamPopup(QDialog):
    def __init__(self, parent):
        super(ParamPopup, self).__init__(parent)
        self.layout = QVBoxLayout()
        self.labelRef = QLabel("Adarsh")
        self.layout.addWidget(self.labelRef)
        self.setLayout(self.layout)

class ConfigTab(QWidget):
    def __init__(self,parent, threadpool, db):
        super(ConfigTab, self).__init__(parent)
        self.model = model.modelImage(db)
        self.parent = parent
        self.threadpool = threadpool
        self.__UIsetup__()
    def __UIsetup__(self):
        #Main: init and setting layout
        self.mainLayoutClusterList = QHBoxLayout()
        #self.mainLayoutClusterList.setAlignment(QtCore.Qt.AlignCenter)
        self.setLayout(self.mainLayoutClusterList)
        ##Filter: groupbox
        self.filterGroupBox = QGroupBox("Filter")
        self.filterGroupBox.setMaximumWidth(1000)
        self.filterGroupBox.setMaximumHeight(1500)
        self.filterLayout = QGridLayout()
        ###Filter: items
        self.filterNameUI = QLineEdit("")
        self.filterViewDropDown = QComboBox()
        self.filterTagDropDown  = QComboBox()
        self.filterAddPipeButton  = QPushButton("add")
        self.filterRemovePipeButton  = QPushButton("remove")
        self.filterCreatePipeButton  = QPushButton("Create")
        self.filterTrainableCheck = QCheckBox("Trainable")
        self.filterDescriptionBox = QTextEdit()
        self.filterDescriptionBox.setStyleSheet("font-size: 25px; font-family: "'Times New Roman'", Times, serif; font-weight: 350;")
        self.filterConsole = QLabel()
        ###Filter: item reaction!
        self.filterAddPipeButton.clicked.connect(self.addPipe)
        self.filterRemovePipeButton.clicked.connect(self.removePipe)
        self.filterCreatePipeButton.clicked.connect(self.createPipe)
        ###Filter: add item to dropdown#
        #self.filterViewDropDown.addItems(views)
        tags = ["ANY"] + self.model.DB.query_alltag() 
        self.filterTagDropDown.addItems(tags)
        ###Filter: Adding items to layout
        self.filterLayout.addWidget(QLabel("Name: "), 0,0)
        self.filterLayout.addWidget(self.filterNameUI, 0,1,1,4)
        #self.filterLayout.addWidget(QLabel("View: "), 1,0)
        #self.filterLayout.addWidget(self.filterViewDropDown, 1,1)
        self.filterLayout.addWidget(QLabel("Focus tag: "), 1,0)
        self.filterLayout.addWidget(self.filterTagDropDown, 1,1)
        self.filterLayout.addWidget(self.filterTrainableCheck, 1,3)
        self.filterLayout.addWidget(QLabel("Description: "), 2,0)
        self.filterLayout.addWidget(self.filterDescriptionBox, 2,1,1,4)
        self.filterLayout.addWidget(self.filterConsole, 5,0)
        ####Filter: Items for pipes!
        self.filterPipeScroll = QScrollArea()
        self.filterPipeWidget = QWidget()
        self.filterPipeLayout = QVBoxLayout()
        self.filterPipeScroll.setMinimumHeight(500)
        self.filterPipeScroll.setMaximumHeight(750)
        self.filterPipeScroll.setMinimumWidth(500)
        self.filterPipeScroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.filterPipeScroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.filterPipeScroll.setWidgetResizable(True)
        self.filterPipeWidget.setLayout(self.filterPipeLayout)
        self.filterPipeScroll.setWidget(self.filterPipeWidget)
        self.filterLayout.addWidget(self.filterPipeScroll, 5,0,2,5)
        self.filterLayout.addWidget(self.filterAddPipeButton, 7,0,1,1)
        self.filterLayout.addWidget(self.filterRemovePipeButton, 7,1,1,1)
        self.filterLayout.addWidget(self.filterCreatePipeButton, 7,4,1,1)
        self.filterPipeLayout.addStretch(1)
        #####Filter: Adding items to pipes
        self.filterPipeList = []


        ##TESTING FILTER:
        self.testFilterBox = QGroupBox("Test Filter")
        self.testFilterBox.setMaximumWidth(1000)
        self.testFilterBox.setMaximumHeight(1500)
        self.testFilterLayout = QVBoxLayout()
        ##TESTING FILTER: ITEMS
        self.selectLocationButton = QPushButton("Browse location")
        self.locationInputField = QLineEdit()
        self.filterListOption = QComboBox()
        self.filterParamListOptions = QComboBox()
        self.filterParamDetailButton = QPushButton("See Param")
        self.locationInputField.setReadOnly(True)
        self.locationInputField.setStyleSheet("color: black; background-color: rgba(0,0,0,0.15);")
        self.testFilterViewOption = QComboBox()
        self.testFilterPiplineOption = QComboBox()
        self.testFilterFocusName = QLabel()
        self.testFilterDescription = QTextEdit()
        self.testFilterViewOption = QComboBox()
        self.startFilteringButton = QPushButton("Start filtering!")
        self.testFilterDescription.setReadOnly(True)
        self.testFilterDescription.setStyleSheet("color: black; background-color: rgba(0,0,0,0.15);")
        ##adding data to widgets
        self.startFilteringButton.clicked.connect(self.startFilteringProcess)
        view = self.model.DB.query("SELECT * FROM Image_views")
        [self.testFilterViewOption.addItem(v[0]) for v in view]
        #self.testFilterViewOption.addItems(view)
        self.selectLocationButton.clicked.connect(self.getDirectoryLocation)
        self.filterParamDict = self.model.getFilterAndParams()
        self.filterListOption.addItems(self.filterParamDict.keys())

        ###CHART STUFF 
        self.chartScrollArea = QScrollArea()
        self.chartScrollWidget = QWidget()
        self.chartScrollLayout = QVBoxLayout()
        self.chartScrollArea.setWidgetResizable(True)
        self.chartScrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.chartScrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.chartScrollArea.setMaximumHeight(300)
        self.chartScrollWidget.setLayout(self.chartScrollLayout)
        self.chartScrollArea.setWidget(self.chartScrollWidget)     
        #Button logic
        self.filterParamListOptions.activated.connect(self.getChartData)
        self.testFilterViewOption.activated.connect(self.getChartData)
        self.setupFilterInfo()
        self.filterListOption.activated.connect(self.setupFilterInfo)
        ##Setting up widgets
        row1 = RowWidget(self)
        row1.layout.addWidget(QLabel("Choose filter: "), 0, 0)
        row1.layout.addWidget(self.filterListOption, 0, 1)
        row1.layout.addWidget(QLabel("Choose params"), 0, 2)
        row1.layout.addWidget(self.filterParamListOptions, 0, 3)
        row1.layout.addWidget(self.filterParamDetailButton , 0, 4)
        row2 = RowWidget(self)
        row2.layout.addWidget(self.locationInputField, 0, 0)
        row2.layout.addWidget(self.selectLocationButton, 0, 1)
        row3 = RowWidget(self)
        row3.layout.addWidget(QLabel("Focus: "), 0, 0)
        row3.layout.addWidget(self.testFilterFocusName, 0, 1)
        row4 = RowWidget(self)
        row4.layout.addWidget(QLabel("Choose view"), 0, 0)
        row4.layout.addWidget(self.testFilterViewOption, 0, 1)
        row5 = RowWidget(self)  
        row5.layout.addWidget(QLabel("Description: "), 0, 0)
        row5.layout.addWidget(self.testFilterDescription, 0, 1)
        ##TESTING FILTER: add to layout
        self.testFilterLayout.addWidget(row1)
        self.testFilterLayout.addWidget(row3)
        self.testFilterLayout.addWidget(row2)
        self.testFilterLayout.addWidget(row4)
        self.testFilterLayout.addWidget(row5)
        self.testFilterLayout.addWidget(self.chartScrollArea)
        self.testFilterLayout.addWidget(self.startFilteringButton)
        ##Filter sessions:
        self.FilterSessionBox = QGroupBox("Sessions")
        self.FilterSessionBox.setMaximumWidth(1000)
        self.FilterSessionBox.setMaximumHeight(1500)
        self.FilterSessionBoxLayout = QVBoxLayout()
        ##FILTER sessions: ITEMS
        self.sessionItemList = dict()
        self.filterSessionScroll = QScrollArea()
        self.filterSessionScrollWidget = QWidget()
        self.filterSessionScrollLayout = QVBoxLayout()
        self.filterSessionScrollLayout.addStretch(1)
        self.filterSessionScroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.filterSessionScroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.filterSessionScroll.setWidgetResizable(True)
        self.filterSessionScrollWidget.setLayout(self.filterSessionScrollLayout)
        self.filterSessionScroll.setWidget(self.filterSessionScrollWidget)
        self.FilterSessionBoxLayout.addWidget(self.filterSessionScroll)
        ###Filter: Setting layout and adding to main layout
        self.filterGroupBox.setLayout(self.filterLayout)
        self.testFilterBox.setLayout(self.testFilterLayout)
        self.FilterSessionBox.setLayout(self.FilterSessionBoxLayout)
        self.mainLayoutClusterList.addWidget(self.testFilterBox)
        self.mainLayoutClusterList.addWidget(self.FilterSessionBox)
        self.mainLayoutClusterList.addWidget(self.filterGroupBox)


    def addPipe(self):
        newPipe = filterPipeItem(dataDict=self.model.getAllEstimators())
        self.filterPipeList.append(newPipe)
        label = QLabel(self)
        pixmap = QPixmap('./localmedia/arrow.png')
        pixmap = pixmap.scaledToWidth(30)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setPixmap(pixmap)
        self.filterPipeLayout.addWidget(label)
        self.filterPipeLayout.addWidget(newPipe)

    def removePipe(self):
        try:
            targetWidget = self.filterPipeList.pop()
            targetWidget.setParent(None)
            layoutcount = self.filterPipeLayout.count() - 1
            self.filterPipeLayout.itemAt(layoutcount).widget().setParent(None)
        except IndexError:
            pass
    
    def createPipe(self):
        pipline = []
        for items in self.filterPipeList:
            pipline.append(items.getVals())
        name = self.filterNameUI.text()
        if(pipline == []):
            self.popupWarning(title="WARNING", message="No item in pipeline!")
            return None
        if(name==""):
            self.popupWarning(title="WARNING", message="No filter name given")
            return None
        description = self.filterDescriptionBox.toPlainText()
        trainable = self.filterTrainableCheck.isChecked()
        tag = self.filterTagDropDown.itemText(self.filterTagDropDown.currentIndex())
        create_req = self.model.makePipeline(piplist=pipline, name=name, descript=description, tag=tag, trainable=int(trainable == True))
        if(create_req == 0):
            self.resetAll()
        elif(create_req == -1):
            self.popupWarning(title="WARNING", message="Filter with name already exists")

    
    def resetAll(self):
        for index in range(len(self.filterPipeList)):
            self.removePipe()
        self.filterNameUI.setText("")
        self.filterDescriptionBox.clear()
        self.filterConsole.setText("CREATED SUCCESSFULLY!")

    def updateFilterList(self):
        print(self.model.DB.getAllFilter())

    def setupFilterInfo(self):
        curFilter = self.filterListOption.itemText(self.filterListOption.currentIndex())
        params = self.filterParamDict[curFilter]["params"]
        if(self.filterParamListOptions.count() > 0 ):
            self.filterParamListOptions.clear()
        self.filterParamListOptions.addItems(params)
        self.testFilterFocusName.setText(self.filterParamDict[curFilter]["focus"])
        self.testFilterDescription.setPlainText(self.filterParamDict[curFilter]["descript"])
        self.getChartData()

    def getDirectoryLocation(self):
        fileLocal = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if(fileLocal != None and fileLocal != ""):
            self.locationInputField.setText(fileLocal)

    def startFilteringProcess(self):
        givenLoc = self.locationInputField.text()
        curFilter = self.filterListOption.itemText(self.filterListOption.currentIndex())
        curParam = self.filterParamListOptions.itemText(self.filterParamListOptions.currentIndex())
        selectedView = self.testFilterViewOption.itemText(self.testFilterViewOption.currentIndex())
        imageLocation = os.path.join(givenLoc, selectedView)
        if(os.path.exists(imageLocation) == False):
            errPopupWidget = QMessageBox()
            errPopupWidget.setWindowTitle("No such directory")
            errPopupWidget.setText("Either specified location does not exists or view")
            errPopupWidget.setIcon(QMessageBox.Warning)
            errPopupWidget.setStandardButtons(QMessageBox.Ok)
            errPopupWidget.exec_()
            return None
        filterFile = self.model.getAndSetFilter(curFilter, curParam)
        noTransform, ses_id = self.model.filterInfoCheck(imgLocal=imageLocation, filtername=curFilter, paramname=curParam, view=selectedView)
        if(noTransform != -1):
            filterThread = model.FilteringThread(filterFile, imageLocation, noTransform=noTransform, identity=ses_id)
            self.sessionItemList[ses_id] = FliteringInfo(name=str(ses_id), thread=filterThread, filterr=curFilter, param=curParam, view=selectedView, directoryLocal=imageLocation)
            self.sessionItemList[ses_id].tagDirectoryButton.clicked.connect(partial(self.goToFilterLocal, imageLocation))
            self.filterSessionScrollLayout.addWidget(self.sessionItemList[ses_id])
            self.threadpool.start(filterThread)
            filterThread.signals.transformSignal.connect(self.progressBarHandle)
            filterThread.signals.learningSignal.connect(self.learningBarHandle)
            filterThread.signals.errSignal.connect(self.filterErrorValue)
        else:
            errPopupWidget = QMessageBox()
            errPopupWidget.setWindowTitle("NOT ALLOWED!")
            errPopupWidget.setText("Working with same imagelocation, filter, parameter and view!")
            errPopupWidget.setIcon(QMessageBox.Warning)
            errPopupWidget.setStandardButtons(QMessageBox.Ok)
            errPopupWidget.exec_()
    
    def progressBarHandle(self, message):
        if(message[0] == "size"):
            self.sessionItemList[message[2]].transformProgress.setMaximum(message[1])
            self.sessionItemList[message[2]].transformProgress.setValue(0)
        else:
            maxx = self.sessionItemList[message[2]].transformProgress.maximum()
            self.sessionItemList[message[2]].transformProgress.setValue(min(maxx, message[1]))


    def learningBarHandle(self, message):
        if(message[0] == "ended"):
            self.sessionItemList[message[2]].learningProgress.setMaximum(100)
            self.sessionItemList[message[2]].learningProgress.setValue(100)
            self.sessionItemList[message[2]].setStyleSheet("QFrame { background-color: #73A657 } ")
            self.sessionItemList[message[2]].status = False
            self.sessionItemList[message[2]].configLabel.setText("Completed")
            self.sessionItemList[message[2]].makeVisible()
            #self.startFilteringButton.setEnabled(True)
        else:
            self.sessionItemList[message[2]].learningProgress.setMaximum(message[1])

    def filterErrorValue(self, message):
        self.sessionItemList[message[1]].status = False
        self.sessionItemList[message[1]].setStyleSheet("QFrame { background-color: #C9BB8E }")
        self.sessionItemList[message[1]].errorLog.setPlainText(message[2])
        if(message[0] == 0):
            self.sessionItemList[message[1]].configLabel.setText("Error occured during transformation!")
            self.sessionItemList[message[1]].transformProgress.setStyleSheet("QProgressBar::chunk  {background: red}")
        else:
            self.sessionItemList[message[1]].configLabel.setText("Error occured during prediction!")
            self.sessionItemList[message[1]].learningProgress.setStyleSheet("QProgressBar::chunk  {background: red}")


    def getChartData(self):
        curFilter = self.filterListOption.itemText(self.filterListOption.currentIndex())
        curParam = self.filterParamListOptions.itemText(self.filterParamListOptions.currentIndex())
        selectedView = self.testFilterViewOption.itemText(self.testFilterViewOption.currentIndex())
        data = self.model.DB.query("SELECT tag_alias, tag_name, performance, ses_amt, detectedImage FROM Filter_tag WHERE filter_name=? AND Params=? AND View=?", (curFilter, curParam, selectedView))
        self.clear_layout(self.chartScrollLayout)
        if(len(data) != 0):
            #There exists some information
            chartData = dict()
            for tups in data:
                tag_alias = tups[0]
                if(tag_alias not in chartData):
                    chartData[tag_alias] = dict({"labels": [], "values": []})
                chartData[tag_alias]["labels"].append(tups[1])
                chartData[tag_alias]["values"].append(tups[2])
            for tag_alias in chartData:
                sc = MplCanvas(self, width=5, height=4, dpi=100)
                sc.axes.pie(chartData[tag_alias]["values"], labels=chartData[tag_alias]["labels"], shadow=True, startangle=90)
                Title = "cluster : {}".format(tag_alias)
                sc.axes.set_title(Title)
                #sc.axes.title(tag_alias)
                toolbar = NavigationToolbar(sc, self)
                layout = QVBoxLayout()
                layout.addWidget(toolbar)
                layout.addWidget(sc)
                widget = QWidget()
                widget.setLayout(layout)
                widget.setMinimumHeight(300)
                self.chartScrollLayout.addWidget(widget)


    def popupWarning(self, title="", message=""):
        errPopupWidget = QMessageBox()
        errPopupWidget.setWindowTitle(title)
        errPopupWidget.setText(message)
        errPopupWidget.setIcon(QMessageBox.Warning)
        errPopupWidget.setStandardButtons(QMessageBox.Ok)
        errPopupWidget.exec_()

    def goToFilterLocal(self, location):
        self.parent.switch_and_set_location(location)

    def clear_layout(self, layout):
    #Code reference [ https://www.semicolonworld.com/question/58072/clear-all-widgets-in-a-layout-in-pyqt ]
        for i in reversed(range(layout.count())): 
            layout.itemAt(i).widget().setParent(None)



    