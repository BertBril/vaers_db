# COVID info from VxDB


# Not using an IntEnum because pickle and dill choke on it.
NrVxCovTypes = 4
VxCovType_UNK = 0
VxCovType_MOD = 1
VxCovType_PFI = 2
VxCovType_JAN = 3
VxCovType_names = ['UNKNOWN MANUFACTURER','MODERNA','PFIZER\\BIONTECH','JANSSEN']
VxCovType_prettynames = ['Unknown', 'Moderna', 'Pfizer/BionTech', 'Janssen']
VxCovType_startchars = 'UMPJ'
Cov_Vx_Type = 'COVID19'


from vxobjs import VxEventBase



class VxCovidEvent( VxEventBase ):


  def __init__( self ):

    VxEventBase.__init__( self, 0 )
    self.vxtype = VxCovType_UNK
    self.lot = None


  def __init__( self, vxev ):

    VxEventBase.__init__( self, vxev.id )
    self.__dict__.update( vxev.__dict__ )
    brand = vxev.brands[0]
    self.lot = None
    for lot in brand.lots:
      if lot.hasID( self.id ):
        self.lot = lot
        break
    self.vxtype = VxCovType_startchars.find( brand.producer.name()[0] )
    if self.vxtype < 0 or self.vxtype >= NrVxCovTypes:
      self.vxtype = 0


  def dump( self ):

    VxEventBase.dump( self )
    lotnm = '<None>' if self.lot is None else self.lot.name()
    print( "\tType:", VxCovType_names[self.vxtype], "Lot:", lotnm )


class VxCovidDB():

  def __init__( self ):

    self.events = []
    self.id2event = {}
    self.lotevents = {}
    self.refdate = self.daterange = self.agerange = None


  def get():

    from common import pr_dbg, pr_dbgline
    from utils import file_exists
    ret = None

    if ( file_exists(VxCovidDB.dillFileName()) ):
      pr_dbg( 'Reading fast access COVID-only database ...' )
      ret = VxCovidDB.readDilled()

    if ret is not None:
      pr_dbgline( " done." )
    else:
      ret = VxCovidDB.buildFromFull()
      ret.writeDilled()

    return ret


  @staticmethod
  def dillFileName():

    from common import dataFile
    return dataFile( "covvxdb.bin" )


  @staticmethod
  def readDilled():

    from utils import open_for_read
    ret = None
    fp = open_for_read( VxCovidDB.dillFileName(), True )
    if fp is None:
      return ret

    import dill
    try:
      ret = dill.load( fp );
    except:
      pass
    fp.close()
    return ret


  def writeDilled( self ):

    from common import report_error
    from utils import open_for_write
    ret = False
    fp = open_for_write( VxCovidDB.dillFileName(), True )
    if fp is None:
      return ret

    import dill
    try:
      dill.dump( self, fp )
      ret = True
    except Exception as e:
      report_error( str(e) )
      ret = False
    fp.close()
    return ret


  @staticmethod
  def buildFromFull():

    from vxdb import VxDB
    from common import pr_dbg, pr_dbgline
    from utils import file_exists, RefDate
    from datetime import datetime
    global Cov_Vx_Type

    ret = VxCovidDB()
    vxdb = VxDB.get()
    if not vxdb:
      return None

    pr_dbgline( "\nScanning the entire input database into COVID-only data, which will be cached." )
    pr_dbgline( "That cache will take only seconds to read." )

    cov_type = None
    for type in vxdb.types:
      if type.name() == Cov_Vx_Type:
        cov_type = type
        break

    # Create VxCovidEvent's, i.e. mostly figure out the lot for each event
    nrevs = len( vxdb.events )
    pr_dbgline( 'Determining the lot for each event:' )

    nov_1_2020 = datetime( year=2020, month=11, day=1 )
    evnr = 1
    for vxev in vxdb.events:
      if vxev.brands[0].type == cov_type:
        covev = VxCovidEvent( vxev )
        if covev.date > nov_1_2020:
          ret.events.append( covev )
      if evnr % 50000 == 0:
        promille = round(evnr*1000.0) // nrevs
        pr_dbgline( str(promille//10)+'.'+str(promille%10)+'%' )
      elif evnr % 5000 == 0:
        pr_dbg( '.' )
      evnr += 1

    ret.determineRanges()
    ret.refdate = RefDate( ret.daterange[0] )

    # Create lot events lookup table
    for event in ret.events:
      ret.id2event[ event.id ] = event
      levs = ret.lotevents.get( event.lot )
      if levs is None:
        ret.lotevents[ event.lot ] = [ event ]
      else:
        levs.append( event )

    pr_dbgline( "\nScanning done, storing cache as: " + VxCovidDB.dillFileName() )
    pr_dbgline( "If you obtain new data, remove all .BIN files to ensure re-scan." )

    return ret


  def determineRanges( self ):
    from utils import range_include

    isfirst = True
    for covev in self.events:
      if isfirst:
        self.agerange = [covev.age,covev.age]
        self.daterange = [covev.date,covev.date]
        isfirst = False
      else:
        range_include( self.agerange, covev.age )
        range_include( self.daterange, covev.date )


if __name__ == "__main__":

  from common import initMain, setDebugLevel
  initMain()
  setDebugLevel( 2 )

  covdb = VxCovidDB.get()
  print( "Number of COV events:", len(covdb.events) )
  print( "Number of lots:", len(covdb.lotevents) )
