import argparse
import db_connection as db  # subbroutine to connect to the database
import json
import pandas as pd

import iso_mapping as im  # subroutine with maps for cloud and weather codes
import time_utils as tu  # subroutine to get times
import transcription_data_processing as td  # subroutine to clean, validate and convert data


# argument parser for command line. options -u for UTC time, -cw for cloud and wind in text form. Config file
# neceesary for each station
parser = argparse.ArgumentParser(description='Generates SEF file from DB.')
parser.add_argument('config', metavar='config', type=str, nargs=1,
                    help='json config file for each station')
parser.add_argument('-u', action="store_true", help='apply utc offset')
parser.add_argument('-cw', action="store_true", help='keep original wind and cloud type')
args = parser.parse_args()

# Getting debug flag from the arguments
apply_utc_offset = args.u
keep_wind_cloud_type = args.cw

# open config file
with open(args.config[0]) as json_data_file:
    cfg = json.load(json_data_file)  # cfg is the json config file

(mydb, mycursor,engine) = db.connect(cfg)  # connect to the database

# set utcOffset: either 0 for local time or read from config file for timezone
utcOffset = 0
if apply_utc_offset:
    utcOffset = cfg["site"]["utcOffset"]
timezone = cfg["site"]["timezone"]


dateFormat = "%Y-%m-%d"
debugLog = open(cfg["site"]["name"] + ".log", "w")  # log with error notes
value = None  # inititalize values as None
# set up dataframe for cleaned data, original units
df_clean = pd.DataFrame(columns=['StationName', 'Timezone', 'UTCoffset', 'ObservationDate', 'UTCDate', 'value', 'unit',
                        'field_key', 'fieldID', 'annotationID', 'transcriptionID', 'pageID'])
# set up dataframe for cleaned data, iso units
df_iso = pd.DataFrame(columns=['StationName', 'Timezone', 'UTCoffset', 'ObservationDate', 'UTCDate', 'origValue', 'value', 'unit',
                      'field_key', 'fieldID', 'annotationID', 'transcriptionID', 'pageID'])

# filenames for csv file
filename_clean = cfg["site"]["source"] + "_" + cfg["site"]["org"] + "_" + cfg["site"]["name"] + "_" + "clean" + ".csv"
df_clean.to_csv(filename_clean)

filename_iso = cfg["site"]["source"] + "_" + cfg["site"]["org"] + "_" + cfg["site"]["name"] + "_" + "iso" + ".csv"
df_iso.to_csv(filename_iso)

clean_list=[]
iso_list=[]

# checking the types we should look at
# types = [{'type': 'wf', 'title': 'Wind_Force'}]

# for indexing rowxs in dataframe to send to db and csv
i = 1
j = 1

for type in cfg["types"]:  # go through all types in the config file
    # name of tsv (sef) file starts to be composed here
    filename = cfg["site"]["source"] + "_" + cfg["site"]["org"] + "_" + cfg["site"]["name"] + "_"
    t = type["type"]
    print(t)
    type_result_set = []
    type_error_set = []
    if cfg["fields"][t] is not None:
        # go through all fields that correspond to the type
        # sys.stderr.write("Field ID: " +fields["id"]+"\n")

        for fields in cfg["fields"][t]:
            timeOfDay = fields["timeOfDay"]
            unit = fields["unit"]  # original unit
            # build the query to send to the database to obtain the information needed to clean and transform data
            query = ('select a.observation_date, de1.value, de1.id, p.image_file_name, a.transcription_id, '
                     'pi2.location, f.field_key, field_id, de1.annotation_id, de1.page_id '
                     'from annotations a '
                     'join data_entries de1 on (de1.annotation_id=a.id and de1.field_id='+fields["id"]+') '
                     'join pages p on (p.id=a.page_id) '
                     'join fields f on de1.field_id = f.id '
                     'join page_infos pi2 on pi2.page_id = de1.page_id '
                     'where a.page_id in (select id from pages where title like \''+cfg["site"]["prefix"]+'%\') '
                     'order by  a.observation_date asc, a.updated_at desc')
            debugLog.write(query+"\n")
            mycursor.execute(query)
            results = mycursor.fetchall()
            previous_result_day = None
            for result in results:  # assign query results to variables
                flag = "passed"
                result_day = result[0]
                value = result[1]
                data_entry_id = result[2]
                image_file_name = result[3]
                transcription_id = result[4]
                station_name = result[5]
                field_name = result[6]
                field_id = result[7]
                annotation_id = result[8]
                page_id = result[9]
                #  print(value)
                if value == "":
                    value = None


# if more than one transcription take the most recent
                if (previous_result_day is None or
                   (result_day != previous_result_day and value is not None)):
                    error = None
                    result_day = result_day.replace(hour=0)
                    result_day = result_day.replace(minute=0)
                    (period, non_utc_result_day, hour, minute) = tu.getUTCResultDay(0, cfg, t, timeOfDay, result_day)
                    (period, utc_result_day, hour, minute) = tu.getUTCResultDay(utcOffset, cfg, t,
                                                                                timeOfDay, result_day)
                    unit = tu.getUnit(cfg, unit, t, result_day)
                    result_datetime = tu.getDateTimeResult(cfg, t, timeOfDay, result_day)


                    # Transform and validate data into SI
                    error_prefix = ("Field: " + fields["id"] + " - " + fields["name"] + "\t" +
                                    result_day.strftime('%Y-%m-%d') + " " + str(hour) + ":00:00\t " +
                                    str(value) + "\t")


                    # Pre-processing value entry
                    if value is not None:
                        (correctedValue, flag) = td.preProcess(value, debugLog, result_day, fields,
                                                               transcription_id, unit)
                        pre_iso_value = correctedValue
                        #  write cleaned value to dataframe
                        new_row_clean = (station_name, timezone, str(utcOffset), non_utc_result_day, utc_result_day,
                                         str(pre_iso_value), unit, field_name, str(field_id), str(annotation_id),
                                         str(transcription_id), str(page_id))
                        #df_clean.loc[i] = new_row_clean
                        clean_list.append(new_row_clean)
                        i += 1
                        debugLog.write(station_name + "," + str(utc_result_day) + "," + str(pre_iso_value) +
                                       "," + field_name + ", " + str(field_id) + "," + str(annotation_id) +
                                       "," + str(transcription_id) + "," + str(page_id) + "\n")
                    else:
                        pre_iso_value = None

                    if pre_iso_value is not None:
                        (flag, correctedValue, error) = td.getProcessedDataValue(flag, unit, pre_iso_value,
                                                                                 error_prefix, data_entry_id,
                                                                                 debugLog, t, transcription_id,
                                                                                 result_day, fields, hour,
                                                                                 keep_wind_cloud_type)

                        # #write ISO value to table in database
                        if correctedValue is not None:

                            new_row_iso = (station_name, timezone, str(utcOffset), non_utc_result_day, utc_result_day,
                                           str(pre_iso_value), str(correctedValue), unit,str(field_name), str(field_id), str(annotation_id),
                                           str(transcription_id), str(page_id))
                            #df_iso.loc[j] = new_row_iso
                            iso_list.append(new_row_iso)
                            j += 1

                        # build line to be written to SEF file
                        resultAsString = (utc_result_day.strftime('%Y') + "\t" + str(utc_result_day.strftime('%m')) +
                                          "\t" + str(utc_result_day.strftime('%d')) + "\t" +
                                          str(utc_result_day.strftime('%H')) + "\t" + str(minute) + "\t" + str(period) +
                                          "\t" + str(correctedValue) + "\t|" + "\torig=" + str(value) +
                                          " " + str(unit) + "|Local time: " + str(timeOfDay) + "|QC flag: " +
                                          str(flag) + "|Image File: ")
                        if image_file_name is None:
                            resultAsString += "None"
                        else:
                            resultAsString += str(image_file_name)
                        resultAsString += "\n"
                        #  "|link: https://eccc.opendatarescue.org/en/transcriptions/"+str(transcription_id)+"/edit\n"
                        # print(resultAsString)
                        type_result_set.append(resultAsString)
                        if error is not None:
                            type_error_set.append(error)
                            error = None
                previous_result_day = result_day


        if len(type_result_set) > 0:
            sorted_type_results = sorted(type_result_set)  # sort results by date
            # need the start and end dates for naming the SEF file
            # Get start
            start_found = 0
            index_start = 0
            while start_found == 0 and index_start < len(type_result_set):
                entry_value = sorted_type_results[index_start].split("\t")[6]
                if entry_value == "-999":  # we want to remove the leading -999 ato make the SEF file more compact
                    index_start += 1
                else:
                    start_found = 1
            # Get end
            end_found = 0
            index_end = -1
            while end_found == 0 and index_end > -len(type_result_set):
                entry_value = sorted_type_results[index_end].split("\t")[6]
                if entry_value == "-999":  # we want to remove the trailing -999 ato make the SEF file more compact
                    index_end -= 1
                else:
                    end_found = 1

            if index_start < len(type_result_set):
                startStr = sorted_type_results[index_start].split("\t")
                filename = filename+startStr[0] + "-"+startStr[1] + "_"
                endStr = sorted_type_results[index_end].split("\t")
                # complete the building of the SEF filename
                filename = filename+endStr[0] + "-"+endStr[1] + "-" + t + ".tsv"
                print(filename)
                f = open(filename, "w", encoding="utf-8")
                #  write the metadata for the SEF file
                f.write("SEF\t1.0.0\n")
                f.write("ID\t"+cfg["site"]["id"]+"\n")
                f.write("Name\t" + cfg["site"]["name"]+"\n")
                f.write("Lat\t" + cfg["site"]["lat"]+"\n")
                f.write("Lon\t" + cfg["site"]["lon"]+"\n")
                f.write("Alt\t" + cfg["site"]["alt"]+"\n")
                f.write("Source\t" + cfg["site"]["source"]+"\n")
                f.write("Link\t" + cfg["site"]["link"]+"\n")
                f.write("Vbl\t" + t.split("_")[0]+"\n")
                f.write("Stat\t")
                if "mean" in t:
                    f.write("mean\n")
                else:
                    f.write("point\n")
                f.write("Unit\t" + im.map_unit[unit] + "\n")
                f.write("Meta\t")
                # indicate whether the pressure has been temperature gravity corrected
                # if (sub_type=='PGC_PTC'):
                #    f.write("PGC=Y\tPTC=Y\t")
                # elif (sub_type=='PGC'):
                #    f.write('PGC=Y\t')
                # elif (sub_type=='PTC'):
                #    f.write('PTC=Y\t')
                # else:
                #   f.write("NO")
                # f.write("Observer Name="+str(observer_name))
                f.write("\tUTCOffset=")  # indicate if the time is in UTC or local
                if (utcOffset != 0):
                    f.write("Applied\tUTCOffset=" + str(utcOffset))  # UTC time
                else:
                    f.write("NO")  # local time
                f.write("\n")
                f.write("Year\tMonth\tDay\tHour\tMinute\tPeriod\tValue\t|\tMeta\n")
                index = 0
                for res in sorted_type_results:
                    if index >= index_start and index <= index_end + len(sorted_type_results):
                        f.write(res)  # write the main body of the SEF file
                    index += 1
        if len(type_error_set) > 0:
            error_filename = cfg["site"]["source"]+"_"+cfg["site"]["org"]+"_"+cfg["site"]["name"]+"_"+t+".err"
            error_file = open(error_filename, "w")
            for err in type_error_set:
                error_file.write(err)


# insert df to database:

df_clean=pd.DataFrame(clean_list, columns=['StationName', 'Timezone', 'UTCoffset', 'ObservationDate', 'UTCDate', 'value', 'unit',
                        'field_key', 'fieldID', 'annotationID', 'transcriptionID', 'pageID']).astype('string')
df_iso=pd.DataFrame(iso_list, columns=['StationName', 'Timezone', 'UTCoffset', 'ObservationDate', 'UTCDate', 'origValue', 'value', 'unit',
                        'field_key', 'fieldID', 'annotationID', 'transcriptionID', 'pageID']).astype('string')

df_clean.to_sql(con=engine, name='data_clean', if_exists='append')
df_iso.to_sql(con=engine, name='data_iso', if_exists='append')

df_clean.to_csv(filename_clean, encoding='utf-8')
df_iso.to_csv(filename_iso, encoding='utf-8')
