#!/bin/bash

templateCase=template
# Name of file containing list of parameters to change and values
parmScanFile=cases
# Prefix name of created numbered test cases
scanName=case
# Script to execute in each created case
settingSFile=settings
execScript=

# Reading list of parameters to change
parmNames=($(sed -n '1p' $parmScanFile))
nCases=$(($(wc -l < $parmScanFile)))
echo "$nCases case(s) to be gererated"
nDigits=4

#Running through cases and generating or running them
for ((i=0; i<nCases; i++)); do
    caseNumber=$(printf "%0${nDigits}d" "$i")
    #Which line in parmScanFile specifies parameter values of current case 
    parmLineNumber=$((i + 2))
    #Current case parameter values
    caseParms=($(sed -n ${parmLineNumber}p $parmScanFile))
    #Name of current case directory
    caseName=${scanName}_${caseNumber}
    if [ -d "$caseName" ];
    then
        if [ -z "$execScript" ]; then
            echo Case $caseName already exists - doing nothing.
        else
            cd ${caseName}
            echo Running script $caseScript in case $caseName
            ./$execScript
            cd -
        fi
    else
        echo Creating case $caseName
        cp -r $templateCase $caseName
        caseParmFile=$caseName/$settingSFile
        for m in ${!parmNames[*]}
        do
            parmName=${parmNames[$m]}
            parmValue=${caseParms[$m]}
            sed -i "1i $parmName $parmValue;" "$caseParmFile"
            #echo "$parmName $parmValue;" >> $caseParmFile
        done
    fi
done