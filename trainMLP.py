#%% 
### Imports
# baseline keras model
import numpy as np
import pandas as pd
import h5py
import pickle
import os
from keras.models import Sequential, Model
from keras.layers import Input, Activation, Dense, Convolution2D, MaxPooling2D, Dropout, Flatten
from keras.utils import np_utils
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import random

# Number of Outputs From Dense()
n = 3

# If n = 3, set either 800, 1400, or 2000, if n = 5, set 4200
signal = 800;

# %%
### Loading data
npzPath = 'NewAnalysisArrays.npz'
if (signal == 800): outPath = 'AnalysisModels-800' # changes the path of the output data
elif (signal == 1400): outPath = 'AnalysisModels-1400' # changes the path of the output data
elif (signal == 2000): outPath = 'AnalysisModels-2000' # changes the path of the output data
elif (signal == 4200): outPath = 'AnalysisModels-all' # changes the path of the output data


if not os.path.exists(outPath): 
   os.system('mkdir '+ outPath)
outPath = './' + outPath + '/'
if not os.path.exists(outPath+'/plots/'): os.system('mkdir '+outPath+'/plots')

print('Importing data from {}...'.format(npzPath))
archive = np.load(npzPath)

# Three datasets
background = archive['background']
Bp800 = archive['mass800']
Bp1400 = archive['mass1400']
Bp2000 = archive['mass2000']

VARS = ['pNet_J_1',#'pNet_J_2',
        'pNet_T_1',#'pNet_T_2',
        'pNet_W_1',#'pNet_W_2',
        'FatJet_pt_1',#'FatJet_pt_2',
        'FatJet_sdMass_1',#'FatJet_sdMass_2',
        'tau21_1',#'tau21_2',
        'nJ_pNet','nT_pNet','nW_pNet',
        'Jet_HT','Jet_ST','MET_pt',
        't_pt','t_mass', 'Bprime_mass',
        #'t_dRWb', # t_dRWb does not exist, should check RDF script
        'NJets_central', 'NJets_DeepFlavM','NFatJets','NJets_forward',
        'Bprime_DR','Bprime_ptbal','Bprime_chi2'] # choose which vars to use (2d)

NDIM = len(VARS)
inputs = Input(shape=(NDIM,), name = 'input')
dense1 = Dense(10, activation = 'relu')(inputs)
dense2 = Dense(25, activation = 'relu')(dense1)
dense3 = Dense(10, activation = 'relu')(dense2)   
outputs = Dense(n, name = 'output', kernel_initializer='normal', activation='softmax')(dense3)

#%%
### Creating the model
print('Generating model...')
model = Model(inputs = inputs, outputs = outputs)

# compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
# print the model summary
model.summary()

if (n == 5):
	relativeSize = (len(Bp800) + len(Bp1400) + len(Bp2000)) / len(background)
elif (signal == 800):
	relativeSize = (len(Bp800)) / len(background)
elif (signal == 1400):
	relativeSize = (len(Bp1400)) / len(background)
elif (signal == 2000):
	relativeSize = (len(Bp2000)) / len(background)
print("Relative Size: ",relativeSize, " Length: ",len(Bp2000))

# %%
### Processing data
print('Scaling and separating data...')
# Background events are undersampled to balance dataset
eventData = []
weights = []
labels = []
for i in range(len(background)):
      if(random.random() < relativeSize*10):
            eventData.append(background[i, :NDIM])
            labels.append(background[i, NDIM + 1])
            weights.append(background[i, NDIM])
eventData = np.array(eventData)
weights = np.array(weights)
labels = np.array(labels)
X_Back_train_val, X_Back_test, Y_Back_train_val, Y_Back_test, weights_Back_train, weights_Back_test = train_test_split(eventData, labels, weights, test_size=0.9, random_state=7) # Changes: 0.9->0.7



# Printing Background
print('Background Train: ', X_Back_train_val.shape)
print('Background Test: ', X_Back_test.shape)

# Low Mass Bprime
eventData = Bp800[:, :NDIM]
weights = Bp800[:, NDIM]
labels = Bp800[:, NDIM + 1]
X_800_train_val, X_800_test, Y_800_train_val, Y_800_test, weights_800_train, weights_800_test = train_test_split(eventData, labels, weights, test_size=0.1, random_state=7)

# Printing Low Mass
print('800 Train: ', X_800_train_val.shape)
print('800 Test: ', X_800_test.shape)

# Medium Mass Bprime
eventData = Bp1400[:, :NDIM]
weights = Bp1400[:, NDIM]
labels = Bp1400[:, NDIM + 1]
X_1400_train_val, X_1400_test, Y_1400_train_val, Y_1400_test, weights_1400_train, weights_1400_test = train_test_split(eventData, labels, weights, test_size=0.1, random_state=7)
if (n == 3): Y_1400_train_val = [2] * len(Y_1400_train_val)

# Printing Low Mass
print('1400 Train: ', X_1400_train_val.shape)
print('1400 Test: ', X_1400_test.shape)

# Large Mass Bprime
eventData = Bp2000[:, :NDIM]
weights = Bp2000[:, NDIM]
labels = Bp2000[:, NDIM + 1]
X_2000_train_val, X_2000_test, Y_2000_train_val, Y_2000_test, weights_2000_train, weights_2000_test = train_test_split(eventData, labels, weights, test_size=0.1, random_state=7)
if (n == 3): Y_2000_train_val = [2] * len(Y_2000_train_val)

# Printing Low Mass
print('2000 Train: ', X_2000_train_val.shape)
print('2000 Test: ', X_2000_test.shape)

if (signal == 800):
	X_mass_train_val = X_800_train_val
	Y_mass_train_val = Y_800_train_val
	weights_mass_train = weights_800_train	
elif (signal == 1400):
	X_mass_train_val = X_1400_train_val
	Y_mass_train_val = Y_1400_train_val
	weights_mass_train = weights_1400_train	
elif (signal == 2000):
	X_mass_train_val = X_2000_train_val
	Y_mass_train_val = Y_2000_train_val
	weights_mass_train = weights_2000_train	

X_train_val = np.concatenate((X_Back_train_val, X_mass_train_val)) #, X_1400_train_val, X_2000_train_val)) # Take low mass BP and background for training
Y_train_val = np.concatenate((Y_Back_train_val, Y_mass_train_val)) 
weights_train = np.concatenate((weights_Back_train, weights_mass_train))

# Randomly shuffling training set
indices = np.random.permutation(len(X_train_val))
#print('X_train_val Length: ', len(X_train_val[0]))
X_train_val = X_train_val[indices]
Y_train_val = Y_train_val[indices]
weights_train = weights_train[indices]

# 800: Building testing set out of all events left
X_test_800 = np.concatenate((X_Back_test, X_800_test)) #, X_1400_test, X_2000_test))
Y_test_800 = np.concatenate((Y_Back_test, Y_800_test)) #, Y_1400_test, Y_2000_test))
weights_test_800 = np.concatenate((weights_Back_test, weights_800_test)) #, weights_1400_test, weights_2000_test))

# Randomly shuffling testing set
indices = np.random.permutation(len(X_test_800))
X_test_800 = X_test_800[indices]
Y_test_800 = Y_test_800[indices]
weights_test_800 = weights_test_800[indices]

# 1400: Building testing set out of all events left
X_test_1400 = np.concatenate((X_Back_test, X_1400_test)) #, X_1400_test, X_2000_test))
Y_test_1400 = np.concatenate((Y_Back_test, Y_1400_test)) #, Y_1400_test, Y_2000_test))
weights_test_1400 = np.concatenate((weights_Back_test, weights_1400_test)) #, weights_1400_test, weights_2000_test))

# Randomly shuffling testing set
indices = np.random.permutation(len(X_test_1400))
X_test_1400 = X_test_1400[indices]
Y_test_1400 = Y_test_1400[indices]
weights_test_1400 = weights_test_1400[indices]

# 2000: Building testing set out of all events left
X_test_2000 = np.concatenate((X_Back_test, X_2000_test)) #, X_1400_test, X_2000_test))
Y_test_2000 = np.concatenate((Y_Back_test, Y_2000_test)) #, Y_1400_test, Y_2000_test))
weights_test_2000 = np.concatenate((weights_Back_test, weights_2000_test)) #, weights_1400_test, weights_2000_test))

# Randomly shuffling testing set
indices = np.random.permutation(len(X_test_2000))
X_test_2000 = X_test_2000[indices]
Y_test_2000 = Y_test_2000[indices]
weights_test_2000 = weights_test_2000[indices]

# All: Building testing set out of all events left
X_test = np.concatenate((X_Back_test, X_800_test, X_1400_test, X_2000_test))
Y_test = np.concatenate((Y_Back_test, Y_800_test, Y_1400_test, Y_2000_test))
weights_test = np.concatenate((weights_Back_test, weights_800_test, weights_1400_test, weights_2000_test))

# Randomly shuffling testing set
indices = np.random.permutation(len(X_test))
X_test = X_test[indices]
Y_test = Y_test[indices]
weights_test = weights_test[indices]

# Applying scaler to avoid confusing the network
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler().fit(X_train_val)
pickle.dump(scaler, open(outPath + 'dnn_scaler.pkl', 'wb'))
X_train_val = scaler.transform(X_train_val)
X_test_800 = scaler.transform(X_test_800)
X_test_1400 = scaler.transform(X_test_1400)
X_test_2000 = scaler.transform(X_test_2000)
X_test = scaler.transform(X_test)

#%%
### Preparing the model
# early stopping callback
from keras.callbacks import EarlyStopping
early_stopping = EarlyStopping(monitor='val_loss', patience=10)

from keras.callbacks import ModelCheckpoint
model_checkpoint = ModelCheckpoint(outPath + 'MLP.h5', monitor='val_loss', 
                                   verbose=0, save_best_only=True, 
                                   save_weights_only=False, mode='auto', 
                                   period=1)


# %%
### Training the model
# Train classifier
print('Training Model...')
with tf.device('/CPU:0'): # I was experimenting on TF-GPU/CPU, so this line is not necessary on CPU only systems
        history = model.fit(X_train_val, 
                    tf.keras.utils.to_categorical(Y_train_val), 
                    epochs=1000, 
                    batch_size=1024, 
                    verbose=0, # switch to 1 for more verbosity 
                    callbacks=[early_stopping, model_checkpoint], 
                    validation_split=0.1,
                    sample_weight = weights_train
                    )

# %%
### Getting predictions from model
pred_mlp_800 = model.predict(X_test_800).argmax(axis = -1)
pred_mlp_1400 = model.predict(X_test_1400).argmax(axis = -1)
pred_mlp_2000 = model.predict(X_test_2000).argmax(axis = -1)
pred_mlp = model.predict(X_test).argmax(axis = -1)

from sklearn.metrics import confusion_matrix

confusion_matrix(Y_test_800, pred_mlp_800)
confusion_matrix(Y_test_1400, pred_mlp_1400)
confusion_matrix(Y_test_2000, pred_mlp_2000)
confusion_matrix(Y_test, pred_mlp)

wjets_test = X_test[Y_test == 0]
ttbar_test = X_test[Y_test == 1]
bprime_test_800 = X_test_800[Y_test_800 > 1]
bprime_test_1400 = X_test_1400[Y_test_1400 > 1]
bprime_test_2000 = X_test_2000[Y_test_2000 > 1]
bprime_test = X_test[Y_test > 1]

probs_wjets = model.predict(wjets_test)
probs_ttbar = model.predict(ttbar_test)
probs_bprime = model.predict(bprime_test)
probs_bprime_800 = model.predict(bprime_test_800)
probs_bprime_1400 = model.predict(bprime_test_1400)
probs_bprime_2000 = model.predict(bprime_test_2000)

#print('800 Shape',eventData800)
#print('1400 Shape',eventData1400)
#print('2000 Shape',eventData2000)

# Combining Bprime scores to show as a single unified rating for signal
# print(probs_bprime[0])
# probs_bprime_fixed = np.zeros((len(probs_bprime), 3))
# for i, event in enumerate(probs_bprime):
#        probs_bprime_fixed[i][0] = event[0]
#        probs_bprime_fixed[i][1] = event[1]
#        probs_bprime_fixed[i][2] = event[2] + event[3] + event[4]
# probs_bprime = probs_bprime_fixed
# print(probs_bprime.shape)

# %%
### Generating plots for model evaluation
plt.figure()
plt.xlabel('Predicted W boson score',horizontalalignment='right',x=1.0,size=14)
plt.ylabel('Events per bin',horizontalalignment='right',y=1.0,size=14)
plt.title('CMS Simulation',loc='left',size=18)
plt.title('Work in progress',loc='right',size=14,style='italic')
plt.title('Train '+str(signal), loc='left', y=-0.14)
plt.ylim([0.001,10.**3])
plt.hist(probs_wjets.T[0], bins=20, range=(0,1), label=r'$\mathrm{W+jets}$', color='g', histtype='step', log=True, density=True)
plt.hist(probs_ttbar.T[0], bins=20, range=(0,1), label=r'$\mathrm{t\bar{t}}$', color='y', histtype='step', log=True, density=True)

plt.hist(probs_bprime.T[0], bins=20, range=(0,1), label=r'$\mathrm{Bprime}$', color='m', histtype='step', log=True, density=True)

plt.hist(probs_bprime_800.T[0], bins=20, range=(0,1), label=r'$\mathrm{Bprime_{800}}$', linestyle=('dashed'), color='b', histtype='step', log=True, density=True)
plt.hist(probs_bprime_1400.T[0], bins=20, range=(0,1), label=r'$\mathrm{Bprime_{1400}}$', linestyle=('dashed'), color='k', histtype='step', log=True, density=True)
plt.hist(probs_bprime_2000.T[0], bins=20, range=(0,1), label=r'$\mathrm{Bprime_{2000}}$', linestyle=('dashed'), color='c', histtype='step', log=True, density=True)
plt.legend(loc='best', ncol = 2)
plt.savefig(outPath + '/plots/score_WJet.png')

plt.figure()
plt.xlabel('Predicted top quark score',horizontalalignment='right',x=1.0,size=14)
plt.ylabel('Events per bin',horizontalalignment='right',y=1.0,size=14)
plt.title('CMS Simulation',loc='left',size=18)
plt.title('Work in progress',loc='right',size=14,style='italic')
plt.title('Train '+str(signal), loc='left', y=-0.14)
plt.ylim([0.001,10.**3])
plt.hist(probs_wjets.T[1], bins=20, range=(0,1), label=r'$\mathrm{W+jets}$', color='g', histtype='step', log=True, density=True)
plt.hist(probs_ttbar.T[1], bins=20, range=(0,1), label=r'$\mathrm{t\bar{t}}$', color='y', histtype='step', log=True, density=True)

plt.hist(probs_bprime.T[1], bins=20, range=(0,1), label=r'$\mathrm{Bprime}$', color='m', histtype='step', log=True, density=True)

plt.hist(probs_bprime_800.T[1], bins=20, range=(0,1), label=r'$\mathrm{Bprime_{800}}$', linestyle=('dashed'), color='b', histtype='step', log=True, density=True)
plt.hist(probs_bprime_1400.T[1], bins=20, range=(0,1), label=r'$\mathrm{Bprime_{1400}}$', linestyle=('dashed'), color='k', histtype='step', log=True, density=True)
plt.hist(probs_bprime_2000.T[1], bins=20, range=(0,1), label=r'$\mathrm{Bprime_{2000}}$', linestyle=('dashed'), color='c', histtype='step', log=True, density=True)
plt.legend(loc='best', ncol=2)
plt.savefig(outPath + '/plots/score_TTbarT.png')

if (n == 3):
	plt.figure()
	plt.xlabel('Predicted Bprime score',horizontalalignment='right',x=1.0,size=14)
	plt.ylabel('Events per bin',horizontalalignment='right',y=1.0,size=14)
	plt.title('CMS Simulation',loc='left',size=18)
	plt.title('Work in progress',loc='right',size=14,style='italic')
	plt.title('Train '+str(signal), loc='left', y=-0.14)
	plt.ylim([0.001,10.**3])
	plt.hist(probs_wjets.T[2], bins=20, range=(0,1), label=r'$\mathrm{W+jets}$', color='g', histtype='step', log=True, density=True)
	plt.hist(probs_ttbar.T[2], bins=20, range=(0,1), label=r'$\mathrm{t\bar{t}}$', color='y', histtype='step', log=True, density=True)
	plt.hist(probs_bprime.T[2], bins=20, range=(0,1), label=r'$\mathrm{Bprime}$', color='m', histtype='step', log=True, density=True)
	plt.hist(probs_bprime_800.T[2], bins=20, range=(0,1), label=r'$\mathrm{Bprime_{800}}$', linestyle=('dashed'), color='b', histtype='step', log=True, density=True)
	plt.hist(probs_bprime_1400.T[2], bins=20, range=(0,1), label=r'$\mathrm{Bprime_{1400}}$', linestyle=('dashed'), color='k', histtype='step', log=True, density=True)
	plt.hist(probs_bprime_2000.T[2], bins=20, range=(0,1), label=r'$\mathrm{Bprime_{2000}}$', linestyle=('dashed'), color='c', histtype='step', log=True, density=True)
	plt.legend(loc='best', ncol=2)
	plt.savefig(outPath + '/plots/score_bprime.png')
elif (n == 5):
	plt.figure()
	plt.xlabel('Predicted Bprime score',horizontalalignment='right',x=1.0,size=14)
	plt.ylabel('Events per bin',horizontalalignment='right',y=1.0,size=14)
	plt.title('CMS Simulation',loc='left',size=18)
	plt.title('Work in progress',loc='right',size=14,style='italic')
	plt.ylim([0.01,10.**4])
	plt.hist(probs_wjets.T[2]+probs_wjets.T[3]+probs_wjets.T[4], bins=20, range=(0,1), label=r'$\mathrm{W+jets}$', color='g', histtype='step', log=True, density=True)
	plt.hist(probs_ttbar.T[2]+probs_ttbar.T[3]+probs_ttbar.T[4], bins=20, range=(0,1), label=r'$\mathrm{t\bar{t}}$', color='y', histtype='step', log=True, density=True)
	plt.hist(probs_bprime.T[2]+probs_bprime.T[3]+probs_bprime.T[4], bins=20, range=(0,1), label=r'$\mathrm{Bprime}$', color='m', histtype='step', log=True, density=True)
	plt.hist(probs_bprime_800.T[2], bins=20, range=(0,1), label=r'$\mathrm{Bprime_{800}}$', linestyle=('dashed'), color='b', histtype='step', log=True, density=True)
	plt.hist(probs_bprime_1400.T[2], bins=20, range=(0,1), label=r'$\mathrm{Bprime_{1400}}$', linestyle=('dashed'), color='k', histtype='step', log=True, density=True)
	plt.hist(probs_bprime_2000.T[2], bins=20, range=(0,1), label=r'$\mathrm{Bprime_{2000}}$', linestyle=('dashed'), color='c', histtype='step', log=True, density=True)
	plt.legend(loc='best')
	plt.savefig(outPath + '/plots/score_bprime.png')

# Trying to generate a heatmap (so far unsuccessfully)
#myXI, myYI = np.meshgrid(np.linspace(-2, 2, 200), np.linspace(-2, 2, 200))
#print(myXI.shape)
#
#for i in range(len(myXI)):
#        for j in range(len(myYI)):
#                myXI[i, j]
#                myYI[i, j]
#                myZI[i, j] = model.predict
#
#myZI = model.predict(np.c_[myXI.ravel(), myYI.ravel()])
#myZI = myZI.reshape(myXI.shape)
#
#from matplotlib.colors import ListedColormap
#
#plt.figure(figsize=(20, 7))
#
#ax = plt.subplot(1, 2, 1)
#cm = plt.cm.RdBu

# %%
