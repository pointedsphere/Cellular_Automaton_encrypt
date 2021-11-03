import random as r
import sys
import numpy as np


def padLeftZeros(toPad,Size):
    """
    Take an input sting toPad of maximum length Size and padd the array on the left with zeros
    such that the final array is of length Size
    """
    if len(toPad)>Size:
        sys.exit("ERROR : Input string for left padding larger than desired output length.")
    if not isinstance(toPad, str):
        sys.exit("ERROR : Input for padding with zeros must be a string.")
    return ("0" * (Size-len(toPad))) + toPad
    
        

class CA:

    """
    A class for generating and running (both forwards and backwards) reversible cellular automata.
    """

    
    def __init__(self,k):

        # Allow for the setting of a random seed
        self.randSeed = None

        # An empty value to hold the CA rules (as a dict)
        self.rules = None

        # The size of the neighbourhood
        self.k = k
        if not isinstance(k, int):
            sys.exit("ERROR : CA neighbourhood k must be an integer.")
        if k<1:
            sys.exit("ERROR : CA neighbourhood k must be at least 1.")
            
        # The number of possible arrangements of k-1 bits
        self.numkM1 = np.power(2,self.k-1)

        # The number of possible arrangements of k bits
        self.numk = self.numkM1 * 2

        # Start vector with which to run a CA
        self.start = None

        # Temporary vector to use for each time step
        self.CAts = None

        # Final value of the CA
        self.end = None
        
        
    def setRandSeed(self):
        """
        Set the random seed from the class value (if set) else exit with error.
        """
        if self.randSeed is None:
            sys.exit("ERROR : self.randSeed not set as class variable.")
        else:
            r.seed(self.randSeed)
        

    def genRulesLeft(self):
        """
        Generate a dictionary of rules such that Z_left = 1,
        i.e. a rule that we can reverse by moving from left to right
        """

        # Initialise rules dictionary
        self.rules = {}
        # Generate the left most k-1 bytes by converting the integers in [0,2^(k-1)-1]
        for b in range(0,self.numkM1):
            # Start with just the left most bits, i.e. that we use to create a pair, one
            # ending in 1 the other in 0. But these must be distinct, so cant both result
            # in a 0 or 1
            leftMostBits = padLeftZeros("{0:b}".format(b),2)
            # Use RNG to decide which is 1 and which is zero
            if r.randint(0,1) == 0:
                self.rules[leftMostBits+"0"] = 0
                self.rules[leftMostBits+"1"] = 1
            else:
                self.rules[leftMostBits+"0"] = 1
                self.rules[leftMostBits+"1"] = 0
            

    def setBinStartVec(self,startVec):
        """
        Initialise a starting vector for the CA as a binary array
        """

        # First make sure the array contains only ones and zeros
        if np.amax(startVec)>1:
            sys.exit("Error : Staring vector should be binary, contains values > 1.")
        if np.amin(startVec)<0:
            sys.exit("Error : Staring vector should be binary, contains values < 0.")

        # Check that each value in the array is an integer
        for i in range(len(startVec)):
            if not isinstance(startVec[i], int):
                sys.exit("ERROR : Starting vector must be an integer array of only 1's and 0's.")
            
        # If it only contains acceptable values then set the class array as a numpy array (for ease)
        self.start = np.array(startVec,dtype=int)

        # Also set the other arrays as the vector size will always remain the same
        self.CAts = np.array(startVec,dtype=int)
        self.end  = np.array(startVec,dtype=int)

        
