import boto3
import os

def upload_to_s3(file, filename):
    s3 = boto3.client('s3')
    bucket_name = os.getenv("S3_BUCKET_NAME")
    cf_url = os.getenv("CLOUDFRONT_URL") # https://d2m5oabzl8xgps.cloudfront.net

    s3.upload_fileobj(
        file,
        bucket_name,
        filename,
        ExtraArgs={"ContentType": file.content_type}
    )
    
    # MENGEMBALIKAN URL CLOUDFRONT (PENTING!)
    return f"{cf_url}/{filename}"