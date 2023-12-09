#!/usr/bin/activate
import aws_cdk as cdk
from aws_cdk import Tags
from aws_cdk_infra.stack import BucketStack
from aws_cdk_infra.stack import CertStack
import json

# Read configuration from the JSON file
with open('config.json', 'r') as config_file:
    env_params = json.load(config_file)

app = cdk.App()
website_cert = CertStack(app, "simple-statc-site-cert-stack",
    description="Create Cert in us-east-1 (required)",
    env_params = env_params,
    env=cdk.Environment(account=env_params['aws_account'], region='us-east-1'),
    cross_region_references=True
    )

website_bucket = BucketStack(app, f"simple-statc-site-bucket-stack",
    description="Static Site Example",
    env_params = env_params,
    env=cdk.Environment(account=env_params['aws_account'], region=env_params['region']),
    zone=website_cert.zone,
    certificate=website_cert.certificate,
    cross_region_references=True
    )

app.synth()