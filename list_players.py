from subprocess import check_output
from os import system

sUsers  = [ ]

# Parse current connections

system( "cls" )
sOutput = check_output( "netstat -an | findstr 12345", shell=True ).decode()
sOutput = sOutput.split( "\r\n" )
sOutput = sOutput[1:]
for line in sOutput:
    sLine = line.split( )
    if ( len( sLine ) <= 1 ):
        continue
    sUsers.append( sLine[ 2 : ] )

# Read whitelist
aIPtoName = [ ]
with open( "whitelist.txt", encoding="utf8" ) as f:
    aIPtoName = f.readlines( )
aIPtoName = [ x.strip( ) for x in aIPtoName ] 
aIPtoName = [ x.split( "=" ) for x in aIPtoName ] 

# Print usernames
print( "{0} user(s) playing.".format( len( sUsers ) ) )
print( )
print( "Players" )
print( "=======" )

for user in sUsers:
    user = user[ 0 ]
    user = user.split( ":" )[ 0 ]
    user = user.split( "." )
    for i in range( len( user ) - 1, 1, -1 ):
        user[ i ] = "0"
        fullUser = '.'.join( user )
        for ip in aIPtoName:
            if ( ip[ 0 ] == fullUser ):
                print( f"{ip[ 1 ]} - {fullUser}" )


