import shutil
import os
import sys
import time
import subprocess
import flask #to ensure it's installed

if( len( sys.argv ) > 1 ):
    node_file = sys.argv[ 1 ]
    edge_file = sys.argv[ 2 ]
    shutil.copyfile( node_file, './MADB Website/static/data/nodes.json' )
    shutil.copyfile( edge_file, './MADB Website/static/data/edges.json' )

os.system("start \"\" http://127.0.0.1:5000/Main_Page.html")

print( 'Use Ctl+C to stop' )

proc = subprocess.Popen( [ "flask", "run" ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="./MADB Website/" )
proc.communicate()
