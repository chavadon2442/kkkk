import os, shutil, string, glob
import random
import cv2
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import classification_report
from sklearn.utils import all_estimators
import numpy as np
import json
from PyQt5 import Qt,QtCore, QtGui
from clusterLogic.model import View_cluster
from clusterLogic.PipeModules import Functions
import time
import subprocess
from psutil import virtual_memory
# from DB import AppDB
from DB2 import databaseManager
from sklearn.pipeline import Pipeline, make_pipeline
import joblib 
import inspect
from sklearn.model_selection import train_test_split
import copy
import traceback

class cluster:
	def __init__(self):
		self.paths = []
		self.images = []
		self.imgAmtRequired = 30
	def addPath(self, path):
		self.paths.append(path)
	def addImages(self):
		amtFromEach = self.imgAmtRequired//len(self.paths)
		for path in self.paths:
			imgs = os.listdir(path)
			try:
				self.images = self.images +  random.sample(imgs, amtFromEach)
			except:
				self.images = self.images + imgs
			for i,localImgPath in enumerate(self.images):
				self.images[i] = os.path.join(path, localImgPath)
		self.imgAmt = len(self.images)

	def removeImages(self, index):
		self.images.pop(index)
		self.imgAmt -= 1
		if(len(self.images) < 1 and self.getClusterLen() > 0):
			self.addImages()

	def getClusterLen(self):
		clusterLen = 0
		for paths in self.paths:
			clusterLen += len(os.listdir(paths))
		return clusterLen


class modelImage:
	def __init__(self, DB):
		self.storageLocation = "./systeminformation/"
		self.configLocation = "./systeminformation/Config"
		self.modelLocation = "./systeminformation/models"
		self.DB = DB
	def get_cluster_list(self, listLocation):
		pass
	def request_cluster_images(self, clusterLocation, amount="all"):
		imageDict = dict()
		clusters = os.listdir(clusterLocation)
		self.storeInfo(clusterPath=clusterLocation,clusterList=clusters)
		for cluster in clusters:
			clusterImages = os.listdir(clusterLocation+"\\"+cluster)
			clusterLen = len(clusterImages)
			if(amount=="all"):
				amount = clusterLen
			imageDict[cluster] = [clusterLocation+"\\"+cluster+"\\"+clusterImages[random.randint(0,clusterLen-1)] for i in range(amount)]
		return imageDict

	def request_dissimilar_images(self, clusterName):
		#[ (imagelocation, percentageDissimilar), (imagelocation, percentageDissimilar), (imagelocation, percentageDissimilar)... ]
		pass

	def get_cluster_image(self,clusterName,amount=1):
		data = self.getInfo()
		filePath =  data["clusterPath"] + "\\" + clusterName + "\\"
		return filePath + random.choice(os.listdir(filePath))


	def storeInfo(self, clusterPath, clusterList):
		data = dict()
		data["clusters"] = clusterList
		data["clusterPath"] = clusterPath
		with open(self.storageLocation, 'w') as outputfile:
			json.dump(data, outputfile)

	def getInfo(self):
		with open(self.storageLocation)  as inputFile:
			data = json.load(inputFile)
		return data

	def request_dissimilar_images(self, clusterName):
		#[ (imagelocation, percentageDissimilar), (imagelocation, percentageDissimilar), (imagelocation, percentageDissimilar)... ]
		pass

	def quant(self,image,cluster,isArr):
		if(not isArr):
			image = cv2.imread(image)
		(h,w) = image.shape[:2]
		image = image.reshape((image.shape[0] * image.shape[1], 3))
		clt = MiniBatchKMeans(n_clusters = 4)
		labels = clt.fit_predict(image)
		quant = clt.cluster_centers_.astype("uint8")[labels]
		quant = quant.reshape((h, w, 3))
		image = image.reshape((h, w, 3))
		quantized_image = np.hstack([image, quant])
		return quant


	def brightness(self, image, isArr=False, alpha=1.0, beta=0.0):
		if(not isArr):
			image = cv2.imread(image)
		result = cv2.addWeighted(image,alpha,np.zeros(image.shape,image.dtype),0,beta)		
		return result


	def getAllClusterLocal(self):
		with open(self.storageLocation + "cluster_info.json") as configData:
			information = json.load(configData)
			MAINPATH =  information["cluster_locations"]
		return MAINPATH
		
	def get_views_clusters(self, MAINPATH):
		#GET ALL DIRECTORIES
		VIEWS = [files  for files in os.listdir(MAINPATH) if files.find(".") == -1]
		VIEW_AND_CLUSTERS = dict()
		for directs in VIEWS:
		    VIEW_PATH  = os.path.join(os.path.abspath(MAINPATH), directs)
		    CLUSTERS = dict({})
		    #get all cluster of particular view
		    for root, subdirs, files in os.walk(VIEW_PATH):
		        for items in files:
		            if(items.find(".tiff") != -1):
		                clusterName = root.split("\\")[-1]
		                if(clusterName not in CLUSTERS):
		                    CLUSTERS[clusterName] = cluster()
		                CLUSTERS[clusterName].addPath(root)
		                break
		    #set up images for that cluster
		    for cls in CLUSTERS:
		        CLUSTERS[cls].addImages()
		    VIEW_AND_CLUSTERS[directs] = CLUSTERS
		return VIEW_AND_CLUSTERS

	def getAllConfigs(self):
		returnVAl = {}
		for conf in os.listdir(self.configLocation):
			with open(os.path.join(self.configLocation, conf)) as values:
				#confName = conf[:conf.find(".")]
				values = json.load(values)
				returnVAl[conf] = values
		return returnVAl

	def tagCluster(self, view, paths, tag):
		with open(os.path.join(self.storageLocation, "cluster_info.json")) as data:
			data = json.load(data)
			tagLocation = data["datasetLocation"]
		view_loc = os.path.join(tagLocation, view)
		#Check if view location exists (if not create the directory)
		if not os.path.exists(view_loc):
			os.mkdir(view_loc)
		for pt in paths:
			allImgs = os.listdir(pt)
			allImgs = [os.path.join(pt, imgName) for imgName in allImgs]
			for imgPath in allImgs:
				imgFileName = os.path.split(imgPath)[-1]
				self.DB.tag_image(imgFileName, tag)
				shutil.move(imgPath, view_loc)
			os.rmdir(pt)

	def tagImage(self, view, imgLoc, tag):
		with open(os.path.join(self.storageLocation, "cluster_info.json")) as data:
			data = json.load(data)
			tagLocation = data["datasetLocation"]
		imgFileName = os.path.split(imgLoc)[-1]
		view_loc = os.path.join(tagLocation, view)
		#Check if view location exists (if not create the directory)
		if not os.path.exists(view_loc):
			os.mkdir(view_loc)
		try:	
			self.DB.tag_image(imgFileName, tag)
			shutil.move(imgLoc, view_loc)
			return True
		except:
			return False

	def validLocationCheck(self, location):
		try:
			os.listdir(location)
			return True
		except:
			return False
	
	def addClusterLocation(self, location):
		with open("./systeminformation/cluster_info.json", "r+") as configData:
			information = json.load(configData)
			if(os.path.normcase(location) not in [os.path.normcase(pts) for pts in information["cluster_locations"]]):
				information["cluster_locations"].append(location)
			configData.seek(0)
			configData.truncate(0)
			json.dump(information, configData)
	
	def structureFile(self):
		mem = virtual_memory()
		print(mem.total)  # total physical memory available

	def createNewConfig(self, name, mapVal):
		configName = "./systeminformation/Config/{}.json".format(name)
		try:
			with open(configName, "x") as newConfigFile:
				json.dump(mapVal, newConfigFile)
			return True
		except:
			return False

	def getAllEstimators(self):
		datas = dict({})
		for predic in ['classifier', 'cluster', 'transformer']:
			datas[predic] = all_estimators(type_filter=predic)
		madeFunctions = []
		for name, obj in inspect.getmembers(Functions, inspect.isclass):
			if(obj.__module__ == "clusterLogic.PipeModules.Functions" and name != "ImgPathToRGB"):
				madeFunctions.append((name,obj))
		datas["User created"] = madeFunctions
		return datas
		
	def makePipeline(self, piplist, name, descript, tag, trainable):
		filename = name + ".joblib"
		try:
			self.DB.modifyTable("INSERT into Filter VALUES (?,?,?,?)", (name, tag, descript, trainable))
			piplist = [("ImgPathToRGB", Functions.ImgPathToRGB())] + piplist
			pipModel = Pipeline(piplist)
			paramDict = pipModel.get_params()
			joblib.dump(pipModel,os.path.join(self.modelLocation, filename))
			paramLoc = os.path.join(self.modelLocation, name)
			if (os.path.exists(paramLoc) == False):
				os.mkdir(paramLoc)
			filename = os.path.join(paramLoc, "DEFAULT_PARAMS.joblib")
			joblib.dump(paramDict, filename)
			#self.DB.createNewFilter(pipName=name,view=view, tag=tag, description=descript, trainable=int(trainable == True))
		except:
			return -1
		return 0
	def getAllPipeConfig(self):
		return os.listdir(self.modelLocation)

	def getPipeLine(self, filename):
		return joblib.load(os.path.join(self.modelLocation, filename))

	def findImageAbs(self, filename):
		""" Given a search path, find file with requested name """
		with open(os.path.join(self.storageLocation, "cluster_info.json")) as data:
			data = json.load(data)
			search_path = data["datasetLocation"]
		for im in glob.glob(search_path + '/**/*.tiff', recursive=True):
			imname = os.path.split(im)[-1]
			if(filename == imname):
				return im
	
	def getFilterAndParams(self):
		filterList = self.DB.query("SELECT * FROM Filter")
		filterParamDict = dict({})
		for filters in filterList:
			fitlerName = filters[0]
			filterInfo = dict({})
			filterInfo["focus"] = filters[1]
			filterInfo["descript"] = filters[2]
			params = os.listdir(os.path.join(self.modelLocation, fitlerName))
			filterInfo["params"] = params
			filterParamDict[fitlerName] = filterInfo
		return filterParamDict

	def getAndSetFilter(self, filtername, paramname):
		choosenFilter = joblib.load(os.path.join(self.modelLocation, filtername) + ".joblib")
		choosenParam  = joblib.load(os.path.join(self.modelLocation, filtername, paramname))
		choosenFilter.set_params(**choosenParam)
		return choosenFilter
	
	def filterInfoCheck(self, imgLocal, filtername, paramname, view):
		filename = ".cainfo"
		filePath = os.path.join(imgLocal, filename) # C:/images/bottom/.cainfo
		sameParam = False # at first we assume filter and view is different
		if(os.path.exists(filePath) == True): # location has been filtered before
			with open(filePath, "r") as signature:
				ses_id = signature.readline().splitlines()[0]
			oldFilt, oldView, oldParam = self.DB.query("SELECT filter_name, View, Params FROM Filter_Session WHERE sesID=?", (ses_id,))[0]
			if(oldFilt == filtername and oldView == view):
				if(oldParam != paramname):
					oldParamFile = joblib.load(os.path.join(self.modelLocation, filtername, oldParam))
					newParamFile = joblib.load(os.path.join(self.modelLocation, filtername, paramname))
					sameParam = self.checkIfParamNotEq(oldParamFile, newParamFile)
				else:
					return (-1, ses_id) #Why are you using the same filter, view and params??? result will be same!
		ses_id = self.DB.modifyTable("INSERT into Filter_Session(filter_name, View, Params, time, image_amount) VALUES (?,?,?,?,?)", (filtername, view, paramname, 0, 0))
		with open(filePath, "w") as signature:
			signature.write(str(ses_id))
			signature.write(os.linesep)
		return (sameParam, ses_id)
	
	def getSesInformation(self, filepath):
		with open(filepath, "r") as signature:
			ses_id = signature.readline().splitlines()[0]
		return self.DB.query("SELECT filter_name, View, Params FROM Filter_Session WHERE sesID=?", (ses_id,))[0]

	def checkIfParamNotEq(self, oldParamFile, newParamFile):
		for components in oldParamFile["steps"][:-1]:
			#componentName == name of the steps in pipeline
			componentName = components[0]
			for keys in oldParamFile.keys():
				if(keys.find(componentName + "__") >= 0):
					if(newParamFile[keys] != oldParamFile[keys]):
						return False
		return True
	
	def tag_image_trivial(self, imgPath, tag):
		with open("./systeminformation/cluster_info.json", "r") as configData:
			information = json.load(configData)
			storageLocation = information["final_datasetLocation"]
		imgName = os.path.split(imgPath)[-1]
		view = imgName.split("_")[0]
		viewLoc = os.path.join(storageLocation, view)
		if(os.path.exists(viewLoc) == False):
			os.mkdir(viewLoc)
		tagLoc = os.path.join(viewLoc, tag)
		if(os.path.exists(tagLoc) == False):
			os.mkdir(tagLoc)
		shutil.move(imgPath, tagLoc)
		
class threadSignals(QtCore.QObject):
	finished = QtCore.pyqtSignal()
	updateInfo = QtCore.pyqtSignal(str)
	performanceOutput = QtCore.pyqtSignal(str)


class filterSignals(QtCore.QObject):
	transformSignal = QtCore.pyqtSignal(tuple)
	learningSignal = QtCore.pyqtSignal(tuple)
	errSignal = QtCore.pyqtSignal(tuple)
	"""
	errSignal ==> 0-transform err
				  1-prediction err
	"""


class ClusteringThread(QtCore.QRunnable):
	def __init__(self,path,structure,configFile):
		super(ClusteringThread, self).__init__()
		self.path = path
		self.structure = structure
		self.configFile = configFile
		self.model = modelImage()
		self.signals = threadSignals()
		self.configLocation = "./systeminformation/Config" ###########EITHER STORE CONFIG LOCATION SOMEWHERE OR MAKE IT FIXED##########################
	@QtCore.pyqtSlot()
	def run(self):
		configFileName = os.path.join(self.configLocation,self.configFile) 
		with open(configFileName) as vwConfig:
			vwConfig = json.load(vwConfig)
		all_views = [os.path.join(self.path,vw) for vw in os.listdir(self.path) if vw.find(".") == -1]
		os.startfile(self.path) # Does not work on linux! 
		self.model.addClusterLocation(self.path)
		with open("./systeminformation/cluster_info.json", "r+") as configData:
			information = json.load(configData)
			if(os.path.normcase(self.path) not in [os.path.normcase(pts) for pts in information["cluster_locations"]]):
				information["cluster_locations"].append(self.path)
			configData.seek(0)
			configData.truncate(0)
			json.dump(information, configData)

		for viewPath in all_views:
			vwName = os.path.split(viewPath)[-1] # get tail of path
			update = "Working on "+ vwName
			self.signals.updateInfo.emit(update)
			self.signals.updateInfo.emit("{} ==CONFIG==> {}".format(vwName, vwConfig[vwName]))
			vwClass = View_cluster(vwName, viewPath, self.signals)
			vwClass.START(model=vwConfig[vwName]["model"], isSave=vwConfig[vwName]["isSave"], k=vwConfig[vwName]["k"], focusPoint=vwConfig[vwName]["focusPoint"])
		self.signals.finished.emit()



class FilteringThread(QtCore.QRunnable):
	def __init__(self, pipeline, location, noTransform, identity):
		super(FilteringThread, self).__init__()
		self.pipline = pipeline
		self.imageLocal = location
		self.signals = filterSignals()
		self.imgArrFileName = "imgArr.data"
		self.noTransform = noTransform
		self.identity = identity
		self.threadactive = True
	@QtCore.pyqtSlot()
	def run(self):
		try:
			imgList = self.imageList()
			learnPipline = self.pipline[-1]
			learnPipline.set_params(verbose=True)
			transformArr = []
			imgArrFileLoc = os.path.join(self.imageLocal, self.imgArrFileName)
			self.signals.transformSignal.emit(("size", len(imgList), self.identity))
			if(self.noTransform == False or os.path.exists(imgArrFileLoc) == False):
				self.cleanOldArrFile()
				transformPipline = self.pipline[:-1]
				transformPipline.set_params(verbose=True)
				batchSize = 10
				for i in range(0, len(imgList), batchSize):
					imgBatch = imgList[i:i+batchSize]
					batchTransform = transformPipline.transform(imgBatch)
					transformArr += batchTransform.tolist()
					#Saving the array in a file
					self.saveImgInfo(imgList=imgBatch, imgArrList=batchTransform)
					#Inform user about completion of batch transformation
					self.signals.transformSignal.emit(("comp", i + batchSize, self.identity))
			else:
				transformArr = self.getSavedImageData(imgList)
				self.signals.transformSignal.emit(("comp", len(imgList), self.identity))
			return None
		except:
			errMsg = traceback.format_exc()
			self.signals.errSignal.emit((0, self.identity, errMsg)) 
			self.deleteFiles()
			return None
		try:
			print("Starting esitmator step!")
			self.signals.learningSignal.emit(("started", 0, self.identity))
			pred = learnPipline.fit_predict(transformArr)
			self.signals.learningSignal.emit(("ended", 100, self.identity))
			self.moveImagesToDirect(imgList=imgList, predClass=pred)
			print("Completed!")
			return None
		except:
			errMsg = traceback.format_exc()
			self.signals.errSignal.emit((1, self.identity, errMsg))
			self.deleteFiles()
			return None 

	def imageList(self):
		imgList = []
		for imgs in glob.glob(self.imageLocal + "/**/*.tiff", recursive=True):
			imgList.append(imgs)
		return imgList 
	
	def cleanOldArrFile(self):
		imgFile = os.path.join(self.imageLocal, self.imgArrFileName)
		with open(imgFile, "w") as arrFile:
			pass

	def deleteFiles(self):
		caFile = os.path.join(self.imageLocal, ".cainfo")
		imgFile = os.path.join(self.imageLocal, self.imgArrFileName)
		if(os.path.exists(imgFile)):
			os.remove(imgFile)
		if(os.path.exists(caFile)):
			os.remove(caFile)

	def saveImgInfo(self, imgList, imgArrList):
		imgDict = dict({})
		for i in range(len(imgList)):
			arr = imgArrList[i]
			imgName = os.path.split(imgList[i])[-1]
			if(type(arr) == np.ndarray):
				arr = arr.tolist()
			imgDict[imgName] = arr
		imgFile = os.path.join(self.imageLocal, self.imgArrFileName)
		with open(imgFile, "a") as f:
			json.dump(imgDict, f)
			f.write(os.linesep)
	
	def moveImagesToDirect(self, imgList, predClass):
		for index, imgPath in enumerate(imgList):
			directPath = os.path.join(self.imageLocal, str(predClass[index]))
			if(os.path.exists(directPath) == False):
				os.mkdir(directPath)
			try:
				shutil.move(imgPath, directPath)
			except:
				pass #most probably due to file existing in same directory!
		imgDirects = [os.path.join(self.imageLocal, direcs) for direcs in os.listdir(self.imageLocal)]
		for direcs in imgDirects:
			try:
				os.rmdir(direcs)
			except:
				print("Not empty")
	
	def getSavedImageData(self, imgList):
		fileLocation = os.path.join(self.imageLocal, self.imgArrFileName)
		imgArr = []
		with open(fileLocation, "r") as imgInfo:
			imgDict = dict({})
			for imgJson in [line for line in imgInfo.read().splitlines() if len(line) > 0 ]:
				imgDict.update(json.loads(imgJson))
		for imgPath in imgList:
			imgName = os.path.split(imgPath)[-1]
			imgArr.append(imgDict[imgName])
		return imgArr

	def stop(self):
		self.deleteFiles()
		self.threadactive = False
	
class TrainingThread(QtCore.QRunnable):
	def __init__(self,X,y,pipeline, location):
		super(TrainingThread, self).__init__()
		self.X = X
		self.y = y
		self.pipline = pipeline
		self.imageLocal = location
	@QtCore.pyqtSlot()
	def run(self):
		X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.33)
		print("Starting .....")
		self.pipline.fit(X_train,y_train)
		print("Over .......")
		pred = self.pipline.predict(X_test)
		print(classification_report(y_test, pred))
		self.signals.performanceOutput.emit(classification_report(y_test, pred))



if __name__ == "__main__":
	db = databaseManager()
	modelClass = modelImage(DB=db)
	returnv = modelClass.filterInfoCheck(imgLocal=r"D:\Documents\Capstone_Work\Testing_Sample_keras\Dummy", filtername="adarsh", paramname="DEFAULT_PARAMS.joblib", view="Bottom")
	print(returnv)
	#modelClass.filterInfoCheck("./", "adarsh", "adasa", "Bottom")