from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_certificatemanager as acm,
    aws_s3_deployment as s3deploy,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_iam as iam,
    RemovalPolicy
)
from constructs import Construct

class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #ADD YOUR DOMAIN HERE
        site_domain_name = 'example.com'

        #ADD YOUR DOMAIN HERE
        www_domain_name = 'www.example.com'

        #Specify hosted zone that is already created
        hosted_zone = route53.HostedZone.from_hosted_zone_attributes(self,"hosted_zone",
            zone_name=site_domain_name+'.',
            hosted_zone_id='YOUR_HOSTED_ZONE_ID_HERE',
        )

        #Create certificate in ACM
        certificate = acm.Certificate(self,"site_certificate",
            domain_name=www_domain_name,
            subject_alternative_names=[site_domain_name],
            validation=acm.CertificateValidation.from_dns()
        )

        #Create S3 bucket to host website files
        website_bucket = s3.Bucket(self, "WebsiteBucket",
            website_index_document="index.html",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        #This property will place your website files into the bucket, a zip folder that conatains directory for website
        s3deploy.BucketDeployment(self, "DeployWebsite",
            sources=[s3deploy.Source.asset(r"/Path/to/ZipFolder")],
            destination_bucket=website_bucket,
        )

        #Create Access OIA to only allow access to bucket from CloudFront
        origin_access_identity = cloudfront.OriginAccessIdentity(self, "MyOriginAccessIdentity",
            comment="OIA for S3 site"
        )

        #Create IAM Policy si that only CloudFront can get S3 objects
        cloudfrontUserAccessPolicy = iam.PolicyStatement()
        cloudfrontUserAccessPolicy.add_actions('s3:GetObject')
        cloudfrontUserAccessPolicy.add_principals(origin_access_identity.grant_principal)
        cloudfrontUserAccessPolicy.add_resources(website_bucket.arn_for_objects('*'))
        website_bucket.add_to_resource_policy(cloudfrontUserAccessPolicy)

        #Create Cloudfront distrobution and specify where index.html resides
        cf_distribution = cloudfront.CloudFrontWebDistribution(self, "MyCfWebDistribution",
            origin_configs=[cloudfront.SourceConfiguration(
                s3_origin_source=cloudfront.S3OriginConfig(
                    s3_bucket_source=website_bucket,
                    origin_access_identity=origin_access_identity,
                    origin_path="/Path/To/index.html",
                ),
                behaviors=[cloudfront.Behavior(is_default_behavior=True)]
            )
            ],  
            viewer_certificate=cloudfront.ViewerCertificate.from_acm_certificate(
                certificate,aliases=[site_domain_name, www_domain_name]
            )
        )

        #Create record within Hosted Zone
        hosted_zone_record = route53.ARecord(self,"site-alias-record",
            record_name=site_domain_name,
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(cf_distribution)
            ),
        )
