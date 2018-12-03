#!/bin/python3

import math
import os
import random
import re
import sys
import urllib.request
import json


def ipTracker(ip):
    # Build API URL
    url = f"https://jsonmock.hackerrank.com/api/ip?ip={ip}"
    
    # Fetch API response
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
    
    # If no record exists
    if data.get("total", 0) == 0:
        return "No Result Found"
    
    # Return the country code
    return data["data"][0]["country"]


if __name__ == '__main__':
    fptr = open("output.txt", 'w')

    ip = input().strip()
    result = ipTracker(ip)

    fptr.write(str(result) + '\n')
    fptr.close()
