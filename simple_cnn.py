'''Trains a simple convnet on the MNIST dataset.
Gets to 99.25% test accuracy after 12 epochs
(there is still a lot of margin for parameter tuning).
16 seconds per epoch on a GRID K520 GPU.
'''
from __future__ import print_function
import numpy as np
import cv2
import scipy.ndimage as ndimage
import keras
import scipy.io
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
import glob, os
from numpy import array
from numpy import argmax
from keras.utils import to_categorical

def read_in_data():
    path = './data/clips/class0/*.mat'   
    files=glob.glob(path)   
    class0 = []
    for file in files:
        class0.append(scipy.io.loadmat(file)['regions'])
        
    path = './data/clips/class1/*.mat'
    files=glob.glob(path)
    class1 = []
    for file in files:
        class1.append(scipy.io.loadmat(file)['regions'])
 
    class0 = np.concatenate(class0, 2)
    class0 = np.transpose(class0, (2, 0, 1))
    class1 = np.concatenate(class1, 2)
    class1 = np.transpose(class1, (2, 0, 1))
    imgs = np.concatenate((class0, class1))
    
    labels0 = np.zeros((class0.shape[0],))
    labels1 = np.ones((class1.shape[0],))
    labels = np.hstack((labels0, labels1))
    #labels = to_categorical(labels)

    # Shuffle labels with images
    randomize = np.arange(labels.shape[0])
    np.random.shuffle(randomize)
    imgs = imgs[randomize,:,:]
    labels = labels[randomize]
    return imgs, labels

def split_data(imgs, labels):
    x_train = imgs[:int(imgs.shape[0]*0.7),:,:]
    y_train = labels[:int(imgs.shape[0]*0.7)]

    x_val = imgs[int(imgs.shape[0]*0.7):int(imgs.shape[0]*0.9),:,:]
    y_val = labels[int(imgs.shape[0]*0.7):int(imgs.shape[0]*0.9)]
    
    x_test = imgs[int(imgs.shape[0]*0.9):, :, :]
    y_test = labels[int(imgs.shape[0]*0.9):]

    return x_train, y_train, x_val, y_val, x_test, y_test

imgs, labels = read_in_data()
x_train, y_train, x_val, y_val, x_test, y_test = split_data(imgs, labels)

batch_size = 128
num_classes = 2
epochs = 12

# input image dimensions
#img_rows, img_cols = 28, 28
img_rows, img_cols = 32, 32

print(x_train.shape, x_test.shape, x_val.shape, y_val.shape, y_train.shape, y_test.shape)

if K.image_data_format() == 'channels_first':
    x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
    x_val = x_val.reshape(x_val.shape[0], 1, img_rows, img_cols)
    x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
    input_shape = (1, img_rows, img_cols)
else:
    x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
    x_val = x_val.reshape(x_val.shape[0], img_rows, img_cols, 1)
    x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
    input_shape = (img_rows, img_cols, 1)

x_train = x_train.astype('float32')
x_val = x_val.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_val /= 255
x_test /= 255
print('x_train shape:', x_train.shape)
print(x_train.shape[0], 'train samples')
print(x_test.shape[0], 'test samples')

# convert class vectors to binary class matrices
y_train = keras.utils.to_categorical(y_train, num_classes)
y_val = keras.utils.to_categorical(y_val, num_classes)
y_test = keras.utils.to_categorical(y_test, num_classes)

# debugging
print('DEBUGGING')
print(x_train.shape, 'training images')
print(x_test.shape, 'test images')
print(y_train.shape, 'training labels')
print(y_test.shape, 'testing labels')

#x_train = cv2.resize(x_train, (60000, 64, 64, 1))
#x_test = cv2.resize(x_test, (10000, 64, 64, 1))

#x_train = ndimage.zoom(x_train, (1, 2, 2, 1))
#x_test = ndimage.zoom(x_test, (1, 2, 2, 1))

print(x_train.shape, 'training images')
print(x_test.shape, 'test images')

model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3),
                 activation='relu',
                 input_shape=input_shape))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(num_classes, activation='softmax'))

model.compile(loss=keras.losses.categorical_crossentropy,
              optimizer=keras.optimizers.Adadelta(),
              metrics=['accuracy'])

model.fit(x_train, y_train,
          batch_size=batch_size,
          epochs=epochs,
          verbose=1,
          validation_data=(x_test, y_test))
score = model.evaluate(x_test, y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])
