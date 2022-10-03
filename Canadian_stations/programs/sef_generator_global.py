import argparse
import datetime
import sys
import csv
import fractions
import json
import pymysql
from lmrlib import *

def getTimeOfDay (cfg, sefType, time, date):
	if "changetimeOfDay" in cfg and cfg["changetimeOfDay"]["active"] == True :
		for timeChange in cfg["timeChanges"] :
			if sefType in timeChange["sefTypes"]:
				for change in timeChange["changes"]:
					if change["fromTime"] == time and \
						date>=datetime.datetime.strptime(change["fromDate"],"%Y-%m-%d") and \
						date <=datetime.datetime.strptime(change["toDate"],"%Y-%m-%d"):
						return change["toTime"]
	return time

parser = argparse.ArgumentParser(description='Generates SEF file from DB.')
parser.add_argument('config', metavar='config', type=str, nargs=1,
                     help='json config file for each station')
parser.add_argument('-u',action="store_true",help='apply utc offset')
parser.add_argument('-cw',action="store_true",help='keep original wind and cloud type')
args = parser.parse_args()

#map to convert directions to iso
convert_directions={"north" : 0,
"North":0,
"north-north-east": 22.5,
"North-North-East" :22.5,
"north-east":45,
"North-East":45,
"east-north-east":67.5,
"East-North-East":67.5,
"east":90,
"East":90,
"east-south-east":112.5,
"East-South-East":112.5,
"south-east":135,
"South-East":135,
"south-south-east": 157.5,
"South-South-East":157.5,
"south":180,
"South":180,
"south-south-west": 202.5,
"South-South-West":202.5,
"south-west":225,
"South-West":225,
"west-south-west":247.5,
"West-South-West":247.5,
"west":270,
"West":270,
"west-north-west":292.5,
"West-North-West":292.5,
"north-west":315,
"North-West":315,
"north-north-west":337.5,
"North-North-West":337.5} 

# map to convert directions to abbreviation
abbr_directions={"north" :"N",
"North": "N",
"north-north-east": "NNE",
"North-North-East": "NNE",
"north-east":"NE",
"North-East":"NE",
"east-north-east":"ENE",
"East-North-East":"ENE",
"east":"E",
"East":"E",
"east-south-east":"ESE",
"East-South-East":"ESE",
"south-east":"SE",
"South-East":"SE",
"south-south-east": "SSE",
"South-South-East": "SSE",
"south":"S",
"South":"S",
"south-south-west": "SSW",
"South-South-West": "SSW",
"south-west":"SW",
"South-West":"SW",
"west-south-west":"WSW",
"West-South-West":"WSW",
"west":"W",
"West":"W",
"west-north-west":"WNW",
"West-North-West":"WNW",
"north-west":"NW",
"North-West":"NW",
"north-north-west":"NNW",
"North-North-West":"NNW",
"calm":"C",
"Calm":"C",
"0":"C"
}

convert_clouds_upper={"cirrus" : "Ch6",
"cirro-stratus": "Ch8",
"Cirrostratus":"Ch8",
"Nimbostratus":"Cm2",
"Cumulonimbus": "Cl9",
"cirro-cumulus":"Ch9",
"stratus": "Ch8",
"nimbus":"Cm2",
"cumulo-stratus":"Cm7",
"Cumulostratus":"Cm7",
"cirro-cumulus":"Ch9",
"cumulus":"Ch9",
"passing":"Cm4",
"scud": "Cm4",
"obscured":"Ch/",
"hidden": "Ch/",
"mist":"Ch/",
"fog":"Ch/",
"haze":"Ch/",
"smoke":"Ch/",
"?":"Ch/",
"clear":"Ch0",
"0":"Ch0"} 

convert_cloud_lower={"cirrus" : "Ch6",
"cirro-stratus": "Ch8",
"Cirrostratus":"Ch8",
"cirro-cumulus":"Ch9",
"Cirrocumulus":"Ch9",
"Nimbostratus":"Cm2",
"stratus":"Cl6",
"nimbus":"Cl7",
"cumulo-stratus":"Cl4",
"Cumulostratus":"Cl4",
"Cumulonimbus": "Cl9",
"cumulus":"Cl2",
"passing": "Cl2",
"scud":"Cl5",
"hidden": "Cl/",
"obscured":"Cl/",
"mist":"Cl/",
"fog":"Cl/",
"haze":"Cl/",
"smoke":"Cl/",
"overcast":"Cl7",
"?":"Cl/",
"0":"Cl0",
"clear":"Cl0"}

abbr_cloud={"cirrus" : "Ci",
"cirro-stratus": "CiSt",
"cirro-cumulus":"CiCu",
"stratus":"St",
"nimbus":"Ni",
"Nimbostratus": "NiSt",
"cumulo-stratus":"CuSt",
"Cirrostratus":"CiSt",
"Cirrocumulus": "CiCu",
"Cumulonimbus":"CuNi",
"cumulus":"Cu",
"overcast": "NiSt",
"passing": "P",
"scud":"Sc",
"hidden": "Hi",
"obscured":"Hi",
"mist":"Ms",
"fog":"Fg",
"haze":"Hz",
"smoke":"Sm",
"clear":"Cl",
"0":"Cl"}

# weather: R =rain, D =drizzle, F = foggy, Gloomy = cloudy


#Getting debug flag from the arguments
apply_utc_offset=args.u
keep_wind_cloud_type=args.cw

#print (type(keep_wind_cloud_type))
print(keep_wind_cloud_type)
# open config file
with open(args.config[0]) as json_data_file:
	cfg = json.load(json_data_file)	 # cfg is the json config file

#connecting to DB
mydb = pymysql.connect(
host=cfg["db"]["host"],
port=cfg["db"]["port"],
user=cfg["db"]["user"],
password=cfg["db"]["password"],
database=cfg["db"]["database"])

mycursor = mydb.cursor()

# set utcOffset either 0 for local time or read from config file for timezone 
utcOffset=0
if apply_utc_offset:
	utcOffset=cfg["site"]["utcOffset"]

dateFormat="%Y-%m-%d "

debugLog=open(cfg["site"]["name"]+".log","w")

# define unit translation
map_unit = {"F":"C",
			"inHg":"hPa",
			"in":"mm",
			"okta":"okta",
			"dir":"deg",
			"lct":"cloudatlas",
			"uct":"cloudatlas",
			"Sm":"Beaufort",
			"p":"%",
			"mno":"manual observation",
			"cloudvel":"0-10",
			"hcv":"0-10",
			"cv":"0-10",
			"hr":"hour",
			"tenths": "tenths",
			"abb":"1-10",
			"text":"none",
			"du":"du"
					}

#checking the types we should look at
for type in cfg["types"]:  # go through all types in the config file
	sys.stderr.write(type["title"]+"\n")
	filename=cfg["site"]["source"]+"_"+cfg["site"]["org"]+"_"+cfg["site"]["name"]+"_" # name of tsv (sef) file starts to be composed here
	
	t=type["type"]
	type_result_set=[]
	type_error_set=[]
	if cfg["fields"][t] != None:
		for fields in cfg["fields"][t]:	 # go through all fields tht correspond to the type
			sys.stderr.write("Field ID: " +fields["id"]+"\n")
			timeOfDay=fields["timeOfDay"]
			unit=fields["unit"]	 # original unit
			query=('select a.observation_date,de1.value,de1.id,p.image_file_name , a.transcription_id  '
				   'from annotations a ' 
				   'join data_entries de1 on (de1.annotation_id =a.id and de1.field_id='+fields["id"]+') '
				   'join pages p on (p.id=a.page_id) '
				   'where a.page_id in (select id from pages where title like \''+cfg["site"]["prefix"]+'%\') '
				   'order by  a.observation_date asc, a.updated_at asc')
			#debugLog.write(query+"\n")
			mycursor.execute(query)
			results=mycursor.fetchall()
			previous_result_day=None
			for result in results:
				flag="passed"
				#print(result)
				result_day=result[0]
				value=result[1]
				data_entry_id=result[2]
				image_file_name=result[3]
				transcription_id=result[4]

				if (previous_result_day is None or (result_day != previous_result_day and value != None)):	# if more than one transcription take the most recent
					error=None
					#print(fields["name"]+" - "+result_day.strftime(dateFormat) + " - " + result[1])
					if (timeOfDay == "mean" or timeOfDay == "total" or timeOfDay == "daily" ):
						period='24'
						hour=0
						minute='00'
					elif timeOfDay=="sunrise":
						period='0'
						hour=6+utcOffset
						minute="{0:02d}".format(int(0+60*(utcOffset-int(utcOffset))))
					else:
						period='0'
					
						overridenTimeOfDay=getTimeOfDay(cfg, t, timeOfDay, result_day)
						hour=int(overridenTimeOfDay[:2])
						hour=hour + utcOffset
						minute="{0:02d}".format(int(0+60*(utcOffset-int(utcOffset))))
					utc_result_day = result_day + datetime.timedelta(hours=hour)
					#Transform and validate data into SI
					error_prefix="Field: "+fields["id"]+ " - " + fields["name"]+ "\t"+result_day.strftime('%Y-%m-%d')+" "+str(hour)+":00:00\t"+str(value)+"\t"
					
					# Handle the case where the data is considered as missing
					if (value is None or "retracted" in value.lower() or value=="-999"	or value=="-" or "empty" in value.lower() or value==" " or value=="") :
						correctedValue='-999'
						flag="missing"
						if value is None:
							value="-999"
							flag="missing"
					elif "illegible" in value.lower():
						correctedValue=-888
						flag="illegible"
						debugLog.write("\tTranscriptionID: "+ str(transcription_id) +" " + "Invalid data: " + value +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )		 

					else:
						
						#### PRESSURE
						if unit == "inHg":
							try:
								if (" " in value):
									value=value.replace(" ",".")
									error=error_prefix + "SYNTAX\tSpace in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"
								if ("," in value):
									value=value.replace(",",".")
									error=error_prefix + "SYNTAX\tComma in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"
								if (".." in value):
									value=value.replace("..",".")
									error=error_prefix + "SYNTAX\t\"..\" in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"
									
								
								if ("\"" in value or "'" in value or value =="~" or value=="-" or value=="”"):
									correctedValue=-222
									flag="value unable to be recorded"
								else:
									v=float(value)

									# Handling case of pressure correction, where sometimes the dot is missing in the transcription
									if t=="e" and "." not in value and v>1:
										v=v/1000

									res=baro_Eng_in2mb(v)  # use value from iCoads lmrlib.py 2021.11.16
									correctedValue="{0:.2f}".format(res)

									#Some pressure values are correction data so range is different
									if (t!="e" and (v<27 or v>32)) or (t=="e" and (v<0 or v>2)):
										debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " + "Out of range: " + value +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"] + "\n" )
										flag="out of range"
									#Flag values which are not out of range for Canada but which are still high or low
									if (t!="e" and (v<28.5 and v>=-100)):
										flag="low value"
									elif(t!="e" and (v>28.5 and v<=30.6)):
										flag="none"	
									elif (t!="e" and (v>30.6)):
										flag="high value"
									if (t == "e" and (v<0.2 and v>=-100)):
										flag="low value"
									elif(t =="e" and (v>0.2 and v<=1.5)):
										flag="none"	
									elif (t =="e" and (v>1.5)):
										flag="high value"		
							except ValueError:
								debugLog.write("\tTranscriptionID: "+ str(transcription_id) + "Invalid data: " + value +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )		
								correctedValue='-999'
								flag="missing"
							
						### PRESSURE (mmHg)	
						
						if unit == "mmHg":
							try:
								if (" " in value):
									value=value.replace(" ",".")
									error=error_prefix + "SYNTAX\tSpace in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"
								if ("," in value):
									value=value.replace(",",".")
									error=error_prefix + "SYNTAX\tComma in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"
								if (".." in value):
									value=value.replace("..",".")
									error=error_prefix + "SYNTAX\t\"..\" in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"
									
								
								if ("\"" in value or "'" in value or value =="~" or value=="-" or value=="”"):
									correctedValue=-222
									flag="value unable to be recorded"
								else:
									v=float(value)

									# Handling case of pressure correction, where sometimes the dot is missing in the transcription
									if t=="e" and "." not in value and v>1:
										v=v/1000

									res=baro_mm2mb(v)  # use value from iCoads lmrlib.py 2021.11.16
									correctedValue="{0:.2f}".format(res)

									#Some pressure values are correction data so range is different
									if (t!="e" and (v<700 or v>780)) or (t=="e" and (v<0 or v>5)):
										debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " + "Out of range: " + value +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"] + "\n" )
										flag="out of range"
									#Flag values which are not out of range for Canada but which are still high or low
									if (t!="e" and (v<700 and v>=-100)):
										flag="low value"
									elif(t!="e" and (v>740 and v<=780)):
										flag="none"	
									elif (t!="e" and (v>780)):
										flag="high value"
									if (t == "e" and (v<0.5 and v>=-100)):
										flag="low value"
									elif(t =="e" and (v>0.5 and v<=5)):
										flag="none"	
									elif (t =="e" and (v>5)):
										flag="high value"	
										
							except ValueError:
								debugLog.write("\tTranscriptionID: "+ str(transcription_id) + "Invalid data: " + value +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )		
								correctedValue='-999'
								flag="missing"	

						### TEMPERATURE
						elif  unit == "F" or unit == "ºF":
							try:
								if ("- " in value):
									value=value.replace("- ","-")
									error=error_prefix + "SYNTAX\tSpace in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"
								if ("+ " in value):
									value=value.replace("+ ","")
									error=error_prefix + "SYNTAX\tSpace in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"

								if (" " in value):
									value=value.replace(" ",".")
									error=error_prefix + "SYNTAX\tSpace in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"
								if ("," in value):
									value=value.replace(",",".")
									error=error_prefix + "SYNTAX\tComma in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"
								if (".." in value):
									value=value.replace("..",".")
									error=error_prefix + "SYNTAX\t\"..\" in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"
								if ("." in value and "/" in value):
									value=value.replace("."," ")
								
								if ("tdb" in t or t=="tb" or t =="td") and (value=="\"" or value =="'" or value =="~" or value=="-" or value=="\'\'" or value=="\"\"" or "*" in value):
									correctedValue=-222
									flag= "value unable to be recorded"
								else:

									from fractions import Fraction
									temperature=float(sum(Fraction(s) for s in value.split()))
									if (temperature<-50 or temperature>120):
										debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " + "Out of range: " + value +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )
										flag="out of range"
									if (temperature <-45):
										flag="low value"	
									elif(temperature >100):
										flag="high value" 
									res=(float(temperature)-32)*5/9
									correctedValue="{0:.2f}".format(res)
							except ValueError:
								debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " + "Invalid data: " + value +" on " + result_day.strftime(dateFormat)+" Hour:" + str(hour)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )		   
								correctedValue='-999'
								flag="missing"
						### PERCENTAGE DATA
						elif unit =="p":
							if (" " in value):
								value=value.replace(" ",".")
								error=error_prefix + "SYNTAX\tSpace in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"
							if ("," in value):
								value=value.replace(",",".")
								error=error_prefix + "SYNTAX\tComma in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"
							if (".." in value):
								value=value.replace("..",".")
								error=error_prefix + "SYNTAX\t\"..\" in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"
							if value=="\"" or value =="'" or value =="~" or value=="-" or value=="\'\'" or value=="\"\"" or ":" in value or "*" in value:
								correctedValue=-222
								flag="value unable to be recorded"
							else:
 
								try:
									res=float(value)
									if (res<0 or res>100):
										debugLog.write("\tTranscriptionID: "+ str(transcription_id) +  " " + "Out of range: " + value +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )				
									elif (res>0 and res<=1):
										debugLog.write("TranscriptionID: "+ str(transcription_id) + "\less than 1: " + value +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )
										res=res*100	
										flag="multiply by 100"
									correctedValue =	"{0:.2f}".format(res)		
								except ValueError:
									debugLog.write("\tTranscriptionID: "+ str(transcription_id) + "Invalid data: " + value +" on " + result_day.strftime(dateFormat)+" Hour:" + str(hour)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )		 
									correctedValue='-999'
									flag="missing"
						elif unit =="rh":
							if (" " in value):
								value=value.replace(" ",".")
								error=error_prefix + "SYNTAX\tSpace in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"
							if ("," in value):
								value=value.replace(",",".")
								error=error_prefix + "SYNTAX\tComma in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"
							if (".." in value):
								value=value.replace("..",".")
								error=error_prefix + "SYNTAX\t\"..\" in value\tUPDATE data_entries set value='"+str(value)+"' WHERE id="+str(data_entry_id)+";\n"
							if value=="\"" or value =="'" or value =="~" or value=="-" or value=="\'\'" or value=="\"\"" or ":" in value or "*" in value:
								correctedValue=-222
								flag="value unable to be recorded"
							else:
 
								try:
									res=float(value)
									if (res<0 or res>100):
										debugLog.write("\tTranscriptionID: "+ str(transcription_id) +  " " + "Out of range: " + value +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )				
									elif (res>0 and res<=1):
										debugLog.write("TranscriptionID: "+ str(transcription_id) + "\less than 1: " + value +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )
										res=res*100	
										flag="multiply by 100"
									correctedValue =	"{0:.2f}".format(res)		
								except ValueError:
									debugLog.write("\tTranscriptionID: "+ str(transcription_id) + "Invalid data: " + value +" on " + result_day.strftime(dateFormat)+" Hour:" + str(hour)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )		 
									correctedValue='-999'
									flag="missing"			
									
						### BEAUFORT SCALE (WIND SPEED should make a conversion) 
						elif unit =="Sm":
							field_id=fields["id"]

							#This is bad, I know, but some fields contain two different data entries: wind force and direction
							if field_id=="177" or field_id=="178" or field_id=="179" or field_id=="180":
								value=value.replace(","," ")
								if value != "0":
									values=value.split(" ")
									debugLog.write(result_day.strftime(dateFormat)+" Wind force. Values:" + value+ " - looking if isdigit for: " +values[-1]+"\n")
									if values[-1].isdigit():
										value=values[-1]
									else:
										value=values[0]
									debugLog.write("Selected wind force: "+value+"\n")

							try:
								from fractions import Fraction
								res=float(sum(Fraction(s) for s in value.split()))
								if (res<0 or res>10):
									debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " + "Out of range: " + value +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )
									flag="out of range"
									correctedValue='-999'
								else:
									if (res==4):
										res=5
									elif (res==5):
										res=7
									elif res==6:
										res=8
									elif res==7:
										res=9
									elif res==8:
										res=11
									elif res==9:
										res=12
								
								correctedValue="{0:.0f}".format(res)
							except ValueError:
								debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " + "Invalid data: " + value +" on " + result_day.strftime(dateFormat)+" Hour:" + str(hour)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )		   
								correctedValue='-999'
								flag='missing'
						### INCHES
						elif unit =="in":
							ress=value
							ress=ress.replace("R ","")
							ress=ress.replace ("S ","")
							ress=ress.replace (",",".")
							try:
								if ("in" in value.lower() or "slight" in value.lower() or "meas" in value.lower() or "trace" in value.lower()):
									res=0.005
									flag='trace'
								elif " / " in ress:
									values=ress.split(" / ")
									res=0
									for v in values:
										res+=float(v)
								elif "/" in ress:
									ress=ress.replace(".", " ")
									from fractions import Fraction
									res=float(sum(Fraction(s) for s in ress.split()))
								elif "|" in ress:
									values=ress.split("|")
									res=0
									for v in values:
										res+=float(v)
										debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " + "Two values added: " + value +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )
										flag="Two values added"
								elif "," in ress:
									values=ress.split("|")
									res=0
									for v in values:
										res+=float(v)
										debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " + "Two values added: " + value +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )
										flag="Two values added"		
								else:
									res=float(ress)
								if (res<0 or res>30):
									debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " + "Out of range: " + value +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )
									flag='high value'
								res=res*25.4
								correctedValue="{0:.2f}".format(res)
							except ValueError:
								debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " + "Invalid data: " + value +" on " + result_day.strftime(dateFormat)+" Hour:" + str(hour)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )		   
								correctedValue='-999'
							except ZeroDivisionError:
								debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " + "Invalid data: " + value +" on " + result_day.strftime(dateFormat)+" Hour:" + str(hour)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )		   
								correctedValue='-999'
								flag='missing'
						### DIRECTIONS
						
### I think in the clouds and wind for all fields (direction, type, amount, speed) there will be instances where multiple entries are added into the same field, so we will need to split them up. We might even need to add in as a default for almost every field					
						elif unit=="dir":
							field_id=fields["id"]
							# Some fields contains the direction and the speed of the wind, so extracting the direction
							if field_id=="177" or field_id=="178" or field_id=="179" or field_id=="180" or field_id=="181" or field_id=="182" or field_id=="183" or field_id=="184":
								value=value.replace(","," ")
								if value != "0":
									values=value.split(" ")
									if values[-1].isdigit():
										value = values[0]
									else:
										value=values[-1]
								else:
									value="Calm"
							if value=="Calm" or "perceptible" in value.lower() or value=="0" or "not" in value.lower():
								correctedValue="Calm"
							elif "variable" in value.lower():
								correctedValue="Variable"
							elif "passing" in value.lower():
								correctedValue=-999
								flag='missing'
							elif "Hidden" in value.lower():
								correctedValue=-999	 
								flag='missing'
							else:
								#No text found, we will try to map the value
								try:
									if keep_wind_cloud_type:
										correctedValue=abbr_directions[value.lower()]
									else: 
										correctedValue=convert_directions[value.lower()]
								except KeyError:
									debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " + "Invalid data: " + value +" on " + result_day.strftime(dateFormat)+" Hour:" + str(hour)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )		   
									correctedValue='-999'
									flag='missing'
																		
						### UPPER CLOUD TYPE
						elif unit=="uct":
							try:
								if keep_wind_cloud_type:
									correctedValue=abbr_cloud[value.lower()]
								else: 
									correctedValue=convert_clouds_upper[value.lower()]
							except KeyError:
									debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " + "Invalid data: " + value +" on " + result_day.strftime(dateFormat)+" Hour:" + str(hour)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )		   
									correctedValue='-999'
									flag='missing'
						

						### LOWER CLOUD TYPE
						elif unit=="lct":
							try:
								if keep_wind_cloud_type:
									correctedValue=abbr_cloud[value.lower()]
								else: 
									correctedValue=convert_cloud_lower[value.lower()]
							except KeyError:
									debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " + "Invalid data: " + value +" on " + result_day.strftime(dateFormat)+" Hour:" + str(hour)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )		   
									correctedValue='-999'
									flag='missing'

						### MANUAL OBSERVATION
						elif unit=="mno":
							if "snow" in value.lower():
								correctedValue="SN"
							elif "rain" in value.lower():
								correctedValue="RA"
							elif "thunder" in value.lower():
								correctedValue="TS"
							elif "lightning" in value.lower():
								correctedValue="LT"
							elif "freezing drizzle" in value.lower():
								correctedValue="FZDZ"
							elif "freezing rain" in value.lower():
								correctedValue="FZRA"
							elif "hail" in value.lower():
								correctedValue="GR"
							elif "small hailsteon" in value.lower():
								correctedValue="SHGS"
							elif "ice crystals" in value.lower():
								correctedValue="IC"
							elif "fog" in value.lower():
								correctedValue="FG"
							elif "freezing fog" in value.lower():
								correctedValue="FZFG"
							elif "mist" in value.lower():
								correctedValue="BR"
							elif "fog patches" in value.lower():
								correctedValue="BCFG"
							elif "shallow fog" in value.lower():
								correctedValue="MIFG"
							elif "blow" in value.lower():
								correctedValue="BLSN"
							elif "blowing dust" in value.lower():
								correctedValue="BLDU"
							elif "drift" in value.lower():
								correctedValue="DRSN"
							elif "ice pellets" in value.lower():
								correctedValue="PL"
							elif "driz" in value.lower():
								correctedValue="DZ"
							elif "shower" in value.lower():
								correctedValue="SH"
							elif "squal" in value.lower():
								correctedValue="SQ"
							elif "dust haze" in value.lower():
								correctedValue="DU"
							elif "haz" in value.lower():
								correctedValue="HZ"
							elif "smok" in value.lower():
								correctedValue="FU"
							elif "sleet" in value.lower():
								correctedValue="RN +SN +IP"
							elif "aurora" in value.lower():
								correctedValue="AU"
							elif "parhelia" in value.lower() or "parahelia" in value.lower():
								correctedValue="PARHEL"
							elif "parasel" in value.lower():
								correctedValue="PARSEL"
							elif "halo" in value.lower():
								correctedValue="HALO"
							elif "corona" in value.lower():
								correctedValue="CORONA"
							elif "shower" in value.lower():
								correctedValue="SH"
							elif "sky" in value.lower() and "clear" in value.lower():
								correctedValue="SKC"
							elif "frost" in value.lower():
								correctedValue="FRST"
							else:
								debugLog.write("\tTranscriptionID: "+ str(transcription_id) +" " + "Invalid data: " + value +" on " + result_day.strftime(dateFormat)+" Hour:" + str(hour)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )		  
								correctedValue='-999'
								flag='missing'		
						### CLOUD VELOCITY - THAT IS A SMITHSONIAN TYPE OF MEASUREMENT
						elif unit=="cloudvel":
							if value != "0":
									values=value.split(" ")
									value = values[-1]
							try:
								if value =="P" or value=="perceptible":
									res="1"
									correctedValue="1"
								else:
									res=float(value)
									if (res<0 or res>10):
										debugLog.write("\tTranscriptionID: "+ str(transcription_id) + "Out of range: " + value +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )
									correctedValue="{0:.0f}".format(res)
							except ValueError:
								debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " + "Invalid data: " + value +" on " + result_day.strftime(dateFormat)+" Hour:" + str(hour)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )		   
								correctedValue='-999'
								flag='missing'
						#### OKTA : [Upper] Cloud Amount
						elif unit =="okta":
							if "fog" in value.lower() or "smoke" in value.lower() or "haze" in value.lower() or "scud" in value.lower() or "hidden" in value.lower():
								correctedValue=9
							elif value=="Zero" or "clear" in value.lower():
								correctedValue=0
							else:
								try:
									res=float(value)
									if (res<0 or res>10):
										debugLog.write("\tTranscriptionID: "+ str(transcription_id)+ " " + "Out of range: " + value +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )
										falg='out of range'
									else:
										res=res*0.8
									correctedValue="{0:.2f}".format(res)
								except ValueError:
									debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " +"Invalid data: " + value +" on " + result_day.strftime(dateFormat)+" Hour:" + str(hour)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )		  
									correctedValue='-999'
									flag='missing'

						else:
							correctedValue=value
					   

					resultAsString=utc_result_day.strftime('%Y')+"\t"+utc_result_day.strftime('%m')+"\t"+utc_result_day.strftime('%d')+"\t"+utc_result_day.strftime('%H')+"\t"+minute+"\t"+period+"\t"+ \
							str(correctedValue)+"\t|"+"\torig="+value+" "+unit+"|Local time: "+timeOfDay+"|QC flag: " + flag+  \
							"|Image File: "
					if image_file_name is None:
						resultAsString+= "None" 
					else: 
						resultAsString+=str(image_file_name) 
					resultAsString+="\n"
							
					 #		 "|link: https://eccc.opendatarescue.org/en/transcriptions/"+str(transcription_id)+"/edit\n"
					#print(resultAsString)
					type_result_set.append(resultAsString)
					if error is not None:
						type_error_set.append(error)
						error=None
				previous_result_day=result_day
			

		if len(type_result_set)>0:
			sorted_type_results=sorted(type_result_set)
			#if t=="ta":
				#for res in sorted_type_results:
					#print(res)
			# now we can complete the file name
			#we want to remove the leading -999 and the trailing -999
			#Get start
			start_found=0
			index_start=0
			while start_found==0 and index_start<len(type_result_set):
				entry_value=sorted_type_results[index_start].split("\t")[6]
				if entry_value=="-999":
					#debugLog.write("Skipping for start : " +sorted_type_results[index_start])
					index_start+=1
				else:
					start_found=1
			#Get end
			end_found=0
			index_end=-1
			while end_found==0 and index_end > -len(type_result_set):
				entry_value=sorted_type_results[index_end].split("\t")[6]
				if entry_value=="-999":
					#debugLog.write("Skipping for end : " +sorted_type_results[index_end])
					index_end-=1
				else:
					end_found=1
			
			if index_start<len(type_result_set):
				startStr=sorted_type_results[index_start].split("\t")
				filename=filename+startStr[0]+"-"+startStr[1]+"_"
				endStr=sorted_type_results[index_end].split("\t")
				filename=filename+endStr[0]+"-"+endStr[1]+"-"+t+".tsv"
				print(filename)
				f=open(filename,"w")
				f.write ("SEF\t1.0.0\n")
				f.write ("ID\t"+cfg["site"]["id"]+"\n")
				f.write ("Name\t" + cfg["site"]["name"]+"\n")
				f.write ("Lat\t" + cfg["site"]["lat"]+"\n")
				f.write ("Lon\t" + cfg["site"]["lon"]+"\n")
				f.write ("Alt\t" + cfg["site"]["alt"]+"\n")
				f.write ("Source\t" + cfg["site"]["source"]+"\n")				 
				f.write ("Link\t" + cfg["site"]["link"]+"\n")
				f.write ("Vbl\t" + t.split("_")[0]+"\n")
				f.write ("Stat\t")
				if "mean" in t:
					f.write("mean\n")
				else:
					f.write("point\n")
				f.write ("Unit\t" + map_unit[unit]+"\n")
				f.write("Meta\t")
				#if (sub_type=='PGC_PTC'):
				#	 f.write("PGC=Y\tPTC=Y\t")
				#elif (sub_type=='PGC'):
				#	 f.write('PGC=Y\t')
				#elif (sub_type=='PTC'):
				#	 f.write('PTC=Y\t')
				#else:
				#	f.write("NO")
				#f.write("Observer Name="+str(observer_name))
				f.write("\tUTCOffset=")
				if (utcOffset!=0):
					f.write("Applied\tUTCOffset="+str(utcOffset))
				else:
					f.write("NO")
				f.write("\n")
				f.write ("Year\tMonth\tDay\tHour\tMinute\tPeriod\tValue\t|\tMeta\n")
				index=0
				for res in sorted_type_results:
					if index>=index_start and index<=index_end+len(sorted_type_results):
						f.write(res)
					index+=1
		if len(type_error_set)>0:
			error_filename=cfg["site"]["source"]+"_"+cfg["site"]["org"]+"_"+cfg["site"]["name"]+"_"+t+".err"
			error_file=open(error_filename,"w")
			for err in type_error_set:
				error_file.write(err)
