#!/usr/bin/python

infilename = '/Volumes/files/business/NYCEP/tables 2010:8:2/specimen.csv'
outfilename = '/Volumes/files/business/NYCEP/tables 2010:8:2/specimen_out.csv'

infile  = open(infilename, 'r')
outfile = open(outfilename, 'w')

for i in range(15):
    line = infile.readline().rstrip()
    arr  = line.split(',')
    j    = 0
    while j < len(arr):
        arr2 = []
        arr2.append(arr[j])
        if arr[j] != '' and arr[j][0] == '"':
            while arr[j][-1] != '"':
                k = j + 1
                arr[j] += ', ' + arr[k]
                k += 1
            j += k - j
        j += 1
    print arr2
    print ''

infile.close()
outfile.close()