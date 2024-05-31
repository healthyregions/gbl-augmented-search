#! /usr/bin/bash

docker build -f ./ecr.dockerfile -t lambda_nltk . && \
   docker tag lambda_nltk:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com/geoblacklight-search-plugin && \
   docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com/geoblacklight-search-plugin
