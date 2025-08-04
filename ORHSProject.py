import copy
from mantid.simpleapi import * #we need to figure out how to tell this program what conda environment to run our code in
import matplotlib.pyplot as plt #type:ignore
import numpy as np #type:ignore
import skimage as ski #type:ignore

class imageToolbox:
    def __init__(self, wsName, uMin, uMax):
        self.wsName = wsName #string
        self.uMin = uMin #number
        self.uMax = uMax #number
        self.image = self.imageFactory()
        
        maskArray = np.empty_like(self.image, dtype=bool)
        maskArray[:] = False #false means not masked
        self.mask = maskArray
        
        self.applymask()
        print('imbox initialized')

    def rowCol(self, specID):
        NRowModule = 3      
        NColumnModule = 3  
        NModule = NRowModule*NColumnModule 
        NRowPixel = 32 
        NColumnPixel = 32 
        NPixel = NRowPixel*NColumnPixel 
        idModule = specID // NPixel
        jModule = idModule // NColumnModule 
        iModule = idModule % NRowModule
        firstPixelInModule = idModule*NPixel
        idPixel = int(specID - firstPixelInModule) 
        jPixel =  idPixel // NColumnPixel
        iPixel = specID % NRowPixel
        jModuleMap=[3,4,5,0,1,2]
        jModule = jModuleMap.index(jModule)

        j = jModule*NColumnPixel+jPixel
        i = (iModule)*NRowPixel+iPixel

        i= NRowPixel*NRowModule-i-1

        return i,j

    def imageFactory(self):
        uMax = self.uMax 
        uMin= self.uMin 
        wsName = self.wsName

        uBin = np.abs(uMax-uMin)
        tempSlice = Rebin(InputWorkspace=wsName, Params=f'{uMin},{uBin},{uMax}')
        ws = mtd['tempSlice']
        image = np.empty((96,192))  
        for spec in range(ws.getNumberHistograms()):
            i,j = self.rowCol(spec)
            image[i,j] = ws.dataY(spec)[0] 

        self.zMax = np.max(image)
        self.zMin = np.min(image)
        print('zMax', self.zMax)
        print('zMin', self.zMin)
            
        return image
    
    def plotImage(self, displayMax, displayMin): 

        plt.imshow(self.image) #v stands for visualization, not where we are     
    
    def darkMask(self):

        mask_vals = self.image < np.max(self.image)
        self.mask[mask_vals] = True #true means masked- masks everything other than the single brightest pixel
        
        print(mask_vals)
        #print(f'The dimensions of the dark_mask_vals array are {mask_vals.shape} and its type is {mask_vals.dtype}')

    def threshMask(self, thresh, greaterThan=True):

        if greaterThan: 
            mask_vals = self.image > thresh*self.image.mean()
        else:
            mask_vals = self.image < thresh*self.image.mean()

        self.mask[mask_vals]= True

        #print(f'The dimensions of the dark_mask_vals array are {mask_vals.shape} and its type is {mask_vals.dtype}')

    def applyMask(self):

        imageCopy = copy.copy(self.image)
        imageCopy[self.mask] = 0
        self.maskedImage = imageCopy

        print(f'The dimensions of the self.mask array are {self.mask.shape} and its type is {self.mask.dtype}')
        print(f'The dimensions of the self.image array are {self.image.shape} and its type is {self.image.dtype}')
        print(f"There are {np.sum(self.mask)} masked pixels out of 18432 pixels, or {(np.sum(self.mask)/18432)*100}%.") #number of pixels changes with the dataset used

    def erasemask(self):
        
        self.mask[:] = False