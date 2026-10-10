import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


def get_s3_client():
    if not settings.S3_BUCKET_NAME:
        raise RuntimeError("S3_BUCKET_NAME is not configured.")

    kwargs = {"region_name": settings.AWS_REGION}

    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

    return boto3.client("s3", **kwargs)


def upload_bytes(data: bytes, key: str, content_type: str) -> None:
    client = get_s3_client()
    client.put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=key,
        Body=data,
        ContentType=content_type,
    )


def create_download_url(key: str, filename: str) -> str:
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.S3_BUCKET_NAME,
            "Key": key,
            "ResponseContentDisposition": f'attachment; filename="{filename}"',
        },
        ExpiresIn=settings.S3_PRESIGNED_URL_EXPIRE_SECONDS,
    )


def delete_object(key: str) -> None:
    client = get_s3_client()
    client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)


def is_s3_error(exc: Exception) -> bool:
    return isinstance(exc, (ClientError, RuntimeError))