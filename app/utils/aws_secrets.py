import boto3
import json

def get_aws_secret(secret_id: str) -> str:
    """
    AWS Secrets Manager에서 문자열(또는 JSON)을 바로 가져온다.
    """
    client = boto3.client("secretsmanager", region_name="ap-northeast-2")
    resp = client.get_secret_value(SecretId=secret_id)
    
    access_token = json.loads(resp["SecretString"])["access_token"]
    return access_token
