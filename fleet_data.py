import pandas as pd
from datetime import datetime

def initialize_fleet_data():
    data = {
        'Reg.': ['TC-ABC', 'TC-DEF', 'TC-GHI'],
        'Aircraft Type': ['B737', 'B737', 'A320'],
        'Aircraft Variant': ['800NG', 'MAX8', '320ceo'],
        'Date of Manufacture': [datetime(2010, 5, 20), datetime(2018, 6, 15), datetime(2012, 7, 10)],
        'DOI': [datetime(2011, 3, 1), datetime(2019, 1, 15), datetime(2013, 9, 5)],
        'DOE': [pd.NaT, pd.NaT, pd.NaT],
        'Lease Type': ['operational', 'financial', 'own'],
        'Lease End Date': [datetime(2026, 3, 1), pd.NaT, pd.NaT],
        'Market Value': [18000000, 25000000, 11500000],
        'Monthly Lease (OPS)': [250000, pd.NA, pd.NA]
    }
    return pd.DataFrame(data)
