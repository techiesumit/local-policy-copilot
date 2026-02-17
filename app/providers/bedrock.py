import json
import boto3
from botocore.config import Config
from .base import ModelProvider

class BedrockProvider(ModelProvider):
    def __init__(self, region: str, model_id: str, timeout_seconds: int):
        self.model_id = model_id
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=region,
            config=Config(read_timeout=timeout_seconds, connect_timeout=5, retries={"max_attempts": 2}),
        )

    def chat(self, user_text: str) -> str:
        # invoke_model requires JSON body, modelId, and permission bedrock:InvokeModel. [page:1]
        body = json.dumps({"inputText": user_text}).encode("utf-8")
        resp = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=body,
        )  # [page:1]
        return resp["body"].read().decode("utf-8")
