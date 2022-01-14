# some common stuff, convenient or glueing together bits&pieces


DATA_DIRECTORY = 'data'
DEBUG_LEVEL = 1           # 0 is none, 2 is high
YEARS_HANDLED = [2020, 2021]


def homeDir():
  from os import path

  return path.expanduser( '~' )


def baseDir():
  from os import getenv, path
  val = getenv('VX_PY_BASE_DIR')
  if not val:
    import sys
    return path.dirname( path.realpath(sys.argv[0]) )
  return val


def userDataDir():
  from os import getenv

  val = getenv('VX_PY_USER_DATA_DIR')
  if not val:
    val = homeDir()
  return val


def report_error( inp ):

  print( inp )


def setDebugLevel( lvl ):

  global DEBUG_LEVEL
  DEBUG_LEVEL = lvl


def pr_dbg( inp, lvl=1, addnl=False ):
  from sys import stdout

  if DEBUG_LEVEL >= lvl:
    if addnl:
      print( inp )
    else:
      print( inp, end=' ' )
      stdout.flush()


def pr_dbgline( inp, lvl=1 ):

  pr_dbg( inp, lvl, True )


def runningInDebugger():

  import sys
  gettrace = getattr( sys, 'gettrace', None )
  return True if gettrace is None else False


def setDataDirectory( dir ):

  global DATA_DIRECTORY
  DATA_DIRECTORY = dir


def dataPath():

  from os import path
  return path.join( baseDir(), DATA_DIRECTORY )


def dataFile( fnm ):

  from os import path
  return path.join( dataPath(), fnm )


def initMain():

  import sys
  if len(sys.argv) > 1:
    if sys.argv[1] == 'd' or sys.argv[1] == 'D':
      setDebugLevel( 2 )
      setDataDirectory( 'testdata' )
      del sys.argv[1] # remove this arg


if __name__ == "__main__":

  initMain()
  print( "Data path="+dataPath() )
