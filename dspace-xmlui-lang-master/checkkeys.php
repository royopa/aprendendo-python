<?php
#
# The contents of this file are subject to the license and copyright
# detailed in the LICENSE and NOTICE files at the root of the source
# tree and available online at
#
# http://www.dspace.org/license/
#

###########################################################################
#
# checkkeys.php
#
###########################################################################

# Simple tool to compare two properties files, finding out which keys
# are present in one file but not the other.  It

if ($argc != 3) {
    echo "Usage: checkkeys.php <master> <tocheck>\n";
    exit(1);
}

$masterKeys  = readFileKey($argv[1]);
$toCheckKeys = readFileKey($argv[2]);

function readFileKey($path) {
    if (! $fileContent = @file($path)) {
        echo "Can't open $path \n";
        exit(1);
    }

    //$fileContent = mb_convert_encoding(
        //$fileContent,
        //'UTF-8',
        //mb_detect_encoding($fileContent, 'UTF-8, ISO-8859-1', true)
    //);


    readKeys($fileContent);

    return $fileContent;
}

function readKeys($file)
{
    foreach ($file as $key => $line) {
        if (strpos($line, '<message key="') === false) {
            continue;
        }

        $line = trim($line);

        $line = substr($line, 14);

        $charEnd = var_dump(strpos($line, '">'));

        var_dump($line);

        var_dump($charEnd);

        //$key = substr($line, 14, 45);

        //var_dump($key);

        //pegar o que tiver na frente de ">
        //e antes de </message>

        echo "$line \n";
    }
}