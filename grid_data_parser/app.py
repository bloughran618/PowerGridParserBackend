import json

import boto3
import pandas as pd


def lambda_handler(event, context):
    s3_client = boto3.client("s3")

    # Fetch the time series from the S3 bucket
    try:
        s3_response = s3_client.get_object(
            Bucket="power-grid-time-series",
            Key="time_series_sample_json.txt"
        )
        s3_object_body = s3_response.get('Body')
        content_str = s3_object_body.read().decode()

    except s3_client.exceptions.NoSuchBucket as e:
        print('The S3 bucket does not exist.')
        print(e)

    except s3_client.exceptions.NoSuchKey as e:
        print('The S3 objects does not exist in the S3 bucket.')
        print(e)

    content_json = json.loads(content_str)
    try:
        df = pd.json_normalize(content_json["time_series"])
    except Exception as e:
        print("Failed to parse power grid time series data:")
        raise(e)

    print(f"head: {df.head}")

    # linearly interpolate BESS, Solar, Utility and Load values
    df["BESS"] = df["BESS"].interpolate()
    df["BESS_min"] = df["BESS_min"].interpolate()
    df["BESS_max"] = df["BESS_max"].interpolate()
    df["Solar"] = df["Solar"].interpolate()
    df["Solar_min"] = df["Solar_min"].interpolate()
    df["Solar_max"] = df["Solar_max"].interpolate()
    df["Utility"] = df["Utility"].interpolate()
    df["Utility_min"] = df["Utility_min"].interpolate()
    df["Utility_max"] = df["Utility_max"].interpolate()
    df["Load"] = df["Load"].interpolate()

    # fill Genset null values with 0's
    df["Genset"] = df["Genset"].fillna(0)
    df["Genset_min"] = df["Genset_min"].fillna(0)
    df["Genset_max"] = df["Genset_max"].fillna(0)

    # different interpolation methods can be easily applied using pandas

    # write processed data to .csv file in managed S3 bucket
    df.to_csv("/tmp/persist.csv", index=False)
    s3_client.upload_file(
        "/tmp/persist.csv",
        "power-grid-persisted-data",
        "persist.csv"
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Power grid time series persisted to power-grid-persisted-data",
        }),
    }
