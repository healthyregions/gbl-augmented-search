# Creating Image

> Instructions are for Windows, minor changes might be needed for Linux of Mac

[AWS Documentation](https://docs.aws.amazon.com/AmazonECR/latest/userguide/getting-started-cli.html)

## Install AWS CLI

## Configure AWS CLI
```bash
aws configure
```

## Login to ECR
```bash
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 321523027620.dkr.ecr.us-east-2.amazonaws.com
```

## Creating AWS ECR Repository
```bash
aws ecr create-repository \
    --repository-name sdoh-ecr \
    --region us-east-2
```

## Creating Docker Build
```bash
docker build -f .\ecr.dockerfile -t lambda_nltk .
```

## Adding Tag to the Docker Build
```bash
docker tag lambda_nltk:latest 321523027620.dkr.ecr.us-east-2.amazonaws.com/sdoh-ecr
```

## Pushing the Build to AWS
```bash
docker push 321523027620.dkr.ecr.us-east-2.amazonaws.com/sdoh-ecr
```

docker build -f .\ecr.dockerfile -t lambda_nltk . | docker tag lambda_nltk:latest 321523027620.dkr.ecr.us-east-2.amazonaws.com/sdoh-ecr | docker push 321523027620.dkr.ecr.us-east-2.amazonaws.com/sdoh-ecr