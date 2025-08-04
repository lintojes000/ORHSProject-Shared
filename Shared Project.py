import copy
from mantid.simpleapi import *
import matplotlib.pyplot as plt
import numpy as np 
import skimage as ski

class imageToolbox:
    def __init__(self, wsName, uMin, uMax):
        self.wsName = wsName
        self.uMin = uMin
        self.uMax = uMax
        self.image = self.imageFactory()
        maskArray = np.empty_like(self.image, dtype=bool)
        maskArray[:] = False
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
         uMin = self.uMin
         wsName = self.wsName
         uBin = np.abs(uMax-uMin)
         tempSlice = Rebin(InputWorkspace=wsName, Params=f'{uMin},{uBin},{uMax}')
         ws = mtd['tempSlice']
         image = np.empty((96, 192))
         for spec in range(ws.getNumberHistograms()):
              i,j = self.rowCol(spec)
              image[i,j] = ws.dataY(spec)[0]
         self.zMax = np.max(image)
         self.zMin = np.min(image)
         print('zMax', self.zMax)
         print('zMin', self.zMin)

         return image
    
    def plotimage(self, displayMax, displayMin):
     plt.imshow(self.image)

    def darkMask(self):
         mask_vals = self.image < np.max(self.image)
         self.mask[mask_vals] = True
         print(mask_vals)
         print(f'The length of the dark_mask_vals is {len(mask_vals)}')
         print(f'The dimensions of the dark_mask_vals are {mask_vals.shape} and its type is {mask_vals.dtype}')

    def applymask(self):
         imagecopy = copy.copy(self.image)
         imagecopy[self.mask] = 0
         self.maskedimage = imagecopy
         print(f'The dimensions of the self.mask array are {self.mask.shape} and its type is {self.mask.dtype}')
         print(f'The dimensions of the self.image array are {self.image.shape} and its type is {self.image.dtype}')
         print(f'There are {np.sum(self.mask)} masked pixels out of 18432 pixels, or {(np.sum(self.mask)/18432)*100}%.')

    def erasemask(self):
         self.mask[:] = False

    def threshmask(self, thresh, greaterthan=True):
         if greaterthan:
              mask_vals = self.image > thresh*self.image.mean()
         else:
              mask_vals = self.image < thresh*self.image.mean()

         self.mask[mask_vals] = True

         print(f'The dimensions of the dark_mask_vals array are {mask_vals.shape} and its type is {mask_vals.dtype}')