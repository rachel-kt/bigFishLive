#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 14:55:15 2022

@author: rachel
"""

#%reset -f
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QRunnable, QObject, QThreadPool
from PyQt5.QtCore import pyqtSignal as Sgnl
from PyQt5.QtCore import pyqtSlot as Slot
import matplotlib
matplotlib.use('Qt5Agg')
matplotlib.ticker
import numpy as np
import os
import shutil
import multiprocessing as mp
from predictPostions import predictPositions
from common_part_fitting import fitShort
from fit import fitLong
from readDrosoData_v2 import readRawIntensities
from readRawFileUtilities import readRawFiles
#import time

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("modelCon.ui", self)
        self.deconvolve.clicked.connect(self.gotodrosoDialog)
        self.readDatabutton.clicked.connect(self.gotopreProcessDialog)
        self.exitButton.clicked.connect(self.shutprocess)
        
    def gotodrosoDialog(self):
        drosoDialog = droso()
        widget.addWidget(drosoDialog)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotopreProcessDialog(self):
        hivDialog = preProcessDec()
        widget.addWidget(hivDialog)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def shutprocess(self):
        reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to close the window?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            widget.close()
            app.quit()
        else:
            pass
    
class Signals(QObject):
    started = Sgnl(int)
    completed = Sgnl(int,int)
    result = Sgnl(object, str, str, int, int)
    startedFit = Sgnl(str)
    completedFit = Sgnl(str)

class poolWorker(QRunnable):
    def __init__(self, n,T, DataExp, generations, fParam, outFolder, DataFileName, num_possible_poly):
        super().__init__()
        self.n = n
        self.T = T
        self.DataExp = DataExp
        self.generations = generations
        self.fParam = fParam
        self.outFolder = outFolder
        self.DataFileName = DataFileName
        self.num_possible_poly = num_possible_poly
        self.signals = Signals()  
    
    @Slot()
    def run(self):
        self.signals.started.emit(self.n)
        result = predictPositions(self.n-1, self.DataExp, self.generations, self.fParam)
        self.signals.result.emit(result,self.outFolder, self.DataFileName, self.T, self.num_possible_poly)
        self.signals.completed.emit(self.n, self.T)
        QApplication.processEvents()

        
class Stock(QRunnable):
    def __init__(self, filePathToPreProcessedFiles, parameterFilePath, fit3exp, fit2exp, useLongScript):
        super().__init__()
        self.filePathToPreProcessedFiles = filePathToPreProcessedFiles
        self.fit3exp = fit3exp
        self.fit2exp = fit2exp
        self.useLongScript = useLongScript
        self.parameterFilePath = parameterFilePath
        self.signals = Signals()

    @Slot()
    def run(self):
        self.pathToDeconvolutionResultsFolder = os.path.join(self.filePathToPreProcessedFiles,'resultDec/')
        self.pathToFitResultsFolder = os.path.join(self.filePathToPreProcessedFiles)
        if self.fit2exp:
            self.signals.startedFit.emit('Performing a 2 state fit...')
            QApplication.processEvents()          
        #--------------- Fit short movie -----------------------------#
        
        if self.useLongScript==False:
            if self.fit3exp:
                self.signals.startedFit.emit('Performing a 3 state fit...')
                QApplication.processEvents() 
            fitShort(self.pathToDeconvolutionResultsFolder, self.parameterFilePath, combined=0, outputpath=self.pathToFitResultsFolder, fit3exp=self.fit3exp)                            
        #--------------- Fit Long + Short movie ----------------------#
        
        if self.useLongScript==True:
            self.signals.startedFit.emit("Long + short movie analysis will be done")          
            self.signals.startedFit.emit("Looking for long movie data file")
            fileListDeconvolved = os.listdir(self.pathToDeconvolutionResultsFolder)
            ffrag = self.pathToDeconvolutionResultsFolder.split('/')
            if 'shortDataFile' in ffrag:
                ffrag = '/'.join(ffrag[:ffrag.index('shortDataFile')+1])
                ffrag = ffrag.replace('shortDataFile', 'longDataFile')
            for jjj in range(len(fileListDeconvolved)):
                if 'result_' in fileListDeconvolved[jjj]:   
                    exp_name_tmp = fileListDeconvolved[jjj].split('_')[1]
                    exp_name_tmp = exp_name_tmp.split('.')[0]
                    expNameLongFile = 'data_'+exp_name_tmp+'_long.npz'
                    if not os.path.exists(os.path.join(ffrag,expNameLongFile)):
                        self.signals.startedFit.emit("Can't find long movie data file for "+exp_name_tmp+"!")
                    else:    
                        shutil.copy(os.path.join(ffrag,expNameLongFile),self.pathToDeconvolutionResultsFolder)
                        self.signals.startedFit.emit("Long movie data file for "+exp_name_tmp+" moved to Deoconvolution Results folder!")
            QApplication.processEvents()
            if self.fit3exp:
                self.signals.startedFit.emit('Performing a 3 state fit...')      
            QApplication.processEvents()                
            fitLong(self.pathToDeconvolutionResultsFolder, self.parameterFilePath, combined=0, visualize=1, outputpath=self.pathToFitResultsFolder, fit3exp=self.fit3exp)
        self.signals.completedFit.emit("ANALYSIS COMPLETE!")
     
        
class droso(QDialog):
    def __init__(self):
        super(droso, self).__init__()
        loadUi("droso.ui", self)
        self.parameterFilePath = None 
        self.gobackbutton.clicked.connect(self.goBack)
        self.dataBrowseButton.setToolTip('Browse folders')
        self.dataBrowseButton.clicked.connect(self.selectFolder)
        self.saveParameters.clicked.connect(self.setParameters)
        self.parameterBrowseButton.clicked.connect(self.loadParameters)
        self.startAnalysisButton.clicked.connect(self.startAnalysis)
        self.checkMaxThreadsButton.clicked.connect(self.checkNumberOfThreads)
        self.signals = Signals()
        self.comleted_jobs = []
        self.result = []
        
    
    def goBack(self):
        mainwindow = MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def selectFolder(self):
        self.folder2 = QFileDialog.getExistingDirectory(self, "Select Source Directory")
        if self.folder2:
            self.drosoDataFolderBrowseBox.setText(self.folder2+'/')

    def setParameters(self):
        self.Polym_speed = int(self.PolSpeedLineEdit.text())
        self.TaillePreMarq = int(self.TaillePreLineEdit.text())
        self.TailleSeqMarq = int(self.TailleSeqLineEdit.text())
        self.TaillePostMarq = int(self.TaillePostLineEdit.text())
        self.EspaceInterPolyMin = int(self.InterPolDistanceLineEdit.text())
        self.FrameLen = float(self.frameLengthLineEdit.text())
        self.Intensity_for_1_Polym = 1
        self.FreqEchImg = (1/self.FrameLen)
        self.DureeSignal = (self.TaillePreMarq + self.TailleSeqMarq + self.TaillePostMarq) / self.Polym_speed
        self.FreqEchSimu = 1/(self.EspaceInterPolyMin/self.Polym_speed)
        self.parameterFileName = str(self.paramNameLineEdit.text() + 'Parameters')
        
        np.savez(self.drosoDataFolderBrowseBox.text()+self.parameterFileName, 
                  Polym_speed = self.Polym_speed, 
                  TaillePreMarq = self.TaillePreMarq,
                  TailleSeqMarq = self.TailleSeqMarq,
                  TaillePostMarq = self.TaillePostMarq,
                  EspaceInterPolyMin = self.EspaceInterPolyMin,
                  FrameLen = self.FrameLen,
                  Intensity_for_1_Polym = self.Intensity_for_1_Polym,
                  FreqEchImg = self.FreqEchImg,
                  DureeSignal = self.DureeSignal,
                  FreqEchSimu = self.FreqEchSimu
                )
        self.parameterFilePath = self.drosoDataFolderBrowseBox.text()+self.parameterFileName+'.npz'
        QMessageBox.question(self, ' ', "Parameters saved and loaded!", QMessageBox.Ok)
        if self.parameterFilePath:
            self.frameLoad.setEnabled(False)
        return self.parameterFilePath
        
    def loadParameters(self):
        self.parameterFilePath = QFileDialog.getOpenFileName(self, "Select Parameter file")[0]
        if self.parameterFilePath:
            self.parameterBrowseBox.setText(self.parameterFilePath)        
        return self.parameterFilePath
    

    def save_result(self, result, outFolder, DataFileName, num_possible_poly):
        self.result.append(result)
        if len(self.result) == self.job_count:
            DataExptmp = self.result[0][3]
            sd = DataExptmp.shape
            PosPred=np.zeros((self.num_possible_poly,self.job_count)) # np.zeros(num_possible_poly,(len(DataExp[0]))) # short for positions predictions
            DataPred =np.zeros((sd[0],sd[1])) #signal prediction
            Fit=np.zeros((self.job_count))
            Nbr_poly_estimate=np.zeros((self.job_count))
            #rearrange the returned results [iexp, Min_Fit, prediction, DataExp, positions_fit]
            for ll in range(len(self.result)):
                iexp = self.result[ll][0]
                Fit[iexp] = self.result[ll][1]
                DataPred[:,iexp] = self.result[ll][2]
                DataExp = self.result[ll][3]
                positions_fit = self.result[ll][4]
                Nbr_poly_estimate[iexp]=self.result[ll][5]
                for i in range(len(positions_fit)):
                    PosPred[positions_fit[i],iexp]=1 # fill Positions of polymerases with 1
            fname = os.path.join(outFolder,DataFileName.replace('data_','result_'))
            print("Results saved in {}".format(fname))
            np.savez(fname, Fit=Fit, DataPred=DataPred, DataExp=DataExp, PosPred=PosPred)      
            QMessageBox.question(self, ' ', "Deconvolution Finished!", QMessageBox.Ok)
            if self.fitPerform==True:
                self.startFitFunction(self.filePathToPreProcessedFiles, self.parameterFilePath, self.fit3exp, self.fit2exp, self.useLongScript)
            
    def startAnalysis(self):
        self.generations = 10
        self.numberOfWorkers = 1
        if self.fit2CheckBox.isChecked():
            self.fit2exp=True
        else:
            self.fit2exp=False
        if self.fit3CheckBox.isChecked():
            self.fit3exp=True 
        else:
            self.fit3exp=False          
        if self.checkBoxLongMovie.isChecked():
            self.useLongScript = True            
        else:
            self.useLongScript = False 
        if self.fit2exp or self.fit3exp:
            self.fitPerform = True
        else:
            self.fitPerform = False
        #----------------------------------------------------------------------------#
        self.filePathToPreProcessedFiles = os.path.join(self.drosoDataFolderBrowseBox.text(),'npzdatafiles/')        
        if self.checkBoxDeconvolution.isChecked():
            self.performDeconvolution=True
            print("Performing deconvolution")
        else:
            self.performDeconvolution=False
        if self.performDeconvolution==True:
            self.numberOfWorkers = int(self.numberOfWorkersLineEdit.text())
            self.generations = int(self.generationsLineEdit.text())
            self.outFolder = os.path.join(self.filePathToPreProcessedFiles,'resultDec')
            if os.path.exists(self.outFolder): 
                shutil.rmtree(self.outFolder, ignore_errors = True)  
            os.mkdir(self.outFolder)
            fParam = self.parameterFilePath
            #print(fParam)
            fileFormatData='.npz'
            for DataFileName in os.listdir(self.filePathToPreProcessedFiles):
                if DataFileName.endswith(fileFormatData):
                # we load the result from read_data.m
                    fname = os.path.join(self.filePathToPreProcessedFiles,DataFileName)
                    if '.npz' in fname:
                        matcontent=np.load(fname)

                    elif '.mat' in fname:
                        matcontent=loadmat(fname)

                    DataExp=matcontent['DataExp']
                    if 'Parameters.npz' in fParam:
                        deconParameters=np.load(fParam)

                    ### calculate data specific parameters

                    sd=DataExp.shape
                    nloops = sd[1]
                    frame_num=sd[0] ### number of frames
                    FrameLen = deconParameters['FrameLen']
                    DureeSignal = deconParameters['DureeSignal']
                    DureeSimu = frame_num*FrameLen  ### film duration in s
                    DureeAnalysee = DureeSignal + DureeSimu ###(s)
                    EspaceInterPolyMin = deconParameters['EspaceInterPolyMin']
                    Polym_speed = deconParameters['Polym_speed']
                    self.num_possible_poly = round(DureeAnalysee/(EspaceInterPolyMin/Polym_speed)) # maximal number of polymerase positions
                    self.generations
                    self.job_count = nloops

                    # ------ Parallel pool this part ------ #
                    self.restart()
                    pool = QThreadPool.globalInstance()
                    pool.setMaxThreadCount(self.numberOfWorkers)
                    for i in range(1, self.job_count+1):
                        worker = poolWorker(i,self.job_count, DataExp, self.generations, fParam, self.outFolder, DataFileName,self.num_possible_poly)
                        worker.signals.completed.connect(self.complete)
                        worker.signals.started.connect(self.start)
                        worker.signals.result.connect(self.save_result)
                        pool.start(worker)                                       
                    self.pathToDeconvolutionResultsFolder = os.path.join(self.filePathToPreProcessedFiles,'resultDec/')
                    self.pathToFitResultsFolder = os.path.join(self.filePathToPreProcessedFiles)
            
                    # -------- Deconvolution Finished ---------#
        elif self.performDeconvolution==False:
              if self.fitPerform:
                  if np.size(os.path.join(self.filePathToPreProcessedFiles,'resultDec/')):                    
                      self.restart()
                      pool = QThreadPool.globalInstance()
                      worker = Stock(self.filePathToPreProcessedFiles, self.parameterFilePath, self.fit3exp, self.fit2exp, self.useLongScript)
                      worker.signals.completedFit.connect(self.completeFit)
                      worker.signals.startedFit.connect(self.startFit)
                      pool.start(worker)
                  
                    
        #------------ Whether to perform fit or not? ------------#
        
        #------------ Threads for fit funcitons -----------------#
        # ------------------ Fit ------------------#


    def restart(self):
        self.progressBarDeconvolution.setValue(0)
        self.comleted_jobs = []
        self.startAnalysisButton.setEnabled(False)
        self.gobackbutton.setEnabled(False)

    def start(self, n):
        self.listWidget.addItem(f'Deconvolving signal for nuclei #{n}...')


    def complete(self, n, T):
        self.listWidget.addItem(f'Deconvolution of nuclei #{n} signal completed.')
        self.comleted_jobs.append(n)
        self.progressBarDeconvolution.setValue(int(np.round(100*len(self.comleted_jobs)/T)))
        if len(self.comleted_jobs) == self.job_count:
            self.startAnalysisButton.setEnabled(True)
            self.gobackbutton.setEnabled(True)

    def startFit(self, n):
        self.listWidget.addItem(f'{n}...')
        self.progressBarDeconvolution.setValue(12)
        
        
    def completeFit(self, n):
        self.listWidget.addItem(f'{n}')
        self.progressBarDeconvolution.setValue(100)
        QMessageBox.question(self, ' ', "Fit Performed!", QMessageBox.Ok)
        self.startAnalysisButton.setEnabled(True)
        self.gobackbutton.setEnabled(True)
    
    def startFitFunction(self,filePathToPreProcessedFiles, parameterFilePath, fit3exp, fit2exp, useLongScript):
        self.restart()
        self.pathToDeconvolutionResultsFolder = os.path.join(self.filePathToPreProcessedFiles,'resultDec/')
        self.pathToFitResultsFolder = os.path.join(self.filePathToPreProcessedFiles)
        if self.fit2exp:
            self.listWidget.addItem('Performing a 2 state fit...')  
            self.progressBarDeconvolution.setValue(12)
        QApplication.processEvents()
        #--------------- Fit short movie -----------------------------#
        
        if self.useLongScript==False:
            if self.fit3exp:
                self.listWidget.addItem('Performing a 3 state fit...')
            QApplication.processEvents()
            fitShort(self.pathToDeconvolutionResultsFolder, self.parameterFilePath, combined=0, outputpath=self.pathToFitResultsFolder, fit3exp=self.fit3exp)                            
        #--------------- Fit Long + Short movie ----------------------#
        
        if self.useLongScript==True:
            self.listWidget.addItem("Long + short movie analysis will be done")          
            self.listWidget.addItem("Looking for long movie data file")
            fileListDeconvolved = os.listdir(self.pathToDeconvolutionResultsFolder)
            ffrag = self.pathToDeconvolutionResultsFolder.split('/')
            if 'shortDataFile' in ffrag:
                ffrag = '/'.join(ffrag[:ffrag.index('shortDataFile')+1])
                ffrag = ffrag.replace('shortDataFile', 'longDataFile')
            for jjj in range(len(fileListDeconvolved)):
                if 'result_' in fileListDeconvolved[jjj]:   
                    exp_name_tmp = fileListDeconvolved[jjj].split('_')[1]
                    exp_name_tmp = exp_name_tmp.split('.')[0]
                    expNameLongFile = 'data_'+exp_name_tmp+'_long.npz'
                    if not os.path.exists(os.path.join(ffrag,expNameLongFile)):
                        self.listWidget.addItem("Can't find long movie data file for "+exp_name_tmp+"!")
                    else:    
                        shutil.copy(os.path.join(ffrag,expNameLongFile),self.pathToDeconvolutionResultsFolder)
                        self.listWidget.addItem("Long movie data file for "+exp_name_tmp+" moved to Deoconvolution Results folder!")
            if self.fit3exp:
                self.listWidget.addItem('Performing a 3 state fit...')
            QApplication.processEvents()                     
            fitLong(self.pathToDeconvolutionResultsFolder, self.parameterFilePath, combined=0, visualize=1, outputpath=self.pathToFitResultsFolder, fit3exp=self.fit3exp)
        self.progressBarDeconvolution.setValue(100)
        self.listWidget.addItem("ANALYSIS COMPLETE!")
        QMessageBox.question(self, ' ', "Fit Performed!", QMessageBox.Ok)
        self.startAnalysisButton.setEnabled(True)
        self.gobackbutton.setEnabled(True)
        QApplication.processEvents()

                               
    def checkNumberOfThreads(self):        
        QMessageBox.question(self, 'Maximum threads available', "You can use {} threads".format(mp.cpu_count()), QMessageBox.Ok)
        
    
class preProcessDec(QDialog):
    def __init__(self):
        super(preProcessDec, self).__init__()
        loadUi("preProcess.ui", self)
        self.gobackbuttonpreProcess.clicked.connect(self.goBack)
        self.preProcessBrowseButton.setToolTip('Browse folders')
        self.preProcessBrowseButton.clicked.connect(self.selectFolderProcessShort)
        self.preProcessButton.clicked.connect(self.startPreProcessShort)
        
        self.preProcessBrowseButtonLongMovie.setToolTip('Browse folders')
        self.preProcessBrowseButtonLongMovie.clicked.connect(self.selectFolderProcessLong)
        self.preProcessButtonLongMovie.clicked.connect(self.startPreProcessLong)
        
        self.preProcessBrowseButtonLongMovieShort.setToolTip('Browse folders')
        self.preProcessBrowseButtonLongMovieShort.clicked.connect(self.selectFolderProcessLongShort)
        self.preProcessButtonLongMovie.clicked.connect(self.startPreProcessLong)
        

    def goBack(self):
        mainwindow = MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def selectFolderProcessShort(self):
        self.folder3 = QFileDialog.getExistingDirectory(self, "Select Source Directory")
        if self.folder3:
            print(self.folder3)
            self.preProcessDataFolderBrowseBox.setText(self.folder3+'/')
            

    def selectFolderProcessLong(self):
        self.folderlong = QFileDialog.getExistingDirectory(self, "Select Source Directory")
        if self.folderlong:
            print(self.folderlong)
            self.preProcessDataFolderBrowseBoxLongMovie.setText(self.folderlong+'/')  
            
    def selectFolderProcessLongShort(self):
        self.folderlongShort = QFileDialog.getExistingDirectory(self, "Select Source Directory")
        if self.folderlongShort:
            print(self.folderlongShort)
            self.preProcessDataFolderBrowseBoxLongMovieShort.setText(self.folderlongShort+'/')  
 
    def startPreProcessShort(self):
        self.fileExtension = str(self.fileExtensionLineEdit.text())
        self.filePathToRawFiles = os.path.join(self.preProcessDataFolderBrowseBox.text())
        intensityData = readRawIntensities(self.filePathToRawFiles, self.fileExtension)
        intensityData.readRawIntensitiesFromXls(0)
        QMessageBox.question(self, ' ', "Files Processed!", QMessageBox.Ok)
        
    def startPreProcessLong(self):
        
        self.filePathToRawFilesLong = os.path.join(self.preProcessDataFolderBrowseBoxLongMovie.text())
        self.mixedMovies = readRawFiles(self.filePathToRawFilesLong)
        self.thresholdLong = int(self.thresholdBox.text())       
        self.filePathLongData = self.mixedMovies.readLongMovieFiles(self.mixedMovies.longFilePath,self.thresholdLong)
        self.filePathXls = self.mixedMovies.gatherShortFiles(self.mixedMovies.shortFilePath)
        self.filePathShortData = self.mixedMovies.readRawIntensitiesFromXls(self.filePathXls)
        QMessageBox.question(self, ' ', "Files Processed!", QMessageBox.Ok)
        

app = QApplication(sys.argv)
widget = QtWidgets.QStackedWidget()
mainwindow = MainWindow()
widget.addWidget(mainwindow)
widget.setFixedHeight(648)
widget.setFixedWidth(813)
widget.show()

try:
    sys.exit(app.exec())
except:
    print("Exiting")
