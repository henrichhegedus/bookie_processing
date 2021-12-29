export BOOKIE_PROCESSING=/code/bookie_processing
. /code/venv/bin/activate
echo Ladbrokes
/code/venv/bin/python3 $BOOKIE_PROCESSING/ladbrokes/ladbrokes_save_to_db.py