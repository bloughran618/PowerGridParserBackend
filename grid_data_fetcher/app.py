import json
from io import StringIO

import boto3
import pandas as pd


def lambda_handler(event, context):
    s3_client = boto3.client("s3")

    # Fetch the time series from the S3 bucket
    try:
        s3_response = s3_client.get_object(
            Bucket="power-grid-persisted-data",
            Key="persist.csv"
        )
        s3_object_body = s3_response.get('Body')
        content_str = s3_object_body.read().decode()

    except s3_client.exceptions.NoSuchBucket as e:
        print('The S3 bucket does not exist.')
        print(e)

    except s3_client.exceptions.NoSuchKey as e:
        print('The S3 objects does not exist in the S3 bucket.')
        print(e)

    # create the time series data for line plots
    df = pd.read_csv(StringIO(content_str))
    df_subset = df[["bucket", "BESS", "Solar", "Utility", "Genset", "Load"]]
    df_json = df_subset.to_json(orient="records")
    print(df_json)

    # build aggregate data for donut chart
    aggregate_data = []
    for col in ["BESS", "Solar", "Utility", "Genset"]:
        aggregate_data.append({
            "type": col,
            "value": round(df[col].sum(), 0)
        })
    aggregate_data_json = json.dumps(aggregate_data)
    print(aggregate_data_json)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "time_series": df_json,
            "aggregate_data": aggregate_data_json
        }),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        }
    }
