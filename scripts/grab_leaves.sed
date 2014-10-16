#!/bin/sed -f

# Sed script to extract the leaves from a PTB-style parse
s/[^)]*\(([^()]*)\)[) ]*/\1 /g

# clean out extra spaces
s=  *= =g
s=^ *==g
