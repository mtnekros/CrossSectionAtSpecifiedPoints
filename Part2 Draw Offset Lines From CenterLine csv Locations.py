""" Name: Draw Offset Lines From CenterLine
Description: Creates a polyline shapefile with perpendicular offsets from a centre line
at chainage or locations read from a csv file """

import arcpy
import math

# function to read locations or chainage from the csv file created in part1
def GetLocationFromFile(csv_file):
    locations = []
    with open(csv_file,'r') as in_file:
        in_file.readline()
        for line in in_file:
            locations.append(float(line))
    return sorted(locations)

# function to return bearing angle between two points
def AngleBetween(p1,p2):
    return math.degrees( math.atan2( p1.X-p2.X,p1.Y-p2.Y ) )

# function to return distance between two points
def DistanceBetween(p1,p2):
    return math.sqrt( ( p1.X-p2.X )**2 + ( p1.Y-p2.Y )**2 )

def GetLine(midPoint,angle,length):
    leftGeom = midPoint.pointFromAngleAndDistance( angle,length )
    rightGeom = midPoint.pointFromAngleAndDistance( angle-180,length )

    left = arcpy.Point( leftGeom.centroid.X,leftGeom.centroid.Y )
    right = arcpy.Point( rightGeom.centroid.X,rightGeom.centroid.Y )

    return arcpy.Polyline( arcpy.Array( [left,right] ) )

# main function to call for drawing perpendicular lines
def DrawPerpLinesToShapeFile(centerLine_fc, outPath, outLayerName, csv_file, perpLineLength):
    locations = GetLocationFromFile(csv_file)
    arcpy.env.overwriteOutput = True

    # making feature layers out of the addresses shapefile
    arcpy.MakeFeatureLayer_management(centerLine_fc,'centreLine_layer')

    # making new feature class for saving perpendiculars lines
    spatialRef = arcpy.Describe(centerLine_fc).SpatialReference
    arcpy.CreateFeatureclass_management(outPath, outLayerName, geometry_type='Polyline', spatial_reference=spatialRef)
    # adding fields
    arcpy.AddField_management(outPath+'\\'+outLayerName, field_name='Location', field_type='DOUBLE')
    arcpy.AddMessage('New Shapefile Created')

    # insertcursor for adding row
    perpLineCursor = arcpy.da.InsertCursor(outPath+'\\'+outLayerName,['Location','Shape@'])

    with arcpy.da.SearchCursor('centreLine_layer',['Shape@']) as centerLineCursor:
        for row in centerLineCursor: # looping the records (usually only 1 polyline in centerline)
            for part in row[0]: # looping through the line in the polyline, row[0] (usually only 1 line in centerline)
                iLocation = 0 # to keep track of lines to be added at location from csv
                checkLocation = 0.0 # to make sure right angle is used
                print len(part)
                for i in range(len(part)-1): # part is a line which acts a list of points in that line
                    p1 = part[i]
                    p2 = part[i+1]
                    segmentAngle = AngleBetween(p1,p2)
                    segmentLength = DistanceBetween(p1,p2)

                    print 'Angle', segmentAngle, 'Length of segment', segmentLength

                    checkLocation += segmentLength # incrementing checklocation

                    while checkLocation > locations[iLocation]:
                        point = row[0].positionAlongLine(locations[iLocation]) # row[0] is polyline
                        perpLineCursor.insertRow( ( locations[iLocation],GetLine(point,segmentAngle-90,perpLineLength) ) )
                        print 'Row#', iLocation, 'is added to the shapeFile at location', locations[iLocation], '\n'
                        arcpy.AddMessage('Row #{} is added to the perpLine shapeFile for  location {}m\n'.format(iLocation,locations[iLocation]))

                        iLocation+=1
                        arcpy.AddMessage(str(iLocation)+ ' ' + str(len(locations)) + '\n')
                        if iLocation >= len(locations):
                            return


    del perpLineCursor

# Main execution starts here
line_fc = arcpy.GetParameterAsText(0)
outPath = arcpy.GetParameterAsText(1)
layerName = arcpy.GetParameterAsText(2)
csv_file = arcpy.GetParameterAsText(3)
perpLineLength = float(arcpy.GetParameterAsText(4))
# executing the drawperpline method
DrawPerpLinesToShapeFile(line_fc, outPath, layerName, csv_file,perpLineLength)
arcpy.AddMessage('Perpendicular Lines Shape File has been created!\n')
