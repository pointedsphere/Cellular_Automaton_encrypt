import random as r
import sys
import numpy as np

from PIL import Image
import time

from CAencrypt.util import *
from CAencrypt.rand import *
from CAencrypt.enc  import *

        
S = 5

K = 7

NS = 3574541233091423

# Import an image (black and white) and make binary black and white
A, d = readBWImage2BinArr("circles.png")

C = CA(k=K)

R = r.randint(1,1000000)
C.randSeed = R
C.setRandSeed()
C.setNoiseSeed(NS)
C.setNumSteps(S)
C.genRulesLeftReversible()

print("random seed:",C.randSeed)

print("number of rules:",len(C.rules))
print("Z_right:",C.Zright)
            
# Set initial `end point'
C.setBinEndVec(A.flatten())

# save end point
saveBinArr2BWImage("input.png",C.end,d)

# And XOR this end point with a random array
C.XORendArr()
C.CAts = C.end

# save end point
saveBinArr2BWImage("input_xored.png",C.end,d)

print("Input length:", len(C.end))
print("\nEND   ",C.end)
print("")

# Step backwards from end to encrypt saving each image
for i in range(S):
    t = time.time()
    C.singleCAstepReverseL()
    saveBinArr2BWImage("enc"+str(i)+".png",C.CAts,d)
    print(i,C.CAts, time.time()-t)
    
print("\n\n")

# Now create a new class instance
D = CA(k=K)
C.saveRules()

# Step forwards to decrypt
D.readRules()
D.setBinStartVec(C.CAts)
t = time.time()
D.CAsteps()

# And XOR with the same random array as the input was XORed with
D.setNoiseSeed(NS)
D.XORendArr()


saveBinArr2BWImage("output.png",D.end,d)

print("\nEND   ",D.end, time.time()-t)

for i in range(len(A)):
    if A.flatten()[i] != D.end[i]:
        EXIT("Beginning and end do not match")
print("Beginning and end match")


