# -*- coding: utf-8 -*-
"""submission_3_shape_classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LSoRD8YMkh2OpzEsAcdRpxx_EdBJW7K3

# Welcome to Shape Classification

### Import all dependencies
"""

pip install pydot==1.3.0

pip install graphviz==0.10.1

import tensorflow as tf
import os
import zipfile
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from keras.utils import plot_model
from keras import callbacks
from keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator

"""### Import Training data"""

DATASET_DIR = './shape-classification-dataset/shapes'

"""#### Check datasets from directory"""

os.listdir(DATASET_DIR)

"""#### Check total dataset"""

print('total circle images :', len(os.listdir(DATASET_DIR + '/circle')))
print('total square images :', len(os.listdir(DATASET_DIR + '/square')))
print('total star images :', len(os.listdir(DATASET_DIR + '/star')))
print('total triangle images :', len(os.listdir(DATASET_DIR + '/triangle')))

"""#### Example data from dataset"""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
img = image.load_img(DATASET_DIR + '/circle/0.png')
imgplot = plt.imshow(img)

"""### Preprocessing

#### Image Augmentation (Rescaling and Splitting)
"""

train_dir = os.path.join(DATASET_DIR)
train_datagen = ImageDataGenerator(rescale=1./255,
    rotation_range=20,
    zoom_range=0.2,
    shear_range=0.2,
    fill_mode = 'nearest',
    validation_split=0.2) # set validation split

"""#### Generate for training and validation"""

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(16, 16),
    batch_size=8,
    class_mode='categorical',
    subset='training') # set as training data
validation_generator = train_datagen.flow_from_directory(
    train_dir, # same directory as training data
    target_size=(16, 16),
    batch_size=16,
    class_mode='categorical',
    subset='validation')

"""### Create the model"""

model = tf.keras.models.Sequential([
    # Note the input shape is the desired size of the image 150x150 with 3 bytes color
    tf.keras.layers.Conv2D(4, (3,3), activation='relu', input_shape=(16, 16, 3)),
    tf.keras.layers.MaxPooling2D(2,2),
    tf.keras.layers.Dropout(0.4),  
    # Flatten the results to feed into a DNN
    tf.keras.layers.Flatten(), 
    # 512 neuron hidden layer
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(8, activation='relu'),
    # Give output of 4 labels
    tf.keras.layers.Dense(4, activation='softmax')  
])

"""##### Create the loss and optimizer function

1. Adam Optimizer => replacement optimization algorithm for stochastic gradient descent 
2. metrics to benchmark is accuracy
"""

model.compile(optimizer=tf.optimizers.Adam(),
              loss='categorical_crossentropy',
              metrics = ['accuracy'])

print(model.summary())

plot_model(model, to_file='submission_3_shape_classification.png')

"""### Create Callback"""

class myCallback(callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>0.92):
      print("\nYour Accuracy >92%!")
      self.model.stop_training = True

callbacks = myCallback()

"""### Fit the model and Save the History"""

history = model.fit(train_generator,
                              validation_data=validation_generator,
                              epochs=50,
                              verbose=2,
                              callbacks=[callbacks])

"""### Plotting

#### Plot Model Loss
"""

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss Model')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

"""#### Plot Model Accuracy"""

plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Akurasi Model')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

"""## Convert to Tensorflow Lite"""

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with tf.io.gfile.GFile('model.tflite', 'wb') as f:
  f.write(tflite_model)

