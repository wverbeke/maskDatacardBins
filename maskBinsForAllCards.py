import os, sys

from maskBins import *


def isDataCard( file_path ):
    return file_path.endswith( '.txt' )


def removeBinsForAllCards( directory_path, bins_to_remove ):
    for path, directories, files in os.walk( directory_path ):
        for f in files:
            if isDataCard( f ):
                maskBins( os.path.join( path, f ), bins_to_remove )


if __name__ == '__main__':
    if len( sys.argv ) < 3:
        error_text = 'At least 3 arguments should be specified:\n'
        error_text += 'Usage : python maskBinsForAllCards.py < datacard directory path > < space separated list of bin numbers >'
        raise RuntimeError( error_text )

    datacard_directory = sys.argv[1]
    bins_to_remove = set( int(b) for b in sys.argv[2:] )

    removeBinsForAllCards( datacard_directory, bins_to_remove )
