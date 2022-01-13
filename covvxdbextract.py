# Squeeze selected info from CovidVxDB
# Thus, set sub-selections, the use go()


NrVxSeverities = 3
VxSeverity_Minor = 0
VxSeverity_Major = 1
VxSeverity_Death = 2
VxSeverity_names = ['Minor','Major','Death']


class VxCovidDBExtracter():

  def __init__( self, db ):
    from covvxdb import NrVxCovTypes, VxCovType_prettynames

    self.db = db

    # Selections
    self.dolotcount = False
    self.useweeks = True
    self.daterange = self.db.daterange
    self.agerange = self.db.agerange
    self.filterwidth = 0
    self.genders = [True, True]
    self.severities = []
    for isev in range( NrVxSeverities ):
      self.severities.append( [VxSeverity_names[isev],True] )

    self.clear()


  def clear( self ):

    self.brandcounts = None
    self.lotinfo = None


  def hasBrandCountData( self ):
  
    return self.brandcounts is not None and len( self.brandcounts ) > 0


  def hasLotCountData( self ):
  
    return self.lotinfo is not None and len( self.lotinfo ) > 0


  def tmRg( self ):

    return [self.tmNr(self.daterange[0]),self.tmNr(self.daterange[1])]


  def setDateRgFromTmRg( self, tmrg ):

      self.daterange[0] = self.dateAt( tmrg[0] )
      self.daterange[1] = self.dateAt( tmrg[1] )



  def tmVal( self, dt ):

    return self.db.refdate.weeks(dt) if self.useweeks else self.db.refdate.nrDays( dt )


  def tmNr( self, dt ):

    return self.db.refdate.nrWeeks(dt) if self.useweeks else self.db.refdate.nrDays( dt )


  def dateAt( self, tmnr ):

    return self.db.refdate.dateAtWeek(tmnr) if self.useweeks else self.db.refdate.dateAtDay(tmnr)


  def checkEv( self, ev, starttmnr, nrtmnrs ):
    from utils import range_includes

    genderreject = (not self.genders[0] and ev.ismale) or (not self.genders[1] and not ev.ismale)
    sevreject = ev.severityReject( self.severities[0][1], self.severities[1][1], self.severities[2][1] )
    agereject = not range_includes( self.agerange, ev.age )
    if genderreject or sevreject or agereject:
      return [0, True]

    tmnr = self.tmNr( ev.date ) - starttmnr
    return [tmnr, tmnr < 0 or tmnr >= nrtmnrs]


  def getCounts( self ):

    if self.dolotcount:
        self.getLotCounts()
    else:
        self.getBrandCounts()


  def getLotCounts( self ):
    from covvxdb import VxCovType_UNK
    from utils import putInSortedList

    starttmnr = self.tmNr( self.daterange[0] )
    endtmnr = self.tmNr( self.daterange[1] ) + 1
    nrtmnrs = endtmnr - starttmnr + 1
    linfo = []
    for lot in self.db.lotevents:
      evs = self.db.lotevents[lot]
      if len(evs) < 2:
        continue

      tmnrs = []
      covtyp = 0
      for ev in evs:
        [tmnr, isrejected] = self.checkEv( ev, starttmnr, nrtmnrs )
        if not isrejected:
          putInSortedList( tmnrs, tmnr )
          if len(tmnrs) == 1:
            covtyp = ev.vxtype
            if covtyp == VxCovType_UNK:
              break

      count = len( tmnrs )
      if count < 1 or covtyp == VxCovType_UNK:
        continue

      tmnrrg = [tmnrs[0], tmnrs[-1]]
      lottmnr = tmnrrg[0] if count < 2 else tmnrs[1] # protect against one wild low date

      linfo.append( [lot, covtyp, lottmnr, count, tmnrrg )

    self.lotinfo = linfo 


  def getBrandCounts( self ):
    from covvxdb import NrVxCovTypes

    bcounts = []
    starttmnr = self.tmNr( self.daterange[0] )
    endtmnr = self.tmNr( self.daterange[1] ) + 1
    for tm in range( starttmnr, endtmnr ):
      tmcounts = []
      for ityp in range( NrVxCovTypes ):
        tmcounts.append( int(0) )
      bcounts.append( tmcounts )

    nrtmnrs = len( bcounts )
    for ev in self.db.events:

      [tmnr, isrejected] = self.checkEv( ev, starttmnr, nrtmnrs )
      if not isrejected:
        bcounts[tmnr][ev.vxtype] += 1

    self.brandcounts = bcounts 
    if self.filterwidth > 0:
      self.applyBrandCountFilter()


  def applyBrandCountFilter( self ):
    from covvxdb import NrVxCovTypes

    if not self.hasBrandCountData():
      return

    orgcounts = self.brandcounts.copy()
    nrcounts = len( self.brandcounts )
    nrsamples = 2*self.filterwidth + 1
    for ityp in range( NrVxCovTypes ):
      for idx in range( nrcounts ):
        tot = 0
        for locidx in range( idx-self.filterwidth, idx+self.filterwidth ):
          useidx = locidx
          if locidx<0:
            useidx = 0
          if locidx>=nrcounts:
            useidx = nrcounts-1
          tot += orgcounts[useidx][ityp]
        self.brandcounts[idx][ityp] = round( tot/nrsamples )


  def brandCount( self, tmnr, vxtyp ):

    if not self.hasBrandCountData():
      return 0

    tmnr = tmnr - self.tmNr( self.daterange[0] )
    return 0 if tmnr<0 or tmnr>=len(self.brandcounts) else self.brandcounts[tmnr][vxtyp]


  def outputCSV( self, fp, brandcount, covtyps=None, topnr=0 ):

    from common import report_error
    from utils import SortedMultiArrBuilder
    from covvxdb import NrVxCovTypes, VxCovType_prettynames

    if not fp:
      return False

    if brandcount:
      if not self.hasBrandCountData():
        report_error( "Cannot write: no brand count data available" )
        return False
    else:
      if not self.hasLotCountData():
        report_error( "Cannot write: no lot count data available" )
        return False

    if covtyps is None:
      covtyps = []
      for covtyp in range( 1, NrVxCovTypes ):
        covtyps.append( covtyp )

    if brandcount:
      tmrg = self.tmRg()
      fp.write( 'DATE' )
      for covtyp in covtyps:
        fp.write( ','+VxCovType_prettynames[covtyp] )
      fp.write( '\n' )
      for tmnr in range( tmrg[0], tmrg[1]+1 ):
        date = self.dateAt( tmnr )
        fp.write( date.strftime('%Y-%m-%d') )
        for covtyp in covtyps:
          fp.write( ','+str(self.brandCount(tmnr,covtyp)) )
        fp.write( '\n' )
    else:
      arrbuilder = SortedMultiArrBuilder()
      for rec in self.lotinfo:
        covtyp = rec[1]
        if not covtyp in covtyps:
          continue
        lotnm = rec[0].name()
        count = rec[3]
        arrbuilder.add( count, [covtyp, lotnm] )
      fp.write( 'RANK,MANUFACTURER,LOT_ID,NUMBER_OF_ADVERSE_EVENTS\n' )
      nrrecs = len( arrbuilder.xs )
      rg_end = nrrecs
      if topnr > 0 and topnr < rg_end:
        rg_end = topnr
      for idx in range( rg_end ):
        recnr = nrrecs - idx - 1
        rec = arrbuilder.ys[recnr]
        count = arrbuilder.xs[recnr]
        fp.write( str(idx+1) + ',' + VxCovType_prettynames[rec[0]] + ',' + rec[1] + ',' + str(count) + '\n' )


if __name__ == "__main__":

  from common import initMain
  from covvxdb import VxCovidDB, NrVxCovTypes, VxCovType_prettynames
  import sys

  initMain()

  covdb = VxCovidDB.get()
  extr = VxCovidDBExtracter( covdb )
  extr.getCounts()
  extr.outputCSV( sys.stdout, True )
  extr.dolotcount = True
  extr.getCounts()
  extr.outputCSV( sys.stdout, False, 100 )
