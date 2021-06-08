import numpy as np
import tensorflow.keras as keras
import pandas as pd
import librosa
import pickle
import os

MODEL_PATH = os.path.join(os.getcwd(),r'GUI\core\model_h5_2.h5')
ENCODER_PATH = os.path.join(os.getcwd(),r'GUI\core\label_encode')

MODEL_PATH_VN_11 = os.path.join(os.getcwd(),r'GUI\core\model_convd_11.h5')
MODEL_PATH_VN_8 = os.path.join(os.getcwd(),r'GUI\core\model_h5_conv1d_8.h5')
DECODE = {'1':'cheo','2':'quan ho','3':'xam','4':'catru'}

class GModule:
    def __init__(self):
        self.path = None
        self.model = keras.models.load_model(MODEL_PATH)
        with open(ENCODER_PATH,'rb') as f:
            self.encoder = pickle.load(f)
    
    def get(self,path):
        self.path = path

    def cleansing(self,x):
        if x.shape[1] == 1293:
            x = x[:,:-1]
        return x

    def flatten_1(self,x):
        a,b = x.shape
        return x.reshape([a*b,])
        
    def flatten_2(self,df,col):
        dic = {}
        a = len(df.iloc[0,0])
        tmp = df[col]
        for i in range(a):
            dic[str(i)] = tmp.apply(lambda x:x[i]).to_list()
        df_flatten = pd.DataFrame(dic)
        return df_flatten

    def result_by_label(self,x):
        return [(self.encoder.inverse_transform([i]),ele) for i,ele in enumerate(x)]    
    
    def predict(self):
        y, sr = librosa.load(self.path)
        step = sr*30
        n = len(y)//step
        start = 0
        sub = []
        for i in range(n):
            sub.append(y[start:start+step])
            start += step
        tmp = [librosa.feature.mfcc(y=ele, sr=sr, n_mfcc=13) for ele in sub]
        df = pd.DataFrame({'mfcc':tmp})
        df['mfcc'] = df['mfcc'].apply(self.cleansing)
        df['mfcc'] = df['mfcc'].apply(self.flatten_1)
            
        mfcc = self.flatten_2(df,'mfcc')
        X = mfcc.astype('float32')
        X_input = X.to_numpy().reshape([X.shape[0],13,1292])
        X_input = X_input[...,np.newaxis]
        check = [self.result_by_label(ele) for ele in self.model.predict(X_input)]
        label = [ele[0] if ele[0] != 'Rap' else 'Hip hop' for ele in check[0]]
        #re = [(ele,"%.4f" %sum([ele2[i][1] for ele2 in check])) for i,ele in enumerate(label)]
        re = [(ele,sum([ele2[i][1] for ele2 in check])) for i,ele in enumerate(label)]
        n = sum(ele[1] for ele in re)
        print(n,re)
        re_ = [(x,"%.4f" %(y/n)) for x,y in re]
        print(re_)
        return re_
    
class GModuleVN:
    def __init__(self):
        self.path = None
        self.model = keras.models.load_model(MODEL_PATH_VN_11)
        self.decode = DECODE

    def get(self,path):
        self.path = path

    def sliding_window(self,y,sr,size = 5,stride = 3):
        sr_size = sr*size
        step = sr*stride
        
        start = 0
        
        n = len(y)
        tmp = np.zeros(((n - (size - stride))//(sr*stride),1,22050*5),dtype = 'float32')
        i = 0
        while start + sr_size < n:
            tmp[i,:,:] = y[start:start + sr_size]
            start += step
            i += 1
        return tmp

    def predict(self):
        y ,sr = librosa.load(self.path)
        tmp = self.sliding_window(y,sr)
        tmp = tmp.reshape(tmp.shape[0],tmp.shape[2],tmp.shape[1])
        re = self.model.predict(tmp)
        re = np.sum(re,axis = 0)
        re = re/np.sum(re)
        re = [(DECODE[str(i+1)],re[i]) for i in range(len(re))]
        re_ = [(x,"%.4f" %(y)) for x,y in re]
        return re_

