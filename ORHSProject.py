import copy
from mantid.simpleapi import *
import matplotlib.pyplot as plt
import numpy as np
import skimage as ski

class imageToolbox:
    def __init__(self, wsName, uMin, uMax):
        self.wsName = wsName #string
        self.uMin = uMin #number
        self.uMax = uMax #number
        self.image = self.imageFactory()
        self.blankmask = None
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
    
    def plotimage(self, displayMax, displayMin): 
          plt.imshow(self.image) #v stands for visualization, not where we are     
    
    def darkMask(self):

        maskArray = np.empty_like(self.image, dtype=bool)
        maskArray[:] = False

        dark_mask_vals = self.image < np.max(self.image)
        maskArray[dark_mask_vals] = True

        self.blankmask = maskArray

        print(dark_mask_vals)