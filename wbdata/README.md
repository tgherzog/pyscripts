

**api_climate_test.py**  
**api_finance_test.py**  
**api_gep_test.py**  
**api_project_test.py**  
**api_survey_test.py**  

These five scripts mimic functionality on data.wb that pulls country/region/topic specific
data from other WB APIs to display on the respective views. This is designed to make it easier
to validate the numbers appearing on the data site. Most of these scripts take a country
or topic code and return the appropriate data. 

Note that these scripts employ either the iso2, iso3 or country codes from the data API, but
in many cases there are exceptions in the target API that need to be corrected for. Most scripts
include a `code_mapping` dict that documents the necessary mappings. This may need updates from
time to time as various APIs make changes.

**config_check.py**

This script is designed to run sanity checks on config files, for instance, to look for indicators
that may have been removed from the API. Currently it only works on indicator_groups.yaml, but the
intent is to add other sanity checks on other files in the future
