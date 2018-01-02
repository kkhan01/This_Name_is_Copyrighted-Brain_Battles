DATE=`date '+%Y-%m-%d %H:%M:%S'`
ENTRY="$1 -- $DATE\n$2\n"

if [ $# -eq 2 ]; then
    if [ ! -e devlog.txt ]; then
        touch devlog.txt
    fi
    echo -e "$ENTRY" >> devlog.txt   
else
    echo -e "Incorrect number of arguments supplied\nUsage: $ ./log.sh <firstL> <message>"  
fi
