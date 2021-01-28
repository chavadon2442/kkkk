from sklearn.cluster import KMeans
import cv2
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
import glob
import os
import time
import datetime

class View_cluster:
    def __init__(self, view, path, signal):
        self.view = view
        self.PATH = path
        self.data = {}
        self.signal =  signal
        self.__setupImgDim()
    def START(self, model, isSave, k, focusPoint):
        if(isSave == True):
            self.__setupSavedData(model, focusPoint)
        self.startCluster(model, isSave, k)
    def startCluster(self, model, isSave, k):
        allSection = [os.path.join(self.PATH,section) for section in os.listdir(self.PATH) if section.find(".") == -1]
        for paths in allSection:
            self.signal.updateInfo.emit("Started")
            self.signal.updateInfo.emit(paths)
            img_list = []
            start_time = time.time()
            feature_list, img_list = self.extract_vector(model, paths, img_list) 
            if isSave == True:
                self.data['timeExtractFeature'] = time.time() - start_time
                self.data['totalImages'] = len(img_list)
            _str = 'timeExtractFeature ' + str(time.time() - start_time)
            self.signal.updateInfo.emit(_str)
            start_time = time.time()
            kmeans = KMeans(n_clusters=k, random_state=0).fit(feature_list)
            _str = "timeClustering with k = {} is {}".format(k, time.time() - start_time)
            self.signal.updateInfo.emit(_str)
            self.cluster_by_folder(k, img_list, kmeans, paths)
            if isSave == True:
                results = []
                if len(feature_list) == len(img_list):
                    for i in range(len(feature_list)):
                        temp_result = {}
                        im = img_list[i]
                        im = im.replace('\\', '/')
                        temp_result['name'] = (im.split('/'))[-1]
                        temp_result['feature'] = feature_list[i].tolist()
                        results.append(temp_result)
                self.data['results'] = results
                with open('D:/' + ('_'.join([view, model, createdAt]) + '.json'), 'w') as outfile:
                    json.dump(self.data, outfile)
    def __setupSavedData(self, model, focusPoint):
        createdAt = (datetime.datetime.now()).strftime('%Y%m%d%H%M%S')
        self.data['view'] = view
        self.data['totalImages'] = 0
        self.data['pretrainedModel'] = model
        self.data['timeExtractFeature'] = 0
        self.data['settings'] = {}
        self.data['settings']['focusPoint'] = focusPoint
        self.data['settings']['crop'] = {}
        self.data['settings']['crop']['y1'] = self.y1
        self.data['settings']['crop']['y2'] = self.y2
        self.data['settings']['crop']['x1'] = self.x1
        self.data['settings']['crop']['x2'] = self.x2
        self.data['createdAt'] = createdAt
        self.data['results'] = []
    def __setupImgDim(self):
        if self.view == 'bottom_view' or self.view == 'top_view':
            self.y1 = 0
            self.y2 = 1200
            self.x1 = 0
            self.x2 = 1920
        elif self.view == 'left_view':
            self.y1 = 0
            self.y2 = 1200
            self.x1 = 0
            self.x2 = 1920
        elif self.view == 'right_view':
            self.y1 = 280
            self.y2 = 770
            self.x1 = 0
            self.x2 = 1920
    def extract_vector(self, model, path, img_list):
        if model != 'sreena':
            from keras.models import Sequential
            from keras.applications.resnet50 import ResNet50, preprocess_input
            from keras.applications.resnet import ResNet101
            from keras.applications.resnet_v2 import ResNet152V2
            from keras.applications.inception_resnet_v2 import InceptionResNetV2
            from keras.applications.nasnet import NASNetLarge
            my_new_model = Sequential()
            if model == 'resnet50':
                resnet_weights_path = 'resnet50_weights_tf_dim_ordering_tf_kernels_notop.h5'
                my_new_model.add(ResNet50(include_top=False, pooling='avg', weights='imagenet'))
                #my_new_model.add(ResNet50(include_top=False, pooling='avg', weights=resnet_weights_path))
            elif model == 'resnet152':
                resnet_weights_path = 'resnet152v2_weights_tf_dim_ordering_tf_kernels_notop.h5'
                my_new_model.add(ResNet152V2(include_top=False, weights='imagenet', pooling='max'))
                #my_new_model.add(ResNet152V2(include_top=False, weights=resnet_weights_path, pooling='max'))
            elif model == 'resnet101':
                my_new_model.add(ResNet101(include_top=False, weights='imagenet',pooling='max'))
            elif model == 'inception':
                my_new_model.add(InceptionResNetV2(include_top=False, weights='imagenet',pooling='avg'))
            elif model == 'nasnet':
                resnet_weights_path = 'NASNet-large-no-top.h5'
                my_new_model.add(NASNetLarge(include_top=False, weights='imagenet',pooling='avg', classes=1000))
                #my_new_model.add(NASNetLarge(include_top=False, weights=resnet_weights_path,pooling='avg', classes=1000))

            # Say not to train first layer (ResNet) model. It is already trained
            my_new_model.layers[0].trainable = False
        else:
            from sreena import BottleNet_Plus
            import torch
            import torchvision
            import torchvision.transforms as transforms
            from PIL import Image
            device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
            sreena_model = BottleNet_Plus(num_classes=3)
            sreena_model.load_state_dict(torch.load("top_model.ckpt"))
            sreena_model.to(device)

        resnet_feature_list = []
        index = 0
        for im in glob.glob(path + '/**/*.tiff', recursive=True):
            _str = "Working on {}\n{}\nimg={}".format(os.path.split(im)[1], os.path.split(im)[0],index)
            self.signal.updateInfo.emit(_str)
            index += 1
            img_list.append(im)
            if model == 'sreena':
                img = Image.open(im)
                preprocess = transforms.Compose([transforms.Resize((224,224), interpolation = 2), transforms.ToTensor()])
                image = preprocess(img).to(device)
                shape = image.size()
                image = image.view(1,shape[0], shape[1], shape[2])
                sreena_model.eval()
                output = sreena_model(image)
                a = output.detach().cpu().numpy()
                resnet_feature_list.append(a[0])
            else:
                try: 
                    im = cv2.imread(im)
                    im = im[self.y1:self.y2, self.x1:self.x2]
                    if model != 'sreena':
                        if model == 'nasnet':
                            im = cv2.resize(im,(331,331))
                        elif model == 'inception':
                            im = cv2.resize(im,(299,299))
                        else:
                            im = cv2.resize(im,(244,244))
                except:
                    img_list.pop()
                    continue
                img = preprocess_input(np.expand_dims(im.copy(), axis=0))
                resnet_feature = my_new_model.predict(img)
                resnet_feature_np = np.array(resnet_feature)
                resnet_feature_list.append(resnet_feature_np.flatten())
        print("asdsad")
        return np.array(resnet_feature_list), img_list
    def cluster_by_folder(self, k, img_list, kmeans, path):
        for i in range(k):
            if not os.path.exists(path + "/" + str(i)):
                os.makedirs(path + "/" + str(i))

        for i, im in enumerate(img_list):
            im = im.replace('\\', '/')
            try:
                resultPathImg = os.path.join( path, str((kmeans.labels_)[i]), os.path.split(im)[1] ) 
                os.rename(im, resultPathImg)
            except:
                continue
