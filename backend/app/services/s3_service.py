import json
from typing import Any, Dict, Optional
import boto3
from botocore.exceptions import ClientError, BotoCoreError
from loguru import logger

from app.core.config import settings

FEATURE_PREFIXES = {
    "requirements": "requirements",
    "user_stories": "user-stories",
    "srs": "srs-diagrams",
    "uml": "uml-diagrams",
    "dfd": "dfd-diagrams",
    "database": "database-design",
    "planning": "project-planning",
    "estimation": "estimation",
    "risks": "risk-management",
    "tests": "test-cases",
    "traceability": "traceability",
    "metrics": "quality-metrics",
    "maintenance": "maintenance",
}


def get_s3_client():
    if not settings.S3_BUCKET_NAME:
        raise RuntimeError("S3_BUCKET_NAME is not configured.")

    kwargs = {"region_name": settings.AWS_REGION}

    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

    return boto3.client("s3", **kwargs)


def get_feature_s3_key(user_id: int, project_id: int, feature: str, document_id: str) -> str:
    """Generate consistent feature-specific S3 key for a project document."""
    prefix = FEATURE_PREFIXES.get(feature, feature)
    return f"users/{user_id}/projects/{project_id}/{prefix}/{document_id}.json"


def upload_bytes(data: bytes, key: str, content_type: str) -> None:
    client = get_s3_client()
    client.put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=key,
        Body=data,
        ContentType=content_type,
    )


def upload_json(data: Dict[str, Any], key: str) -> bytes:
    """Serialize and upload JSON to S3, returning the raw bytes."""
    payload = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
    upload_bytes(payload, key, "application/json")
    return payload


def get_json(key: str) -> Dict[str, Any]:
    """Retrieve and deserialize JSON document from S3."""
    client = get_s3_client()
    response = client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=key)
    body = response["Body"].read()
    return json.loads(body.decode("utf-8"))


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
    return isinstance(exc, (ClientError, BotoCoreError, RuntimeError))