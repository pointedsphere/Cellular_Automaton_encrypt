# CA_encrypt

An encryption method using Cellular Automata (CA) following the work of Wuensche in [^1]. This is constructed here for the purposes of better understanding Wuensche's proposed method of CA based encryption and to test the cryptographic strength of the algorithm.



## Some Initial Definitions/Methods

Before considering the CA encryption method we assume a degree of familiarity with CAs (see for example [^2], [^3] or [^4]). With this in mind we only consider only elementary cellular automata, i.e. 1 dimensional CA with a rule-set dependant only on the cells nearest neighbours. Let the size of this neighbourhood be `k` where `k` is odd such that to calculate the ith cell at the next time step we consider the cells [i-((k-1)/2),i+((k-1)/2)].

Then consider a CA rule-set `R : b^k to b` for `b in {0,1}`. Note the rule-set `R` need not be injective or surjective, and therefore need not have an inverse. However, we can construct a rule-set such that there exists an algorithm that can reverse a CA step following [^1].

Consider the set of unique permutations of `k-1` bits, then let `p` be some element of this set. To construct a pair of rules for the CA we can take `p` and append a 0 (to the right) then designate the output of the rule for these `k` bits to be `b_0`. We can do the same again but this time appending a 1 resulting in `b_1`. We say that this pair of `k-1` bits is distinct if `b_0 /= b_1`. We then do this for all permutations of `k-1` bits totalling up the number of distinct pairs and divide by the number of permutations to give us `Z_left`, where a similar approach (but with appending on the left) would give us `Z_right` [^1].

Note the left and right in the previous paragraph may seem to be the wrong way around, but the above naming convention makes more sense once a backwards CA step has been ran.



### Running a CA Backwards

We start by generating a CA rule-set such that `Z_left = 1`, furthermore we require `Z_right>=0.5` (following [^1]).

We then assume we know all `i` cells in a 1D periodic array indexed from `1` to `N` at a current time `j`. To find valid cells at time `j-1` we first guess the first `k-1` bits in the neighbourhood of cell `1`. As the pair of possible sets of `k` neighbourhood bits starting the `k-1` are distinct the known cell value at time `j` can be found.

We then move along the cell from left to right, ending on cell `N`. At this point we have an array of cells at time `j` that is of length `N+k-1`, where the `(k-1)/2` elements on either end of this new array are the 'wraparound values' that result from the periodicity of the array. If the periodic conditions are met the guessed bits are sufficient, if not we guess again and repeat until we find a valid backwards step. This approach is as described in more detail in [^1].

Note, it is possible that we cannot find a backwards step. However, this is unlikely to happen given a large enough state space (i.e. array of cells of bits).



#### Example

Let `k=3` and `N=5`. Also let the array of cells at time `j` be given by
```
| 1 | 0 | 0 | 1 | 1 |
```
Then we guess our first two bits (labelled `G_N` and `G_1`) to be `0` and `1` where we wish to calculate the bit labelled `C_2`:
```
 G_N=0 | G_1=1 | C_2 |
       | 1     | 0   | 0 | 1 | 1 |
```
As the pairs of rules for `010` and `011` are distinct (i.e. one leads to a `1` and the other a `0`) we can find `C_2` from the two guessed values and the result of `1`. We then have the two `G` values and `C_2`, where we use `G_1` and `C_2` to find `C_3`
```
 G_N=0 | G_1=1 | C_2 | C_3 |
       | 1     | 0   | 0   | 1 | 1 |
```
We continue in this way to find all `C` values:
```
 G_N=0 | G_1=1 | C_2 | C_3 | C_4 | C_5 | C_6
       | 1     | 0   | 0   | 1   | 1   |
```
Due to the periodicity of the array it must be the case that `G_N=C_5` and `G_1=C_6`. If this is the case then the previous step we have found is valid (though it is not necessarily the only valid 'backwards step').



## CA Only Symmetric Key Encryption

Let us assume Alice has some binary data represented as a 1D array of cells she wishes to encrypt, `D`. Let us also assume she wishes to send the encrypted data to Bob.

First Alice decides on some odd `k>1` and then generates a random CA rule list `R` that fulfils `Z_left=1` and `Z_right>=0.5`. Alice also decides on the number of CA steps to use, `T>=1`. This rule list along with `k` and `T` is the symmetric key which must be secretly shared with Bob.

Alice then steps backwards from `D` by `T` steps using `R`. This data is the encrypted data that is sent to Bob. Bob can then decrypt by taking `T` forward steps using `R` (which is a much cheaper operation).



### Example

We start by setting `T=5` and `k=7` and randomly generate a rule set with `Z_left=1` and `Z_right>=0.5`. We then take our initial data (i.e. cells at time `j`) from a simple image, where each pixel of the image is either `0` (white) or `1` (black). Encrypting by evolving the CA backwards in time by 5 steps gives the results below, where each CA backwards step is shown (going from right to left with each step separated by a red line):

![Steps backwards using a CA with `k=1`](images/multiple_enc_no_noise.png)

It is clear the encryption is 'not enough' after these 5 steps to completely obscure all the information in input. Of particular note are the low entropy areas at the top and bottom of the image (where there were large blocks of `0`s) and the central point (where a similar pattern repeated over many lines).

One way to get around this is by stepping back by a much larger number of steps. However, the cost involved in the encryption stepping backwards is not trivial as such adding many more steps is far from ideal.



## Adding a XOR to Increase Entropy

One idea to increase the entropy is to XOR our input data with a pseudo random bit string. One method would be for Alice to publicly distribute this random bit string. Bob could then take the string and XOR it with the result of performing decryption to recover the encrypted message.

It is hoped that this will lead to more entropy in the encrypted data regardless as to if blocks of data are repeated.

As this random bit string is public it can be varied with each message in order to further obfuscate the key.

### Method

Instead of distributing a large bit string (of the same size as the encrypted data) we distribute a random seed. This is coupled with (for now) the 'Even Quicker and Dirtier Generator' for random numbers from [^5] (p275-276). To generate the a random number `R` we need an initial seed `S`, then for every random number we perform:

```
R = S * 1664525 + 1013904223 (mod 2^32)
S = R
```

### Example of XORing

If we take the same image input as earlier and just XOR with a bit string create with the random seed `3574541233091423` we get

![Example of circle XORed](images/curcles_XORed_example.png)

This, on first look, does seem more random, almost encrypted. However, if Alice were to just perform this step and ignore the CA, Eve (who's been listening in) also has access to the pseudo random bit string (or at least the seed used to generate it). This means Alice could easily just XOR with the random noise bit string and recover the original message.







## References

[^1]:Wuensche A. Encryption using cellular automata chain-rules. In: Adamatzky AR, Alonso-Sanz RA, editors. Automata [Internet]. Luniver Press; 2008. p. 126--138. Available from: https://users.sussex.ac.uk/~andywu/downloads/papers/2008_encryption.pdf

[^2]:Wolfram S. Statistical mechanics of cellular automata. Rev Mod Phys. 1983;55(3):601–44. 

[^3]:1. Wuensche A, Lesser M. The Global Dynamics of Cellular Automata [Internet]. 1st ed. Reading, Massachusetts, USA: Addison Wesley Publishing Company; 1992. Available from: https://users.sussex.ac.uk/~andywu/gdca.html

[^4]:Dascălu M. Cellular Automata and Randomization: A Structural Overview. In: López-Ruiz R, editor. From Natural to Artificial Intelligence - Algorithms and Applications [Internet]. Rijeka: IntechOpen; 2018. p. 165–83. Available from: https://www.intechopen.com/chapters/62760

[^5]:``Numerical Recipes in Fortran 77, The Art of Scientific Computing, Vol 1'', Press W.H. and Teukolsky S.A. and Vetterling W.T. and Flannery B.P., 2nd ed, Cambridge University Press.

