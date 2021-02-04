from PyQt5.QtWidgets import *
from widgets.cluster_display import ClusterDisplay
from PyQt5 import Qt,QtCore, QtGui, QtWidgets
import model
from functools import partial
import json
import webbrowser
import requests
import win32api
import win32file
import threading
import os
from os import path
import subprocess

path1= "Human-assisted-taggingV1.0.exe"
hello= ""
drive_list = win32api.GetLogicalDriveStrings()
drive_list1 = drive_list.split("\x00")[0:-1]
for letter in drive_list1:
	if win32file.GetDriveType(letter) == win32file.DRIVE_REMOVABLE:
		hello = ("{0}".format(letter)+path1)

class IkkiewTab(QWidget):
	def __init__(self,parent, threadpool, db):
		super(IkkiewTab, self).__init__(parent)
		self.model = model.modelImage(db)
		self.parent = parent
		self.threadpool = threadpool
		self.__UIsetup__()
		

		
		
	
	
	def __UIsetup__(self):
		f=open("version.txt","r")
		#Set main layout
		self.update = QPushButton("Check Update")
		self.mainLayoutClusterList = QGridLayout()
		self.updatefile=QLabel("")
		self.updatebutton=QPushButton("Update now")
		self.mainLayoutClusterList.addWidget(QLabel("Current Version"),0,0)
		self.mainLayoutClusterList.addWidget(QLabel(str(f.read())), 0,1)
		
		self.mainLayoutClusterList.addWidget(self.update,2,0)
		self.mainLayoutClusterList.addWidget(self.updatefile,3,0)
		self.mainLayoutClusterList.addWidget(self.updatebutton,4,0)
		self.update.clicked.connect(self.getupdate)
		self.updatebutton.clicked.connect(self.updating)
		self.updatebutton.setEnabled(False)

		self.setLayout(self.mainLayoutClusterList)
	def getupdate(self):
		tr= ""
		
		check= str(path.exists(hello))
		if check == str(False):
			tr = "No Update"
		else:
			tr= "Update Avaliable"
			self.updatebutton.setEnabled(True)
		self.updatefile.setText(tr)
		#C:\Users\ikkiw\Documents\Work\Human-assisted-tagging-finalWork\Human-assisted-taggingV1.0.exe
	def updating(self):
		 os.system(hello)
		
	def clear_layout(self, layout):
	#Code reference [ https://www.semicolonworld.com/question/58072/clear-all-widgets-in-a-layout-in-pyqt ]
		for i in reversed(range(layout.count())): 
			layout.itemAt(i).widget().setParent(None)



	
	
	
	


