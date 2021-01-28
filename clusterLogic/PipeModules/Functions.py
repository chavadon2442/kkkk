import cv2 
from sklearn.base import BaseEstimator, ClassifierMixin, TransformerMixin
from keras.applications.resnet import ResNet101,preprocess_input
import numpy as np
import os
import random


class ImgPathToRGB(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        imgArr = []
        for imgs in X:
            imgArr.append(cv2.cvtColor(cv2.imread(imgs, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB))
        return np.array(imgArr)
    
class Resnet101Transformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        model = ResNet101()
        imgArr = []
        for index, imgs in enumerate(X):
            imgs = cv2.resize(imgs, (224,224))
            img_data = np.expand_dims(imgs, axis=0)
            img_data = preprocess_input(img_data)
            dataPoint = model.predict(img_data)
            dataPoint = np.array(dataPoint).flatten()
            imgArr.append(dataPoint)
        return np.array(imgArr)
