#open the file x
#read one JSON object from the file
#close the file x
#load JSON array from file y
#add new object to array according to web site graph directive view requirements
#close the file
import json
import os.path
import statistics

inputFile = '/home/pi/code/data/weather.json'
graphDataFile = '/home/pi/code/data/barometerGraphData.json'
graphViewModelFile = '/home/pi/code/data/barometerGraphViewModel.json'
graphDataMaxRecords = 720 # data collected every 2 minutes 24x7. 720 records per day
viewModelSegmentCount = 20
presssureKey = 'PressureMb'


if not os.path.isfile(inputFile):
    exit #no work to do

with open(inputFile, encoding='utf-8') as inputData:
    inputModel = json.loads(inputData.read())

# load graph model from the graph model file. Check the length of the model
# and if it is at the max length, remove the oldest record. Then append the
# newest record
graphModel = []
if os.path.exists(graphDataFile) == True and os.path.getsize(graphDataFile) > 0:
    with open(graphDataFile, 'r', encoding='utf-8') as graphData:
        graphModel = json.load(graphData)

if len(graphModel) == graphDataMaxRecords :
    graphModel.pop(0)
graphModel.append(inputModel)

with open(graphDataFile, 'w', encoding='utf-8') as graphDataOutput:
    json.dump(graphModel, graphDataOutput)

# the view is a bar graph with viewModelSegmentCount segments so the graphModel
# needs to be separated into viewModelSegmentCount segments
viewModelSegments = [] #this will be a list of the floating point numbers that is the mean of each segment in the data set
viewModelSegment = [] #this will be a list of floating point nums in each segment
for dataRecord in graphModel:
    viewModelSegment.append(dataRecord[presssureKey])
    if len(viewModelSegment)==viewModelSegmentCount:
        viewModelSegments.append(statistics.mean(viewModelSegment))
        viewModelSegment.clear()
if len(viewModelSegment) > 0: # have to print the last segment
    viewModelSegments.append(statistics.mean(viewModelSegment))

maxMeasurement = max(viewModelSegments)
minMeasurement = min(viewModelSegments)
median = statistics.median(viewModelSegments)
outObj = {}
outObj["segments"]=viewModelSegments
outObj["max"]=maxMeasurement
outObj["min"]=minMeasurement
outObj["median"]=median

    
with open(graphViewModelFile, 'w', encoding='utf-8') as viewModelFile:
    json.dump(outObj, viewModelFile)
    
                                 

    


