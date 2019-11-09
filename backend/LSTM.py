import pandas as pd
import numpy as np
import os
import collections
import re
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.layers import CuDNNLSTM, Conv2D, Embedding, Dense, Dropout
from keras.models import Model, Sequential
from keras.optimizers import Adam
import keras
import tensorflow

os.environ["CUDA_VISIBLE_DEVICES"]="0,1"


def load_data(inputDir):
    trainingPath = os.path.join(inputDir, "train.csv")
    df = pd.read_csv(trainingPath)
    data = df.dropna()
    data['Body'] = data['Body'].apply((lambda x: re.sub('[^a-zA-z0-9\s]','',x)))
    for idx,row in data.iterrows():
        row[0] = row[0].replace('rt',' ')    
    tokenizer = Tokenizer(nb_words = 50000, lower = True, split = ' ')
    tokenizer.fit_on_texts(data['Body'].values)
    train_data = tokenizer.texts_to_sequences(data['Body'].values)
    train_data = pad_sequences(train_data)

    Y = data['Label'].values
    return train_data, Y

def build_model(train_data):
    model = Sequential()
    model.add(Embedding(50000, 128, input_length = train_data.shape[1]))
    model.add(CuDNNLSTM(100))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation = 'sigmoid'))
    print(model)
    return model

train_data, labels = load_data("./train_data/")
model = build_model(train_data)
model = keras.utils.multi_gpu_model(model, gpus = 2)
optimizer = Adam(.01, .5)
model.compile(optimizer, loss = 'binary_crossentropy', metrics = ['accuracy'])
model.fit(train_data, labels, batch_size = 256, epochs = 1)