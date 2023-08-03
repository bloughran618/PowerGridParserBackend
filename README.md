This application is a serverless application used to process time series data and provide the processed values to a frontend application via API Gateway
This is an AWS SAM application, see SAM docs for usage.

grid_data_parser is a function to process time series data
- Read the data from designated S3 bucket
- Interpolate the data so that there are no null values
- Persist the data in tabular format via .csv in another S3 bucket

grid_data_fetcher is a function to pass the time series data via API 
- Fetch the data persisted by grid_data_parser
- Calculate aggregate power generation values
- Return time series and aggregate values