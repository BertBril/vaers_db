# Vx database. Collects the VAERS data
# - From the CSV file (initial fill, slow)
# - From imported json (fast)
# to refresh (new data) just remove the vxdb.json file

from vxobjs import VxProducer, VxType, VxLot, VxBrand, VxEventBase


class VxEvent( VxEventBase ):


  def __init__( self, id, brands ):

    VxEventBase.__init__( self, id )
    self.brands = brands


  def lot( self, brandidx ):

    if self.brands is None:
      return None
    brand = self.brands[brandidx]
    for lot in brand.lots:
      if self.id in lot.ids:
        return lot
    return None


  def dump( self ):

    VxEventBase.dump( self )
    for idx in range( len(self.brands) ):
      lt = self.lot( idx )
      br = self.brands[idx]
      print( "\tVax:", br.type.name(), '('+br.name()+')', 'lot:', lt.name() )


class VxDB:


  def __init__( self ):
    import re

    self.producers = []         # all VxProducer's
    self.types = []             # all VxType's
    self.brands = []            # all VxBrand's
    self.events = []            # all VxEvent's
    self.id2brands = {}         # ID -> [VxBrand]
    self.id2event = {}          # ID -> VxEvent

    # stats, filled at end
    self.daterange = self.agerange = None

    unk_patterns = [ r'.*UNK.*', r'.*DONT.*', r'.*DONOT.*', r'.*NOT .*', r'.*NONE.*', r'N/A.*', r'.*NUMBER.*' ]
    remove_patterns = [ r'\s+', r'[?\'-()*+.]+', r'.*[#:]', r'[/;].*', r'PFIZER', r'JANSSEN', r'MODERNA' ]
    all_unk_patterns = r'|'.join(map(r'(?:{})'.format, unk_patterns))
    all_remove_patterns = r'|'.join(map(r'(?:{})'.format, remove_patterns))
    self.unk_re = re.compile( all_unk_patterns )
    self.remove_re = re.compile( all_remove_patterns )

    self.nobrand_re = re.compile( '.*no brand.*', re.IGNORECASE )
    self.uknown_str = "Unknown"


  @staticmethod
  def get():
    from common import pr_dbg, pr_dbgline
    from utils import file_exists

    ret = None
    if ( file_exists(VxDB.dillFileName()) ):
      pr_dbg( 'Reading fast access Vx database ...' )
      ret = VxDB.readDilled()

    if ret is not None:
      pr_dbgline( ' done.' )
    else:
      ret = VxDB()
      ret.buildFromFiles()
      ret.collectStats()
      ret.writeDilled()
    return ret



  def findProducer( self, nm ):
    
    for pr in self.producers:
      if pr.name() == nm:
        return pr
    return None


  def findType( self, nm ):
    
    for typ in self.types:
      if typ.name() == nm:
        return typ
    return None


  def findBrand( self, nm ):
    
    for brand in self.brands:
      if brand.name() == nm:
        return brand
    return None


  @staticmethod
  def dillFileName():

    from common import dataFile
    return dataFile( "vxdb.bin" )


  @staticmethod
  def readDilled():

    from utils import open_for_read
    ret = None
    fp = open_for_read( VxDB.dillFileName(), True )
    if fp is None:
      return ret
    import dill
    try:
      ret = dill.load( fp );
    except:
      pass
    return ret


  def writeDilled( self ):

    from common import report_error
    from utils import open_for_write
    fp = open_for_write( VxDB.dillFileName(), True )

    import dill
    ret = False
    try:
      dill.dump( self, fp )
      ret = True
      fp.close()
    except Exception as e:
      report_error( str(e) )
      ret = False
    return ret


  def buildFromFiles( self ):

    from os import path
    from csvio import getVaersCSVData
    from common import pr_dbg, pr_dbgline, YEARS_HANDLED

    pr_dbgline( '\nHandling the VAERS .CSV files to create a cache. This will take a lot of time.' )
    pr_dbgline( 'Note that reading next time (from the cache) will be incomparably much faster (a few seconds).' )

    pr_dbg( '\nHandling .CSV files (\'VAX\'): ' )
    for year in YEARS_HANDLED:
      yearstr = str( year )
      pr_dbg( yearstr + ' ...' )
      data = getVaersCSVData( 'VAX', yearstr )
      self.addVxFileData( data )
    pr_dbg( 'processing ...' )
    self.handleVxUnknowns()
    self.createBrandFinder()
    pr_dbgline( ' done.' )

    pr_dbg( 'Handling .CSV files (\'DATA\'): ' )
    for year in YEARS_HANDLED:
      yearstr = str( year )
      pr_dbg( yearstr + ' ...' )
      data = getVaersCSVData( 'DATA', yearstr )
      self.addEventFileData( data )
    pr_dbg( 'processing ...' )
    self.createEventFinder()
    self.splitUnknownLotsByDate()
    pr_dbgline( ' done.' )

    pr_dbgline( '\nCache created, storing into: ' + VxDB.dillFileName() )
    pr_dbgline( 'If you obtain new .CSV files, remove this .BIN file to force re-build.' )


  def parseID( self, fld ):
    
    while fld and fld[0] == '0':
      fld = fld[1:]
    return int(fld) if fld else 0


  def addVxFileData( self, data ):

    for flds in data[1:]:
      id = self.parseID( flds[0] )
      vals = flds[1:]
      self.handleVxScanData( id, vals[0], vals[1], vals[6], vals[2] )


  def addEventFileData( self, data ):

    previd = 0
    for flds in data[1:]:
      id = self.parseID( flds[0] )
      if id == 0:
        continue
      if id == previd:
        from common import report_error
        report_error( "Duplicate ID found: " + str(id) );
        continue
      vals = flds[1:]
      self.handleEventScanData( id, vals )
      previd = id


  def handleVxScanData( self, id, typnm, prnm, brandnm, lotnm ):
    import re

    if prnm == 'SMITHKLINE BEECHAM':
      prnm = 'GLAXOSMITHKLINE BIOLOGICALS'
    elif self.unk_re.match( prnm.upper() ):
      prnm = self.uknown_str

    producer = self.findProducer( prnm )
    if producer is None:
      producer = VxProducer( prnm )
      self.producers.append( producer )

    if self.unk_re.match( typnm.upper() ):
      typnm = self.uknown_str
    type = self.findType( typnm )
    if type is None:
      type = VxType( typnm )
      self.types.append( type )

    brandnm_upp = brandnm.upper()
    if self.unk_re.match( brandnm_upp ) or self.nobrand_re.match( brandnm_upp ):
      brandnm = self.uknown_str
    brand = self.findBrand( brandnm )
    if brand is None:
      brand = VxBrand( producer, type, brandnm )
      self.brands.append( brand )

    lotnm = lotnm.upper()
    if self.unk_re.match( lotnm ):
      lotnm = self.uknown_str
    else:
      lotnm = self.remove_re.sub( '', lotnm )
    lot = brand.findLot( lotnm )
    lot.ids.add( id )


  def guessIsMale( self, code ):

    # Safe space violation warning: this code is non-woke, maybe even sexist.
    if code == 'M':
      return True
    elif code == 'F':
      return False
    from random import choice
    return choice( [True,False] )


  def guessIsSevere( self, vals ):

    # L_THREAT, ER_VISIT, HOSPITAL, DISABLE, BIRTH_DEFECT, ER_ED_VISIT
    for idx in [8, 10, 11, 12, 15, 30, 32]:
      v = vals[idx]
      if len(v) > 0:
        return True

    recov = vals[16]
    return recov and recov[0] == 'N' # Not recovered? That's serious.


  def determineVxDate( self, vals ):

    datestr = vals[17] # VAX_DATE, filled about 87%
    if len(datestr) < 1:
      datestr = vals[0] # RECVDATE, filled 100%

    # date fmt is MM/DD/YYYY
    from datetime import datetime
    return datetime.strptime( datestr, '%m/%d/%Y' )


  def determineAge( self, age, age2 ):

    iage = round( float(age) ) if age else -1
    if iage < 0:
      iage = round( float(age2) ) if age2 else -1
    return iage if iage >= 0 else 50


  def handleEventScanData( self, id, vals ):

    brands = self.id2brands.get( id )
    if brands is None:
      return

    event = VxEvent( id, brands )
    event.date = self.determineVxDate( vals )
    from datetime import datetime
    from common import YEARS_HANDLED
    if event.date > datetime.today() or event.date.year < YEARS_HANDLED[0] or event.date.year > YEARS_HANDLED[-1]:
      from common import pr_dbgline
      pr_dbgline( 'Skipping date: ' + event.date.strftime("%Y-%m-%d") + ' (ID=' + str(id) + ')', 2 )
    else:
      event.state = vals[1]
      event.age = self.determineAge( vals[2], vals[3] )
      event.ismale = self.guessIsMale( vals[5][0] )
      event.isdeath = len( vals[8] ) > 0
      event.issevere = event.isdeath or self.guessIsSevere( vals )
      self.events.append( event )


  def handleVxUnknowns( self ):
    from common import pr_dbgline

    toremove = []
    unkproducer = self.findProducer( "UNKNOWN MANUFACTURER" )
    for unkbrand in self.brands:
      if unkbrand.producer != unkproducer:
        continue

      # will redistribute only if there is a single other producer of this type
      nrfound = 0
      adoptingbrand = None
      nradopters = 0
      for candidatebrand in self.brands:
        if candidatebrand.producer == unkproducer:
          continue
        if candidatebrand.type == unkbrand.type:
          nradopters += 1
          adoptingbrand = candidatebrand
      if nradopters < 1:
        pr_dbgline( 'Cannot place ' + unkbrand.name() + ': no candidates for ' + unkbrand.type.name(), 2 )
      if nradopters == 1:
        pr_dbgline( 'Adding \'unknown\' ' + unkbrand.name() + ' to ' + adoptingbrand.name(), 2 )
        for lot in unkbrand.lots:
          adoptinglot = adoptingbrand.findLot( lot.name() )
          if adoptinglot is None:
            adoptingbrand.lots.append( lot )
          else:
            adoptinglot.ids.update( lot.ids )
        toremove.append( unkbrand );
      if nradopters > 1:
        pr_dbgline( 'Cannot place ' + unkbrand.name() + ': multiple candidates for ' + unkbrand.type.name(), 2 )

    for torembrand in toremove:
      self.brands.remove( torembrand )


  def createBrandFinder( self ):

    for brand in self.brands:
      for lot in brand.lots:
        for id in lot.ids:

          rec = self.id2brands.get( id )
          if rec is None:
            self.id2brands[ id ] = [brand]
          else:
            rec.append( brand )


  def splitUnknownLotsByDate( self ):

    for brand in self.brands:
      for lot in brand.lots:
        if lot.name() != self.uknown_str:
          continue

        for id in lot.ids:
          ev = self.id2event.get( id )
          if ev:
            newlotnm = (self.uknown_str + '@' + ev.date.strftime( "%b_%-d_%y" )).lower()
            targetlot = brand.findLot( newlotnm )
            targetlot.ids.add( id )

        brand.lots.remove( lot )


  def createEventFinder( self ):

    self.id2event = {}
    for event in self.events:
      self.id2event[ event.id ] = event


  def collectStats( self ):
    from utils import range_include

    first_rec = True
    for ev in self.events:
    
      if first_rec:
        self.daterange = [ev.date, ev.date]
        self.agerange = [ev.age, ev.age]
        first_rec = False
      else:
        range_include( self.daterange, ev.date )
        range_include( self.agerange, ev.age )


if __name__ == "__main__":

  from common import initMain, setDebugLevel
  initMain()
  setDebugLevel( 2 )

  vxdb = VxDB().get()
  print( 'Number of vaccination types:', len(vxdb.types) )
  print( 'Number of events:', len(vxdb.events) )
  print( 'Date range: ['+vxdb.daterange[0].strftime("%Y-%m-%d")+', '+vxdb.daterange[1].strftime("%Y-%m-%d")+']' )
  print( 'Age range:', vxdb.agerange )
