import random as r
import sys
import numpy as np

from PIL import Image
import time

from CAencrypt.util import *
from CAencrypt.rand import *
from CAencrypt.enc  import *

        
S = 2

K = 7

NS = 3574541233091423

# Import an image (black and white) and make binary black and white
A = np.asarray(Image.open("circles.png"))
A = np.array(A/255,dtype=int)
Ashape = A.shape

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

def saveImage(fname,D1arr,outShape):
    im = Image.fromarray(np.array(np.resize(D1arr,outShape)*255,dtype=np.uint8))
    im.save(fname)
            
# Set initial `end point'
C.setBinEndVec(A.flatten())

# save end point
saveImage("input.png",C.end,Ashape)

# And XOR this end point with a random array
C.XORendArr()
C.CAts = C.end

# save end point
saveImage("input_XORed.png",C.end,Ashape)

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

# Step forwards to decrypt
D.readRules()
D.setBinStartVec(C.CAts)
D.CAsteps()

# And XOR with the same random array as the input was XORed with
D.setNoiseSeed(NS)
D.XORendArr()

saveImage("output.png",D.end,Ashape)

print("\nEND   ",D.end)

# # Xor for the final result
# D.CAts = xorArrays(D.CAts,randArr)
# saveImage("output.png",D.CAts,Ashape)

for i in range(len(A)):
    if A.flatten()[i] != D.end[i]:
        EXIT("Beginning and end do not match")
print("Beginning and end match")


