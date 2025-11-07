import copy
from mantid.simpleapi import * #we need to figure out how to tell this program what conda environment to run our code in
import matplotlib.pyplot as plt #type:ignore
import numpy as np #type:ignore
import skimage as ski #type:ignore

class imageToolbox:
    def __init__(self, wsName=None, uMin=None, uMax=None, image=None):
        if image is None:
            self.wsName = wsName #string
            self.uMin = uMin #number
            self.uMax = uMax #number
            self.image = self.imageFactory()
        elif image is not None:
            self.image = image

        max=self.image.max()
        self.image=(self.image)/max #normalizing image into 0-1 scale/range
        self.pixelnumber = self.image.size

        maskArray = np.empty_like(self.image, dtype=bool)
        maskArray[:] = False #false means not masked
        self.mask = maskArray
        
        self.applyMask()
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
    
    def plotImage(self, displayMax=1, displayMin=0): 

        plt.imshow(self.image, vmin=displayMin, vmax=displayMax, cmap='gray') #v stands for visualization, not where we are     
    
    def darkMask(self):

        mask_vals = self.image < np.max(self.image)
        self.mask[mask_vals] = True #true means masked- masks everything other than the single brightest pixel
        
        print(mask_vals)
        #print(f'The dimensions of the dark_mask_vals array are {mask_vals.shape} and its type is {mask_vals.dtype}')

    def threshMask(self, thresh, greaterThan=True):

        if greaterThan: 
            mask_vals = self.image > thresh
        else:
            mask_vals = self.image < thresh

        self.mask[mask_vals]= True

        #print(f'The dimensions of the dark_mask_vals array are {mask_vals.shape} and its type is {mask_vals.dtype}')

    def applyMask(self):

        imageCopy = copy.copy(self.image)
        imageCopy[self.mask] = 0
        self.maskedImage = imageCopy

        print(f'The dimensions of the self.mask array are {self.mask.shape} and its type is {self.mask.dtype}')
        print(f'The dimensions of the self.image array are {self.image.shape} and its type is {self.image.dtype}')
        print(f"There are {np.sum(self.mask)} masked pixels out of {self.pixelnumber} pixels, or {(np.sum(self.mask)/18432)*100}%.") #number of pixels changes with the dataset used

    def eraseMask(self):
        
        self.mask[:] = False

    def spectrumIDMap(self):

    #This builds an ndarray that is identical to the image of sliceImage, but populates this with the 
    # spectrum numbers from the original input workspace. The resultant array provides a convenient way
    # to recover the spectrum ID of any pair of image (i,j) coordinates.

        ws = mtd[str(self.wsName)]
        
        mapImage = np.zeros((96,192),dtype=int)  #empty array to hold data

        nSpectra = ws.getNumberHistograms()

        for spec in range(nSpectra):
        
            i,j = self.rowCol(spec) #returns indices
            
            mapImage[i,j] = int(spec) #assign y value of pixel to image array

        return mapImage
    
    def compressIDs(self,id_list):

    # Takes list (or np array) of integer pixel IDs and converts to mantid style string
        id_list = sorted(set(id_list.tolist() if isinstance(id_list, np.ndarray) else id_list))
        
        if len(id_list) == 0:
            print("empty list of pixel IDs, can\'t make a string")
            return ""

        result = []
        start = prev = id_list[0]

        for num in id_list[1:]:
            if num == prev + 1:
                prev = num
            else:
                sep = '-'
                result.append(str(start) if start == prev else f"{start}{sep}{prev}")
                start = prev = num

        # Append the last range
        sep = '-'
        result.append(str(start) if start == prev else f"{start}{sep}{prev}")

        return ",".join(result)

    def getListOfMaskedPixels(self):

    # return a list of pixel IDs that are masked.

        pixelMap = self.spectrumIDMap() # map between image and mantid spectrum numbers
        maskedPixelList = pixelMap[self.mask] # a list of spectrum IDs as integers
        return self.compressIDs(maskedPixelList) #mantid needs list as a string



