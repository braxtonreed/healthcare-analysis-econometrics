import requests
import pandas as pd


def get_county_codes():
    url = 'https://api.census.gov/data/2010/dec/sf1?get=NAME&for=county:*'
    state_url = 'https://api.census.gov/data/2010/dec/sf1?get=NAME&for=state:*'

    # get the fips data
    r = requests.get(url)
    r2 = requests.get(state_url)
    fips_codes = pd.DataFrame.from_records(r.json())
    state_codes = pd.DataFrame.from_records(r2.json())

    # elevate headers from the first record
    fips_codes.columns = fips_codes.iloc[0]
    fips_codes = fips_codes[1:]

    state_codes.columns = state_codes.iloc[0]
    state_codes = state_codes[1:]

    fips_codes['cnty_fips'] = fips_codes['state'].astype(str) + fips_codes['county'].astype(str)
    fips_codes['cnty_fips'] = fips_codes['cnty_fips'].astype('int64')

    merged = pd.merge(fips_codes, state_codes, on='state', how='left', suffixes=('_county', '_state'))

    '''
        Clean up the data and remove unnecessary stuff
    '''

    # clean up d types
    merged['NAME_county'] = merged['NAME_county'].astype(str)
    merged['NAME_state'] = merged['NAME_state'].astype(str)

    # delete unnecessary columns
    del merged['state']
    del merged['county']

    # rename county name
    merged['County Name'] = merged['NAME_county'].str.split(',').str[0]

    del merged['NAME_county']
    merged['State Name'] = merged['NAME_state']
    del merged['NAME_state']

    return merged


def get_insurance_data():
    df = pd.read_csv('insurance rates.csv')

    del df['theme_range']
    del df['display_name']

    df['pctuninsure'] = df['Value'] / 100
    del df['Value']

    return df


counties = get_county_codes()
insurance = get_insurance_data()

merged = pd.merge(counties, insurance, on='cnty_fips', how='left')

print(merged.info())
print(merged.head())
