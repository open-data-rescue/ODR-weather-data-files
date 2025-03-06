# -*- coding: utf-8 -*-
import lmrlib as lmr  # code from NOAA to convert historical units to SI
import iso_mapping as im  # subroutines written as part of post-processing
from numpy import sqrt

dateFormat = "%Y-%m-%d "


# pre-processing  # removes extraneous characters
def preProcess(value, debugLog, result_day, fields, transcription_id, unit):
    if value is not None:
        value = value.casefold()
        correctedValue = value
    if unit == "mno" and value is not None:
        return (value, None)
    #  variables where empty is not missing but no value or zero value, e.g. precipitation, wind
    if (unit == "Bf" or unit == "Sm" or unit == "mph" or unit == "lbsft" or unit == "lct" or
            unit == "uct" or unit == "cloudvel" or unit == "okta" or unit == "in") and (value == "empty" or value == "dot"):
        return ("0", "empty")
    elif unit == "in" and value == "None":
        return ("0", "empty")
    elif unit == "dir" and value == "empty":
        return ("calm", "empty")

# Handle the case where the data is considered as missing
    missing_terms = ["not.taken", "not taken", "unknown symbol", "retracted", "-999", "none", "no grass",
                     "no place", "suspended", "abt on duty"]
    instrument_error_terms = ["out of order", "out.of.order", "broken", "unserviceable", "-888", "incorrect",
                              "not reliable", "covered in snow", "covered with snow", "observer", "no error"]

    if (value is None or value == "-" or value == " " or value == "" or value == '"' or
       any([x.lower() in value for x in missing_terms])):
        correctedValue = '-999'
        flag = "missing"

    elif (value == '*' or any([x.lower() in value for x in instrument_error_terms])):
        correctedValue = '-999'
        flag = "instrument error"
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Invalid data: " + value + " on " +
                       result_day.strftime(dateFormat) + "\tField: " + fields["id"] + " - " + fields["name"] + "\n")

    elif ("cirrus" in value):
        correctedValue = 'cirrus'
        flag = "cloud illegible"
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Invalid data: " + value + " on " +
                       result_day.strftime(dateFormat) + "\tField: " + fields["id"] + " - " + fields["name"] + "\n")

    elif ("illegible" in value.lower() or "Illegible" in value ):
        correctedValue = '-999'
        flag = "illegible"
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Invalid data: " + value + " on " +
               result_day.strftime(dateFormat) + "\tField: " + fields["id"] + " - " + fields["name"] + "\n")

    else:
        correctedValue = value
        flag = "None"
    return (correctedValue, flag)


# get processed (cleaned and SI unit) value depending on unit.  Including errors and debug. Keep wind and cloud type
# returns values in cloud type (Ci, Cu, etc) and compass rose directions
def getProcessedDataValue(flag, unit, value, error_prefix, data_entry_id,
                          debugLog, t, transcription_id, result_day, fields, hour,
                          keep_wind_cloud_type):
    value = value.casefold()
    match unit:
        case "inHg":  # inches of mercury e.g. barometer, vapour pressure
            return getInHg(flag, unit, value, error_prefix, data_entry_id,
                           debugLog, t, transcription_id, result_day, fields, hour,
                           keep_wind_cloud_type)
        case "mmHg":  # mm of mercury e.g. barometer, vapour pressure
            return getmmHg(flag, unit, value, error_prefix, data_entry_id,
                           debugLog, t, transcription_id, result_day, fields, hour,
                           keep_wind_cloud_type)
        case "F":  # all thermometer values
            return getF(flag, unit, value, error_prefix, data_entry_id,
                        debugLog, t, transcription_id, result_day, fields,
                        hour, keep_wind_cloud_type)
        case "ºF":  # all thermometer values
            return getF(flag, unit, value, error_prefix, data_entry_id,
                        debugLog, t, transcription_id, result_day, fields, hour,
                        keep_wind_cloud_type)
        case "p":  # percentage values
            return getP(flag, unit, value, error_prefix, data_entry_id,
                        debugLog, t, transcription_id, result_day, fields, hour,
                        keep_wind_cloud_type)
        case "rh":  # relative humidty
            return getRH(flag, unit, value, error_prefix, data_entry_id,
                         debugLog, t, transcription_id, result_day, fields, hour,
                         keep_wind_cloud_type)
        case "Sm":  # Smithsonian wind scale (0-12)
            return getSM(flag, unit, value, error_prefix, data_entry_id,
                         debugLog, t, transcription_id, result_day, fields, hour,
                         keep_wind_cloud_type)
        case "Bf":  # Beaufort wind scale (0-10), also for cloud velocity
            return getBf(flag, unit, value, error_prefix, data_entry_id,
                         debugLog, t, transcription_id, result_day, fields, hour,
                         keep_wind_cloud_type)
        case "Bf_text":  # Beaufort wind scale in text format (light, strong, etc)
            return getBf_text(flag, unit, value, error_prefix, data_entry_id,
                              debugLog, t, transcription_id, result_day, fields, hour,
                              keep_wind_cloud_type)
        case "mph":  # miles per hour e.g. wind
            return getMPH(flag, unit, value, error_prefix, data_entry_id,
                          debugLog, t, transcription_id, result_day, fields, hour,
                          keep_wind_cloud_type)
        case "lbsft":  # pounds per square inch, e.g. wind force
            return getLbsFt(flag, unit, value, error_prefix, data_entry_id,
                            debugLog, t, transcription_id, result_day, fields, hour,
                            keep_wind_cloud_type)
        case "in":  # inches, e.g. precipitation
            return getIn(flag, unit, value, error_prefix, data_entry_id,
                         debugLog, t, transcription_id, result_day, fields, hour,
                         keep_wind_cloud_type)
        case "dir":  # direction
            return getDir(flag, unit, value, error_prefix, data_entry_id,
                          debugLog, t, transcription_id, result_day, fields, hour,
                          keep_wind_cloud_type)
        case "uct":  # upper cloud type
            return getUCT(flag, unit, value, error_prefix, data_entry_id,
                          debugLog, t, transcription_id, result_day, fields, hour,
                          keep_wind_cloud_type)
        case "lct":  # lower cloud type
            return getLCT(flag, unit, value, error_prefix, data_entry_id,
                          debugLog, t, transcription_id, result_day, fields, hour,
                          keep_wind_cloud_type)
        case "mno":  # manual observation, e.g. weather
            return getMNO(flag, unit, value, error_prefix, data_entry_id,
                          debugLog, t, transcription_id, result_day, fields, hour,
                          keep_wind_cloud_type)
        case "oz":  # ozone. No conversion yet
            return getOz(flag, unit, value, error_prefix, data_entry_id,
                         debugLog, t, transcription_id, result_day, fields, hour,
                         keep_wind_cloud_type)
        case "cloudvel":  # cloud velocity
            return getCloudVel(flag, unit, value, error_prefix, data_entry_id,
                               debugLog, t, transcription_id, result_day, fields, hour,
                               keep_wind_cloud_type)
        case "okta":  # cloud cover
            return getOkta(flag, unit, value, error_prefix, data_entry_id,
                           debugLog, t, transcription_id, result_day, fields, hour,
                           keep_wind_cloud_type)
        case "tenths":  # cloud cover in tenths /clearness of sky
            return getOkta(flag, unit, value, error_prefix, data_entry_id,
                           debugLog, t, transcription_id, result_day, fields, hour,
                           keep_wind_cloud_type)
        case _:
            return (None, value, None)


# Cleaning up value -replace spaces, commas or double points with decimal point
def cleanupValue(error_prefix, value, data_entry_id, flag):
    error = None
    value = value.casefold()
    correctedValue = value
    error_suffix = "UPDATE data_entries set value='" + str(value) + "' WHERE id=" + str(data_entry_id) + ";\n"
#  common transcription errors
    if (" " in value):
        value = value.replace(" ", ".")
        error = error_prefix + "SYNTAX\tSpace in value\t" + error_suffix
    if ("," in value):
        value = value.replace(",", ".")
        error = error_prefix + "SYNTAX\tComma in value\t" + error_suffix
    if (".." in value):
        value = value.replace("..", ".")
        error = error_prefix + "SYNTAX\t\"..\" in value\t" + error_suffix
    if ("- " in value):  # negative sign has space between it and value
        value = value.replace("- ", "-")
        error = error_prefix + "SYNTAX\tSpace in negative sign\t" + error_suffix
    if ("+ " in value):  # value has unnecessary positive sign
        value = value.replace("+ ", "")
    if ("[" in value):  # value has unnecessary bracket
        value = value.replace("[", "")
    if ("]" in value):  # value has unnecessary bracket
        value = value.replace("]", "")
        error = error_prefix + "SYNTAX\tSpace in postive sign\t" + error_suffix
    if ("." in value and "/" in value):  # remove decimal if value is fraction
        value = value.replace(".", " ")
#  values indicating the observation could not be recorded
    if ("\"" in value or "'" in value or "~" in value or value=="-" or "\'\'" in value or "\"\"" in value
            or ":" in value or "*" in value or "”" in value):
        correctedValue = -222
        flag = "value unable to be recorded"
    else:
        correctedValue=value
    return (value, error, flag, correctedValue)


# convert values based on unit

# Beaufort wind scale conversion
def getBf(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
          transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    value=value.lower()
    field_id = fields["id"]
    (value, error, flag, correctedValue) = cleanupValue(error_prefix, value, data_entry_id, flag)
    # Some fields contain two different data entries: wind force and direction. Here we select wind force
    if field_id == "177" or field_id == "178" or field_id == "179" or field_id == "180":
        value = value.replace(",", " ")
        # if value != "0":
        if ("." in value):
            values = value.split(".")
        else:
            values = value.split(" ")

        debugLog.write(result_day.strftime(dateFormat)+" Wind force. Values:"
                       + value + " - looking if isdigit for: " + values[-1] + "\n")
        if values[-1].isdigit():  # if both direction and force in same entry, see which value is numeric
            value = values[-1]
        else:
            value = values[0]

        if ("|" in value):
            values = value.split("|")
            value = values[-1]
            debugLog.write("Selected wind force: " + value + "\n")
    try:
        if (value == "-222" or value == "-888"):
            value = '-999'  # remove -888 and -222
        if (value == "empty" or flag == "empty"):
            value = "0"
            correctedValue = 0
            flag = "no entry: calm"
        elif (flag != "missing" and flag != "instrument error" and
                flag != "illegible" and flag != "empty" and flag != "no entry: calm"):
            from fractions import Fraction
            res = float(sum(Fraction(s) for s in value.split()))
            res = int(res)
            if (res < 0 or res > 12):  # if value is out of range, write debug log and error type
                debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Out of range: " + value + " on " +
                               result_day.strftime(dateFormat) + "\tField: "+fields["id"] +
                               " - " + fields["name"] + "\n")
                flag = "out of range"
                correctedValue = -999
            else:
                # next, take these units in Beaufort and convert using lmrlib function wind_Beaufort2mps
                # res = lmr.wind_Beaufort2mps(res)
                res = im.convertBeaufort(res)
                correctedValue = "{0:.0f}".format(res)
        else:
            correctedValue = -999
            flag = 'missing'
    except ValueError:  # if value does not conform, write debug log and error type
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Invalid data: " + value + " on " +
                       result_day.strftime(dateFormat) + " Hour:" + str(hour) + "\tField: " + fields["id"] +
                       " - " + fields["name"] + "\n")
        correctedValue = -999
        flag = 'missing'
    return (flag, correctedValue, error)


# Beaufort text wind scale conversion
def getBf_text(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
               transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    value = value.lower()
    (value, error, flag, correctedValue) = cleanupValue(error_prefix, value, data_entry_id, flag)
    try:
        if (value == "-222" or value == "-888"):
            value = '-999'  # remove -888 and -222
        if (value == "empty" or flag == "empty"):
            value = "0"
            correctedValue = 0
            flag = "no entry: calm"
        elif (flag != "missing" and flag != "instrument error" and
                flag != "illegible" and flag != "empty" and flag != "no entry: calm"):
            res = im.convertBeauforttext(value)
            correctedValue = "{0:.0f}".format(res)
        else:
            correctedValue = -999
            flag = 'missing'
    except ValueError:  # if value does not conform, write debug log and error type
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Invalid data: " + value + " on " +
                       result_day.strftime(dateFormat) + " Hour:" + str(hour) + "\tField: " + fields["id"] +
                       " - " + fields["name"] + "\n")
        correctedValue = -999
        flag = 'missing'
    return (flag, correctedValue, error)


# CLoudVel cloud velocity
def getCloudVel(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
                transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    (value, error, flag, correctedValue) = cleanupValue(error_prefix, value, data_entry_id, flag)
    try:
        if (value == "-222" or value == "-888"):
            value = '-999'  # remove -888 and -222
        if (value == "empty" or flag == "empty"):
            value = "0"
            correctedValue = 0
            flag = "no entry: calm"
        if (value == "s"):
            value = "-999"
            flag = "missing"
            correctedValue = 0
            flag = "no entry: calm"
        if (flag != "missing" and flag != "instrument error" and flag != "illegible" and flag != "empty" and flag!="no entry: calm"):
            # if more than one value in entry, choose first value
            if len(value) > 1:
                values = value.split(" ")
                value = values[-1]
            if value != "0":
                if value == "P" or value == "perceptible":
                    res = "1"
                    correctedValue = "1"
            res = float(value)
            correctedValue = res
            # Check range
            if (res < 0 or res > 10):
                debugLog.write("\tTranscriptionID: " + str(transcription_id) + "Out of range: " + value +
                               " on " + result_day.strftime(dateFormat) + "\tField: " +
                               fields["id"] + " - " + fields["name"]+"\n")
                flag = 'out of range'
                correctedValue = -999
            correctedValue = "{0:.0f}".format(res)
        else:
            correctedValue = -999
            flag = 'missing'
    except ValueError:  # if value does not conform, write debug log and error type
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Invalid data: " +
                       value + " on " + result_day.strftime(dateFormat) + " Hour:" +
                       str(str(hour) + "\tField: " + fields["id"] + " - " + fields["name"] + "\n"))
    return (flag, correctedValue, error)


# DIR direction
def getDir(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
           transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    (value, error, flag, correctedValue) = cleanupValue(error_prefix, value, data_entry_id, flag)
    field_id = fields["id"]
    # Some fields contains both the direction and the speed of the wind, so here we extract the direction
    if (field_id == "177" or field_id == "178" or field_id == "179" or
            field_id == "180" or field_id == "181" or field_id == "182" or
            field_id == "183" or field_id == "184"):
        value = value.replace(",", " ")
        if value != "0":
            values = value.split(" ")  # if more than one value in entry split by space
            if values[-1].isdigit():  # if the value is a number than treat it as wind velocity
                value = values[0]
            else:
                value = values[-1]  # else it is wind direction
        else:
            value = "Calm"  # if value = 0 descriptor is "Calm"
            correctedValue = 'Calm'
    try:
        if (value == "empty" or flag == 'empty'):
            value = "0"
            correctedValue = 'Calm'
            flag = "no entry: calm"
        if (flag != "missing" and flag != "instrument error" and
                flag != "illegible" and flag != "empty"):
            if (value == "Calm" or value == "perceptible" or value == "none" or
                    value == "imp" or value == "not" in value.lower() or
                    value == "0" in value.lower()):
                correctedValue = "Calm"
            elif "variable" in value.lower():
                correctedValue = "Variable"
            elif "passing" in value.lower():
                correctedValue = "Scud"
            elif "Hidden" in value.lower():
                correctedValue = "Hidden"
        # if no extraneous text found, we will try to map the value and convert
            if keep_wind_cloud_type:
                correctedValue = im.abbr_directions[value.split()[0].lower()]
            else:
                correctedValue = im.convert_directions[value.split()[0].lower()]
        else:
            correctedValue = -999
            flag = 'missing'
    except KeyError:  # if value does not conform, write debug log and error type
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " +
                       "Invalid data: " + value + " on " + result_day.strftime(dateFormat) +
                       " Hour:" + str(hour) + "\tField: " + fields["id"] + " - " +
                       fields["name"]+"\n")
        correctedValue = -999
        flag = 'missing'
    return (flag, correctedValue, error)


# Fahrenheit
def getF(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
         transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    try:
        if (value == "-222" or value == "-888"):
            value = '-999'  # remove -888 and -222
        # find error = None common errors in temperature data
        # common signs for values not able to be recorded (instrument error, too cold, etc in cleanup)
        if ("tdb" in t or "tb" in t or "td" in t):
            (value, error, flag, correctedValue) = cleanupValue(error_prefix, value, data_entry_id, flag)
        if (value.lower() == "empty" ):
            value = "-999"
            correctedValue = "-999"
            flag = "missing"
        elif (flag != "missing" and flag != "instrument error"
                and flag != "illegible" and flag != "empty" and value != "-999" and value != "-888"
                and value != "-222" and value != "empty"  and value != "Empty"):
            from fractions import Fraction  # if value contaisn fraction
            temperature = float(sum(Fraction(s) for s in value.split()))
            if (temperature < -50 or temperature > 120):  # out of range
                debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Out of range: " + value +
                               " on " + result_day.strftime(dateFormat) + "\tField: " + fields["id"] +
                               " - " + fields["name"]+"\n")
                flag = "out of range"
            if (temperature < -45):  # low values
                flag = "low value"
            elif (temperature > 100):  # high values
                flag = "high value"
            # convert
            res = (float(temperature)-32)*5/9
            correctedValue = "{0:.2f}".format(res)
        else:
            correctedValue = -999
            flag = 'missing'
    except ValueError:  # if value does not conform, write debug log and error type
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Invalid data: " + value +
                       " on " + result_day.strftime(dateFormat) + " Hour:" + str(hour) + "\tField: " + fields["id"]
                       + " - " + fields["name"]+"\n")
        correctedValue = '-999'
        flag = "missing"
    return (flag, correctedValue, error)


# Inches e.g. precipitation
def getIn(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
          transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    try:
        if value == "-222" :
            value = -999  # remove -888 and -222
            flag ='unable to record'
        if value == "-888":
            value = -999  # remove -888 and -222
            flag ='illegible'
        if (value == "empty"):
            if (t == 'eee'):
                correctedValue = -999
                flag = "no entry"
            else:
                value = "0"
                correctedValue = 0
                flag = "no entry"
        if (flag == "empty"):
                value = "0"
                correctedValue = 0
        if (flag != "missing" and flag != "instrument error" and
                flag != "illegible" and value != -999 and flag != "no entry"
                and flag != "unable to record"):
            ress = value
            if ("in" in value.lower() or "slight" in value.lower()
                    or "meas" in value.lower() or "trace" in value.lower()):
                ress = 0.009
                flag = 'trace'
            elif "R" in ress:
                ress = ress.replace("R ", "0.009")
                flag = 'trace'
            elif "S" in ress:
                ress = ress.replace("S ", "0.009")
                flag = 'trace'
            elif (", " in ress or "|" in ress or " / " in ress):
                values = ress.split(",")
                res = 0
                for v in values:
                    res += float(v)
                    debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Two values added: " + value +
                                   " on " + result_day.strftime(dateFormat) + "\tField: " + fields["id"] +
                                   " - " + fields["name"] + "\n")
                    flag = "Two values added"
            elif "," in ress:
                ress = ress.replace(",", ".")
            elif "/" in ress:  # fraction
                try:
                    ress = ress.replace(".", " ")
                    from fractions import Fraction
                    res = float(sum(Fraction(s) for s in ress.split()))
                except ZeroDivisionError:
                    debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Invalid data: " + value +
                                   " on " + result_day.strftime(dateFormat) + " Hour:" + str(hour) +
                                   "\tField: " + fields["id"] + " - " + fields["name"] + "\n")
                    correctedValue = '-999'
                    flag = 'missing'
            res = float(ress)
            #  convert value
            res = res*25.4
            correctedValue = "{0:.2f}".format(res)

            if (res < 0 or res > 30):
                debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Out of range: " + value +
                               " on " + result_day.strftime(dateFormat) + "\tField: " + fields["id"] +
                               " - " + fields["name"]+"\n")
                flag = 'high value'
        else:
            correctedValue = -999
            flag = 'missing'
    except ValueError:  # if value does not conform, write debug log and error type
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Invalid data: " + value +
                       " on " + result_day.strftime(dateFormat) + " Hour:" + str(hour) + "\tField: " + fields["id"]
                       + " - " + fields["name"] + "\n")
        correctedValue = -999
        flag = 'missing'
    return (flag, correctedValue, error)


# LCT  lower cloud type. Conversions in iso_mapping (im). Option keep_cloud_wind_type allows for either letter codes
# (Ci, St) or Cloud Atlas types
def getLCT(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
           transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    (value, error, flag, correctedValue) = cleanupValue(error_prefix, value, data_entry_id, flag)
    try:
        if (value == "empty" or flag == "empty"):
            value = "0"
            correctedValue = "Cl0"
            flag = "no entry: clear"
        if (flag != "missing" and flag != "instrument error"
                and flag != "illegible" and flag != "empty"):
            if keep_wind_cloud_type == True:
                correctedValue = str(im.abbr_cloud[value.lower()])
                flag = "None"
            else:
                correctedValue = str(im.convertLowerCloud(value.lower()))
                flag = "None"
        else:
            correctedValue = "-999"
            debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " +
                           "Missing data: " + value + " on " + result_day.strftime(dateFormat) +
                           " Hour:" + str(hour) + "\tField: " + fields["id"] + " - " + fields["name"]+"\n")
            flag = 'missing'
    except KeyError:  # if value does not conform, write debug log and error type
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Invalid data: " +
                       value.lower() + " on " + result_day.strftime(dateFormat) +
                       " Hour:" + str(hour) + "\tField: " + fields["id"] + " - " + fields["name"]+"\n")
        correctedValue = "-999"
        flag = 'missing'
    return (flag, correctedValue, error)


# LBSFT  pounds per square foot (e.g. wind force)
def getLbsFt(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
             transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    (value, error, flag, correctedValue) = cleanupValue(error_prefix, value, data_entry_id, flag)
    try:
        if (value == "-222" or value == "-888"):
            value = '-999'  # remove -888 and -222
        if (value == "empty" or flag == "empty"):
            value = "0"
            correctedValue = 0
            flag = "no entry: calm"
        elif (flag != "missing" and flag != "instrument error" and
                flag != "illegible" and flag != "empty" and flag != "no entry: calm"):
            v = value
            if (" " in value):  # if fraction in value
                (main, remainder) = value.split()
                v = float(main) + float(remainder)/16  # 16 ounces = 1 pound
            v = float(v)
            if (v >= 0):
                vel = sqrt(float(v)/0.00256)
                res = vel*0.44704
                correctedValue = "{0:.2f}".format(res)
        else:
            correctedValue = -999
            flag = 'missing'
    except ValueError:  # if value does not conform, write debug log and error type
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Invalid data: " + value + " on " +
                       result_day.strftime(dateFormat)+" Hour:" + str(hour) + "\tField: "+fields["id"] +
                       " - " + fields["name"]+"\n")
        correctedValue = -999
        flag = 'missing'
    return (flag, correctedValue, error)


# Inches Mercury  pressure
def getInHg(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
            transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    if result_day.day==2 and result_day.month==10 and result_day.year==1870 and t=="e":
        print("found")

    if value =="-999":
        return (flag, value, "")
    flag=None
    error=None
    try:
        (value,error, flag, correctedValue)=cleanupValue(error_prefix, value, data_entry_id,flag)
        if ("\"" in str(value) or "'" in str(value) or "ill" in str(value) or value =="~" or value=="-" or value=="”"):
            correctedValue = -999
            flag="value unable to be recorded"
        else:
            v=float(str(correctedValue))
            # Handling case of pressure correction, where sometimes the dot is missing in the transcription
            if t=="e" and "." not in str(value):
                v=v/1000
            res=lmr.baro_Eng_in2mb(v)  # use value from iCoads lmrlib.py 2021.11.16
            correctedValue="{0:.2f}".format(res)
            #Some pressure values are correction data so range is different
            if (t!="e" and (v<27 or v>32)) or (t=="e" and (v<0 or v>2)):
                debugLog.write("\tTranscriptionID: "+ str(transcription_id) + " " + "Out of range: " + str(value) +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"] + "\n" )
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
        debugLog.write("\tTranscriptionID: "+ str(transcription_id) + "Invalid data: " + str(value) +" on " + result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )
        correctedValue='-999'
        flag="missing"
    return (flag, correctedValue, error)

# mm Mercury  e.g. pressure
def getmmHg(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
            transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    try:
        if (value == "-222" or value == "-888"):
            value = '-999'  # remove -888 and -222
        if (value == "empty"):
            value = "-999"
            correctedValue = -999
            flag = "missing"
        if (flag != "missing" and flag != "instrument error" and
                    flag != "illegible" and flag != "empty"):
            (value, error, flag, correctedValue) = cleanupValue(error_prefix, value, data_entry_id, flag)
            v = float(value)
            # Handling case of pressure correction, where sometimes the dot is missing in the transcription
            if t == "e" and "." not in value and v > 1:  # checking for vapour pressure. If decimal place not recorded, divide to get decimal value
                v = v/1000
            res = lmr.baro_mm2mb(v)  # use value from iCoads lmrlib.py 2021.11.16
            correctedValue = "{0:.2f}".format(res)
            # Some pressure values are correction data so range is different
            if (t != "e" and (v < 700 or v > 780)) or (t == "e" and (v < 0 or v > 5)):  # check range
                debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Out of range: " + value +
                               " on " + result_day.strftime(dateFormat) + "\tField: " + fields["id"] +
                               " - " + fields["name"] + "\n")
                flag = "out of range"
            # Flag values which are not out of range for Canada but which are still high or low
            if (t != "e" and (v < 700 and v >= -100)):
                flag = "low value"
            elif (t != "e" and (v > 740 and v <= 780)):
                flag = "none"
            elif (t != "e" and (v > 780)):
                flag = "high value"
            if (t == "e" and (v < 0.5 and v >= -100)):
                flag = "low value"
            elif (t == "e" and (v > 0.5 and v <= 5)):
                flag = "None"
            elif (t == "e" and (v > 5)):
                flag = "high value"
        else:
            correctedValue = -999
            flag = 'missing'
    except ValueError:  # if value does not conform, write debug log and error type
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + "Invalid data: " + value + " on " +
                       result_day.strftime(dateFormat) + "\tField: " + fields["id"] + " - " + fields["name"] + "\n")
        correctedValue = '-999'
        flag = "missing"
    return (flag, correctedValue, error)


# MNO
def getMNO(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
           transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    if (value == "empty" or flag == "empty"):
        value = "no data"
        correctedValue = "no data"
        flag = "no entry"
    if (flag != "missing" and flag != "instrument error" and flag != "illegible"
            and flag != "empty"):
        v = value.lower()
        # synoptic codes for weather types
        if "snow" in v:
            correctedValue = "SN"
        elif "rain" in v:
            correctedValue = "RA"
        elif "thunder" in v:
            correctedValue = "TS"
        elif "lightning" in v:
            correctedValue = "LT"
        elif "freezing drizzle" in v:
            correctedValue = "FZDZ"
        elif "freezing rain" in v:
            correctedValue = "FZRA"
        elif "hail" in v:
            correctedValue = "GR"
        elif "small hail" in v:
            correctedValue = "SHGS"
        elif "ice crystals" in v:
            correctedValue = "IC"
        elif "fog" in v:
            correctedValue = "FG"
        elif "freezing fog" in v:
            correctedValue = "FZFG"
        elif "mist" in v:
            correctedValue = "BR"
        elif "fog patches" in v:
            correctedValue = "BCFG"
        elif "shallow fog" in v:
            correctedValue = "MIFG"
        elif "blow" in v:
            correctedValue = "BLSN"
        elif "blowing dust" in v:
            correctedValue = "BLDU"
        elif "drift" in v:
            correctedValue = "DRSN"
        elif "ice pellets" in v:
            correctedValue = "PL"
        elif "driz" in v:
            correctedValue = "DZ"
        elif "shower" in v:
            correctedValue = "SH"
        elif "squal" in v:
            correctedValue = "SQ"
        elif "dust haze" in v:
            correctedValue = "DU"
        elif "haz" in v:
            correctedValue = "HZ"
        elif "smok" in v:
            correctedValue = "FU"
        elif "sleet" in v:
            correctedValue = "RN +SN +IP"
        elif "aurora" in v or "aur." in v:
            correctedValue = "AU"
        elif "parhelia" in v or "parahelia" in v:
            correctedValue = "PARHEL"
        elif "parasel" in v:
            correctedValue = "PARSEL"
        elif "halo" in v:
            correctedValue = "HALO"
        elif "corona" in v:
            correctedValue = "CORONA"
        elif "shower" in v:
            correctedValue = "SH"
        elif "sky" in v and "clear" in v:
            correctedValue = "SKC"
        elif "sky" in v and "blue" in v:
            correctedValue = "SKC"
        elif "frost" in v:
            correctedValue = "FRST"
        elif "clear clearing_weather" in v:
            correctedValue = "SKC"
        elif "clear cloudy" in v:
            correctedValue = "FRST"
        elif "clear illegible" in v:
            correctedValue = "SKC"
        elif "clear overcast" in v:
            correctedValue = "SCT"
        elif "clearing_weather" in v:
            correctedValue = "SCT"
        elif "cloudy gloomy" in v:
            correctedValue = "OVC"
        elif "cloudy illegible" in v:
            correctedValue = "BKN"
        elif "cloudy overcast" in v:
            correctedValue = "OVC"
        elif "fine" in v:
            correctedValue = "SKC"
        elif "gloomy" in v:
            correctedValue = "OVC"
        elif "overcast illegible" in v:
            correctedValue = "OVC"
        elif "cloudy" in v:
            correctedValue = "BKN"
        elif "illegible" in v:
            correctedValue = "missing"
        elif "overcast" in v:
            correctedValue = "OVC"
        elif "overcast gloomy" in v:
            correctedValue = "OVC"
        elif "overcast ugly" in v:
            correctedValue = "OVC"
        elif "clear" in v:
            correctedValue = "SKC"
        else:  # if value does not conform, write debug log and error type
            debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " +
                           "Invalid data: " + str(value) + " on " +
                           result_day.strftime(dateFormat) + " Hour:"
                           + str(hour) + "\tField: " + fields["id"] + " - " +
                           fields["name"] + "\n")
            correctedValue = '-999'
            flag = 'missing'
        # if len(correctedValue) > 90:
        #    correctedValue = correctedValue[0:90]

    return (flag, correctedValue, error)


# MPH miles per hour
def getMPH(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
           transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    (value, error, flag, correctedValue) = cleanupValue(error_prefix, value, data_entry_id, flag)
    try:
        if (value == "-222" or value == "-888"):
            value = '-999'  # remove -888 and -222
        if (value == "empty" or flag == "empty"):
            value = "0"
            correctedValue = 0
            flag = "no entry: calm"
        elif (flag != "missing" and flag != "instrument error" and
                flag != "illegible" and flag != "empty"   and flag != " no entry: calm"):
            res = float(value)/2.237
            correctedValue = "{0:.2f}".format(res)
        else:
            correctedValue = -999
            flag = 'missing'
    except ValueError:  # if value does not conform, write debug log and error type
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Invalid data: " + value + " on " +
                       result_day.strftime(dateFormat) + " Hour:" + str(hour) + "\tField: " + fields["id"] +
                       " - " + fields["name"]+"\n")
        correctedValue = -999
        flag = 'missing'
    return (flag, correctedValue, error)


# Okta cloud cover in eighths. Most historical cloud is in tenths
def getOkta(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
            transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    field_id = fields["id"]
    field_name = fields["name"]

    (value, error, flag, correctedValue) = cleanupValue(error_prefix, value, data_entry_id, flag)
    if "clearness" in field_name:  # test for clearness of sky
    # if field_id == "173" or field_id == "174" or field_id == "175" or field_id == "176":
    #
        try:
            if (value == "-222" or value == "-888"):
                value = '-999'  # remove -888 and -222
            if (value == "empty" or flag == "empty"):
                value = "0"
                correctedValue = "0"
                flag = "no entry: clear"
            if (flag != "missing" and flag != "instrument error" and
                    flag != "illegible" and flag != "empty"):
                if ("fog" in value.lower() or "smoke" in value.lower() or "haze" in value.lower()
                        or "scud" in value.lower() or "hidden" in value.lower()):
                    value = "9"
                elif value == "Zero" or "clear" in value.lower():
                    value = "0"
                res = int(value)
                # out of range test
                if (res < 0 or res > 10):
                    debugLog.write("\tTranscriptionID: " + str(transcription_id) +
                                   " " + "Out of range: " + value + " on " +
                                   result_day.strftime(dateFormat) + "\tField: " + fields["id"] +
                                   " - " + fields["name"] + "\n")
                    flag = 'out of range'
                else:
                    res = lmr.cloud_tenthsclear2oktas(res)
            else:
                correctedValue = -999
                flag = 'missing'
        except ValueError:  # if value does not conform, write debug log and error type
            debugLog.write("\tTranscriptionID: " + str(transcription_id) +
                           " " + "Invalid data: " + value + " on " + result_day.strftime(dateFormat) +
                           " Hour:" + str(hour) + "\tField: " +
                           fields["id"] + " - " + fields["name"] + "\n")
        correctedValue = -999
        flag = 'missing'

    else:

        try:
            if (value == "empty" or flag == "empty"):
                value = "0"
                correctedValue = "0"
                flag = "no entry: clear"
            if (value == "-222" or value == "-888"):
                    value = '-999'  # remove -888 and -222
            if (flag != "missing" and flag != "instrument error" and
                    flag != "illegible" and flag != "empty"):
                if ("fog" in value.lower() or "smoke" in value.lower() or "haze" in value.lower()
                        or "scud" in value.lower() or "hidden" in value.lower()):
                    value = "9"
                elif value == "Zero" or "clear" in value.lower():
                    value = "0"
                res = float(value)
                # out of range
                if (res < 0 or res > 10):
                    debugLog.write("\tTranscriptionID: " + str(transcription_id) +
                                   " " + "Out of range: " + value + " on " +
                                   result_day.strftime(dateFormat) + "\tField: " + fields["id"] +
                                   " - " + fields["name"] + "\n")
                    flag = 'out of range'
                else:
                    res = res*0.8
                correctedValue = "{0:.2f}".format(res)
            else:
                correctedValue = -999
                flag = 'missing'
        except ValueError:  # if value does not conform, write debug log and error type
            debugLog.write("\tTranscriptionID: " + str(transcription_id) +
                           " " + "Invalid data: " + value + " on " + result_day.strftime(dateFormat) +
                           " Hour:" + str(hour) + "\tField: " +
                           fields["id"] + " - " + fields["name"] + "\n")
            correctedValue = -999
            flag = 'missing'
    return (flag, correctedValue, error)


# Ozone (Oz) No known conversion
def getOz(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
          transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    (value, error, flag, correctedValue) = cleanupValue(error_prefix, value, data_entry_id, flag)
    if (value == "empty" or flag == "empty"):
        value = "-999"
        correctedValue = "-999"
        flag = "missing"
    if (flag != "missing" and flag != "instrument error" and
            flag != "illegible" and flag != "empty"):
        correctedValue = value
        flag = "None"
    else:
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + "Invalid data: " + value + " on " +
                       result_day.strftime(dateFormat) + "\tField: " + fields["id"] +
                       " - " + fields["name"] + "\n")
        correctedValue = -999
        flag = "missing"
    return (flag, correctedValue, error)


# Percentage
def getP(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
         transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    (value, error, flag, correctedValue) = cleanupValue(error_prefix, value, data_entry_id, flag)
    try:
        if (value == "-222" or value == "-888"):
            value = '-999'  # remove -888 and -222
        if (value == "empty"):
            value = "-999"
            correctedValue = "-999"
            flag = "missing"
        if (flag != "missing" and flag != "instrument error" and
                flag != "illegible" and flag != "empty"):
            res = float(value)
            if (res < 0 or res > 100):  # check range
                debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Out of range: " + value +
                               " on " + result_day.strftime(dateFormat) + "\tField: " + fields["id"] +
                               " - " + fields["name"]+"\n")
            elif (res > 0 and res <= 1):  # check if decimal instead of prercentage
                # debugLog.write("TranscriptionID: "+ str(transcription_id) + "\less than 1: " + value +" on " +
                # result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )
                res = res*100
                flag = "multiply by 100"
            correctedValue = "{0:.2f}".format(res)
        else:
            correctedValue = -999
            flag = 'missing'
    except ValueError:
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + "Invalid data: " + value + " on " +
                       result_day.strftime(dateFormat) + " Hour:" + str(hour) + "\tField: " + fields["id"] +
                       " - " + fields["name"] + "\n")
        correctedValue = '-999'
    return (flag, correctedValue, error)


# Relative humidity  check if in fraction pr precentage
def getRH(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
          transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    (value, error, flag, correctedValue) = cleanupValue(error_prefix, value, data_entry_id, flag)
    try:
        if (value == "-222" or value == "-888"):
            value = '-999'  # remove -888 and -222
        if (value == "empty" or flag == "empty"):
            value = "-999"
            correctedValue = -999
            flag = "missing"
        if (flag != "missing" and flag != "instrument error" and
                flag != "illegible" and flag != "empty"):
            res = float(value)
            if (res < 0 or res > 100):  # range for precentage data
                debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Out of range: " + value +
                               " on " + result_day.strftime(dateFormat) + "\tField: " + fields["id"] +
                               " - " + fields["name"] + "\n")
            elif (res > 0 and res <= 1):  # if value recorded as fraction instead of percentage
                # lines below removed as too many values were transformed
                # debugLog.write("TranscriptionID: "+ str(transcription_id) + "\less than 1: " + value +" on " +
                # result_day.strftime(dateFormat)+"\tField: "+fields["id"]+ " - " + fields["name"]+"\n" )
                res = res*100
                flag = "multiply by 100"
            correctedValue = "{0:.2f}".format(res)
        else:
            correctedValue = -999
            flag = 'missing'
    except ValueError:  # if value does not conform, write debug log and error type
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + "Invalid data: " + value + " on " +
                       result_day.strftime(dateFormat) + " Hour:" + str(hour) + "\tField: " + fields["id"] +
                       " - " + fields["name"] + "\n")
        correctedValue = -999
        flag = "missing"
    return (flag, correctedValue, error)


# SM  Smithsonian wind force scale (0-10)
def getSM(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
          transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    field_id = fields["id"]
    (value, error, flag, correctedValue) = cleanupValue(error_prefix, value, data_entry_id, flag)
    # Some fields contain two different data entries: wind force and direction. Here we select wind force
    if field_id == "177" or field_id == "178" or field_id == "179" or field_id == "180":
        value = value.replace(",", " ")
        # if value != "0":
        if ("." in value):
            values = value.split(".")
        else:
            values = value.split(" ")

        debugLog.write(result_day.strftime(dateFormat)+" Wind force. Values:"
                       + value + " - looking if isdigit for: " + values[-1] + "\n")
        if values[-1].isdigit():  # if both direction and force in same entry, see which value is numeric
            value = values[-1]
        else:
            value = values[0]

        if ("|" in value):
            values = value.split("|")
            value = values[-1]
        flag = 'None'

        debugLog.write("Selected wind force: " + value + "\n")
        # print("split dir, force", "force = ", value)
    try:
        if (value == "-222" or value == "-888"):
            value = '-999'  # remove -888 and -222
        if (value == "empty" or flag == "empty"):
            value = "0"
            correctedValue = 0
            flag = "no entry: calm"
        elif (flag != "missing" and flag != "instrument error" and
                flag != "illegible" and flag != "empty" and flag != "no entry: calm"):
            from fractions import Fraction
            res = float(sum(Fraction(s) for s in value.split()))
            res = int(res)
            if (res < 0 or res > 10):  # if value out of range write debug log and error type
                debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Out of range: " + value +
                               " on " + result_day.strftime(dateFormat) + "\tField: " + fields["id"] +
                               " - " + fields["name"] + "\n")
                flag = "out of range"
                correctedValue = -999
            else:
                res = im.convertSmithsonian(res)
            correctedValue = "{0:.0f}".format(res)
        else:
            correctedValue = -999
            flag = 'missing'
    except ValueError:  # if value does not conform, write debug log and error type
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " + "Invalid data: " + value + " on " +
                       result_day.strftime(dateFormat) + " Hour:" + str(hour) + "\tField: " + fields["id"] +
                       " - " + fields["name"]+"\n")
        correctedValue = -999
        flag = 'missing'
    return (flag, correctedValue, error)


# UCT upper cloud type
def getUCT(flag, unit, value, error_prefix, data_entry_id, debugLog, t,
           transcription_id, result_day, fields, hour, keep_wind_cloud_type):
    error = None
    (value, error, flag, correctedValue) = cleanupValue(error_prefix, value, data_entry_id, flag)
    try:
        if (value == "empty" or flag == "empty"):
            value = "0"
            correctedValue = "Ch0"
            flag = "no entry: clear"
        if (flag != "missing" and flag != "instrument error" and
                flag != "illegible" and flag != "empty"):
            if keep_wind_cloud_type:
                correctedValue = im.abbr_cloud[value.lower()]
            else:
                correctedValue = im.convert_clouds_upper[value.lower()]
        else:
            correctedValue = "-999"
            debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " +
                           "Missing data: " + value + " on " + result_day.strftime(dateFormat) +
                           " Hour:" + str(hour) + "\tField: " + fields["id"] + " - " + fields["name"]+"\n")
            flag = 'missing'
    except KeyError:  # if value does not conform, write debug log and error type
        debugLog.write("\tTranscriptionID: " + str(transcription_id) + " " +
                       "Invalid data: " + value + " on " + result_day.strftime(dateFormat) +
                       " Hour:" + str(hour) + "\tField: " + fields["id"] + " - " +
                       fields["name"] + "\n")
        correctedValue = '-999'
        flag = 'missing'
    return (flag, correctedValue, error)
