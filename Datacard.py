import os
from ROOT import TFile


def findLine( datacard_lines, query ):
    for l in datacard_lines:
        if query( l ):
            return l
    raise KeyError( 'No line matching the requested criteria is found in the datacard' )


def shapeFileLine( datacard_lines ):
    return findLine( datacard_lines, lambda l : '$PROCESS_$SYSTEMATIC' in l )


def shapeFilePath( shape_file_line ):
    for part in shape_file_line.split():
        if '.root' in part:
            return part
    raise KeyError( 'No .root file is specified in line "{}".'.format( shape_path_line ) )


def rateLine( datacard_lines ):
    return findLine( datacard_lines, lambda l : l.startswith( 'rate' ) )


def processLine( datacard_lines ):
    return findLine( datacard_lines, lambda l : l.startswith( 'process' ) )


def observedLine( datacard_lines ):
    return findLine( datacard_lines, lambda l : l.startswith( 'observation' ) )



class Datacard:

    def __init__( self, datacard_path ):
        self.__path = datacard_path
        self.__lines = None
        with open( self.__path ) as f:
            self.__lines = f.readlines()
        self.__directory = os.path.dirname( self.__path )
        self.__extractShapeFilePath()
        

    def __extractShapeFilePath( self ):
        relative_path = shapeFilePath( shapeFileLine( self.__lines ) )
        self.__shape_path = os.path.join( self.__directory, relative_path )


    def path( self ):
        return self.__path


    def directory( self ):
        return self.__directory


    def shapeFilePath( self ):
        return self.__shape_path


    def shapeDirectory( self ):
        return os.path.dirname( self.__shape_path )


    def lines( self ):
        return self.__lines


    def __rewriteCard( self ):
        with open( self.__path, 'w' ) as f:
            for l in self.__lines:
                f.write( l )


    def rewriteShapeFile( self, new_hist_dict ):
        f = TFile( self.__shape_path, 'RECREATE' )
        for key, hist in new_hist_dict.items():
            hist.Write( key )
        f.Close()


    def modifyRatesAndObservation( self, new_yield_dict ):
        old_rate_line = rateLine( self.__lines )

        #important to make sure the process order is correctly read from datacard, since the given dictionary might not respect this order
        processes = processLine( self.__lines ).split()[1:]

        #make a new rate line
        new_rate_line = 'rate'
        for p in processes:
            new_rate_line += ' {}'.format( new_yield_dict[ p ] )
        new_rate_line += '\n'

        #make a new observation line
        new_obs_line = 'observation {}\n'.format( int( new_yield_dict[ 'data_obs' ] ) )
        old_obs_line = observedLine( self.__lines )

        #replace the old rate and observation lines with the new ones
        replaced_rate = False
        replaced_obs = False
        for i, l in enumerate( self.__lines ):
            if l == old_rate_line:
                self.__lines[ i ] = new_rate_line
                replaced_rate = True
            elif l == old_obs_line:
                self.__lines[ i ] = new_obs_line
                replaced_obs = True
            if replaced_rate and replaced_obs:
                break

        #rewrite the datacard
        self.__rewriteCard()
