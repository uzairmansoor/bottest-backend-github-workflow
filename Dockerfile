FROM public.ecr.aws/lambda/python:3.10

# Copy function code into a subdirectory named "src"
COPY ./src ${LAMBDA_TASK_ROOT}/src

# Add the "src" subdirectory to the Python path
ENV PYTHONPATH=${PYTHONPATH}:${LAMBDA_TASK_ROOT}/src

# Install the function's dependencies using file requirements.txt from your project folder.
COPY requirements.txt .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}" -U --no-cache-dir

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.handler" ]