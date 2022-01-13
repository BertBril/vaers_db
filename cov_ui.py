import qt


class uiVxCovidDB( qt.MainWindow ):


  def __init__( self, useweeks, parent=None ):
    from covvxdb import VxCovidDB, NrVxCovTypes, VxCovType_prettynames
    from covvxdbextract import VxCovidDBExtracter

    qt.MainWindow.__init__( self, parent )

    self.layout = qt.BoxLayout( True )
    mainframe = qt.Frame( self, self.layout )
    self.setCentralWidget( mainframe )
    self.setWindowTitle( 'VAERS Data Analysis (Covid)' )
    self.width = 2200; self.height = 1300
    self.selfldwidth = 250; self.selfldheight = 60

    self.db = VxCovidDB.get()
    self.extracter = VxCovidDBExtracter( self.db )
    self.extracter.useweeks = useweeks
    self.extracter.dolotcount = False
    self.globdefnrevs = 20000 if self.useWeeks() else 4000
    self.lotdefnrevs = 6000
    self.nrevsrange = [0, self.globdefnrevs]
    self.types = []
    for itype in range( NrVxCovTypes ):
      self.types.append( [VxCovType_prettynames[itype],True] )

    self.createPlot()
    self.createControls()

    self.setGeometry( 500, 500, self.width, self.height )


  def useWeeks( self ):

      return self.extracter.useweeks


  def lotCountMode( self ):

    return self.extracter.dolotcount


  def createPlot( self ):
    from pointplot import PointPlot
    from datetime import datetime

    pltlayout = qt.BoxLayout( False )
    self.layout.addLayout( pltlayout, 1 )
    wdth = round( self.width*0.8 )

    tmrg = self.extracter.tmRg()
    self.pp = PointPlot( 'Adverse effects in time', tmrg[0], tmrg[1], self.nrevsrange[0], self.nrevsrange[1] )
    self.pp.qObj().setGeometry( 0, 0, wdth, self.height )
    pltlayout.addWidget( self.pp.qObj(), 1 )

    for covtyp in range( 1, len(self.types) ):
      nm = self.types[covtyp][0]
      col = qt.StdLineColor( covtyp-1 )
      self.pp.addCurve( nm, col )
      ss = self.pp.addScatter( nm, col )
      ss.clicked.connect( self.pointClicked )
      ss.setVisible( False )

    def addMonthMarker( self, yr, mnth ):
      from datetime import datetime
      from utils import range_includes
      dt = datetime( yr, mnth, 1 )
      if yr == 2022 or range_includes( self.db.daterange, dt ):
        dstr = dt.strftime( '%Y-%m-%d' )
        col = '#cccccc'
        if mnth % 3 == 1:
          col = '#aaaacc'
          if mnth % 12 == 1:
            col = '#0000aa'
        self.pp.addFlatLine( dstr, False, self.extracter.tmVal(dt), [0,100000], col )

    for yr in range( 2020, 2022 ):
      for mnth in range( 1, 13 ):
        addMonthMarker( self, yr, mnth )
    addMonthMarker( self, 2022, 1 )


  def addLabel( self, txt, wdth, vpos, lyo, hpos=0 ):

    lbl = qt.Label( txt, False )
    lbl.setFixedWidth( wdth )
    lyo.addWidget( lbl, vpos, hpos )
    return lbl


  def addCheckBox( self, txt, xpos, ypos, lyo, callback=None, checked=True ):

    cb = qt.CheckBox( txt, callback )
    cb.setFixedSize( self.selfldwidth, self.selfldheight )
    cb.setChecked( checked )
    lyo.addWidget( cb, ypos, xpos )
    return cb


  def addCountModeSel( self, parentlayout, ypos ):

    lyo = qt.GridLayout()
    parentlayout.addLayout( lyo, ypos, 1 )
    cbcount = self.addCheckBox( 'Summed count', ypos, 0, lyo, self.globCountModeSel )
    cblot = self.addCheckBox( 'Per-Lot count', ypos, 1, lyo, self.lotCountModeSel, False )
    return [cbcount, cblot]


  def addGenderFlds( self, parentlayout, ypos ):

    lyo = qt.BoxLayout( True )
    parentlayout.addLayout( lyo, ypos, 1 )
    def addCB( txt ):
      cb = qt.CheckBox( txt )
      cb.setFixedSize( self.selfldwidth, self.selfldheight )
      cb.setChecked( True )
      lyo.addWidget( cb )
      return cb

    cbmale = addCB( "Male" )
    cbfemale = addCB( "Female" )
    return [cbmale, cbfemale]


  def addLineEdit( self, lyo ):

    le = qt.LineEdit()
    le.setFixedSize( self.selfldwidth, self.selfldheight )
    lyo.addWidget( le )
    return le


  def addRangeFlds( self, parentlayout, ypos, rg ):

    lyo = qt.BoxLayout( True )
    parentlayout.addLayout( lyo, ypos, 1 )
    ret = []
    for ifld in range( len(rg) ):
      le = self.addLineEdit( lyo )
      le.setText( str(round(rg[ifld])) )
      le.returnPressed.connect( self.updatePlot )
      ret.append( le )
    return ret


  def addTypeSels( self, parentlayout, ypos ):

    lyo = qt.GridLayout()
    parentlayout.addLayout( lyo, ypos, 1 )

    def addCB( lyo, typ, xpos, ypos ):
      from covvxdb import VxCovType_names
      global VxCovType_names
      return self.addCheckBox( VxCovType_names[typ], ypos, xpos, lyo, self.typeSelected )

    from covvxdb import VxCovType_MOD, VxCovType_PFI, VxCovType_JAN
    cbmod = addCB( lyo, VxCovType_MOD, 0, 0 )
    cbpfi = addCB( lyo, VxCovType_PFI, 0, 1 )
    cbjan = addCB( lyo, VxCovType_JAN, 1, 0 )
    return [None, cbmod, cbpfi, cbjan]


  def addSeveritySels( self, parentlayout, ypos ):
    from covvxdbextract import VxSeverity_names
    global VxSeverity_names

    lyo = qt.GridLayout()
    parentlayout.addLayout( lyo, ypos, 1 )

    cbminor = self.addCheckBox( VxSeverity_names[0], 0, 0, lyo )
    cbmajor = self.addCheckBox( VxSeverity_names[1], 1, 0, lyo )
    cbdeath = self.addCheckBox( VxSeverity_names[2], 0, 1, lyo )
    return [cbminor, cbmajor, cbdeath]


  def createControls( self ):

    lyo = qt.BoxLayout( True )
    ctrllayout = qt.GridLayout()
    self.layout.addLayout( ctrllayout, 2 )

    leftwidth = round( self.width*0.09 )
    self.addLabel( 'Analysis', leftwidth, 0, ctrllayout )
    self.addLabel( 'Age Range', leftwidth, 1, ctrllayout )
    self.addLabel( 'Gender', leftwidth, 2, ctrllayout )
    self.addLabel( 'Severity', leftwidth, 3, ctrllayout )
    self.addLabel( 'HOR: '+('weeks' if self.useWeeks() else 'days'), leftwidth, 4, ctrllayout )
    self.addLabel( 'VER: count', leftwidth, 5, ctrllayout )
    self.addLabel( '<---------------------', leftwidth, 6, ctrllayout )
    self.addLabel( 'Show', leftwidth, 7, ctrllayout )

    self.countmodesel = None; self.handlingcountmodesel = False
    tmrg = self.extracter.tmRg()
    self.countmodesel = self.addCountModeSel( ctrllayout, 0 )
    self.agerginp = self.addRangeFlds( ctrllayout, 1, self.extracter.agerange )
    self.genderinp = self.addGenderFlds( ctrllayout, 2 )
    self.severityinp = self.addSeveritySels( ctrllayout, 3 )
    self.tmrginp = self.addRangeFlds( ctrllayout, 4, tmrg )
    self.nrevsrginp = self.addRangeFlds( ctrllayout, 5, self.nrevsrange )

    updbut = qt.PushButton( 'Update', self.updatePlot )
    updbut.setFixedSize( 250, 60 )
    ctrllayout.addWidget( updbut, 6, 1 )
    csvbut = qt.PushButton( 'Export CSV', self.exportCSV )
    csvbut.setFixedSize( 250, 60 )
    ctrllayout.addWidget( csvbut, 6, 2 )

    self.typeinp = None
    self.typeinp = self.addTypeSels( ctrllayout, 7 )


  def getSelections( self ):

    def getRg( rg, flds ):
      for ifld in range( len(rg) ):
        rg[ifld] = qt.getLineEditValue( flds[ifld], False, rg[ifld] )

    tmrg = self.extracter.tmRg()
    getRg( tmrg, self.tmrginp )
    self.extracter.setDateRgFromTmRg( tmrg )
    getRg( self.nrevsrange, self.nrevsrginp )
    getRg( self.extracter.agerange, self.agerginp )
    self.extracter.genders = [self.genderinp[0].isChecked(), self.genderinp[1].isChecked()]
    for isev in range( len(self.severityinp) ):
      self.extracter.severities[isev][1] = self.severityinp[isev].isChecked()
    self.updateTypeSelections()


  def updateTypeSelections( self ):

    if self.typeinp:
      self.types[0][1] = False
      for ityp in range( 1, len(self.typeinp) ):
        self.types[ityp][1] = self.typeinp[ityp].isChecked()


  def updatePlot( self ):
  
    self.getSelections()
    self.extracter.getCounts()
    self.fillPlot()


  def exportCSV( self ):
    from common import userDataDir
    from utils import open_for_write, dismiss_file
    from qt import dispError, dispInfo

    fnm = qt.doFileDialog( self, False, userDataDir(), "CSV files (*.csv)" )
    if fnm is None or len(fnm) < 1:
      return

    fp = open_for_write( fnm )
    if fp is None:
      qt.dispError( self, "Cannot open '" + fnm + "'" )
    else:
      covtyps = []
      for covtyp in range( 1, len(self.types) ):
        if self.dataVisible( covtyp ):
          covtyps.append( covtyp )
      self.extracter.outputCSV( fp, not self.lotCountMode(), covtyps, 500 )
      dismiss_file( fp )
      qt.dispInfo( self, "Wrote to: '" +  fnm + "'" )


  def globCountModeSel( self ):
    self.countModeSel( 0 )
  def lotCountModeSel( self ):
    self.countModeSel( 1 )


  def countModeSel( self, bidx ):

    if self.countmodesel is None or self.handlingcountmodesel:
      return

    self.handlingcountmodesel = True
    clickedonlotcount = bidx == 1
    clickbut = self.countmodesel[bidx]
    othbut = self.countmodesel[1 if bidx==0 else 0]
    wantlotcount = clickedonlotcount == clickbut.isChecked()
    othbut.setChecked( clickedonlotcount != wantlotcount )
    self.handlingcountmodesel = False

    if wantlotcount != self.extracter.dolotcount:
      self.extracter.dolotcount = wantlotcount
      self.handleCountModeChange()


  def handleCountModeChange( self ):

    self.extracter.clear()
    self.nrevsrginp[1].setText( str(self.lotdefnrevs if self.extracter.dolotcount else self.globdefnrevs) )
    self.fillPlot()


  def typeSelected( self ):

    self.updateTypeSelections()
    for covtyp in range( 1, len(self.types) ):
      isvis = self.dataVisible( covtyp )
      if self.lotCountMode():
        scat = self.scatterForType( covtyp )
        scat.setVisible( isvis )
      else:
        curv = self.curveForType( covtyp )
        curv.setVisible( isvis )


  def curveForType( self, covtyp ):

    return self.pp.curves[covtyp-1]


  def scatterForType( self, covtyp ):

    return self.pp.scatters[covtyp-1]


  def dataVisible( self, covtyp ):

    return self.types[covtyp][1]


  def fillPlot( self ):

    tmrg = self.extracter.tmRg()
    self.pp.xAxis().setMin( tmrg[0] )
    self.pp.xAxis().setMax( tmrg[1] )
    self.pp.yAxis().setMin( self.nrevsrange[0] )
    self.pp.yAxis().setMax( self.nrevsrange[1] )

    self.fillPlotContent()


  def fillPlotContent( self ):

    tmrg = self.extracter.tmRg()
    for covtyp in range( 1, len(self.types) ):

      scat = self.scatterForType( covtyp )
      scat.clear()
      curv = self.curveForType( covtyp )
      curv.clear()
      typevisible = self.dataVisible( covtyp )
      if self.lotCountMode():
        if self.extracter.hasLotCountData():
          for rec in self.extracter.lotinfo:
            if rec[1] == covtyp:
              scat.append( float(rec[2]), float(rec[3]) )
        scat.setVisible( typevisible )
        curv.setVisible( False )
      else:
        if self.extracter.hasBrandCountData():
          for tmnr in range( tmrg[0], tmrg[1]+1 ):
            curv.append( float(tmnr), float(self.extracter.brandCount(tmnr,covtyp)) )
        curv.setVisible( typevisible )
        scat.setVisible( False )


  def pointClicked( self, pt ):
    from covvxdb import VxCovType_prettynames
    from qt import dispInfo
    
    if not self.extracter.lotinfo:
      return

    tmnr = round( pt.x() )
    nrevs = pt.y()
    smallestdist = 999999
    nearestinf = None
    for inf in self.extracter.lotinfo:
      if inf[2] == tmnr:
        dist = abs( inf[3]-nrevs )
        if smallestdist > dist:
          nearestinf = inf
          smallestdist = dist

    if nearestinf is None:
      return

    disptxt = 'Type: ' + VxCovType_prettynames[nearestinf[1]] + ', ' \
            + 'Lot:  ' + nearestinf[0].name()
    detailedtxt = 'Number of adverse events: ' + str(nearestinf[3]) + '\n' \
                + 'Average date of injection: ' + self.extracter.dateAt(nearestinf[2]).strftime('%b %-d')
    qt.dispInfo( self.pp.qObj(), disptxt, "Clicked Lot", detailedtxt )



if __name__== '__main__':
  from common import initMain
  import sys
  initMain()

  useweeks = True
  if len(sys.argv) > 1:
    useweeks = sys.argv[1] != 'DAY'

  app = qt.Application()
  win = uiVxCovidDB( useweeks )
  win.show()
  qt.runApplication( app )
