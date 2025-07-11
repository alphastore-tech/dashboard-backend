import boto3


def get_aws_secret(secret_id: str, region: str = "ap-northeast-2") -> str:
    """
    AWS Secrets Manager에서 문자열(또는 JSON)을 바로 가져온다.
    """
    client = boto3.client("secretsmanager", region_name="ap-northeast-2")
    resp = client.get_secret_value(SecretId=secret_id)
    return resp["SecretString"]
