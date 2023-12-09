import aws_cdk as cdk
from aws_cdk import (
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam as iam,
    aws_route53 as route53,
    aws_s3 as s3
)
from aws_cdk.aws_cloudfront import (
    HttpVersion,
    PriceClass,
    ViewerProtocolPolicy
)
from aws_cdk.aws_route53_targets import CloudFrontTarget

class CertStack(cdk.Stack):
    
    def __init__(self, scope: cdk.App, construct_id: str, env_params:dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        root_domain_name = env_params['domain_name']
        full_domain_name = env_params['sub_domain']+env_params['domain_name']
        zone = route53.HostedZone.from_lookup(self, 'HostedZone', domain_name=root_domain_name)

        # In order to redirect HTTP request to HTTPS, create TLS cert with ACM. A CNAME record will be added to the hosted zone.
        certificate = acm.Certificate(self, 'SiteCertificate',
            domain_name=full_domain_name,
            validation=acm.CertificateValidation.from_dns(zone))
        
        # Expose these as properties of the class for other stack to use
        self.zone = zone
        self.certificate = certificate

class BucketStack(cdk.Stack):
    
    def __init__(self, scope: cdk.App, construct_id: str, env_params:dict, zone, certificate, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create S3 bucket for website files
        bucket = s3.Bucket(self, env_params['github_repository'],
            bucket_name = f"{env_params['github_repository']}-aws-cdk-demo-001",
            versioned=True,
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            access_control=s3.BucketAccessControl.PRIVATE,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True)
        
        # Create OAI, Origin Access Identity, user (allows users to access the file on the S3 bucket through CloudFront)
        cloudfrontOAI = cloudfront.OriginAccessIdentity(self, 'CloudFrontAccess')
        
        # Create bucket resource policy to grant the OAI user read only access
        cloudfrontUserAccessPolicy = iam.PolicyStatement()
        cloudfrontUserAccessPolicy.add_actions('s3:GetObject')
        cloudfrontUserAccessPolicy.add_principals(cloudfrontOAI.grant_principal)
        cloudfrontUserAccessPolicy.add_resources(bucket.arn_for_objects('*'))
        bucket.add_to_resource_policy(cloudfrontUserAccessPolicy)

        full_domain_name = env_params['sub_domain']+env_params['domain_name']

        # Create the CDN (cloudfront distribution)
        cloudfrontDistribution = cloudfront.Distribution(self, 'CloudFrontDistribution',
            comment='CDK Cloudfront Secure S3',
            certificate=certificate,
            domain_names=[full_domain_name],
            default_root_object=env_params['root_index_file'],
            price_class=PriceClass.PRICE_CLASS_100,
            http_version=HttpVersion.HTTP2,
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(bucket=bucket, origin_access_identity=cloudfrontOAI, origin_path=('/'+env_params['index_file_location'])),
                viewer_protocol_policy=ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                ))
        
        # Create the A record in the domain's hosted zone and point it to the CloudFront distribution
        route53.ARecord(self, 'ARecord',
            zone=zone,
            record_name=full_domain_name,
            target=route53.RecordTarget.from_alias(CloudFrontTarget(cloudfrontDistribution)))
        
        # Create S3 bucket for pipeline artifacts (this is necessary for automatic removal of the bucket)
        artifact_bucket = s3.Bucket(self, f"{env_params['github_repository']}Artifacts",
            bucket_name = f"{env_params['github_repository']}-pipeline-artifacts",
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True)

        # ----- Create pipeline for updating the web applicaiton code in S3 bucket -----
        pipeline_web_app =  codepipeline.Pipeline(self, "CDK_Pipeline_WebApp",
            pipeline_name=f"{env_params['github_repository']}-pipeline",
            restart_execution_on_update=True,
            cross_account_keys=False,
            artifact_bucket=artifact_bucket)
        source_output = codepipeline.Artifact()
        output_website = codepipeline.Artifact()
        
        pipeline_web_app.add_stage(
            stage_name="Source",
            actions=[codepipeline_actions.GitHubSourceAction(
                action_name="GitHub_Source",
                owner=env_params['github_owner'],
                repo=env_params['github_repository'],
                oauth_token=cdk.SecretValue.secrets_manager("github-token"),
                output=source_output,
                branch=env_params['branch'])])

        pipeline_web_app.add_stage(
            stage_name="Deploy",
            actions=[codepipeline_actions.S3DeployAction(
                action_name="DeployToS3",
                bucket=bucket,
                input=source_output)])
 