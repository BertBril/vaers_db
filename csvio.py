# VAERS .csv is a variant that MAY have double quotes around strings.
# It will only have that if there is a comma in the string


VAERS_CSV_FIELD_SEP = ','
VAERS_CSV_STRING_QUOTE = '"'


def readVaersCSVFileLines( type, year ):
  from common import dataFile
  from utils import read_file_lines

  return read_file_lines( dataFile(str(year) + 'VAERS' + type + '.csv') )


def parseVaersCSVFileLines( lines ):

  wordsets = []

  for line in lines:

    inquotes = False
    words = []
    word = ""

    for char in line:
      if char == VAERS_CSV_STRING_QUOTE:
        inquotes = not inquotes
      else:
        if inquotes or char != VAERS_CSV_FIELD_SEP:
          word += char
        elif not inquotes:
          words.append( word )
          word = ""

    words.append( word )
    wordsets.append( words )

  return wordsets


def getVaersCSVData( type, year ):

  lines = readVaersCSVFileLines( type, year )
  return parseVaersCSVFileLines( lines ) if lines else None
