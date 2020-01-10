import re
import sys
import math

commentCharRE = re.compile( r"\S*;" )
gRE = re.compile( r"G\S*" )
xRE = re.compile( r"X\S*" )
yRE = re.compile( r"Y\S*" )
zRE = re.compile( r"Z\S*" )
eRE = re.compile( r"E\S*" )
fRE = re.compile( r"F\S*" )
outerPerimRE = re.compile( r";\sfeature\souter\sperimeter" )
denseSupportRE = re.compile( r";\sfeature\sdense\ssupport" )
layerComRE = re.compile( r";\s*layer" )

sampleString = "; none"
slowDownFeatures = 1
denseSupportToggle = 0
outerPerimeterToggle = 1
slowedSpeed = "F360"
lengthThreshold = 30
relativeE = 0

currentX = 0
currentY = 0
currentZ = 0
currentE = 0
currentF = 0
currentFeature = "na"
outerLoopBegin = []
outerLoopEnd = []
outerLoopLength = []
denseSupportBegin = []
denseSupportEnd = []
lineX = 0
lineY = 0
lineZ = 0
lineE = 0
lineF = 0
changeX = 0
changeY = 0
changeZ = 0
changeE = 0
changeF = 0
loopDist = 0

num_lines = 0
linecount = 0

if len(sys.argv) == 4:
	readfile = sys.argv[1]
	if ".gcode" in sys.argv[1]:
		cutLocation = readfile.find(".gcode")
		writefile = readfile[:cutLocation] + "_processed.gcode"
	else:
		print("Please enter a *.gcode file as the first argument")
		sys.exit()
	fr = open(readfile, 'r')
	num_lines = fr.read().count('\n')
	fr.close()
	fr = open(readfile, 'r')
	slowedSpeed = "F" + sys.argv[2]
	lengthThreshold = int(sys.argv[3])
else:
	print("usage: smallLoops.py filename slowedSpeed loopThreshold")
	sys.exit()
if slowDownFeatures == 1:
	for i, line in enumerate(fr):
		sampleString = line
		linecount = linecount + 1
		commentMatch = commentCharRE.match( sampleString )
		if commentMatch:
			outerPerimeterMatch = outerPerimRE.match( sampleString )
			denseSupportMatch = denseSupportRE.match( sampleString )
			layerComMatch = layerComRE.match( sampleString )
			if outerPerimeterToggle == 1 and outerPerimeterMatch:
				outerLoopBegin.append(linecount+1)
				currentFeature = "outer perimeter"
			elif denseSupportToggle == 1 and denseSupportMatch:
				denseSupportBegin.append(linecount+1)
				currentFeature = "dense support"
			elif outerPerimeterToggle == 1 and currentFeature == "outer perimeter" and loopDist > 0:
				outerLoopEnd.append(linecount-1)
				outerLoopLength.append(loopDist)
				loopDist = 0
				currentFeature = "na"
			elif denseSupportToggle == 1 and currentFeature == "dense support":	
					if layerComMatch:
						print("Dense support spanning 2 layers - skipping layer comment")
					else:
						print("ending dense support detection at layer" + str(linecount-1))
						denseSupportEnd.append(linecount-1)
						loopDist = 0
						currentFeature = "na"
		else:
			gMatch = gRE.match( sampleString )
			xMatch = xRE.search( sampleString )
			yMatch = yRE.search( sampleString )
			zMatch = zRE.search( sampleString )
			eMatch = eRE.search( sampleString )
			fMatch = fRE.search( sampleString )
			if gMatch:
				gStr = str(gMatch.group())
				gStr = gStr[1:(len(gStr))]
				gDec = float(gStr)
				if gDec == 1 :
					if xMatch:
						xStr = str(xMatch.group())
						xDec = float(xStr[1:(len(xStr))])
						lineX = xDec
						if xDec == currentX :
							changeX = 0
						else:
							changeX = currentX - lineX
					if yMatch:
						yStr = str(yMatch.group())
						yDec = float(yStr[1:(len(yStr))])
						lineY = yDec
						if yDec == currentY :
							changeY = 0
						else:
							changeY = currentY - lineY
					if zMatch:
						zStr = str(zMatch.group())
						zStr = zStr[1:(len(zStr))]
						zDec = float(zStr)
						lineZ = zDec
						if zDec == currentZ :
							changeZ = 0
						else:
							changeZ = currentZ - lineZ
					if eMatch:
						eStr = str(eMatch.group())
						eStr = eStr[1:(len(eStr))]
						eDec = float(eStr)
						lineE = eDec
						if outerPerimeterToggle == 1 and currentFeature == "outer perimeter":
							if eDec == currentE :
								changeE = 0
							else:
								if relativeE == 0:
									changeE = lineE - currentE 
								else:
									changeE = lineE
								if changeE > 0:
									if changeX > 0 or changeX < 0 or changeY > 0 or changeY < 0:
										dist = math.hypot(changeX, changeY)
										loopDist = loopDist + dist
						elif denseSupportToggle == 1 and currentFeature == "dense support":
							if eDec == currentE :
								changeE = 0
							else:
								if relativeE == 0:
									changeE = lineE - currentE 
								else:
									changeE = lineE
								if changeE > 0:
									if changeX > 0 or changeX < 0 or changeY > 0 or changeY < 0:
										dist = math.hypot(changeX, changeY)
										loopDist = loopDist + dist
					if fMatch:
						fStr = str(fMatch.group())
						fStr = fStr[1:(len(fStr))]
						fDec = float(fStr)
						lineF = fDec
						if fDec == currentF :
							changeF = 0
						else:
							changeF = currentF - lineF
					currentX = lineX
					currentY = lineY
					changeX = 0
					changeY = 0
					changeZ = 0
					changeE = 0
					if relativeE == 1:
						currentE = 0
					changeF = 0
readfile = sys.argv[1]
fr = open(readfile, 'r')
fw = open(writefile, 'w')
if slowDownFeatures == 1:
	outerLoopCount = 0.0
	denseSupportCount = 0.0
	#slowdown features
	for i, line in enumerate(fr):
		temp = []
		if outerPerimeterToggle == 1 and int(outerLoopCount) < len(outerLoopBegin) and i >= outerLoopBegin[int(outerLoopCount)] and i <= outerLoopEnd[int(outerLoopCount)]:
			if outerLoopLength[int(outerLoopCount)] <= lengthThreshold:
				gMatch = gRE.match( line )
				xMatch = xRE.search( line )
				yMatch = yRE.search( line )
				zMatch = zRE.search( line )
				eMatch = eRE.search( line )
				fMatch = fRE.search( line )
				if gMatch:
					if "G1" in gMatch.group() and eMatch and float(eMatch.group()[1:len(eMatch.group())]) > 0:
						temp.append(gMatch.group())
						if xMatch:
							temp.append(xMatch.group())
						if yMatch:
							temp.append(yMatch.group())
						if zMatch:
							temp.append(zMatch.group())
						if eMatch:
							temp.append(eMatch.group())
						if fMatch:
							fStr = str(fMatch.group())
							fStr = fStr[1:(len(fStr))]
							fDec = float(fStr)
							slowedFStr = slowedSpeed[1:len(slowedSpeed)]
							slowedDec = float(slowedFStr)
							if fDec > slowedDec:
								temp.append(slowedSpeed)
								temp.append("\n")
								newline = " ".join(temp)
								print(str(i)+"  Adjusted OuterPerimeter Speed: " + newline)
								fw.write(newline)			
							else:
								temp.append(fMatch.group())
								temp.append("\n")
								newline = " ".join(temp)
								fw.write(newline)
						else:
							temp.append("\n")
							newline = " ".join(temp)
							fw.write(newline)
					else:
						newline = line
						fw.write(newline)
				else:
					newline = line
					fw.write(newline)
			else:
				newline = line
				fw.write(newline)
			if i >= outerLoopEnd[int(outerLoopCount)]:
				outerLoopCount += 1
		elif int(denseSupportCount) < len(denseSupportBegin) and i >= denseSupportBegin[int(denseSupportCount)] and i <= denseSupportEnd[int(denseSupportCount)]:
			gMatch = gRE.match( line )
			xMatch = xRE.search( line )
			yMatch = yRE.search( line )
			zMatch = zRE.search( line )
			eMatch = eRE.search( line )
			fMatch = fRE.search( line )
			if gMatch:
				if "G1" in gMatch.group() and eMatch and float(eMatch.group()[1:len(eMatch.group())]) > 0:
					temp.append(gMatch.group())
					if xMatch:
						temp.append(xMatch.group())
					if yMatch:
						temp.append(yMatch.group())
					if zMatch:
						temp.append(zMatch.group())
					if eMatch:
						temp.append(eMatch.group())
					if fMatch:
						fStr = str(fMatch.group())
						fStr = fStr[1:(len(fStr))]
						fDec = float(fStr)
						slowedFStr = slowedSpeed[1:len(slowedSpeed)]
						slowedDec = float(slowedFStr)
						if fDec > slowedDec:
							temp.append(slowedSpeed)
							temp.append("\n")
							newline = " ".join(temp)
							print(str(i)+"  Adjusted DenseSupport Speed: " + newline)
							fw.write(newline)			
						else:
							temp.append(fMatch.group())
							temp.append("\n")
							newline = " ".join(temp)
							fw.write(newline)
					else:
						temp.append("\n")
						newline = " ".join(temp)
						fw.write(newline)
				else:
					newline = line
					fw.write(newline)

			else:
				newline = line
				fw.write(newline)
			if i >= denseSupportEnd[int(denseSupportCount)]:
				denseSupportCount += 1
		else:
			newline = line
			fw.write(newline)
			
fr.close()
fw.close()
