# Vx objects, holding data like producer, type, etc.

import common
from utils import NamedObj


class VxProducer( NamedObj ):


  def __init__( self, prnm ):

    NamedObj.__init__( self, prnm )



class VxType( NamedObj ):


  def __init__( self, typnm ):

    NamedObj.__init__( self, typnm )



class VxLot( NamedObj ):


  def __init__( self, lotnm ):

    NamedObj.__init__( self, lotnm )
    self.ids = set()


  def hasID( self, id ):

    return id in self.ids




class VxBrand( NamedObj ):


  def __init__( self, pr, typ, brandnm ):

    NamedObj.__init__( self, brandnm )

    self.producer = pr
    self.type = typ
    self.lots = []


  def findLot( self, lotnm ):
    
    if lotnm is None or len(lotnm) < 1:
      lotnm = "Unknown"
    for lot in self.lots:
      if lot.name() == lotnm:
        return lot
    ret = VxLot( lotnm )
    self.lots.append( ret )
    return ret


  def nrIDs( self ):

    ret = 0
    for lot in self.lots:
        ret += len(lot.ids)
    return ret


class VxEventBase:

  def __init__( self, id ):
    from datetime import date

    self.id = id
    self.state = 'TX'
    self.age = 50
    self.ismale = self.issevere = self.isdeath = False
    self.date = date.today()


  def severityReject( self, wantminor, wantmajor, wantdeath ):

    return (not wantminor and not self.issevere) \
        or (not wantdeath and self.isdeath) \
        or (not wantmajor and self.issevere and not self.isdeath)


  def dump( self ):

    print( "Event:", self.id, self.state, self.age, 'M' if self.ismale else 'F', self.date.strftime('%m/%d/%Y') )



if __name__ == "__main__":

  print( 'Pass' )
