#!/bin/python3

import math
import os
import random
import re
import sys



#
# Complete the 'findSum' function below.
#
# The function is expected to return a LONG_INTEGER_ARRAY.
# The function accepts following parameters:
#  1. INTEGER_ARRAY numbers
#  2. 2D_INTEGER_ARRAY queries
#

def findSum(numbers, queries):
    pre_sums = [0] * (len(numbers) + 1)
    zero_counts = [0] * (len(numbers) + 1)
    
    for i in range(1, len(numbers) + 1):
        pre_sums[i] = pre_sums[i - 1] + numbers[i - 1]
        zero_counts[i] = zero_counts[i - 1] + (1 if numbers[i - 1] == 0 else 0)

    result = []
    for l, r, x in queries:
        sum_range = pre_sums[r] - pre_sums[l-1]
        zeros = zero_counts[r] - zero_counts[l-1]
        sum_range += zeros * x
        result.append(sum_range)
    return result

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    numbers_count = int(input().strip())

    numbers = []

    for _ in range(numbers_count):
        numbers_item = int(input().strip())
        numbers.append(numbers_item)

    queries_rows = int(input().strip())
    queries_columns = int(input().strip())

    queries = []

    for _ in range(queries_rows):
        queries.append(list(map(int, input().rstrip().split())))

    result = findSum(numbers, queries)

    fptr.write('\n'.join(map(str, result)))
    fptr.write('\n')

    fptr.close()
