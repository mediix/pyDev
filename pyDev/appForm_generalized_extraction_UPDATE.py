# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 14:36:52 2015

@author: cdrayton
"""
import os
import re
import sys
import gensim
import pprint
import MySQLdb
import pandas as pd


def tabelParse(colKeys, firstRowName, Text):
    TableText = re.split(r'\n(?=%s\b)'%firstRowName,Text)[1]
    TableText = TableText.replace("N/A","0")
    TableText = TableText.replace("(other than A2)","(other than A two)")
    useClassRe = re.compile(r'\n?[A-Z].?\D+(?=\d+\b)')

    yKeys = [i.replace('\n','').replace('\t',' ')  for i in re.findall(useClassRe,TableText)]
    # for i in yKeys:
    #     print i
    Values = re.split(useClassRe,TableText)

    values = [re.findall(r"(-*\d+\.*\d*)",Q)[:4]for Q in Values[:len(yKeys)+1] ]
    floorSpace_D = {k:(v if len(v) == len(colKeys) else ['0']*(len(colKeys)-len(v))+v) for k,v in zip(yKeys,values[1:len(yKeys)+1]) }
    #	for k,v in sorted(floorSpace_D.items()):
    #	     print k
    #	     print "\t",v
    df = pd.DataFrame(floorSpace_D, index=colKeys)
    print colKeys
    print df.shape
    return df

def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

#path ="2014_1495_PCamden.txt"
#path = "PP_15_04649Royal Borough of Kensington and Chelsea.txt"
path = '2014_2664_PCamden.txt'
path = "PP_15_00516Royal Borough of Kensington and Chelsea_application_form.txt"
# pathList = [p for p in os.listdir(os.getcwd()) if p.split('.')[-1] == 'txt']
pathList = ["/Users/medinazari/Downloads/Kensington_txt/ARB_14_00008Royal Borough of Kensington and Chelsea_1.txt"]
for path in pathList:
    exceptionCount = 0
    exceptionlist = []
    extractedcount = 0
    extractedlist = []
    s = ''
    with open(path, 'r') as myfile:
    	s = myfile.read()

    case_ref_borough = path.split('.')[0]
    index_application_form = case_ref_borough.index('_application_form')
    case_ref_borough = case_ref_borough[:index_application_form]
    case_ref_borough = case_ref_borough.replace('_','/')

    s = s.replace('\r\n', '\n')
    k = re.findall(r"\n\d+\.\D((?!.*continued).*)", s)
    v = re.split(r"\n\d+\.\D((?!.*continued).*)", s)

    """
    Creates a list using re.split on the numbered headings each section.
    And the list comprehension below creates a dictionary keyed by the headings with values of the contents.
    """
    # field_D = {k:[i for i in v.split('\n') if 'continued)'not in i if 'Planning Portal Reference:' not in i] for k,v in zip(v[1::2],v[2::2]) }

    # continued = [x for x in v.split('\n') if ['continued)', 'Planning Portal Reference'] not in x]

    check = lambda x: x if ['continued)', 'Planning Portal Reference'] not in v.split('\n')

    # Field-content dictionary
    field_D = dict((key, check(value)) for key, value in zip(v[1::2], v[2::2]))

#     extract_fields_L = ['Vehicle Parking',
#     					'Existing Use',
#     					'Residential Units',
#     					'All Types of Development: Non-residential Floorspace',
#     					'Employment',
#     					'Site Area']

#     """ Dictionary designed to check if 'm' or 'h' is in the unit field
#     	which should corispond to square meters or hectars respectivly
#     	could use same to convert to length if squRooted
#     """
#     convert_D = {'m': 10.7639,
#     			 'h':107639,
#     			 'f':1}

#     DB_field_D = {}
#     """ the Site Area columns for the database are a list
#     	having
#     	0 orginal value as a float
#     	1 line after that as which is hopefully the unit of area
#     	2 the area converted to square feet
#     	3 the string 'sq.feet'
#     """

#     if 'Site Area' in field_D:
#     	area = [i for i in field_D['Site Area'] if is_number(i)]
#     	if len(area) == 1:
#     		unit_s = [i for i in field_D['Site Area'][field_D['Site Area'].index(area[0])+1:] if re.match(r"[a-zA-Z.]+",i)]
#     		if len(unit_s) == 1:
#     			for k in convert_D:
#     				if k in unit_s[0]:
#     					DB_field_D['Site Area'] = [float(area[0]),unit_s[0],float(area[0])*convert_D[k], "sq.feet"]

#     		else:
#                  exceptionCount += 1
#                  exceptionlist.append("Floorspace, IndexError")
# #                print unit_s,"are the possiblities for units\!!!!!!!!!!!!!!!"
#     	else:
#          exceptionCount += 1
#          exceptionlist.append("Floorspace, IndexError")
# #         print len(area),"values for area\n!!!!!!!!!!!!"

# #    print pd.DataFrame(DB_field_D)


#     #floorText =field_D['All Types of Development: Non-residential Floorspace']
#     if 'All Types of Development: Non-residential Floorspace' in field_D:
#         try:
#             floorText = reduce(lambda a,b: a+'\n'+b,field_D['All Types of Development: Non-residential Floorspace'])
#             xKeys = ["Existing Non Res. Floorspace (sq.m)",
#                      "Lost Non Res. floorspace (sq.m)",
#                      "New Non Res. floorspace proposed (sq.m)",
#                      "Net Non Res. floorspace After (sq.m)"]

#             floor_DF = tabelParse(xKeys, 'A1', floorText)
#             extractedcount += 1
#             extractedlist.append('Floorspace')
#         except IndexError:
#             exceptionCount += 1
#             exceptionlist.append("Floorspace, IndexError")
#     else:
#         exceptionCount += 1
#         exceptionlist.append("Floorspace, IndexError")

# #    print pd.DataFrame(DB_field_D)


#     if 'Employment' in field_D:
#         try:
#             employmentText = reduce(lambda a,b: a+'\n'+b,field_D['Employment'])
#             employIndex = ['Full-time','Part-time','Equivalent number of full-time']
#             employSplit= re.split('(Existing employees|Proposed employees)',employmentText)

#             employ_D = {}
#             for i in ['Existing employees','Proposed employees']:
#                 employ_D[i] = ''
#                 try:
#                     employ_D[i] = re.findall(r'\b(\d+)\b',employSplit[employSplit.index(i)+1])
#                 except:
#                     pass

#         #    print pd.DataFrame(employ_D,index = employIndex)
#         except IndexError:
#             exceptionCount += 1
#             exceptionlist.append('Employment, IndexError')
#     else:
#         exceptionCount += 1
#         exceptionlist.append('Employment,KeyError')

#     #print field_D['Existing Use'][field_D['Existing Use'].index('Please describe the current use of the site:')+1]
#     useKey_D= {
#         'Last Use':'If Yes, please describe the last use of the site:',
#         "Current Use":"Please describe the current use of the site:",
#         "Date use ended":"When did this use end (if known) (DD/MM/YYYY)?"
#     }
#     """ ####################
#         Below is Use data
#         ####################"""

#     if 'Existing Use' in field_D:
#         useText = reduce(lambda a,b: a+'\n'+b,field_D['Existing Use'])
# #        print "\n"
#         #print useText

#         for k, v in useKey_D.items():
#         	found = False
#         	n = 1
#         	while found == False:
#         		try:
#         			useLine = field_D['Existing Use'][field_D['Existing Use'].index(v)+n]
#         			if "Yes" in useLine or "No" in useLine or not re.match(r'\b',useLine):
#         				n+=1
#         			elif v == "When did this use end (if known) (DD/MM/YYYY)?":
#         				if re.match(r'\d+/\d+/\d+',useLine):
#         					useKey_D[k]=useLine
#         					found = True
#         				else:
#         					useKey_D[k]=None
#         					found = True
#         			else:
#         				useKey_D[k]=useLine
#         				found = True
#         		except ValueError as e:
#         			found = True
#         			useKey_D[k]=None
#         			continue

# #        for k,v in useKey_D.items():
# #        	print k
# #        	print "\t",v
#         extractedlist.append('Use')
#         extractedcount += 1
#     else:
#         exceptionCount += 1
#         exceptionlist.append("Use, KeyError")

#     """ ##########################################################
#         Below is data on the Number of Parking Spots added or lost
#        ###########################################################"""
#     if 'Vehicle Parking' in field_D:
#         parkingText = reduce(lambda a,b: a+'\n'+b,field_D['Vehicle Parking'])

#         parkingCols = ["Existing spaces",
#         		"New spaces",
#         		"Differnece in spaces"]
#         try:
#             parkingData = tabelParse(parkingCols, 'Cars',parkingText)
#             extractedcount += 1
#             extractedlist.append("Parking")
#         except IndexError as e:
#             exceptionCount += 1
#             exceptionlist.append("Parking,IndexError, %s"%e)
#         except:
#             pass
#     else:
#         exceptionCount += 1
#         exceptionlist.append("Parking,KeyError")


#     conn = MySQLdb.connect(user='colin',
#                           passwd='fQ58g#t]:K*_q6S/',
#                           db='research_uk',
#                           host='granweb01',
#                           charset="utf8",
#                           use_unicode=True)
#     cursor = conn.cursor()

#     try:
#         cursor.execute('''UPDATE boroughs b
#         	SET b.total_existing_non_res_floorspace_sqm = "%s",
#         		b.total_lost_non_res_floorspace_sqm = "%s",
#         		b.`total_new_non_res_floorspace proposed_sqm` = "%s",
#         		b.total_net_non_res_floorspace_after_sqm = "%s"
#         	WHERE b.case_reference_borough = "%s";'''%(floor_DF['Total']["Existing Non Res. Floorspace (sq.m)"], floor_DF['Total']["Lost Non Res. floorspace (sq.m)"], floor_DF['Total']["New Non Res. floorspace proposed (sq.m)"], floor_DF['Total']["Net Non Res. floorspace After (sq.m)"],case_ref_borough)
#              )
#         conn.commit()
#     except Exception  as e:
#         print "ERROR",path.split('.')[0].split('/')[0],e
#     try:
#         cursor.execute('''UPDATE boroughs b
#         	SET b.site_area_in_sq_ft = "%s"
#         	WHERE b.case_reference_borough = "%s";'''%(DB_field_D['Site Area'][2],case_ref_borough)
#              )
#         conn.commit()
#     except Exception  as e:
#         print "\tERROR",path.split('.')[0].split('/')[0],e

#     finally:
#         print exceptionCount + extractedcount, path.split('.')[0].split('/')[0]
#         conn.close()
#     conn = MySQLdb.connect(user='colin',
#                           passwd='fQ58g#t]:K*_q6S/',
#                           db='research_uk',
#                           host='granweb01',
#                           charset="utf8",
#                           use_unicode=True)
#     cursor = conn.cursor()
#     for col,key in zip(['existing_use_last_use','existing_use_current_state','existing_use_last_use_end_date'] ,['Last Use',"Current Use","Date use ended"]):
#         col_key_value = useKey_D[key]
#         if col_key_value:
#             if col == 'existing_use_last_use_end_date' \
#                 and len(col_key_value) > 16:
#                 col_key_value = col_key_value[:16]
#             if col == 'existing_use_current_state' \
#                 and len(col_key_value) > 32:
#                 col_key_value = col_key_value[:32]
#                 print len(col_key_value)

#             col_key_value = col_key_value.replace('\'', '\'\'')

#             try:
#                 cursor.execute( '''UPDATE boroughs b
#                                     SET b.%s = '%s'
#                                     WHERE b.case_reference_borough = '%s';''' % (col, col_key_value, case_ref_borough)
#                             )
#                 conn.commit()
#             except:
#                 pass
#     conn.close()
#d = {'one' : [1., 2., 3., 4.],'two' : [4., 3., 2., 1.]}
#print pd.DataFrame(d, index=['a', 'b', 'c', 'd'])


