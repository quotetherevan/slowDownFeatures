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
outerPerimRE = re.compile( r";\souter\sperimeter" )

sampleString = "; none"
slowDownForSmallLoops = 1
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
	slowedSpeed = sys.argv[2]
	lengthThreshold = int(sys.argv[3])
else:
	print("usage: smallLoops.py filename slowedSpeed loopThreshold")
	sys.exit()
if slowDownForSmallLoops == 1:
	for i, line in enumerate(fr):
		sampleString = line
		linecount = linecount + 1
		commentMatch = commentCharRE.match( sampleString )
		if commentMatch:
			featureMatch = outerPerimRE.match( sampleString )
			if featureMatch:
				outerLoopBegin.append(linecount+1)
				currentFeature = "outer perimeter"
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
					print ("Line: " + str(linecount) + ": " + sampleString )
					if xMatch:
						xStr = str(xMatch.group())
						xDec = float(xStr[1:(len(xStr))])
						lineX = xDec
						if xDec == currentX :
							changeX = 0
						else:
							changeX = currentX - lineX
							#print( "Current X: " + str( currentX ) )
							#print( "New	  X: " + str( xDec ) )
							#print( "Change  X: " + str( changeX ) )
					if yMatch:
						yStr = str(yMatch.group())
						yDec = float(yStr[1:(len(yStr))])
						lineY = yDec
						if yDec == currentY :
							changeY = 0
						else:
							changeY = currentY - lineY
							#print( "Current Y: " + str( currentY ) )
							#print( "New	  Y: " + str( yDec ) )
							#print( "Change  Y: " + str( changeY ) )
					if zMatch:
						zStr = str(zMatch.group())
						zStr = zStr[1:(len(zStr))]
						zDec = float(zStr)
						#print( "ZPos: " +"Z"+zStr )
						lineZ = zDec
						if zDec == currentZ :
							changeZ = 0
						else:
							changeZ = currentZ - lineZ
							#print( "New ZPos: " +"Z"+zStr )
					if eMatch:
						eStr = str(eMatch.group())
						eStr = eStr[1:(len(eStr))]
						eDec = float(eStr)
						#print( "EPos: " +"E"+eStr )
						lineE = eDec
						if currentFeature == "outer perimeter":
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
										#print ("line: " + str(linecount) + "loopDist: " + str(loopDist))
					#any non comment lines without an E value
					else: 
						if loopDist > 0:
							#if non-commented line is featured inside the body of an "outer perimeter"
							if currentFeature == "outer perimeter":
								#log the current line as the last line of the loop
								outerLoopEnd.append(linecount-1)
								#log the current loop length
								outerLoopLength.append(loopDist)
								#reset loop length
								loopDist = 0
								#reset current feature
								currentFeature = "na"
					if fMatch:
						fStr = str(fMatch.group())
						fStr = fStr[1:(len(fStr))]
						fDec = float(fStr)
						#print( "FPos: " +"F"+fStr )
						lineF = fDec
						if fDec == currentF :
							changeF = 0
						else:
							changeF = currentF - lineF
							#print( "New FPos: " +"F"+fStr )
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
if slowDownForSmallLoops == 1:
	loopCount = 0.0
	#slowdown for small loops
	for i, line in enumerate(fr):
		#print( str(i))
		temp = []
		if int(loopCount) < len(outerLoopBegin) and i >= outerLoopBegin[int(loopCount)] and i <= outerLoopEnd[int(loopCount)]:
			#print(str(outerLoopLength[int(loopCount)]) + " loopCount: " + str(loopCount))
			if outerLoopLength[int(loopCount)] <= lengthThreshold:
				gMatch = gRE.match( line )
				xMatch = xRE.search( line )
				yMatch = yRE.search( line )
				zMatch = zRE.search( line )
				eMatch = eRE.search( line )
				fMatch = fRE.search( line )
				if gMatch:
					if "G1" in gMatch.group() and eMatch and float(eMatch.group()[1:len(eMatch.group())]) > 0:
						#print("line " + str(i) + ": " + line)
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
								print("Altering speed")
								temp.append("\n")
								newline = " ".join(temp)
								print("Newline: " + newline)
								fw.write(newline)			
							else:
								print("Original Speed ("+ str(fMatch.group()) + ") <= slowedSpeed (" + slowedSpeed + ")") 
								temp.append(fMatch.group())
								temp.append("\n")
								newline = " ".join(temp)
								fw.write(newline)
						else:
							temp.append("\n")
							newline = " ".join(temp)
							fw.write(newline)
					else:
						#print("line " + str(i+1) + "is not the start of a new loop")
						newline = line
						fw.write(newline)
				else:
					#print("line " + str(i+1) + "is not the start of a new loop")
					newline = line
					fw.write(newline)
			else:
				#print("line " + str(i+1) + "is not the start of a new loop")
				newline = line
				fw.write(newline)
			if i >= outerLoopEnd[int(loopCount)]:
				loopCount += 1
		else:
			#print("line " + str(i+1) + "is not the start of a new loop")
			newline = line
			fw.write(newline)
			
fr.close()
fw.close()