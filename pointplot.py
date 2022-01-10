# Class facilitates scientific graphs with X and Y (maybe Y2) axes
# As usual, you can't do everything, but life is a lot easier if you can live with that


class PointPlot:


  def __init__( self, title, minx, maxx, miny, maxy ):
    import qt

    [self.chart, self.view] = qt.Chart( title )
    self.xax = qt.Axis( self.chart, minx, maxx )
    self.chart.setAxisX( self.xax )
    self.yaxes = []
    self.yaxes.append( qt.Axis(self.chart,miny,maxy) )
    self.chart.setAxisY( self.yaxes[0] )

    self.curves = []
    self.scatters = []
    self.annotxax = None
    self.mousetracktxtprov = None


  def qObj( self ):

    return self.view


  def xAxis( self ):

    return self.xax


  def yAxis( self, y1=True ):

    return self.yaxes[0 if y1 or len(self.yaxes)<2 else 1]


  def clearSeries( self ):

    self.chart.removeAllSeries()


  def addRightAxis( self, miny, maxy ):
    import qt

    self.yaxes.append( qt.Axis(self.chart,miny,maxy) )
    self.chart.addAxis( self.yaxes[-1], qt.Align(True,False) )
    return self.yaxes[-1]


  def addScatter( self, nm, color=None, y1=True ):
    import qt

    if color is None:
      color = qt.StdLineColor( len(self.scatters) )
    ss = qt.ScatterSeries( self.chart, nm, color ) 
    ss.attachAxis( self.xax )
    ss.attachAxis( self.yAxis(y1) )
    self.scatters.append( ss )

    return ss


  def addCurve( self, nm, color=None, y1=True ):
    import qt

    if color is None:
      color = qt.StdLineColor( len(self.curves) )
    ls = qt.LineSeries( self.chart, nm, color ) 
    ls.attachAxis( self.xax )
    ls.attachAxis( self.yAxis(y1) )
    self.curves.append( ls )

    return ls


  def addFlatLine( self, nm, ishor, val, posns, color="#aaaaaa", y1=True ):
    import qt

    ln = self.addCurve( nm, qt.Color(color), y1 )
    if ishor:
      ln.append( posns[0], val )
      ln.append( posns[1], val )
    else:
      ln.append( val, posns[0] )
      ln.append( val, posns[1] )
    self.removeFromLegend( ln )

    return [ln, ishor]


  def axisEnd( self, ismax, ishor, y1=True ):

    if ismax:
      return self.xAxis().max() if ishor else self.yAxis(y1).max()
    else:
      return self.xAxis().min() if ishor else self.yAxis(y1).min()


  def addLevel( self, nm, ishor, color, val=0.0, y1=True ):

    pmin = self.axisEnd( False, ishor, y1 )
    pmax = self.axisEnd( True, ishor, y1 )
    return self.addFlatLine( nm, ishor, val, [pmin,pmax], color, y1 )


  def addCutOffLevels( self, nm, ishor, val=0.0, y1=True ):
    import qt
    
    minlvl = self.addLevel( "min "+nm, True, qt.cutOffLineColor(), val, y1 )
    maxlvl = self.addLevel( "max "+nm, True, qt.cutOffLineColor(), val, y1 )
    return [minlvl, maxlvl]


  def setLevel( self, lvl, val ):
    import qt

    fn = qt.setSeriesY if lvl[1] else qt.setSeriesX
    fn( lvl[0], 0, val )
    fn( lvl[0], 1, val )


  def setCutOffLevels( self, lvls, val ):

    if val < 0:
      val = -val
    self.setLevel( lvls[0], -val )
    self.setLevel( lvls[1], val )


  def removeFromLegend( self, series ):

    self.chart.legend().markers( series )[0].setVisible( False )


  def setNiceAxes( self, x=True, y1=True, y2=True ):

    if x:
      self.xAxis().applyNiceNumbers()
    if y1:
      self.yAxis().applyNiceNumbers()
    y2ax = self.yAxis( False )
    if y2 and y2ax:
      y2ax.applyNiceNumbers()
