# cdk-python-static-site
CDK Stack to create a static S3 site behind a CloudFront Distribution
The resources created include:

- ACM certificate for HTTPS
- Private S3 bucket to host the website files
- CloudFront distribution acting as a CDN and [origin access identity](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html) so that website is only accessible through CloudFront Distrobution


## Prerequisites
- A registered domain (I used Google Domains)
- Already created hosted zone in route 53
- An AWS Account

## Install, Build, Deploy and Clean up
### CDK
Install AWS CDK Toolkit
```sh
npm install -g aws-cdk
```
Verify the installation
```sh
cdk --version
```
Bootstrap the AWS environment
```
cdk bootstrap aws://123456789012/us-east-1
```

### Python Setup
Create a python virtual environment in the root directory of the example.

```sh
python3 -m venv .env
```
Activate the virtual environment and install the dependencies.
```sh
source .env/bin/activate
pip install -r requirements
```

Synthesize the CloudFromation template.
```sh
cdk synth
```
Deploy the stack.
> Make sure your aws profile has sufficient permissions to create the resources. Update the `cdk.json` according to your settings. See the [Context Values](#context-values) down below.
```sh
cdk deploy
```

Set-up the relevant CNAMEs for ACM - the infrastructure deployment will not complete until the ACM validation is complete. (The CNAMEs that need to be created will be visible through the [AWS console](https://us-east-1.console.aws.amazon.com/acm/home?region=us-east-1#/certificates))


Clean up and remove the stack.
```sh
cdk destroy
```
