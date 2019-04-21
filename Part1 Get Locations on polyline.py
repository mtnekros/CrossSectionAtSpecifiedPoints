""" Name: Get Locations on polyline
Description: Measures the distance of points along a polyline and saves it to csv
"""

import arcpy

# defining path to line and point shapefile
line_fc = arcpy.GetParameterAsText(0)
pts_fc = arcpy.GetParameterAsText(1)
outPath = arcpy.GetParameterAsText(2)

# getting layers out of path
arcpy.MakeFeatureLayer_management(line_fc, 'line_layer')
arcpy.MakeFeatureLayer_management(pts_fc, 'pts_layer')

# getting the first line in line layer
line_cursor = arcpy.da.SearchCursor('line_layer',['Shape@']) #shape@ return arcpy.Geometry which in this case is a point
line = line_cursor.next()[0]  # getting the first arcpy.Geometry line in line layer

# creating an output file ot save the locations or chainages  and writing the headings
output_file = open('{}\locations.csv'.format(outPath),'w')
output_file.write('Locations\n')
arcpy.AddMessage('CSV file created')

# getting the cursor for pts_layer(returns iterator) and looping through the rows of specified fields
with arcpy.da.SearchCursor('pts_layer',['Shape@']) as cursor:
    for i,row in enumerate(cursor):
        location = line.measureOnLine(row[0]) # row[0] holds the point shape
        output_file.write(str(location)+'\n')
        print i, location
        arcpy.AddMessage('{} done, location {} added'.format(i, location) )

output_file.close()
del line_cursor

