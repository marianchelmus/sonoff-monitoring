FROM public.ecr.aws/lambda/python:3.11
WORKDIR /app
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt
COPY main.py ${LAMBDA_TASK_ROOT}
CMD ["main.handler"]