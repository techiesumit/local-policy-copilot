"""Bedrock model provider.

This module provides a `BedrockProvider` class that integrates with AWS Bedrock
to handle chat requests using the Bedrock runtime API.
"""

import json
import boto3
from botocore.config import Config
from app.providers.base import ModelProvider

class BedrockProvider(ModelProvider):
    """Provider that calls AWS Bedrock.

    Args:
        region: AWS region string.
        model_id: identifier for the Bedrock model to use.
        timeout_seconds: request timeout in seconds.
    """

    def __init__(self, region: str, model_id: str, timeout_seconds: int):
        self.model_id = model_id
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region,
            config=Config(read_timeout=timeout_seconds, connect_timeout=5, retries={"max_attempts": 2}),
        )

    def chat(self, user_text: str) -> str:
        """Send `user_text` to Bedrock and return the response."""
        # invoke_model requires JSON body, modelId, and permission bedrock:InvokeModel.
        body = json.dumps({"inputText": user_text}).encode("utf-8")
        resp = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=body,
        )
        return resp["body"].read().decode("utf-8")
