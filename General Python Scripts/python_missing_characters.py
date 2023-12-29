#!/bin/python3

import math
import os
import random
import re
import sys


#
# Complete the 'missingCharacters' function below.
#
# The function is expected to return a STRING.
# The function accepts STRING s as parameter.
#

def missingCharacters(s):
    # Write your code here
    lower_letters = set("abcdefghijklmnopqrstuvwxyz")
    digits = set("0123456789")
    
    s_char = set(s)
    
    missing_chars = (digits | lower_letters) - s_char
    
    missing_chars_str = ''.join(sorted(missing_chars))
    
    return missing_chars_str
if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    s = input()

    result = missingCharacters(s)

    fptr.write(result + '\n')

    fptr.close()
