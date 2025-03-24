import boto3
import boto3.session
from django.conf import settings


class bucket:

    def __init__(self):
        session = boto3.session.Session()
        self.connection = session.client(
            service_name = settings.AWS_SERVICE_NAME ,
            aws_access_key_id = settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url = settings.AWS_S3_ENDPOINT_URL
        )

        