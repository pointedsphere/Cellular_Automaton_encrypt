import random as r
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
    
        

class CA:

    """
    A class for generating and running (both forwards and backwards) reversible cellular automata.
    """

    
    def __init__(self,k):

        # Allow for the setting of a random seed
        self.randSeed = None

        # Maximum chances to generate a valid rulest
        self.ruleGenCutoff = 100
        
        # An empty value to hold the CA rules (as a dict)
        self.rules = None

        # The size of the neighbourhood
        self.k = k
        if not isinstance(k, int):
            EXIT("CA neighbourhood k must be an integer.")
        if k<1:
            EXIT("CA neighbourhood k must be at least 1.")

        # Currently we can only use odd k, with neighbourhood centered on cell
        if (self.k%2) == 0:
            EXIT("Currently only implemented for odd k")

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

        # CA array size
        self.CAS = None
        
        # The Zleft and Zright values for checking for reversible rulesets
        self.Zleft  = None
        self.Zright = None

        
    def setRandSeed(self):
        """
        Set the random seed from the class value (if set) else exit with error.
        """
        if self.randSeed is None:
            EXIT("self.randSeed not set as class variable.")
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
            leftMostBits = padLeftZeros("{0:b}".format(b),self.k-1)
            # Use RNG to decide which is 1 and which is zero
            if r.randint(0,1) == 0:
                self.rules[leftMostBits+"0"] = 0
                self.rules[leftMostBits+"1"] = 1
            else:
                self.rules[leftMostBits+"0"] = 1
                self.rules[leftMostBits+"1"] = 0

        # We have constructed the rules with Zleft = 1
        self.Zleft = 1.0
        # But we must calcualte the Cright value
        self.Zright = self.calcZright()


    def calcZright(self):
        """
        Calculate the Zright value from a full CA rule set
        """

        if self.rules is None:
            EXIT("rules not set, so Z_right cannot be calcualted.")

        totDistinct = 0
        # Generate the right most k-1 bytes by converting the integers in [0,2^(k-1)-1]
        for b in range(0,self.numkM1):
            # Start with just the rigt most bits, i.e. that we use to create a pair
            # Use all possible binary numbers to achieve this
            rightMostBits = padLeftZeros("{0:b}".format(b),self.k-1)

            # If each pair, i.e. the two rightMostBits padded with a 1 and a 0 result
            # in a different value then add 1 to the running total of distinct
            if self.rules["1"+rightMostBits] != self.rules["0"+rightMostBits]:
                totDistinct += 2

        # Now we can scale to find the final Zright value
        return totDistinct/self.numk


    def genRulesLeftReversible(self):
        """
        Generate a CA rule set such that Z_left=1 and Z_right>=0.5
        """

        for g in range(self.ruleGenCutoff):
            self.genRulesLeft()
            if self.Zright>=0.5:
                return
            # Change the seed if it has been set, otherwise we'll just repeatedly
            # gen the same rule set
            self.randSeed += 1024
            self.setRandSeed()
            
        EXIT("failed to generate valid ruleset after "+str(self.ruleGenCutoff)+" tries.")
    

    def singleCSstep(self):
        """
        Take a single CA step taking self.CAts as the state at timestep t_{i} and then
        overwriting it with the state at time t_{i+1}
        """

        # Check that everything is set correctly
        if self.CAts is None:
            EXIT("CAts not set, so a step cannot be taken.")
        if self.rules is None:
            EXIT("rules not set, so a step cannot be taken.")
            
        # Loop over each cell, populating the tmp next cell
        tmpArr = []
        kOffset = (self.k-1)//2
        for C in range(self.CAS):
            # Populate the temp string with the central cell and the neighbourhood of k cells
            tmpStr = ""
            for S in range(C-kOffset,C+kOffset+1):
                tmpStr += str(self.CAts[S%self.CAS])

            # Append the resultant cell from the neighbourhood and the rules to a temp array
            tmpArr.append(int(self.rules[tmpStr]))

        # Now overwrite the working array with the current timestep
        self.CAts = np.array(tmpArr)


    def CSsteps(self,numSteps):
        """
        Run the CA for a set number of timesteps and set the result as the final timestep
        """
        for i in range(numSteps):
            self.singleCSstep()
        self.end = self.CAts

        

    def setBinStartVec(self,startVec):
        """
        Initialise a starting vector for the CA as a binary array
        """

        # First make sure the array contains only ones and zeros
        if np.amax(startVec)>1:
            EXIT("Staring vector should be binary, contains values > 1.")
        if np.amin(startVec)<0:
            EXIT("Staring vector should be binary, contains values < 0.")

        # Check that each value in the array is an integer
        for i in range(len(startVec)):
            if not isinstance(startVec[i], int):
                EXIT("Starting vector must be an integer array of only 1's and 0's.")

        # Check that the vector space is sufficiently large
        if len(startVec)<self.k:
            EXIT("Vector size must be at least that of neighbourhood size.")

        # If it only contains acceptable values then set the class array as a numpy array (for ease)
        self.start = np.array(startVec,dtype=int)

        # Also set the other arrays as the vector size will always remain the same
        self.CAts = np.array(startVec,dtype=int)
        self.end  = np.array(startVec,dtype=int)
        self.CAS  = len(self.end)


        
