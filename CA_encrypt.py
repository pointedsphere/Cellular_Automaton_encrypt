import random as r
import sys
import numpy as np

from PIL import Image
import time

from CAencrypt.util import *
from CAencrypt.rand import *
from CAencrypt.enc  import *

import argparse
from argparse import RawTextHelpFormatter

from os.path import exists


prog_description = """

An implementation of the Cellular Automata encryption algorithm in python3.

Based on work by Wuensche and Lesser [1,2].

"""


prog_epilog="""

References:
[1] Wuensche A. Encryption using cellular automata chain-rules. In: Adamatzky AR, Alonso-Sanz RA. Luniver Press; 2008. p. 126--138.
[2] Wuensche A, Lesser M. The Global Dynamics of Cellular Automata. 1st ed. Reading, Massachusetts, USA: Addison Wesley Publishing Company; 1992.

"""


# Add all the possible input flags
# Add the input arguments
parser = argparse.ArgumentParser(prog="CA Encrypt/Decrypt",\
                                 description=prog_description,\
                                 epilog=prog_epilog,\
                                 formatter_class=RawTextHelpFormatter)

# General arguments
parser.add_argument("-f","--keyFile-name",default="key.shared",type=str,\
                    help="The filename of the shared key, default 'key.shared'.")

# Arguments for shared key generation
parser.add_argument("-G","--Gen",action="store_true",\
                    help="Generate a shared keyfile.")
parser.add_argument("-k","--K",default=7,type=int,\
                    help="The neighbourhood size (must be odd), default 7.")
parser.add_argument("-T","--T",default=5,type=int,\
                    help="The number of CA steps to take for encryption/decryption (default 5).")
parser.add_argument("-N","--N",default=-1,type=int,\
                    help="The seed to use for the noise parameter, -ve for random.")

# General arguments
parser.add_argument("-V","--verbose",action="store_true",\
                    help="Use a verbose output.")

# Arguments for the input type
parser.add_argument("-B","--BW",default="img.png",type=str,\
                    help="Use an input image from the given input file, default 'img.png'.")

# Output file
parser.add_argument("-O","--output-file",default="DEFAULT",type=str,\
                    help="output filename, default either encrypted.png or decrypted.png.")

# Options to encrypt or decrypt
parser.add_argument("-E","--Enc",action="store_true",\
                    help="Encrypt the given input file.")
parser.add_argument("-D","--Dec",action="store_true",\
                    help="Decrypt the given input file.")


args = parser.parse_args()






if __name__ == "__main__":

    # Quic error checks
    if args.Gen and args.Enc:
        EXIT("Cannot have -G and -E flags set")
    elif args.Gen and args.Dec:
        EXIT("Cannot have -G and -D flags set")
    elif args.Enc and args.Dec:
        EXIT("Cannot have -E and -D flags set")
    

    if (args.Gen):

        # Generate a shared keyfile and save to the relevant output file

        # Initialise the class for key generation
        C = CA(k=args.K,numSteps=args.T)

        # Set or generate the noise seed
        if args.N>0:
            C.setNoiseSeed(args.N)
        elif args.N<0:
            C.setRandNoiseSeed()
        else:
            EXIT("Noise seed cannot be 0")
        
        # Generate a valid ruleset
        C.genRulesLeftReversible()

        # And save the output
        C.saveKey(args.keyFile_name)


    elif (args.Enc):

        # Encrypt a given input file

        # Start by initialising a CA
        C = CA()

        # Read the input file
        C.readKey(args.keyFile_name)
        
        # Set or generate the noise seed
        if args.N>0:
            C.setNoiseSeed(args.N)
        elif args.N<0:
            C.setRandNoiseSeed()
        else:
            EXIT("Noise seed cannot be 0")
        
        if args.BW:

            if args.verbose:
                print("Attempting to encrypt the greyscale image "+args.BW)
            
            # Encrypt a black and white image
            if not exists(args.BW):
                EXIT("Input black and white image '"+args.BW+"' does not exist.")

            # Read the input image and its dimensions and set the array in the CA class
            I, d = readBWImage2BinArr(args.BW)
            C.setBinEndVec(I.flatten())
            
            if args.verbose:
                print("Loaded image "+args.BW)

            # XOR final encrypted image with noise
            C.XORendArr()
                
            if args.verbose:
                print("XORed input array with random noise generated with seed "+str(C.noiseSeed))
                print("Attempting "+str(C.numSteps)+" encryption steps with k="+str(C.k))
                
            # Perform the encryption steps
            if args.verbose:
                C.CAstepsReverse(numSteps=C.numSteps,verbose=True)
            else:
                C.CAstepsReverse(numSteps=C.numSteps,verbose=False)

            if args.verbose:
                print("Encryption successful, saving output as encrypted.png")
            
            # Then save the output image
            if args.output_file == "DEFAULT":
                outfile = "encrypted.png"
            else:
                outfile = args.output_file
            saveBinArr2BWImage(outfile,C.start,d)

            # And print info about the output image/encryption
            if args.verbose:
                print("Save of encrypted image to '"+outfile+"' successful")
                print("Image/encryption properties:")
            print("    = random noise seed "+str(C.noiseSeed))

        else:

            EXIT("No valid encryption flag/file given")


    elif args.Dec:

        # Decrypt a given input file
        
        # Start by initialising a CA
        C = CA()

        # Read the input file
        C.readKey(args.keyFile_name)

        # Set or generate the noise seed
        if args.N>0:
            C.setNoiseSeed(args.N)
        elif args.N<0:
            EXIT("Noise seed must be set for decryption")
        else:
            EXIT("Noise seed cannot be 0")
            
        if args.BW:

            if args.verbose:
                print("Attempting to decrypt the greyscale image "+args.BW)
            
            # Encrypt a black and white image
            if not exists(args.BW):
                EXIT("Input black and white image '"+args.BW+"' does not exist.")

            # Read the input image and its dimensions and set the array in the CA class
            I, d = readBWImage2BinArr(args.BW)
            C.setBinStartVec(I.flatten())
            
            if args.verbose:
                print("Loaded image "+args.BW)
                
            if args.verbose:
                print("Attempting "+str(C.numSteps)+" decryption steps with k="+str(C.k))
                
            # Perform the encryption steps
            if args.verbose:
                C.CAsteps(numSteps=C.numSteps,verbose=True)
            else:
                C.CAsteps(numSteps=C.numSteps,verbose=False)

            # Then XOR the final step with the random noise
            C.XORendArr()
                
            if args.verbose:
                print("XORed final step with random noise generated with seed "+str(C.noiseSeed))
                print("Decryption successful, saving output as decrypted.png")
            
            # Then save the output image
            if args.output_file == "DEFAULT":
                outfile = "decrypted.png"
            else:
                outfile = args.output_file
            saveBinArr2BWImage(outfile,C.end,d)

            # And print info about the output image/encryption
            if args.verbose:
                print("Save of decrypted image to '"+outfile+"' successful")

        else:

            EXIT("No valid encryption flag/file given")

            
    else:

        print("A flag wasnt given that leads to any action, use one of:")
        print("    -G :: Generate a shared key file")
                

# S = 5

# K = 7

# NS = 3574541233091423

# # Import an image (black and white) and make binary black and white
# A, d = readBWImage2BinArr("circles.png")

# C = CA(k=K)

# R = r.randint(1,1000000)
# C.randSeed = R
# C.setRandSeed()
# C.setNoiseSeed(NS)
# C.setNumSteps(S)
# C.genRulesLeftReversible()

# print("random seed:",C.randSeed)

# print("number of rules:",len(C.rules))
# print("Z_right:",C.Zright)
            
# # Set initial `end point'
# C.setBinEndVec(A.flatten())

# ES,EM = binaryShannonEntroypy(C.end)
# print("Input entropy: ",ES,EM)

# # save end point
# saveBinArr2BWImage("input.png",C.end,d)

# # And XOR this end point with a random array
# C.XORendArr()
# C.CAts = C.end

# # save end point
# saveBinArr2BWImage("input_xored.png",C.end,d)
# ES,EM = binaryShannonEntroypy(C.end)

# print("Input length:", len(C.end))
# print("\nEND   ",C.end,ES,EM)
# print("")

# # Step backwards from end to encrypt saving each image
# for i in range(S):
#     t = time.time()
#     C.singleCAstepReverseL()
#     saveBinArr2BWImage("enc"+str(i)+".png",C.CAts,d)
#     ES,EM = binaryShannonEntroypy(C.CAts)
#     print(i,C.CAts,ES,EM,time.time()-t)
    
# print("\n\n")

# # Now create a new class instance
# D = CA(k=K)
# C.saveKey()

# # Step forwards to decrypt
# D.readKey()
# D.setBinStartVec(C.CAts)
# t = time.time()
# D.CAsteps()

# # And XOR with the same random array as the input was XORed with
# D.setNoiseSeed(NS)
# D.XORendArr()


# saveBinArr2BWImage("output.png",D.end,d)

# print("\nEND   ",D.end, time.time()-t)

# # for i in range(len(A)):
# #     if A.flatten()[i] != D.end[i]:
# #         EXIT("Beginning and end do not match")
# # print("Beginning and end match")


