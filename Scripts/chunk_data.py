import sys
import os


in_file_path = sys.argv[ 1 ]
f = open( in_file_path, 'r')

#change to start later in the file (by line number) use 1 if data has header
start = 0 #58000000

#Change to adjust size of chunk desired in GB(roughly)
chunk_size = 4.0

#dont change
count = 0

line_mod = int( chunk_size * 10000000 ) #rough converison of lines to GB

file_base = in_file_path[:in_file_path.rindex('.')]
on_chunk = 1 + int( start / line_mod )
f2 = open( file_base + '_chunk_' + str(on_chunk) + '.csv','w')


chunk_percent = int( chunk_size * 500000 ) # print at 5%

#nerris starts at 64598681
#dos starts at    59278909
#total lines     539490895

print( "Chunking started...\n" )

while True:
    count += 1

    # Get next line from file
    line = f.readline()

    # in case you wanted to skip some data
    if( count < start ):
        continue

    # check for EoF
    if not line:
        break

    # write line
    f2.write(line)

    if count % chunk_percent == 0:
        print( "chunk " + str( on_chunk ) + " " + str( ( count % line_mod ) * 100 / line_mod ) + "% done\n" )

    # end one chunk, start another
    if count % line_mod == 0:
        on_chunk += 1
        f2.close()
        f2 = open( file_base + '_chunk_' + str( on_chunk ) + '.csv','w')
        print( "Starting on chunk " + str( on_chunk ) + "\n" )

#finish closing files
f.close()
f2.close()
