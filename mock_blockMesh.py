#!/usr/bin/env python3
import sys
import time
import math

# Get parameters
A = float(sys.argv[1])
P = float(sys.argv[2])
M = int(round(float(sys.argv[3])))

# Fake mesh generation time
time.sleep(0.01)

# Mock objective
value = (A - 0.4)**2 + 0.1*math.sin(P) + 0.05*M

# Output in consistent format
print(f"{value:.6f}")