import random as r
import sys
import numpy as np

from PIL import Image
import time

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
    XOR two arrays of equal length that we assume contain only binary values
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


class CA:

    """
    A class for generating and running (both forwards and backwards) reversible cellular automata (CA).

    The CA in question is a nieve type, where we start with a neighbourhood of size k, where k is odd.
    We then update the cell at time t_i+1 from the neighbourhood at time t_i, centered on the cell
    in question.

    NOTABLE VARIABLES
    =================

    rules:
        A dictionary containing the rules for the CA. The key is the k bits from time t_i and the
        value is a 1 or zero corresponding to that neighbourhood.

    """

    
    def __init__(self,k=1):

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
            if self.randSeed is not None:
                self.randSeed += 1024
                self.setRandSeed()
            
        EXIT("failed to generate valid ruleset after "+str(self.ruleGenCutoff)+" tries.")
    

    def singleCAstep(self):
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
        # Find the first k-1 cells of the first neighbourhood with a dummy first bit
        # that will be removed on the first loop
        tmpStr = "B"
        for S in range(-kOffset,kOffset):
            tmpStr += str(self.CAts[S])

        for C in range(self.CAS):
            # Append the final cell in the current neighbourhood to the full neighbourhood
            tmpStr = tmpStr[1:] + str(self.CAts[(C+kOffset)%self.CAS])
            
            # Append the resultant cell from the neighbourhood and the rules to a temp array
            tmpArr.append(int(self.rules[tmpStr]))

        # Now overwrite the working array with the current timestep
        self.CAts = np.array(tmpArr)


    def CAsteps(self,numSteps):
        """
        Run the CA for a set number of timesteps and set the result as the final timestep
        """
        for i in range(numSteps):
            self.singleCAstep()
        self.end = self.CAts


    def singleCAstepReverseL(self):
        """
        Perform a step backwards in the CA using the current rules assuming Z_left=1.

        We do this by starting from the central cell at the position (k-1)/2 from the end
        of the array, i.e. at -((k-1)//2). We then guess the first k-1 cell values at time
        t_i-1. We then use these k-1 values and the known resultant value to determin the
        last bit in the neighbourhood.

        We then step forwards from left to right, going over each cell at time t_i, moving
        from -ve to +ve array indices until we reach element -1. We then have an overlap,
        i.e. the first k-1 and last k-1 cell values should be identical.

        If they are identical, then great, we have reversed the CA. If they are not then
        start again and make a different guess for the first k-1 cell values.

        EXAMPLE
        =======

        Let k=3 and the message to be of length N+1. Then the first known cell at time
        t_i we look at is index 0. We do this by considering the neighbourhood about 0.
        As shown below we guess the two G neighbourhood values at time t_i-1. We also
        consider the value of the -1 index of cell values at time t_i. From this we can
        calculate the value R in the nighbourhood t_i-1.
        
         G  G | R
        -2 -1 | 0 1 2 ... N |  <- cells at time t_i, all known

        We then step forwards and use the previous result (C) and consider the cell at time
        t_i with index 0 to find the last value in the neighbourhood, shown as R below.

         G  G | C R
        -2 -1 | 0 1 2 ... N |  <- cells at time t_i, all known
        
        We keep going until we find all by calcualting the values in such a way shown below

         G  G | C C C ...  C  C |
        -2 -1 | 0 1 2 ... N-1 N |  <- cells at time t_i, all known

        We then compare the two guess values G with the two values C for N-1 and N. They
        should match if we have done everything correctly. If not, start again with a 
        different guess.
        """
        
        # Try for all the possible combinations of the first k-1 bits
        for b in range(0,self.numkM1):
            
            # We have a temporary array to save the attempt at the previous timestep cells to
            CAtmp = []

            # Guess the first k-1 bits
            prevBits = padLeftZeros("{0:b}".format(b),self.k-1)

            # Add these to the CAtmp array
            for l in range(self.k-1):
                CAtmp.append(int(prevBits[l]))

            # Run from the last k-1 cells from the current timestep over a periodic boundary
            # to the last element of the current time step cells
            # for c in range(-((self.k-1)//2),len(self.CAts)-((self.k-1)//2)):
            for c in range(0,len(self.CAts)):
                
                # As we have a binary choice, we only need check if the result of appending the
                # previous bits with a 1 gives the required cell value, otherwise the correct
                # appended bit is a zero
                if self.rules[prevBits+"1"]==self.CAts[c]:
                    appendBit = "1"
                else:
                    appendBit = "0"

                # Add the correct cell to the tmp array for the previous timestep
                CAtmp.append(int(appendBit))

                # Update the previous bits for the next step
                prevBits = prevBits[1:] + appendBit
                
            # Now check that the periodicity condition is also satisfied
            correctGuess = True
            for c in range((self.k-1)//2):
                if (CAtmp[c] != CAtmp[-(self.k-1)+c]) \
                   or (CAtmp[c+(self.k-1)//2] != CAtmp[-(self.k-1)//2+c]):
                    correctGuess = False
            if correctGuess == True:
                self.CAts = np.array(CAtmp[(self.k-1)//2:len(CAtmp)-(self.k-1)//2],dtype=int)
                return

        # If we have got this far something has gone wrong
        EXIT("Cannot reverse CA step")


    def CAstepsReverse(self,numSteps):
        """
        Run the CA backwardsfor a set number of timesteps and set the result as the final timestep
        """
        # Need to initially set the CAts from the end point
        self.CAts = self.end
        for i in range(numSteps):
            self.singleCAstepReverseL()
        self.start = self.CAts

        
    def setBinStartVec(self,startVec):
        """
        Initialise a starting vector for the CA as a binary array
        """

        # First make sure the array contains only ones and zeros
        if np.amax(startVec)>1:
            EXIT("Staring vector should be binary, contains values > 1.")
        if np.amin(startVec)<0:
            EXIT("Staring vector should be binary, contains values < 0.")

        # # Check that each value in the array is an integer
        # for i in range(len(startVec)):
        #     if not isinstance(startVec[i], int):
        #         EXIT("Starting vector must be an integer array of only 1's and 0's.")

        # Check that the vector space is sufficiently large
        if len(startVec)<self.k:
            EXIT("Vector size must be at least that of neighbourhood size.")

        # If it only contains acceptable values then set the class array as a numpy array (for ease)
        self.start = np.array(startVec,dtype=int)

        # Also set the other arrays as the vector size will always remain the same
        self.CAts = np.array(startVec,dtype=int)
        self.end  = np.array(startVec,dtype=int)
        self.CAS  = len(self.end)


    def setBinEndVec(self,endVec):
        """
        Initialise an ending vector for the CA as a binary array
        """

        # First make sure the array contains only ones and zeros
        if np.amax(endVec)>1:
            EXIT("Ending vector should be binary, contains values > 1.")
        if np.amin(endVec)<0:
            EXIT("Ending vector should be binary, contains values < 0.")

        # # Check that each value in the array is an integer
        # for i in range(len(endVec)):
        #     if not isinstance(endVec[i], int):
        #         EXIT("Ending vector must be an integer array of only 1's and 0's.")

        # Check that the vector space is sufficiently large
        if len(endVec)<self.k:
            EXIT("Vector size must be at least that of neighbourhood size.")

        # If it only contains acceptable values then set the class array as a numpy array (for ease)
        self.start = np.array(endVec,dtype=int)

        # Also set the other arrays as the vector size will always remain the same
        self.CAts = np.array(endVec,dtype=int)
        self.end  = np.array(endVec,dtype=int)
        self.CAS  = len(self.end)


    def saveRules(self,filename="key.shared"):
        """
        Save the ruleset by iterating through each pair of integers in [0,k-1] saving output for appending
        0 then the output for appending 1.
        """

        if self.rules is None:
            EXIT("No rules set, so nothing to save")

        outputArr = []
        for b in range(0,self.numkM1):
            if self.rules[padLeftZeros("{0:b}".format(b),self.k-1)+"0"] == 0:
                outputArr.append(0)
                outputArr.append(1)
            else:
                outputArr.append(1)
                outputArr.append(0)

        # Save the data out
        keyHead = "k ::: " + str(self.k) + "\nR :::"
        np.savetxt(filename, np.array(outputArr,dtype=int), newline=" ", fmt="%s", header=keyHead)


    def readRules(self,filename="key.shared"):
        """
        Read the ruleset by iterating through each pair of integers in [0,k-1] saving output for appending
        0 then the output for appending 1.
        """

        # Read the data in from the output file
        with open(filename,"r") as f:
            inputK   = int(f.readline().split(" ")[-1])
            inputArr = np.array(f.readline().split(" ")[3:])

        # Set all the values related to k
        self.numkM1 = np.power(2,self.k-1)
        self.numk = self.numkM1 * 2

        # Empty out all the VA vectors (just in case)
        self.start = None
        self.CAts = None
        self.end = None
        self.CAS = None
        
        # Then save the input ruleset to the class variable
        self.rules = {}
        i = 0
        for b in range(0,self.numkM1):
            self.rules[padLeftZeros("{0:b}".format(b),self.k-1)+"0"] = int(inputArr[i])
            i+=1
            self.rules[padLeftZeros("{0:b}".format(b),self.k-1)+"1"] = int(inputArr[i])
            i+=1
        
        # We currently only use Zleft=1 rulesets, so set/calcualte both Z values
        self.Zleft  = 1.0
        self.Zright = self.calcZright()            
        

S = 2

K = 7

# Import an image (black and white) and make binary black and white
A = np.asarray(Image.open("circles.png"))
A = np.array(A/255,dtype=int)
Ashape = A.shape

C = CA(k=K)

R = r.randint(1,1000000)
C.randSeed = R
C.setRandSeed()

C.genRulesLeftReversible()
print("random seed:",C.randSeed)

print("number of rules:",len(C.rules))
print("Z_right:",C.Zright)

# C.setBinStartVec([0,1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,1,0,0,1,0])
# print(C.start)
# for i in range(20):
#     C.singleCAstep()
#     if i==19:
#         print("\n\n")
#     print(C.CAts)

# print("-------------------------")
# C.setBinStartVec([0,0,0,0,0,0,0,0,0,0,1])
# C.CAsteps(20)
# print(C.end)

# print("\n\n")
# for i in range(20):
#     C.singleCAstepReverseL()
#     if i==19:
#         print("\n\n")
#     print(C.CAts)

def saveImage(fname,D1arr,outShape):
    im = Image.fromarray(np.array(np.resize(D1arr,outShape)*255,dtype=np.uint8))
    im.save(fname)

def randArr(length):
    seed = 1000
    A = []
    for i in range(length):
        seed = ((1664525*seed+1013904223)%0b100000000000000000000000000000000)\
            -0b10000000000000000000000000000000
        if seed<0:
            A.append(1)
        else:
            A.append(0)
    return np.array(A,dtype=int)
            
# Set initial `end point'
C.setBinEndVec(A.flatten())

# save end point
saveImage("input.png",C.end,Ashape)

# Generate a random array (currently for testing XOR)
randArr = randArr(len(C.end))

# Xor the noise array with the end array
C.end = xorArrays(C.end,randArr)
C.CAts = C.end

# save end point
saveImage("input_XORed.png",C.CAts,Ashape)

print("Input length:", len(C.end))
print("\nEND   ",C.end)
print("")

# Step backwards from end to encrypt saving each image
for i in range(S):
    t = time.time()
    C.singleCAstepReverseL()
    saveImage("enc"+str(i)+".png",C.CAts,Ashape)
    print(i,C.CAts, time.time()-t)
    
print("\n\n")

# Now create a new class instance
D = CA(k=K)
C.saveRules()
D.readRules()
D.setBinStartVec(C.CAts)

# Step forwards to decrypt, saving each as an image
for i in range(S):
    t = time.time()
    D.singleCAstep()
    print(i,D.CAts, time.time()-t)
    saveImage("dec"+str(i)+".png",D.CAts,Ashape)

print("\nEND   ",D.CAts)

# Xor for the final result
D.CAts = xorArrays(D.CAts,randArr)
saveImage("output.png",D.CAts,Ashape)

for i in range(len(A)):
    if A.flatten()[i] != D.CAts[i]:
        EXIT("Beginning and end do not match")
print("Beginning and end match")


