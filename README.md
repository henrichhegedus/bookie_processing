# Screping framewor for all bookies

Fo reach bookie we open a certain browser window load the html and scrape it with beautiful soup. 

To translate names we use Google search this normalizes the names from different languages so that they can be matches easily.

## Setup
Set the BOOKIE_PROCESSING environment variable to point to the bookie_processing folder
> echo 'export BOOKIE_PROCESSING=/path/to/bookie_processing' >> ~/.bashrc