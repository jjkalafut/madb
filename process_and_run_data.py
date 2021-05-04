import sys
import os
import subprocess
import glob
import time


if __name__ == '__main__':

    if len( sys.argv ) < 1:
        print( 'Please call script and point at a netflow csv file')
        sys.exit()

    chunked = False
    startTime = time.time()
    #
    #   Chunk data if needed
    #
    if os.path.getsize( sys.argv[ 1 ] ) > 4000000: #4GB
        print( "Chunking file!\n" )
        chunked = True
        chunker = subprocess.Popen( ["py", "./Scripts/chunk_data.py", sys.argv[ 1 ] ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(os.path.realpath(__file__)) )
        for c in iter( lambda: chunker.stdout.read(1), b'' ):
            sys.stdout.buffer.write(c)

    print('Current time in minutes: ' + str( ( time.time() - startTime ) / 60 ) )
    #
    #   Gather file or chunks
    #
    data_folder = os.path.dirname( sys.argv[ 1 ] ) + '/'
    to_process = [ sys.argv[ 1 ] ]
    if chunked:
        to_process = glob.glob( data_folder + "*_chunk_*.csv" )

    #
    #   Pre-process file or chunks
    #
    print( "Files to preprocess: " + str( to_process ) + "\n" )
    for f in to_process:
        print( "On file " + f + "\n" )
        preprop = subprocess.Popen( ["py", "./Scripts/preprocess.py", f ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(os.path.realpath(__file__)) )
        for o in iter( lambda: preprop.stdout.read(1), b'' ):
            sys.stdout.buffer.write( o )

    print('Current time in minutes: ' + str( ( time.time() - startTime ) / 60 ) )
    #
    #   Run MIDAS
    #
    print( "Running MIDAS...\n" )
    for f in to_process:
        print( "On file " + f + "\n" )
        midas = subprocess.Popen( ["./Scripts/MIDAS_R.exe", f+".shape", f+".processed", f+".score", ".75" ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(os.path.realpath(__file__)) )
        for mo in iter( lambda: midas.stdout.read(1), b'' ):
            sys.stdout.buffer.write( mo )

    print('Current time in minutes: ' + str( ( time.time() - startTime ) / 60 ) )
    #
    #   Process with GMM
    #
    print( "Running GMM Adjustment...\n" )
    for f in to_process:
        print( "On file " + f + "\n" )
        midas = subprocess.Popen( ["py", "./Scripts/midas_gmm_prob.py", f ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(os.path.realpath(__file__)) )
        for mo in iter( lambda: midas.stdout.read(1), b'' ):
            sys.stdout.buffer.write( mo )

    print('Current time in minutes: ' + str( ( time.time() - startTime ) / 60 ) )
    #
    #   Process with GMM
    #
    print( "Post Processing...\n" )
    for f in to_process:
        print( "On file " + f + "\n" )
        midas = subprocess.Popen( ["py", "./Scripts/postprocess.py", f ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(os.path.realpath(__file__)) )
        for mo in iter( lambda: midas.stdout.read(1), b'' ):
            sys.stdout.buffer.write( mo )


    #
    #   Calculate ROC scores (labled data only)
    #
    #print( "Calculating ROC...\n" )
    #for f in to_process:
        #print( "On file " + f + "\n" )
        #roc = subprocess.Popen( ["py", "./Scripts/EvaluateScore.py", f+".truth", f+".score", f+".roc.txt" ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.path.dirname(os.path.realpath(__file__)) )
        #for r in iter( lambda: roc.stdout.read(1), b'' ):
            #sys.stdout.buffer.write( r )

    print('Execution time in minutes: ' + str( ( time.time() - startTime ) / 60 ) )
