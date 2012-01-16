#!/usr/bin/python

# Simple python data grabber.
import urllib
import json
import urllib2
import os
import sys
import optparse

hostList = ['scopeone.local', 'scopetwo.local']

def doDownloadData(channel, ip):
	url = 'http://' + ip + '/data/Tek_CH' + str(channel) + '_Wfm.csv'

	# The format of this payload comes from a Wireshark capture from the scope.
	# It's not a standard POST request.
	data = """WFMFILENAME=CH""" + str(channel) + """\r
WFMFILEEXT=csv\r
command=select:control ch""" + str(channel) + """\r
command1=save:waveform:fileformat spreadsheet\r
command2=:data:resolution full;:save:waveform:spreadsheet:resolution full\r
wfmsend=Get\r\n"""

	req = urllib2.Request(url, data)
	response = urllib2.urlopen(req)
	rawData = response.read()

	lines = rawData.split('\n')
	lines = map(lambda x: x.strip().split(','), lines)

	return lines[16:-3]

def rangeFromString(cmdVar):
	ret = set()
	for s in cmdVar.split(','):
		ss = s.split('-')
		ret.update(range(int(ss[0]), int(ss[-1])+1))
	return sorted(ret)

def doReceiveRangeFromUser(valid):
	while True:
		inputString = sys.stdin.readline().strip()
		inputRange = []
		try:
			inputRange = rangeFromString(inputString)
		except:
			print 'Invalid input, please try again'
			continue
		if not (False in map(lambda x: x in valid, inputRange)):
			return inputRange	
		print 'Invalid input, please try again'	

# Check for file name argument				
if len(sys.argv) < 2:
	print 'You must specify the output file name.'
	quit()

# Collect some data from the user.
print 'What is a short description of this data?'
dataDesc = sys.stdin.readline().strip()

print 'Which scopes would you like to collect data from?'
for i in range(len(hostList)):
	print 'Scope %d: %s' % (i, hostList[i])
print 'You can specify any sort of range, i.e. 1-2 or 2,3'

scopes = doReceiveRangeFromUser(range(len(hostList)))

scopes = map(lambda i: hostList[i], scopes)

print 'Which channels would you like to collect from?'
print 'You can enter a range. i.e. 1-4'
print 'This list of channels will be collected from each scope.'

channels = doReceiveRangeFromUser(range(1,5))

# Begin the actual collection of the data
print 'Collecting data from scope... this will take a moment'
print 'Data collection typically takes a minute per channel.'

outputData = []
for s in scopes:
	for i in channels:
		dataSet = doDownloadData(i, s)
		print 'Recieved data set for channel ' + str(i) + ' (sample row):' + json.dumps(dataSet[0])
		outputData.append(dataSet)

finalOutput = []

offset = 2e-3

for l in range(len(outputData[0])):
	listOfData = []
	listOfData.append(str(float(str(outputData[0][l][0])))) 
	for c in range(len(outputData)):
		listOfData.append(str(float(str(outputData[c][l][1]))))
	finalOutput.append(listOfData)

out = open(sys.argv[1] + ".dat", 'w')
descOut = open(sys.argv[1] + ".desc", 'w')
descOut.write("Capture of data from scopes:\n" + json.dumps(scopes) + " Collecting data from channels:\n" + json.dumps(channels))
descOut.write("Text: " + dataDesc + "\n")

for l in finalOutput:
	out.write(' '.join(l) + '\n')

out.close()
