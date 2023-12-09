# AWS CDK Simple S3 Static Site with a Route 53 Domain and CD Pipeline

This project contains AWS CDK (Cloud Development Kit) stacks for deploying a web application with AWS resources like S3, CloudFront, Route53, ACM, IAM, and CodePipeline.

This AWS CDK Project was created in conjuction with [this](https://github.com/grantwittenberg/static-site-example.git) static site repository. However, you can easily adapt this code for your own static site.

Note: The following instructions are for MacOS and Linux

## Prerequisites

### Before you begin, ensure you have the following installed:
- [Node.js](https://nodejs.org/) (For AWS CDK)
- [AWS CLI](https://aws.amazon.com/cli/)
- [Python](https://www.python.org/downloads/) (Version 3.x)
- [Pipenv](https://pipenv.pypa.io/en/latest/) for Python dependency management

### Other Reqirements
- **Domain name available in AWS Route 53**

## Setting Up - AWS Steps
**GitHub Token stored in AWS SSM**:  
This is use for the CD pipeline in order to pull Github updates automatically.
 1. Create a GitHub Token:
     1. In GitHub, go to Settings > Developer settings > Personal access tokens.
     2. Generate a new token with necessary permissions and copy it.
 2. Access AWS SSM:
     1. Log in to the AWS Management Console.
     2. Navigate to Systems Manager > Parameter Store.
 3. Create a New Parameter:
     1. Choose “Create parameter”.
     2. Name the parameter (e.g., /github/token) and set type to “SecureString”.
     3. Paste the GitHub token in the "Value" field.
     4. Click "Create Parameter" to save.

## Setting Up - Add your config.json file
1. Copy the config.example.json file to a new file config.json
2. Add your config.json file to .gitignore if using a public repository
3. Update the config values for your AWS account and website

## Setting Up - CLI Steps

1. **Configure AWS CLI**:8888889
   ```sh
   aws configure
   ```
   Enter your AWS Access Key ID, Secret Access Key, default region name, and output format.

2. **Clone the Repository**:
   ```sh
   git clone https://github.com/grantwittenberg/aws-static-site-example.git
   ```

3. **Install Node.js Dependencies**:
   ```sh
   npm install -g aws-cdk
   ```

4. **Setup Python Virtual Environment**:
   ```sh
   pipenv install
   pipenv shell
   ```

5. **Bootstrap the CDK Toolkit** (if you haven't done this before for your AWS account/region):
   ```sh
   cdk bootstrap
   ```

6. **Manually create a virtualenv**:
    ```sh
    python3 -m venv .venv
    ```

7. **Activate your virtualenv**:
    ```sh
    source .venv/bin/activate
    ```

8. **Once the virtualenv is activated, you can install the required dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

9. **Synthesize the CloudFormation template for this code (this executing successfully is a decent validation of your environment configuration)**:
    ```sh
    cdk synth
    ```

## Deploying the Stacks

To deploy the stacks to your AWS account, execute:

```sh
cdk deploy --all
```

This command will deploy all stacks defined in your application.

## Useful CDK Commands

- `cdk ls` lists all stacks in the app
- `cdk synth` emits the synthesized CloudFormation template
- `cdk diff` compares deployed stack with current state
- `cdk docs` opens the documentation

## Cleaning Up (Destroying Stacks)

To avoid incurring future charges, remember to destroy the stacks:

```sh
cdk destroy --all
```

This command will remove all the resources defined by the stacks from your AWS account.

## Important Notes

- Ensure you have the necessary AWS permissions to create and manage the resources defined in the CDK stacks.
- The `cdk destroy` command will remove all resources, including any stored data.
- Always review the resources and changes before deploying to your AWS environment.