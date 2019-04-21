"""
Name: Draw And Save Graph
Description: Takes DEM, x-section lines shapefile and draws cross-section on every line
and saves the graph as csv and also saves the image
"""

import arcpy

arcpy.env.overwriteOutput = True

# defining variables
xSectionLines = arcpy.GetParameterAsText(0)
DEM = arcpy.GetParameterAsText(1)
outpath = arcpy.GetParameterAsText(2)
graphName = "X_section"

# reading the locations/chainage from x-section shape file into a list
locations = []
with arcpy.da.SearchCursor(xSectionLines,['Location']) as cursor:
    for row in cursor:
        locations.append(row[0])
print 'Successfully loaded the locations!'
arcpy.AddMessage('Successfully loaded the locations!')

# looping through each line in profile lines layer
for i in range(len(locations)):
    # Making temporary layer containing the ith line in the x-section lines shapefile
    arcpy.MakeFeatureLayer_management(xSectionLines,'xSectionLayer',"""OBJECTID = {}""".format(i+1))

    # Execute stackprofile and save the csv file
    arcpy.ddd.StackProfile('xSectionLayer',DEM,r'{0}\xSection_{1}.csv'.format(outpath,locations[i]),graphName)

    # Save the graph image
    arcpy.management.SaveGraph(graphName,r'{0}\xSectionImg_{1}.jpeg'.format(outpath,locations[i]))

    print i, 'Done'
    arcpy.AddMessage('{}th  cross-section saved'.format(i+1))

print 'Successfully completed'
arcpy.AddMessage('Successfully completed\nCheck the output folder for graphs and csv.\n')



