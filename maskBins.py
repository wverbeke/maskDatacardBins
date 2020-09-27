import os, sys
from ROOT import TFile, TH1, TH1D

from Datacard import Datacard


#convert a root file into a dictionary of histograms
def buildHistogramDictionary( root_file_path ):
    root_file = TFile( root_file_path )
    histogram_dict = {}
    for entry in root_file.GetListOfKeys():
        name = entry.GetName()
        hist = root_file.Get( name )
        hist.SetDirectory( 0 )
        if isinstance( hist, TH1 ) :
            histogram_dict[ name ] = hist
    root_file.Close()
    return histogram_dict


#given a histogram and a set of bins, return a new histogram where the specified bin numbers are removed
def removeBins( hist, bins_to_remove ):
    content_to_keep = []
    for b in range( 1, hist.GetNbinsX() + 1 ):
        if b in bins_to_remove: continue
        content_to_keep.append( ( hist.GetBinContent( b ), hist.GetBinError( b ) ) )

    new_name = hist.GetName() + '_reduced'
    new_hist = TH1D( new_name, new_name + ';' + hist.GetXaxis().GetTitle() + ';' + hist.GetYaxis().GetTitle(), hist.GetNbinsX() - len( bins_to_remove ), 0., 1. )
    for i, entry in enumerate( content_to_keep ):
        new_hist.SetBinContent( i + 1, entry[0] )
        new_hist.SetBinError( i + 1, entry[1] )
    return new_hist


#make a backup of the datacard and the shapepath before removing bins
def backupDatacard( datacard ):
    backup_card_directory = os.path.join( 'backup', datacard.directory() ).replace( '../', '' )
    os.system( 'mkdir -p {}'.format( backup_card_directory ) )
    backup_shape_directory = os.path.join( 'backup', datacard.shapeDirectory() ).replace( '../', '' )
    os.system( 'mkdir -p {}'.format( backup_shape_directory ) )
    
    backup_card_path = os.path.join( backup_card_directory, os.path.basename( datacard.path() ) )
    backup_shape_path = os.path.join( backup_shape_directory, os.path.basename( datacard.shapeFilePath() ) )
    os.system( 'cp {} {}'.format( datacard.path(), backup_card_path ) )
    os.system( 'cp {} {}'.format( datacard.shapeFilePath(), backup_shape_path ) )


#check whether a given histogram name corresponds to a nominal histogram or a variation
def isNominal( hist_name ):
    return not ( 'Down' in hist_name or 'Up' in hist_name )


#given a dictionary of all histograms in a shape file, return a dictionary with the nominal yields of each process
def nominalYieldDict( hist_dict ):
    nominal_yields = {}
    for key in hist_dict:
        if isNominal( key ):
            nominal_yields[ key ] = hist_dict[ key ].GetSumOfWeights()
    return nominal_yields


def maskBins( datacard_path, bins_to_remove ):
    
    datacard = Datacard( datacard_path )

    #back up the datacard
    backupDatacard( datacard )

    #read all histograms in the shape file into a dictionary
    hist_dict = buildHistogramDictionary( datacard.shapeFilePath() )

    #make a new histogram dictionary where the requested bins are removed
    new_hist_dict = {}
    for key in hist_dict:
        new_hist_dict[ key ] = removeBins( hist_dict[key], bins_to_remove )

    #determine the updated nominal yields
    new_yields = nominalYieldDict( new_hist_dict )

    #update the datacard and shape file
    datacard.modifyRatesAndObservation( new_yields )
    datacard.rewriteShapeFile( new_hist_dict )


if __name__ == '__main__':
    
    if len( sys.argv ) < 3:
        error_text = 'At least 3 arguments should be specified:\n'
        error_text += 'Usage : python maskBins.py < datacard path > < space separated list of bin numbers >'
        raise RuntimeError( error_text )

    datacard_path = sys.argv[1]
    bins_to_remove = set( int(b) for b in sys.argv[2:] )

    maskBins( datacard_path, bins_to_remove )
