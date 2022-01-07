"""Script to read DC incident csv data and transform into map tiles
"""
import pandas as pd
from tqdm import tqdm
from os import path
from dot.geojson import make_point, make_point_collection
import json


def prepare_dc_crashes():
    df = pd.read_csv("Crashes_in_DC.csv", low_memory=False)
    df = df.dropna(subset=["LONGITUDE", "LATITUDE"])
    points = []
    for k, row in tqdm(df.iterrows(), total=len(df)):
        points.append(
            make_point(row['LONGITUDE'], row['LATITUDE'], drivers_impaired=bool(row['DRIVERSIMPAIRED']), speeding=bool(row['SPEEDING_INVOLVED']), date=row['REPORTDATE'])
        )
    collection = make_point_collection(points)
    with open("dcincidents.json", 'w') as outfile:
        json.dump(collection, outfile)


def prepare_us_accidents():
    us_acc_df = pd.read_csv('US_Accidents_June20.tar', low_memory=False)
    dc_acc_df = us_acc_df[us_acc_df['State'] == 'DC']
    dc_acc_df = dc_acc_df.dropna(subset=["Start_Lat", "Start_Lng"])

    points = []
    for k, row in tqdm(dc_acc_df.iterrows(), total=len(dc_acc_df)):
        points.append(
            make_point(row['Start_Lng'], row['Start_Lat'], date=row['Start_Time'],
                       severity=row['Severity'], temp_f=row['Temperature(F)'])
        )
    collection = make_point_collection(points)
    with open("us_incidents.json", 'w') as outfile:
        json.dump(collection, outfile)


if __name__ == "__main__":
    # TODO: Add CLI to select data to prepare
    prepare_dc_crashes()
    # TODO: Add US_Accidents to dvc
    prepare_us_accidents()
