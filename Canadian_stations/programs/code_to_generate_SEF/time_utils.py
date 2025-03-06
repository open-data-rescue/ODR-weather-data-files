# -*- coding: utf-8 -*-
import datetime


def getTimeOfDay(cfg, sefType, time, date):
    if "changetimeOfDay" in cfg and cfg["changetimeOfDay"]["active"] is True:
        for timeChange in cfg["timeChanges"]:
            if sefType in timeChange["sefTypes"]:
                for change in timeChange["changes"]:
                    if (change["fromTime"] == time and
                        date >= datetime.datetime.strptime(change["fromDate"], "%Y-%m-%d") and
                            date <= datetime.datetime.strptime(change["toDate"], "%Y-%m-%d")):
                        return change["toTime"]
    return time


def getDateTimeResult(cfg, t, timeOfDay, result_day):
    utcOffset = 0
    if (timeOfDay == "mean" or timeOfDay == "total" or timeOfDay == "daily"):
        period = '24'
        hour = 0
        minute = '00'
        dateResult = ''
    elif timeOfDay == "sunrise":
        period = '0'
        hour = 6
        minute = "{0:02d}".format(int(0+60*(utcOffset-int(utcOffset))))
    else:
        period = '0'
        overridenTimeOfDay = getTimeOfDay(cfg, t, timeOfDay, result_day)
        hour = int(overridenTimeOfDay[:2])
        minute = int(overridenTimeOfDay[2:])
        # hour=hour + utcOffset
        minute = "{0:02d}".format(int(minute+60*(utcOffset-int(utcOffset))))
    result_day = result_day + datetime.timedelta(hours=hour, minutes=int(minute))
    return (result_day)


def getUTCResultDay(utcOffset, cfg, t, timeOfDay, result_day):
    if (timeOfDay == "mean" or timeOfDay == "total" or timeOfDay == "daily"):
        period = '24'
        hour = 0
        minute = '00'
    elif timeOfDay == "sunrise":
        period = '0'
        hour = 6 + utcOffset
        minute = "{0:02d}".format(int(0+60*(utcOffset-int(utcOffset))))
    else:
        period = '0'
        overridenTimeOfDay = getTimeOfDay(cfg, t, timeOfDay, result_day)
        hour = int(overridenTimeOfDay[:2])
        minute = int(overridenTimeOfDay[2:])
        hour = hour + utcOffset
        minute = "{0:02d}".format(int(minute+60*(utcOffset-int(utcOffset))))
    utc_result_day = result_day + datetime.timedelta(hours=hour, minutes=int(minute))
    return (period, utc_result_day, hour, minute)


def getUnit(cfg, unit,sefType, date):

    if "unitOverride" in cfg:
        for override in cfg["unitOverride"]:
            if override["type"] == sefType:
                fromDate = "1000-01-01"
                toDate = "2024-01-01"
                if "fromDate" in override and override["fromDate"] != "":
                    fromDate = override["fromDate"]
                if "toDate" in override and override["toDate"] != "":
                    toDate = override["toDate"]
                if (date >= datetime.datetime.strptime(fromDate, "%Y-%m-%d") and
                        date <= datetime.datetime.strptime(toDate, "%Y-%m-%d")):
                    unit = override["unit"]
    return unit
