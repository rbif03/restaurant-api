import boto3
from botocore.exceptions import ClientError


def ssm_get_parameter(name, with_decryption=True):
    """
    Get a parameter from AWS Systems Manager Parameter Store.

    :param name: The name of the parameter to retrieve.
    :param with_decryption: Whether to decrypt the parameter if it's encrypted. Default is True.
    :return: The value of the parameter.
    """
    try:
        ssm_client = boto3.client("ssm")
        response = ssm_client.get_parameter(Name=name, WithDecryption=with_decryption)
        return response["Parameter"]["Value"]

    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "ParameterNotFound":
            return None
        else:
            raise e

    except Exception as e:
        raise e
