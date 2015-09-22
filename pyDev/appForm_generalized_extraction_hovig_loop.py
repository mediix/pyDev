# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 14:36:52 2015

@author: cdrayton
"""
"""if else statment fixes missing values is this the best way?"""
import re
import difflib
import pandas as pd
import MySQLdb, sys, gensim, pprint,os
def tabelParse(colKeys, firstRowName, Text):
	TableText = re.split(r'\n(?=%s\b)'%firstRowName,Text)[1]
	TableText = TableText.replace("(other than A2)","(other than A two)").replace('B8\nS','B8\tS')
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
	return pd.DataFrame(floorSpace_D, index=colKeys)

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
pathList = [p for p in os.listdir(os.getcwd()) if p.split('.')[-1] == 'txt'][::-1]
for path in pathList:
    exceptionCount = 0
    exceptionlist = []
    extractedcount = 0
    extractedlist = []
    s = ''
    with open(path,'r') as myfile:
    	s = myfile.read()
     
     
    case_ref_borough = path.split('.')[0]
    #if '_application_form' not in case_ref_borough:
    #    continue
    
    index_application_form = case_ref_borough.index('_application_form')
    case_ref_borough = case_ref_borough[:index_application_form]
    case_ref_borough = case_ref_borough.replace('_','/')
    
    s = s.replace('\r\n', '\n')
    k =  re.findall(r"\n\d+\.\D((?!.*continued).*)",s)
    v =  re.split(r"\n\d+\.\D((?!.*continued).*)",s)
    
    field_D = {k:[i for i in v.split('\n') if 'continued)'not in i if 'Planning Portal Reference:' not in i] for k,v in zip(v[1::2],v[2::2]) }
    
    # for it in field_D.items():
    #     print it
    
    
    
    extract_fields_L = ['Vehicle Parking',
    					'Existing Use',
    					'Residential Units',
    					'All Types of Development: Non-residential Floorspace',
    					'Employment',
    					'Site Area']
    					
    """ Dictionary designed to check if 'm' or 'h' is in the unit field
    	which should corispond to square meters or hectars respectivly
    	could use same to convert to length if squRooted"""                     
    convert_D = {
    			'm': 10.7639,
    			'h':107639,
    			'f':1
    			}
    
    DB_field_D = {}
    """ the Site Area columns for the database are a list
    	having 
    	0 orginal value as a float
    	1 line after that as which is hopefully the unit of area
    	2 the area converted to square feet
    	3 the string 'sq.feet' """
    
    if 'Site Area' in field_D:
    	area = [i for i in field_D['Site Area'] if is_number(i)]
    	if len(area) == 1:
    		unit_s = [i for i in field_D['Site Area'][field_D['Site Area'].index(area[0])+1:] if re.match(r"[a-zA-Z.]+",i)]
    		if len(unit_s) == 1:
    			for k in convert_D:
    				if k in unit_s[0]:
    					DB_field_D['Site Area'] = [float(area[0]),unit_s[0],float(area[0])*convert_D[k], "sq.feet"]
    
    		else:
                 exceptionCount += 1
                 exceptionlist.append("Floorspace, IndexError")
#                print unit_s,"are the possiblities for units\!!!!!!!!!!!!!!!"
    	else:
         exceptionCount += 1
         exceptionlist.append("Floorspace, IndexError")
#         print len(area),"values for area\n!!!!!!!!!!!!"
    	 
#    print pd.DataFrame(DB_field_D)
    
    
    #floorText =field_D['All Types of Development: Non-residential Floorspace']
    floor_DF = pd.DataFrame().fillna(0)
    if 'All Types of Development: Non-residential Floorspace' in field_D:
        try:
            floorText = reduce(lambda a,b: a+'\n'+b,field_D['All Types of Development: Non-residential Floorspace'])
            xKeys = ["Existing Non Res. Floorspace (sq.m)",
                     "Lost Non Res. floorspace (sq.m)",
                     "New Non Res. floorspace proposed (sq.m)",
                     "Net Non Res. floorspace After (sq.m)"]
            
            floor_DF = tabelParse(xKeys, 'A1', floorText)
            extractedcount += 1
            extractedlist.append('Floorspace')
        except IndexError:
            exceptionCount += 1
            exceptionlist.append("Floorspace, IndexError")  
    else:
        exceptionCount += 1
        exceptionlist.append("Floorspace, IndexError")  
    	
#    print pd.DataFrame(DB_field_D)
    
    if 'Employment' in field_D:
        employmentText = reduce(lambda a,b: a+'\n'+b,field_D['Employment'])
        employIndex = ['Full-time','Part-time','Equivalent number of full-time']
        employSplit= re.split('(Existing employees|Proposed employees)',employmentText)
        
        employ_D = {}
        for i in ['Existing employees','Proposed employees']:
            employ_D[i] = ''
            try:
                employ_D[i] = re.findall(r'\b(\d+)\b',employSplit[employSplit.index(i)+1])
            except:
                pass

#    print pd.DataFrame(employ_D,index = employIndex)
    
    """ ####################
        Below is Use data
        ####################"""
    if 'Existing Use' in field_D:
        useText = reduce(lambda a,b: a+'\n'+b,field_D['Existing Use'])
#        print "\n"
        #print useText
        
        #print field_D['Existing Use'][field_D['Existing Use'].index('Please describe the current use of the site:')+1]
        useKey_D= {
        'Last Use':'If Yes, please describe the last use of the site:',
        "Current Use":"Please describe the current use of the site:",
        "Date use ended":"When did this use end (if known) (DD/MM/YYYY)?"
         }
        
        for k, v in useKey_D.items():    
        	found = False
        	n = 1
        	while found == False:
        		try:
        			useLine = field_D['Existing Use'][field_D['Existing Use'].index(v)+n]
        			if "Yes" in useLine or "No" in useLine or not re.match(r'\b',useLine):
        				n+=1
        			elif v == "When did this use end (if known) (DD/MM/YYYY)?":
        				if re.match(r'\d+/\d+/\d+',useLine):
        					useKey_D[k]=useLine
        					found = True
        				else:
        					useKey_D[k]=None
        					found = True
        			else: 
        				useKey_D[k]=useLine
        				found = True
        		except ValueError as e:
        			found = True
        			useKey_D[k]=None
        			continue
        
#        for k,v in useKey_D.items():
#        	print k
#        	print "\t",v
        extractedlist.append('Use')
        extractedcount += 1
    else:
        exceptionCount +=1
        exceptionlist.append("Use, KeyError")
        
    """ ##########################################################
        Below is data on the Number of Parking Spots added or lost
       ###########################################################"""
    parkingData = pd.DataFrame()
    if 'Vehicle Parking' in field_D:
        parkingText = reduce(lambda a,b: a+'\n'+b,field_D['Vehicle Parking'])
    			
        parkingCols = ["Existing spaces",
        		"New spaces",
        		"Differnece in spaces"]
        try:
            parkingData = tabelParse(parkingCols, 'Cars',parkingText)
            extractedcount += 1
            extractedlist.append("Parking")
        except IndexError as e:
            exceptionCount += 1
            exceptionlist.append("Parking,IndexError, %s"%e)  
        except:
            pass
    else:
        exceptionCount += 1
        exceptionlist.append("Parking,KeyError")  
    
    
    conn = MySQLdb.connect(user='colin',
                          passwd='fQ58g#t]:K*_q6S/',
                          db='research_uk',
                          host='granweb01',
                          charset="utf8",
                          use_unicode=True)
    cursor = conn.cursor()

    try:
        cursor.execute( '''UPDATE boroughs b
        	SET b.total_existing_non_res_floorspace_sqm = "%s",
        		b.total_lost_non_res_floorspace_sqm = "%s",
        		b.`total_new_non_res_floorspace proposed_sqm` = "%s",
        		b.total_net_non_res_floorspace_after_sqm = "%s"
        	WHERE b.case_reference_borough = "%s";'''%(floor_DF['Total']["Existing Non Res. Floorspace (sq.m)"], floor_DF['Total']["Lost Non Res. floorspace (sq.m)"], floor_DF['Total']["New Non Res. floorspace proposed (sq.m)"], floor_DF['Total']["Net Non Res. floorspace After (sq.m)"],case_ref_borough)
             )
        conn.commit()
    except Exception  as e:    
        print "ERROR",path.split('.')[0].split('/')[0],e
    try:
        cursor.execute('''UPDATE boroughs b
        	SET b.site_area_in_sq_ft = "%s"
        	WHERE b.case_reference_borough = "%s";'''%(DB_field_D['Site Area'][2],case_ref_borough)
             )
        conn.commit()
    except Exception  as e:    
        print "\tERROR",path.split('.')[0].split('/')[0],e

    finally:
        #print exceptionCount + extractedcount, path.split('.')[0].split('/')[0]
        conn.close()
    try:
        conn = MySQLdb.connect(user='colin',
                              passwd='fQ58g#t]:K*_q6S/',
                              db='research_uk',
                              host='granweb01',
                              charset="utf8",
                              use_unicode=True)
        cursor = conn.cursor()
    
        for a,b in zip(['existing_use_last_use','existing_use_current_state','existing_use_last_use_end_date'] ,['Last Use',"Current Use","Date use ended"]):       
                cursor.execute( '''UPDATE boroughs b
                	SET b.%s = "%s"
                	WHERE b.case_reference_borough = "%s";'''%(a,useKey_D[b],case_ref_borough)
                     )
                conn.commit()
    except Exception as e:
        print "USE",e
    finally:
        conn.close()
    try:
        conn = MySQLdb.connect(user='colin',
                              passwd='fQ58g#t]:K*_q6S/',
                              db='research_uk',
                              host='granweb01',
                              charset="utf8",
                              use_unicode=True)
        cursor = conn.cursor()
        print "\n######################\n",case_ref_borough
#        print "\t",floor_DF
        for I,k,i in [(I[0],k,I[1]) for k in floor_DF.keys() for I in [ ("%s %s"%(i.strip(),k.strip()),i ) for i in floor_DF.index]]:
#            I = k[1]
#            print I
#            print floor_DF[k][i]
#            print k
#            print i
#            print I
            
#            print case_ref_borough
            cursor.execute("""SELECT bm.*
                            FROM boroughs_metadata bm
                            WHERE bm.`case_reference_borough` = "%s";"""%case_ref_borough)
            # does the boroughs_metadata have any case_reference_borough?
            if cursor.rowcount == 0:
                    # if no, insert that case reference borough
                    cursor.execute("""INSERT INTO boroughs_metadata (case_reference_borough)
                                        VALUES ("%s");"""%case_ref_borough)
            try:
                cursor.execute('''UPDATE boroughs_metadata bm
                SET bm.%s = "%s"
                WHERE bm.case_reference_borough = "%s";'''%(I.replace('.','').replace(' Non Res ',' ').strip().replace(' ','_').replace('(','').replace(')','').replace('space','').replace('-',''),
                                                        floor_DF[k][i], case_ref_borough))
                conn.commit()
            except Exception as e:
                try:
                    cursor.execute('''UPDATE boroughs_metadata bm
                    SET bm.%s = "%s"
                    WHERE bm.case_reference_borough = "%s";'''%(I.replace('.','').replace(' Non Res ',' ').strip().replace(') ','_').replace(' ','_').replace('(','').replace(')','_').replace('space','').replace('-',''),
                                                        floor_DF[k][i], case_ref_borough)
                             )
                    conn.commit()
#                    print case_ref_borough,"HANDLED"
                except Exception as e:
                    print "&&&&&&&&&&&&&&&&&&&&&&&&",case_ref_borough
                    print "\t",e,"\n"
    except Exception as e:
        diFF = difflib.Differ()  
        print case_ref_borough
#        print "USE",e,"*#*#*#*#*#*#*#*"
#        print k
#        print i
#        print I
#        print I.replace('.','').replace(' Non Res ',' ').strip().replace(' ','_').replace('(','').replace(')','').replace('space','').replace('-',''),"\n"
#        print type('Existing_Floor_sqm__B1_c_Light_industrial'),type('Existing_Floor_sqm_B1_c_Light_industrial')
#        print str(e).split()[3].split('.')[1].split("'")[0]
#        print list(diFF.compare('Existing_Floor_sqm_B1_c_Light_industrial'.split('_'), 'Existing_Floor_sqm__B1_c_Light_industrial'.split('_')))
#        print list(diFF.compare('Existing_Floor_sqm__B1_c_Light_industrial'.split('_'),'Existing_Floor_sqm_B1_c_Light_industrial'.split('_')))
    finally:
        conn.close()

#        
#    try:
#        conn = MySQLdb.connect(user='colin',
#                              passwd='fQ58g#t]:K*_q6S/',
#                              db='research_uk',
#                              host='granweb01',
#                              charset="utf8",
#                              use_unicode=True)
#        
#        cursor = conn.cursor()
#        for I,k,i in [(I,k,i) for k in parkingData.keys() for I in [i+' '+k for i in parkingData.index]]:
#            print floor_DF[k][i]
#            print k
#            print i
#            print I
##            case_ref_borough = path.split('.')[0].replace('_application_form','').replace('_','/')
##            cursor.execute("""SELECT bm.*
##                            FROM boroughs_metadata bm
##                            WHERE bm.`case_reference_borough` = %s;""", case_ref_borough)
##            # does the boroughs_metadata have any case_ref_boroughs?
##            if cursor.num_rows == 0:
##                    # if no, insert that case reference borough
##                    cursor.execute("""INSERT INTO boroughs_metadata (case_reference_borough)
##                                        VALUES (%s);""", (case_ref_borough))
##    
##            cursor.execute('''UPDATE boroughs_metadata bm
##            SET bm.%s = "%s"
##            WHERE bm.case_reference_borough = "%s";'''%(I.replace(['.','(',')','space'],'').replace(' Non Res ',' ').strip().replace(' ','_'),
##                                                    floor_DF[k][i], case_ref_borough)
##                     )
##            conn.commit()
#    except Exception as e:
#        print "PARKING",e,"*@*@*@*@*@*@*@*"
#    finally:
#        conn.close()

#d = {'one' : [1., 2., 3., 4.],'two' : [4., 3., 2., 1.]}
#print pd.DataFrame(d, index=['a', 'b', 'c', 'd'])

"""
USE (1054, "Unknown column 'bm.Existing_Floor_sqm_B1_b_Research_and_development' in 'field list'") *#*#*#*#*#*#*#*
B1 (b) Research and development 
Net Non Res. floorspace After (sq.m)
Existing Non Res. Floorspace (sq.m) B1 (b) Research and development
Existing_Floor_sqm_B1_b_Research_and_development
3 PP_15_00582Royal Borough of Kensington and Chelsea_application_form


USE (1054, "Unknown column 'bm.Existing_Floor_sqm_B1_bResearch_and_development' in 'field list'") *#*#*#*#*#*#*#*
B1 (b)Research and development
Net Non Res. floorspace After (sq.m)
Existing Non Res. Floorspace (sq.m) B1 (b)Research and development
Existing_Floor_sqm_B1_bResearch_and_development
3 PP_14_08001Royal Borough of Kensington and Chelsea_application_form
"""
