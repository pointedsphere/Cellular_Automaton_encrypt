import sys
import numpy as np
import os.path
from PIL import Image


def EXIT(msg):
    """
    Exit using sys and print the error msg.
    """
    sys.exit("ERROR : "+str(msg))


def padLeftZeros(toPad,Size):
    """
    Take an input sting toPad of maximum length Size and padd the array on the left with zeros
    such that the final array is of length Size

    INPUTS
    ======
    toPad
        A 1D integer array that will be padded with zeros. Must have a length less than or equal
        to Size.
    Size
        The desired output size after padding.

    RETURNS
    =======
    Padded array
        The array toPad but with zeros appended on the left such that the output array is of 
        length Size.
    """
    if len(toPad)>Size:
        EXIT("Input string for left padding larger than desired output length.")
    if not isinstance(toPad, str):
        EXIT("Input for padding with zeros must be a string.")
    return ("0" * (Size-len(toPad))) + toPad


def xorArrays(A1,A2):
    """
    XOR two arrays of equal length that we assume contain only binary values.

    INPUTS
    ======
    A1, A2
        The two arrays to XOR together. They must both be of the same length and only contain
        binary values (as integers).

    RETURNS
    =======
    XORed array
        An array of binary values containing the result of XORing A1 and A2.
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


def binaryShannonEntroypy(binArr):
    """
    Calcualte the binary Shannon entropy (S) from an array of binary values in {0,1}.
    Also calcualte the metric entropy (M in [0,1]), which is the Shannon entropy divided by 
    the length of the array.

    We want, for a completely random array, the metric entropy to be as close to 1 as possible.

    Shannon entropy is calculated with:
    
        $$$   S = - \sum_{i=0}^{1} p(i)log_{2}(p(i))   $$$

    where 2 is the total number of possible values an element of the input array can have,
    p(i) is the number of values i in the array divided by the length of the array.

    e.g. Let us calcualte the Shannon entropy for the binary array 11001111, we do this with

        S = - ( (0.25 log_2 (0.25)) + (0.75 log_2 (0.75)) )
          = - ( (-0.5) + (-0.311278...) )
          = 0.811278...
    
    and the metric entropy is M=0.101410...
    
    INPUTS
    ======
    binArr
        An array of binary values in {0,1}.

    RETURNS
    =======
    Shannon entropy
        The calcualted Shannon entropy of the current array.
    Metric entropy
        The Shannon entroppy divided by the length of the input array.
    """

    # Convert the input array to a numpy array, just to make sure it's in that form
    B = np.array(binArr,dtype=int)

    # Check that the array only contains the values 0 and 1
    if np.amax(B)>1 or np.amin(B)<0:
        EXIT("binary Shannon entropy calcualtion can only take in array containing binary values")

    # Then calculate the p(0) and p(1) values
    p0 = np.count_nonzero(B==0) / len(B)
    p1 = np.count_nonzero(B==1) / len(B)

    # Then calculate the Shannon entropy
    S = - ( (p0*np.log2(p0)) + (p1*np.log2(p1)) )

    # And the metric entropy
    M = S / len(B)

    return S, M
    

def readBWImage2BinArr(filename):
    """
    Read a black and white image to a binary array.

    This is done by first converting each pixel in the image into an integer in [0,255].

    We then convert each value in the array into an array of 8 binary values and flatten all
    these arrays.

    E.g. if the input is a 50 x 50 pixel black and white image will be converted into a 1D array
         of 2500 values in [0,255]. Each element is then converted into an array of 8 bits which
         results in an array of 20000 bits.

    INPUTS
    ======
    filename
        The filename of the image to read. The image must be greyscale.

    RETURNS
    =======
    image array
        A 1D binary array containing the image data. Each pixel is converted to an 8 bit binary integer.
    
    dims
        The dimensions of the file that is read.
    """

    if not os.path.exists(filename):
        EXIT("File to read as binary array, "+filename+", does not exist")

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

    INPUTS
    ======
    filename
        The filename to save the image to. Image will be greyscale.
    binArr
        A 1d array containing the information about each pixel. Each 8 bits in the array contain
        the greyscale infromation of a single pixel.
    dim
        The dimensions of final saved image.
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


        
        
