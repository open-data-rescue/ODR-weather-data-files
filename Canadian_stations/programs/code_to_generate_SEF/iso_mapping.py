# -*- coding: utf-8 -*-

def convertUpperCloud(cloud):
    value = cloud.lower()
    if "cumulo" in value and "nimbus" in value:
        return "Cl9"
    elif "cumulo" in value and "stratus" in value:
        return "Cm7"
    elif "cirr" in value and "cumul" in value:
        return "Cm8"
    elif "cirr" in value and "strat" in value:
        return "Ch8"
    elif "cirr" in value:
        return "Ch9"
    elif "strat" in value:
        return "Ch8"
    elif "nimb" in value:
        return "Cm2"
    elif "cumul" in value:
        return "Ch9"
    elif "scud" in value or "passing" in value:
        return "Cm4"
    elif ("obscured" in value or "hidden" in value or "fog" in value or "haz" in value or "smoke" in value
          or "mist" in value or "overcast" in value):
        return "Ch/"
    elif ("-" in value or "clear" in value or "none apparent" in value or "0" in value or "imp" in value):
        return "Ch0"
    return "-999"


def convertLowerCloud(cloud):
    value = cloud.lower()
    if "cumul" in value and "nimb" in value:
        return "Cl9"
    elif "cumul" in value and "strat" in value:
        return "Cl4"
    elif "nimb" in value and "strat" in value:
        return "Cm2"
    elif "nimb" in value:
        return "Cl7"
    elif "cirr" in value:
        return "Ch6"
    elif "strat" in value:
        return "Cl6"
    elif "cumul" in value:
        return "Cl2"
    elif "scud" in value or "passing" in value:
        return "Cl5"
    elif ("obscured" in value or "hidden" in value or "fog" in value or "haz" in value or "smoke" in value
          or "mist" in value or "vapour" in value or "overcast" in value):
        return "Cl/"
    elif ("-" in value or "clear" in value or "none apparent" in value or "0" in value or "imp" in value):
        return "Cl0"
    return "-999"


def convertBeauforttext(wf):
    value = wf.lower()
    if "gale" in value:
        if "near" in value:
            return 15.4
        elif "strong" in value:
            return 22.6
        else:
            return 19
    elif "storm" in value:
        if "violent" in value:
            return 30.9
        else:
            return 26.8
    elif "hurricane" in value:
        return 35.
    elif "calm" in value:
        return 0
    elif "air" in value:
        return 1
    elif "light" in value:
        return 2.6
    elif ("gentle" in value or "modest" in value):
        return 4.6
    elif "moderate" in value:
        return 6.7
    elif "fresh" in value:
        return 9.3
    elif "strong" in value:
        return 12.3
    else:
        return -999


def convertBeaufort(wf):
    value = int(wf)
    if value == 0:
        return 0
    elif value == 1:
        return 1
    elif value == 2:
        return 2.6
    elif value == 3:
        return 4.6
    elif value == 4:
        return 6.7
    elif value == 5:
        return 9.3
    elif value == 6:
        return 12.3
    elif value == 7:
        return 15.4
    elif value == 8:
        return 19
    elif value == 9:
        return 22.6
    elif value == 10:
        return 26.8
    elif value == 11:
        return 30.9
    elif value == 12:
        return 35
    else:
        return (-999)


def convertSmithsonian(wf):
    value = int(wf)
    if value == 0:
        return 0
    elif value == 1:
        return 1  # 2mph /2.237
    elif value == 2:
        return (float(4/2.237))
    elif value == 3:
        return (float(12/2.237))
    elif value == 4:
        return (float(25/2.237))
    elif value == 5:
        return (float(35/2.237))
    elif value == 6:
        return (float(45/2.237))
    elif value == 7:
        return (float(60/2.237))
    elif value == 8:
        return (float(75/2.237))
    elif value == 9:
        return (float(90/2.237))
    elif value == 10:
        return (float(100/2.237))
    else:
        return (-999)


#  map to convert directions to iso - key should be lower case
convert_directions = {
    "north": 0,
    "north by east": 11.25,
    "north-north-east": 22.5,
    "northeast by north": 33.75,
    "north-east": 45,
    "northeast by east": 56.25,
    "east-north-east": 67.5,
    "east by north": 78.75,
    "east": 90,
    "east by south": 101.25,
    "east-south-east": 112.5,
    "southeast by east": 123.75,
    "south-east": 135,
    "southeast by south": 146.25,
    "south-south-east": 157.5,
    "south by east": 168.75,
    "south": 180,
    "south by west": 191.25,
    "south-south-west": 202.5,
    "southwest by south": 213.75,
    "south-west": 225,
    "southwest by west": 236.25,
    "west-south-west": 247.5,
    "west by south": 258.75,
    "west": 270,
    "west by north": 281.25,
    "west-north-west": 292.5,
    "northwest by west": 303.75,
    "north-west": 315,
    "northwest by north": 326.25,
    "north-north-west": 337.5,
    "north by west": 348.75,
    "hidden": -999}


# map to convert directions to abbreviation - key should be lower case
abbr_directions = {
    "north": "N",
    "north by east": "NbyE",
    "north-north-east": "NNE",
    "northeast by north": "NEbyN",
    "northeast by east": "NEbyE",
    "north-east": "NE",
    "east-north-east": "ENE",
    "east by north": "EbyN",
    "east": "E",
    "east by south": "EbyS",
    "east-south-east": "ESE",
    "southeast by east": "SEbyE",
    "south-east": "SE",
    "southeast by south": "SEbyS",
    "south-south-east": "SSE",
    "south by east": "SbyE",
    "south": "S",
    "south by west": "SbyW",
    "south-south-west": "SSW",
    "southwest by south": "SWbyS",
    "south-west": "SW",
    "southwest by west": "SWbyW",
    "west-south-west": "WSW",
    "west by south": "WbyS",
    "west": "W",
    "west by north": "WbyN",
    "west-north-west": "WNW",
    "northwest by west": "NWbyW",
    "north-west": "NW",
    "northwest by north": "NwbyN",
    "north-north-west": "NNW",
    "north by west": "NbyW",
    "calm": "C",
    "0": "C",
    "hidden": "N/A"
}


convert_clouds_upper = {"cirrus": "Ch6",
                        "cirrostratus": "Ch8",
                        "cirro-stratus": "Ch8",
                        "cirro-cumulus": "Cm8",
                        "nimbostratus": "Cm2",
                        "cumulonimbus": "Cl9",
                        "stratus": "Ch8",
                        "nimbus": "Cm2",
                        "cumulostratus": "Cm7",
                        "cumulonimbus": "Cl9",
                        "cumulus": "Ch9",
                        "passing": "Cm4",
                        "scud": "Cm4",
                        "obscured": "Ch/",
                        "hidden": "Ch/",
                        "mist": "Ch/",
                        "fog": "Ch/",
                        "haze": "Ch/",
                        "hazy": "Ch/",
                        "smoke": "Ch/",
                        "?": "Ch/",
                        "clear": "Ch0",
                        "none apparent": "C10",
                        "0": "Ch0"
                        }


convert_cloud_lower = {"cirrus": "Ch6",
                       "stratus cirro-stratus": "Ch8 Cl6",
                       "stratus cirrus": "Ch8 Cl6",
                       "stratus cumulonimbus": "Ch6 Ch8 Cl4",
                       "cirro-stratus": "Ch8",
                       "cirrostratus": "Ch8",
                       "cirro-cumulus": "Cm8",
                       "cirro-cumulus illegible": "Ch9",
                       "cirrocumulus": "Ch9",
                       "nimbostratus": "Cm2",
                       "stratus": "Cl6",
                       "nimbus": "Cl7",
                       "cumulo-stratus": "Cl4",
                       "cumulostratus": "Cl4",
                       "cumulonimbus": "Cl9",
                       "cumulus cirro-stratus": "C12, Ch8",
                       "cumulus": "Cl2",
                       "passing": "Cl2",
                       "scud": "Cl5",
                       "hidden": "Cl/",
                       "obscured": "Cl/",
                       "mist": "Cl/",
                       "fog": "Cl/",
                       "haze": "Cl/",
                       "hazy": "Cl/",
                       "smoke": "Cl/",
                       "overcast": "Cl7",
                       "?": "Cl/",
                       "0": "Cl0",
                       "clear": "Cl0",
                       "none apparent": "C10",
                       "imp": "Cl0"
                       }


abbr_cloud = {"cirrus": "Ci",
              "cirro-stratus": "CiSt",
              "cirro-cumulus": "CiCu",
              "stratus": "St",
              "nimbus": "Ni",
              "nimbostratus": "NiSt",
              "cumulo-stratus": "CuSt",
              "cirrostratus": "CiSt",
              "cirrocumulus": "CiCu",
              "cirro-cumulus": "CiCu",
              "cumulonimbus": "CuNi",
              "cumulus": "Cu",
              "overcast": "NiSt",
              "passing": "P",
              "scud": "Sc",
              "hidden": "Hi",
              "obscured": "Hi",
              "mist": "Ms",
              "fog": "Fg",
              "haze": "Hz",
              "hazy": "Hz",
              "smoke": "Sm",
              "clear": "Cl",
              "0": "Cl"
              }

# weather: R =rain, D =drizzle, F = foggy, Gloomy = cloudy
weather = {"dull": "cloudy",
           "gloomy": "cloudy",
           "fair": "clear",
           "r": "rain",
           "d": "drizzle",
           "f": "fog",
           "s": "snow",
           "sh": "shower",
           "sn sh": "snow shower"
           }


# define unit translation
map_unit = {"F": "C",
            "inHg": "hPa",
            "in": "mm",
            "okta": "okta",
            "dir": "deg",
            "direction": "deg",
            "lct": "cloudatlas",
            "uct": "cloudatlas",
            "Sm": "mps",
            "Bf": "mps",
            "p": "%",
            "%": "%",
            "cloudtext": "none",
            "cloudtype": "cloudatlas",
            "mno": "manual observation",
            "cloudvel": "0-10",
            "hcv": "0-10",
            "cv": "0-10",
            "hr": "hour",
            "tenths": "tenths",
            "tenth": "tenths",
            "abb": "1-10",
            "hh:mm": "none",
            "text": "none",
            "du": "du",
            "RE_scale": "Beaufort",
            "mph": "mps",
            "lbsft": "mps",
            "oz": "scale",
            "scale": "scale"
            }
