# Use the official AWS Lambda Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.11

# Set environment variables
ENV API_BASE=/ \
    SOLR_URL=http://3.132.90.207:8983 \
    SOLR_BASE=/solr/blacklight-core/

# Copy function code and requirements.txt to the /var/task directory in the container
COPY lambda_function.py requirements.txt /var/task/

# Install dependencies
RUN pip install -r /var/task/requirements.txt

# Set the CMD to your handler (could be app.lambda_handler if your function is in app.py and named lambda_handler)
CMD ["lambda_function.lambda_handler"]
