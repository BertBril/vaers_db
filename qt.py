# This is a layer on top of Qt, to:
# 1. Make some very easy to use things so you don't need to dive into the vast Qt workings
# 2. Add tools mainly for making line and scatter plots (scientific stuff)
# 3. Combine some very common operation

BACKGROUND_COLOR = "#a0b5a0"
BUTTON_BACKGROUND_COLOR = "#e0e0e0"
TABLE_BACKGROUND_COLOR = "#eeeedd"
TABLE_CELL_BACKGROUND_COLOR = "#ffff00"
TABLE_CELL_SPECIAL_BACKGROUND_COLOR = "#eeffee"

STD_LINE_COLORS = [
    '#f58231', # Orange
    '#911eb4', # Purple
    '#88ffa3', # Mint
    '#808000', # Olive
    '#800000', # Maroon
    '#ffd8b1', # Apricot
    '#469990', # Teal
    '#000075', # Navy
]


def StdLineColor( lnnr ):

  colnr = lnnr % len(STD_LINE_COLORS)
  return STD_LINE_COLORS[ colnr ]


def cutOffLineColor():

  return StdLineColor( 7 )


def Color( colstr ):
  from PyQt5.QtGui import QColor

  return QColor( colstr ) if colstr else QColor()


def Point( x=0.0, y=0.0 ):
  from PyQt5.QtCore import QPointF

  return QPoint( x, y )


def Timer( qobj, fn, nrmsecs ):
  from PyQt5.QtCore import QTimer

  ret = QTimer( qobj )
  ret.setSingleShot( True )
  ret.timeout.connect( fn )
  ret.start( nrmsecs )

  return ret


#----- Dialogs/Messages

def messageBox( par, txt, titl, detailedtxt=None, inftxt=None ):
  from PyQt5.QtWidgets import QMessageBox

  mb = QMessageBox( par )
  mb.setWindowTitle( titl )
  mb.setText( txt )
  if detailedtxt:
    mb.setDetailedText( detailedtxt )
  if inftxt:
    mb.setInformativeText( inftxt )
  return mb


def dispInfo( par, txt, titl='Info', detailedtxt=None, inftxt=None ):
  from PyQt5.QtWidgets import QMessageBox

  mb = messageBox( par, txt, titl, detailedtxt, inftxt )
  mb.setIcon( QMessageBox.Information )
  mb.setStandardButtons( QMessageBox.Close )
  mb.exec_()


def dispWarning( par, txt, titl='Warning', detailedtxt=None, inftxt=None ):
  from PyQt5.QtWidgets import QMessageBox

  mb = messageBox( par, txt, titl, detailedtxt, inftxt )
  mb.setIcon( QMessageBox.Warning )
  mb.setStandardButtons( QMessageBox.Close )
  mb.exec_()


def dispError( par, txt, titl='Error', detailedtxt=None, inftxt=None ):
  from PyQt5.QtWidgets import QMessageBox

  mb = messageBox( par, txt, titl, detailedtxt, inftxt )
  mb.setIcon( QMessageBox.Critical )
  mb.setStandardButtons( QMessageBox.Close )
  mb.exec_()


def doFileDialog( par, forread, defdir='', filt="All files (* *.*)" ):
  from PyQt5.QtWidgets import QFileDialog

  if forread:
    (ret,dum) = QFileDialog.getOpenFileName( parent=par, caption='Open file', directory=defdir, filter=filt )
  else:
    (ret,dum) = QFileDialog.getSaveFileName( parent=par, caption='Save file', directory=defdir, filter=filt )

  return ret


#----- Widgets


def Axis( ch, minval=None, maxval=None ):
  from PyQt5.QtChart import QValueAxis

  ret = QValueAxis()
  if minval:
    ret.setMin( minval )
  if maxval:
    ret.setMax( maxval )
  return ret


def Align( ishor, isstart ):
  from PyQt5.QtCore import Qt

  if ishor:
    return Qt.AlignLeft if isstart else Qt.AlignRight
  else:
    return Qt.AlignBottom if isstart else Qt.AlignTop


def Chart( title ):
  from PyQt5.QtChart import (QChart, QChartView)
  from PyQt5.QtGui import QPainter

  ch = QChart()
  ch.setTitle( title )
  vw = QChartView( ch )
  vw.setRenderHint( QPainter.Antialiasing )
  return [ch, vw]


def Frame( parent, layout=None ):
  from PyQt5.QtWidgets import QFrame

  ret = QFrame( parent )
  ret.setStyleSheet( 'color: black; background-color: ' + BUTTON_BACKGROUND_COLOR )
  if layout != None:
    ret.setLayout( layout )
  return ret


def GridLayout():
  from PyQt5.QtWidgets import QGridLayout

  return QGridLayout()


def BoxLayout( hor ):
  from PyQt5.QtWidgets import QHBoxLayout
  from PyQt5.QtWidgets import QVBoxLayout

  return QHBoxLayout() if hor else QVBoxLayout()


def StackedLayout():
  from PyQt5.QtWidgets import QStackedLayout

  return QStackedLayout()


def LineSeries( ch, nm, color="#000000", wdth=4 ):
  from PyQt5.QtChart import QLineSeries
  from PyQt5.QtGui import QColor

  ls = QLineSeries()
  ls.setName( nm )
  pen = ls.pen()
  pen.setColor( QColor(color) )
  pen.setWidthF( wdth )
  ls.setPen( pen )
  ls.setUseOpenGL( True )
  ch.addSeries( ls )

  return ls


def ScatterSeries( ch, nm, color="#000000", ptsz=10.0 ):
  from PyQt5.QtChart import QScatterSeries
  from PyQt5.QtGui import QColor

  ss = QScatterSeries()
  ss.setName( nm )
  ss.setColor( QColor(color) )
  ss.setBorderColor( QColor(color) )
  ss.setMarkerSize( ptsz )
  ss.setUseOpenGL( True )
  ch.addSeries( ss )

  return ss


def setSeriesX( crv, ipt, xval ):

  pt = crv.at( ipt )
  pt.setX( xval )
  crv.replace( ipt, pt )


def setSeriesY( crv, ipt, yval ):

  pt = crv.at( ipt )
  pt.setY( yval )
  crv.replace( ipt, pt )


def setLineWidth( obj, lwidth ):

  pen = obj.pen()
  pen.setWidth( 5 )
  obj.setPen( pen )


from PyQt5.QtWidgets import QMainWindow

class MainWindow( QMainWindow ):

  def __init__( self, parent=None ):
    
    QMainWindow.__init__( self, parent )


class TestApp:

  def __init__( self, title="Test" ):
    
    self.app = Application()
    self.win = MainWindow()
    self.layout = GridLayout()
    frame = Frame( self.win, self.layout )
    self.win.setCentralWidget( frame )
    self.win.setWindowTitle( title )
    self.win.setGeometry( 300, 300, 1100, 900 )

  def go( self ):
    
    self.win.show()
    runApplication( self.app )


def Table( nrcols, nrrows ):
  from PyQt5.QtWidgets import QTableWidget
  from PyQt5.QtWidgets import QHeaderView

  ret = QTableWidget()
  ret.setColumnCount( nrcols )
  ret.setRowCount( nrrows )
  ret.horizontalHeader().resizeSections( QHeaderView.Interactive )
  ret.setStyleSheet( 'color: black; background-color: ' + BUTTON_BACKGROUND_COLOR )
  return ret


def TableItem( cont ):
  from PyQt5.QtWidgets import QTableWidgetItem

  ret = QTableWidgetItem( cont )
  ret.setBackground( Color(TABLE_CELL_BACKGROUND_COLOR) )
  return ret


def setTableHdr( tbl, idx, cont, hor ):
  from PyQt5.QtWidgets import QTableWidgetItem

  itm = QTableWidgetItem( str(cont) )
  itm.setBackground( Color("#dddddd") )
  if hor:
    tbl.setHorizontalHeaderItem( idx, itm )
  else:
    tbl.setVerticalHeaderItem( idx, itm )


def setTableCell( tbl, ixiy, cont, norm=True ):
  from PyQt5.QtWidgets import QTableWidgetItem

  itm = QTableWidgetItem( str(cont) )
  if norm:
    itm.setBackground( Color(TABLE_CELL_BACKGROUND_COLOR) )
  else:
    itm.setBackground( Color(TABLE_CELL_SPECIAL_BACKGROUND_COLOR) )
  tbl.setItem( ixiy[1], ixiy[0], itm )


def PushButton( txt, onclick ):
  from PyQt5.QtWidgets import QPushButton

  ret = QPushButton( text=txt )
  ret.setStyleSheet( 'color: black; background-color: ' + BUTTON_BACKGROUND_COLOR )
  ret.clicked.connect( onclick )
  return ret


def CheckBox( txt, onclick=None ):
  from PyQt5.QtWidgets import QCheckBox

  ret = QCheckBox( text=txt )
  ret.setStyleSheet( 'color: black; background-color: ' + BUTTON_BACKGROUND_COLOR )
  if onclick is not None:
    ret.stateChanged.connect( onclick )
  return ret


def Label( txt, alignleft=True ):
  from PyQt5.QtWidgets import QLabel

  ret = QLabel( text=txt )
  if not alignleft:
    ret.setAlignment( Align(True,alignleft) )
  return ret


def LineEdit():
  from PyQt5.QtWidgets import QLineEdit

  ret = QLineEdit()
  ret.setStyleSheet( 'color: black; background-color: ' + BUTTON_BACKGROUND_COLOR )
  return ret


def getLineEditValue( le, ret_float, defval=0 ):
  from PyQt5.QtWidgets import QLineEdit

  txt = le.text()
  ret = defval
  try:
    ret = float( txt ) 
    if not ret_float:
      ret = round( ret ) 
  except:
    ret = defval
  return ret


#----- Application


def Application():
  import sys
  from PyQt5.QtWidgets import QApplication
  from PyQt5.QtWidgets import QStyleFactory

  ret = QApplication( sys.argv )
  QApplication.setStyle( QStyleFactory.create('Plastique') )
  return ret


def runApplication( app ):
  import sys
  import PyQt5.QtCore
  from common import runningInDebugger

  # to avoid "QCoreApplication::exec: The event loop is already running" when running in pdb
  PyQt5.QtCore.pyqtRemoveInputHook()

  sys.exit( app.exec_() )


if __name__== '__main__':

  app = Application()

  class TstWin( MainWindow ):

    def __init__( self, parent=None ):
      
      MainWindow.__init__( self, parent )

      layout = GridLayout()
      frame = Frame( self, layout )

      tbl = Table( 3, 8 )
      setTableHdr( tbl, 0, "ST", True )
      setTableHdr( tbl, 1, "LT", True )
      setTableHdr( tbl, 2, "STD", True )
      for i in range( 8 ):
        setTableHdr( tbl, i, "Row "+str(i), False )

      setTableCell( tbl, [1,2], "Cell 1.2" )
      setTableCell( tbl, [2,1], "Cell 2.1" )
      setTableCell( tbl, [2,2], 123 )

      tbl.setGeometry( 0, 0, 1000, 800 )
      layout.addWidget( tbl, 0, 0 )

      self.setCentralWidget( frame )
      self.setWindowTitle( "TEST WIN" )
      self.setGeometry( 300, 300, 1100, 900 )

  win = TstWin()
  win.show()
  runApplication( app )
