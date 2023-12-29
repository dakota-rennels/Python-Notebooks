#!/bin/python3

import math
import os
import random
import re
import sys



# write your code here
def avg(*nums):
    if not nums:
        raise ValueError("At least one argument is required")
    
    total = sum(nums)
    average = total / len(nums)
    
    return round(average, 2)

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    
    nums = list(map(int, input().split()))
    res = avg(*nums)
    
    fptr.write('%.2f' % res + '\n')

    fptr.close()