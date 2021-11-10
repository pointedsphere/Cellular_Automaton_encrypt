class randEQaDG:
    """
    Generate a pseudo random number based on the `Even Quicker and Dirtier Generator' 
    random number generation in [1, p275-276].

    This utilises generates each random integer R using a seed S (given as initialisation param)
    with the formula:

        R = S * 1664525 + 1013904223 (mod 2^32)
        S = R
    
    Where these two lines can be run repeatedly to find pseudo random integer R in [0,2^32)

    IMPORTANT NOTE:
    ==============
    This random number generator is a quick and dirty generator, and is NOT a secure RNG.
    It is used in this module with that knowledge.

    REFERENCES:
    ==========
    [1] ``Numerical Recipes in Fortran 77, The Art of Scientific Computing, Vol 1'', 
        Press W.H. and Teukolsky S.A. and Vetterling W.T. and Flannery B.P., 
        2nd ed, Cambridge University Press.
    """

    def __init__(self,seed=3574541233091423):
        self.rand       = seed
        self.randBit    = None
        self.randBitArr = None

    def EQaDG(self):
        """
        Generate a pseudo random integer in [0,2^32) using `Even Quicker and Dirtier Generator' 
        random number generation from [1, p275-276].
        """
        self.rand = ((self.rand*1664525+1013904223)%0b100000000000000000000000000000000)
        
    def EQaDGmp(self):
        """
        Generate a pseudo random integer in [-2^31,2^31) using `Even Quicker and Dirtier Generator' 
        random number generation from [1, p275-276].
        """        
        self.EQaDG()
        self.rand = self.rand - 0b10000000000000000000000000000000

    def EQaDGb(self):
        """
        Generate a pseudo random bit in {0,1} using `Even Quicker and Dirtier Generator' 
        random number generation from [1, p275-276].
        """
        self.EQaDGmp()
        if self.rand<0:
            self.randBit = 1
        else:
            self.randBit = 0

    def EQaDGbA(self,length):
        """
        Generate an array of pseudo random bits in {0,1} using `Even Quicker and Dirtier Generator' 
        random number generation from [1, p275-276].
        """
        self.randBitArr = []
        for i in range(length):
            self.EQaDGb()
            self.randBitArr.append(self.randBit)
        
