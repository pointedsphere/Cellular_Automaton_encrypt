import sys
import numpy as np
import os.path
from PIL import Image


def EXIT(msg):
    """
    Exit using sys and print the error msg
    """
    sys.exit("ERROR : "+str(msg))


def padLeftZeros(toPad,Size):
    """
    Take an input sting toPad of maximum length Size and padd the array on the left with zeros
    such that the final array is of length Size
    """
    if len(toPad)>Size:
        EXIT("Input string for left padding larger than desired output length.")
    if not isinstance(toPad, str):
        EXIT("Input for padding with zeros must be a string.")
    return ("0" * (Size-len(toPad))) + toPad


def xorArrays(A1,A2):
    """
    XOR two arrays of equal length that we assume contain only binary values.
    """

    # First make sure the arrays are of equal length
    if len(A1) != len(A2):
        EXIT("Arrays to XOR not of equal length")

    # Then XOR the input arrays
    XORed = []
    for i in range(len(A1)):
        if (A1[i]==1 or A1[i]==0) and (A2[i]==1 or A2[i]==0):
            XORed.append(A1[i]^A2[i])
        else:
            EXIT("Arrays to XOR contain non-binary value")

    return np.array(XORed,dtype=int)


def readBWImage2BinArr(filename):
    """
    Read a black and white image to a binary array.

    This is done by first converting each pixel in the image into an integer in [0,255].

    We then convert each value in the array into an array of 8 binary values and flatten all
    these arrays.

    E.g. if the input is a 50 x 50 pixel black and white image will be converted into a 1D array
         of 2500 values in [0,255]. Each element is then converted into an array of 8 bits which
         results in an array of 20000 bits.
    """

    if not os.path.exists(filename):
        EXIT("File to read as binary array does not exist")

    # Load the image in as an array
    I = Image.open(filename)
    I = np.array(I,dtype=int)
    dims = I.shape
    I = I.flatten()

    # Then convert each element to a binary array
    BA = []
    for b in range(len(I)):
        bitString = padLeftZeros(bin(I[b])[2:],8)
        for j in range(8):
            BA.append(int(bitString[j]))

    return np.array(BA,dtype=int), dims


def saveBinArr2BWImage(filename,binArr,dim):
    """
    Take a binary array and save as a black and white png image.

    Each 8 bits of the binary array correspond to a pixel value in [0,255].
    This is then rearranged to the dimensions given in dim and then saved to
    the output filename.
    """

    # Check that the input binary array is 1D
    if len(binArr.shape) != 1:
        EXIT("Array to save as a BW image must be 1D")
    
    # Check that the input binary array is divisable by 8
    if len(binArr)%8 != 0:
        EXIT("Length of array to save as a BW image must be divisable by 8")
    
    # Convert each 8 bit section of the input array 
    IA = []
    for b in range(len(binArr)//8):

        # Convert the 8 bit string to a string
        tmpStr = str(binArr[b*8])
        tmpStr = tmpStr + str(binArr[(b*8)+1])
        tmpStr = tmpStr + str(binArr[(b*8)+2])
        tmpStr = tmpStr + str(binArr[(b*8)+3])
        tmpStr = tmpStr + str(binArr[(b*8)+4])
        tmpStr = tmpStr + str(binArr[(b*8)+5])
        tmpStr = tmpStr + str(binArr[(b*8)+6])
        tmpStr = tmpStr + str(binArr[(b*8)+7])

        # Append this value to the temporary array
        IA.append(int(tmpStr,2))
        
    # Then save this 'image array' to the output file
    im = Image.fromarray(np.array(np.resize(IA,dim),dtype=np.uint8))
    im.save(filename)


        
        
