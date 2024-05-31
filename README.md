# Search Plugin

_Function, but still in development..._

This application creates an endpoint that can be used by GeoBlacklight instances in place of the default `SOLR_URL` environment variable. Hitting this endpoint with a `GET` request that has a `q` (query) parameter will engage `nltk` to expand the query terms and pass this expanded query on to Solr. Any other request will pass right through this function unaltered. When a response is received from Solr, it is passed back to the client.

![deployment architecture](./architecture.png)

## How to (re)build and push image to ECR

### Install and Configure AWS

_To do: What exactly are the necessary credentials?_

You must create an AWS user with the proper credentials, then use these credentials to configure your AWS CLI.

```bash
aws configure
```

### Login to ECR

```bash
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin AWS_ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com
```

If you get an error like this during login:

```
Error saving credentials: error storing credentials - err: exit status 1, out: `error storing credentials - err: exit status 1, out: `pass not initialized: exit status 1: Error: password store is empty. Try "pass init".``
```

try removing the `credsStore` line from your `~/.docker/config.json` file and then rerun the above command.

## Create AWS ECR Repository

_Only needed on first deployment._

```bash
aws ecr create-repository \
    --repository-name geoblacklight-search-plugin \
    --region us-east-2
```

## Create Docker build

```bash
docker build -f ./ecr.dockerfile -t lambda_nltk .
```

-t is the image name

### Add tag to build

Use the URI of the container repository created in the steps above.

```bash
docker tag lambda_nltk:latest AWS_ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com/geoblacklight-search-plugin
```

## Pushing build to AWS

```bash
docker push AWS_ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com/geoblacklight-search-plugin
```

## Simple rebuild commands

The following one-liner combines all steps described above:

```
docker build -f ./ecr.dockerfile -t lambda_nltk . && \
   docker tag lambda_nltk:latest AWS_ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com/geoblacklight-search-plugin && \
   docker push AWS_ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com/geoblacklight-search-plugin
```

There is also a bash script you can use to run the command above, which will look in your environment for an `AWS_ACCOUNT_ID` variable. Set this variable first with

```
export AWS_ACCOUNT_ID=<your account id>
```

and then run the script.

```
source ./scripts/rebuild_container.sh
```

## Update AWS Lambda image

Once an update has been made to the container, the Lambda needs to be redeployed with this new image. Go to **Image** > **Deploy new image** > **Browse images**. You should find the new image that is tagged with `latest`, select this and redeploy.

## Logs

Any `print()` statements in the lambda function will be written to a CloudWatch log for this lambda.

## References

[AWS Documentation](https://docs.aws.amazon.com/AmazonECR/latest/userguide/getting-started-cli.html)
