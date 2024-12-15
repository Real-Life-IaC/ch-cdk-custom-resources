FROM public.ecr.aws/lambda/python:3.11

# Install dependency
RUN pip3 install databricks-sdk boto3

# Copy only the relevant function code to the lambda
COPY handler.py ${LAMBDA_TASK_ROOT}/

CMD [ "handler.lambda_handler" ]
