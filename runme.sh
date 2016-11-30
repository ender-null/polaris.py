#!/bin/bash
DIR=`dirname $0`
export NLTK_DATA=$DIR/nltk_data 

if [ ! -d "$DIR/env" ]; then
    virtualenv -q $DIR/env --no-site-packages
    echo "Virtualenv created."
fi

source $DIR/env/bin/activate

if [ ! -f "$DIR/env/updated" -o $DIR/requirements.txt -nt $DIR/env/updated ]; then
    pip install -r $DIR/requirements.txt --upgrade
    touch $DIR/env/updated
    echo "Requirements installed."
fi

python -B -m textblob.download_corpora
python -B $DIR/loader.py
