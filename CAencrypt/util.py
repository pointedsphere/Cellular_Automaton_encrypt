import sys
import numpy as np


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
