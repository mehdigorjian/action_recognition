# set the matplotlib backend so figures can be saved in the background
import matplotlib
matplotlib.use("Agg")
# import the necessary packages
from keras.preprocessing.image import ImageDataGenerator
from keras.layers.pooling import AveragePooling2D
from keras.applications import ResNet50
from keras.layers.core import Dropout
from keras.layers.core import Flatten
from keras.layers.core import Dense
from keras.layers import Input
from keras.models import Model
from keras.optimizers import SGD
from keras import regularizers
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping, TensorBoard, History, ModelCheckpoint, RemoteMonitor, ReduceLROnPlateau
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from imutils import paths
import matplotlib.pyplot as plt
import numpy as np
import argparse
import warnings
import pickle
import time
import cv2
import os
BATCH_SIZE = 32
# construct the argument parser and parse the arguments
parse = argparse.ArgumentParser()
parse.add_argument("-d", "--data", required=True,
	help="path to input dataset")
parse.add_argument("-m", "--model", required=True,
	help="path to output serialized model")
parse.add_argument("-l", "--label_bin", required=True,
	help="path to output label binarizer")
parse.add_argument("-e", "--epochs", type=int, default=25,
	help="# of epochs to train our network for")
parse.add_argument("-p", "--plot", type=str, default="plot.png",
	help="path to output loss/accuracy plot")
args = parse.parse_args()

# initialize the set of labels from the spots activity dataset we are
# going to train our network on
LABELS = {"cooking", "drinking"}

# grab the list of images in our dataset directory, then initialize
# the list of data (i.e., images) and class images
print("[INFO] loading images...")
imagePaths = list(paths.list_images(args.data))

data = []
labels = []

# loop over the image paths
for imagePath in imagePaths:
	# extract the class label from the filename
	label = imagePath.split(os.path.sep)[-2]
	info_file_name = imagePath.split(os.path.sep)[-1]

	# if the label of the current image is not part of of the labels
	# are interested in, then ignore the image
	if label not in LABELS:
		continue

	# load the image, convert it to RGB channel ordering, and resize
	# it to be a fixed 224x224 pixels, ignoring aspect ratio
	image = cv2.imread(imagePath)
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	image = cv2.resize(image, (224, 224))
	print('[INFO] processing image: ', info_file_name)
	# update the data and labels lists, respectively
	data.append(image)
	labels.append(label)

# convert the data and labels to NumPy arrays
data = np.array(data)
labels = np.array(labels)
# print('labels before one-hot: ', labels)

# perform one-hot encoding on the labels
lb = LabelBinarizer()
labels = lb.fit_transform(labels)
labels = to_categorical(labels)
# print('labels after one-hot: ', labels)

# partition the data into training and testing splits using 75% of
# the data for training and the remaining 25% for testing
print('[INFO] splitting data...')

trainX, testX, trainY, testY = train_test_split(data, labels,
	test_size=0.25, stratify=labels, random_state=42)

print('[INFO] creating generator object...')
# initialize the training data augmentation object
trainAug = ImageDataGenerator(
	rotation_range=30,
	zoom_range=0.15,
	width_shift_range=0.2,
	height_shift_range=0.2,
	shear_range=0.15,
	horizontal_flip=True,
	fill_mode="nearest")

# initialize the validation/testing data augmentation object (which
# we'll be adding mean subtraction to)
valAug = ImageDataGenerator()

# define the ImageNet mean subtraction (in RGB order) and set the
# the mean subtraction value for each of the data augmentation
# objects
mean = np.array([123.68, 116.779, 103.939], dtype="float32")
trainAug.mean = mean
valAug.mean = mean

# train and test generators
train_generator = trainAug.flow(trainX, trainY, batch_size=BATCH_SIZE)
validation_generator = valAug.flow(testX, testY)
# load the ResNet-50 network, ensuring the head FC layer sets are left
# off
# ignore warnings
warnings.filterwarnings("ignore")

# using tensorboard
# tensorboard = TensorBoard(log_dir=f'logs/{time.time()}', batch_size=BATCH_SIZE)

# baseModel = ResNet50(include_top=False, weights="imagenet",
	# input_tensor=Input(shape=(224, 224, 3)))

baseModel = ResNet50(include_top=False, weights="imagenet", input_tensor=Input(shape=(224, 224, 3)), input_shape=(244,244,3))

# construct the head of the model that will be placed on top of the
# the base model
headModel = baseModel.output
headModel = AveragePooling2D(pool_size=(7, 7))(headModel)
headModel = Flatten()(headModel)
headModel = Dense(512, activation="relu", kernel_regularizer=regularizers.l1(0.01))(headModel)
headModel = Dropout(0.5)(headModel)
headModel = Dense(len(lb.classes_), activation="softmax")(headModel)

# place the head FC model on top of the base model (this will become
# the actual model we will train)
model = Model(inputs=baseModel.input, outputs=headModel)

# loop over all layers in the base model and freeze them so they will
# *not* be updated during the training process
for layer in baseModel.layers:
	layer.trainable = False

# compile our model (this needs to be done after our setting our
# layers to being non-trainable)
print("[INFO] compiling model...")
opt = SGD(lr=1e-4, momentum=0.9, decay=1e-4 / args.epochs)
model.compile(loss="categorical_crossentropy", optimizer=opt,
	metrics=["accuracy"])

# reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, min_lr=0.001)
# es_callbacks = EarlyStopping(monitor='val_loss', mode='min', restore_best_weights=True, patience=10)
# check_point = ModelCheckpoint(filepath='weights/weights.hdf5',  save_best_only=True, monitor='val_loss', mode='min', verbose=1)

# train the head of the network for a few epochs (all other layers
# are frozen) -- this will allow the new FC layers to start to become
# initialized with actual "learned" values versus pure random
print("[INFO] training head...")
# H = History()
# R = RemoteMonitor(root='http://localhost:9000', path='output_temp/', field='data')
# model.fit_generator(train_generator, steps_per_epoch=len(trainX) // BATCH_SIZE, validation_data=validation_generator, validation_steps=len(testX) // BATCH_SIZE, epochs=args.epochs, callbacks=[H, tensorboard, check_point, es_callbacks, reduce_lr])

H = model.fit_generator(train_generator, steps_per_epoch=len(trainX) // BATCH_SIZE, validation_data=validation_generator, validation_steps=len(testX) // BATCH_SIZE, epochs=args.epochs)

# evaluate the network
print("[INFO] evaluating network...")
predictions = model.predict(testX, batch_size=BATCH_SIZE)

print(classification_report(testY.argmax(axis=1),
	predictions.argmax(axis=1), target_names=lb.classes_))

# plot the training loss and accuracy
plt.style.use("ggplot")
plt.figure()
plt.plot(H.history["loss"], label="train_loss")
plt.plot(H.history["val_loss"], label="val_loss")
plt.plot(H.history["accuracy"], label="train_acc")
plt.plot(H.history["val_accuracy"], label="val_acc")
plt.title("Training Loss and Accuracy on Dataset")
plt.xlabel("Epoch #")
plt.ylabel("Loss | Accuracy")
plt.legend(loc="lower left")
plt.savefig(args.plot)

# serialize the model to disk
print("[INFO] serializing network...")
model.save(args.model)

# serialize the label binarizer to disk
f = open(args.label_bin, "wb")
f.write(pickle.dumps(lb))
f.close()
print('[INFO] model saved!')

# -------------------------------------------------TESTING RUNS
# TO RUN ON FLOYDHUB: python train.py --data /floyd/input/dlaction --model output/activity.model --label_bin output/lb.pickle --plot output/fig_v1.png --epochs 35

# TO DEBUG ON THE LOCAL SYSTEM: python train.py --data dataset_temp --model output_temp/activity.model --label_bin output_temp/lb.pickle --plot output_temp/_plot1.png --epochs 1

# TO RUN THE CODE GENERALLY: python train.py --data dataset --model output/activity.model --label_bin output/lb.pickle --plot output/fig_v1.png --epochs 50