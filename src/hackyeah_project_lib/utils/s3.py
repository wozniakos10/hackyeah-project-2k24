import logging
import os
from typing import Any

import boto3
from botocore.exceptions import ClientError

from hackyeah_project_lib.config import settings
from hackyeah_project_lib.utils.logger import get_configured_logger

logger = get_configured_logger("app_logger", log_file="logs/app.log", level=logging.DEBUG)


class S3:
    def __init__(self) -> None:
        self.s3_client = self.get_s3_client()

    # Initialize S3 client using environment variables
    def get_s3_client(self) -> boto3.client:
        return boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION,
        )

    def upload_file(self, file_name: Any, bucket: str | None = None, object_name: str | None = None) -> bool:
        """Upload a file to an S3 bucket

        :param file_name: File to upload (path or file-like object)
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified, file_name is used
        :return: True if file was uploaded, else False
        """

        if bucket is None:
            bucket = settings.S3_BUCKET_NAME

        if object_name is None:
            if isinstance(file_name, str):
                object_name = os.path.basename(file_name)
            else:
                object_name = file_name.name
        try:
            if isinstance(file_name, str):
                self.s3_client.upload_file(file_name, bucket, object_name)
            else:
                self.s3_client.upload_fileobj(file_name, bucket, object_name)
        except ClientError as e:
            logger.error(e)
            return False
        return True

    def download_file(self, object_name: str, file_name: str | None = None, bucket: str | None = None) -> bool:
        """Download a file from an S3 bucket

        :param object_name: S3 object name to download
        :param file_name: Local file name to save the downloaded object. If not specified, object_name is used
        :param bucket: Bucket to download from
        :return: True if file was downloaded, else False
        """
        if bucket is None:
            bucket = settings.S3_BUCKET_NAME

        if file_name is None:
            file_name = object_name

        s3_client = self.get_s3_client()
        try:
            s3_client.download_file(bucket, object_name, file_name)
        except ClientError as e:
            logger.error(e)
            return False
        return True

    def get_file_url(self, object_name: str, bucket: str | None = None, expiration: int = 3600) -> str | None:
        """Generate a presigned URL to share an S3 object

        :param object_name: S3 object name
        :param bucket: Bucket name
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Presigned URL as string. If error, returns None.
        """
        if bucket is None:
            bucket = settings.S3_BUCKET_NAME

        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': object_name},
                ExpiresIn=expiration
            )
        except ClientError as e:
            logger.error(e)
            return None

        return response