# some common stuff, convenient or glueing together bits&pieces


def file_exists( fnm ):

  from os import access, R_OK
  return access( fnm, R_OK )
  

def open_file( fnm, forread=True, binary=False, append=False ):
  from common import report_error

  try:

    flags = "r"
    if forread:
      if binary:
        flags = "rb"
    else:
      if binary:
        flags = "ab+" if append else "wb+"
      else:
        flags = "a+" if append else "w+"

    return open( fnm, flags )

  except Exception as e:

    if forread:
      report_error( "Cannot open " + fnm + ':' + str(e) )
    else:
      report_error( "Cannot create " + fnm + ':' + str(e) )
    return None


def open_for_read( fnm, binary=False ):
  return open_file( fnm, True, binary )
def open_for_write( fnm, binary=False, append=False ):
  return open_file( fnm, False, binary, append )


def dismiss_file( fp ):
  import sys

  if not fp:
    return

  fp.flush()
  if fp != sys.stdout and fp != sys.stderr and fp != sys.stdin:
    fp.close()


def read_file_lines( filenm ):

  lines = []
  fp = open_for_read( filenm )
  if fp:
    lines = fp.readlines()
    return [line.strip() for line in lines]
  return lines


def range_include( rg, v ):

  if rg[0] > v:
    rg[0] = v
  if rg[1] < v:
    rg[1] = v

def range_includes( rg, v ):

  return v >= rg[0] and v <= rg[1]


class NamedObj:

  def __init__( self, nm=None ):
    self.nm = nm
  def name( self ):
    return '' if self.nm is None else self.nm
  def setName( self, nm ):
    self.nm = nm


class RefDate:

  def __init__( self, startdate ):
    self.startdate = startdate

  def dateAtDay( self, nrdays ):
    from datetime import datetime, timedelta
    return self.startdate + timedelta(days=nrdays)

  def dateAtWeek( self, nrweeks ):
    from datetime import datetime, timedelta
    return self.startdate + timedelta(weeks=nrweeks)

  def nrDays( self, date ):
    from datetime import datetime, timedelta
    td = date - self.startdate
    return td.days

  def weeks( self, date ):
    return self.nrDays(date) / 7

  def nrWeeks( self, date ):
    return round( self.weeks(date) )


def putInSortedList( l, x ):
  from bisect import insort
  insort( l, x )


class SortedMultiArrBuilder:

  def __init__( self ):

    self.xs = []
    self.ys = []


  def add( self, xx, yy ):
    from bisect import bisect_left

    if xx is None or yy is None:
      return

    sz = len( self.xs )
    if sz > 0 and xx < self.xs[sz-1]:
      pos = bisect_left( self.xs, xx )
      if pos < sz:
        if self.xs[pos] == xx:
          self.ys[pos] = yy
        else:
          self.xs.insert( pos, xx )
          self.ys.insert( pos, yy )
        return pos

    self.xs.append( xx )
    self.ys.append( yy )
    return sz



if __name__ == "__main__":

  from datetime import datetime
  fmt = '%Y-%m-%d'
  dt = datetime.strptime( '2021-12-31', fmt )
  rd = RefDate( dt )
  threedayslater = rd.dateAtDay( 3 )
  twopoint8weekslater = rd.dateAtWeek( 2.8 )
  threeweekslater = rd.dateAtWeek( 3 )
  print( "Org date:", dt.strftime(fmt) )
  print( "3 days later:", threedayslater.strftime(fmt) )
  print( "2.8 weeks later:", threeweekslater.strftime(fmt) )
  print( "3 weeks later:", threeweekslater.strftime(fmt) )
  print( "nrDays: ", rd.nrDays(threedayslater) )
  print( "weeks: ", rd.weeks(twopoint8weekslater), "and", rd.weeks(threeweekslater) )
  print( "nrWeeks: ", rd.nrWeeks(twopoint8weekslater), "and", rd.nrWeeks(threeweekslater) )
