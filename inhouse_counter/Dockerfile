FROM python:3.9
# Or any preferred Python version.
ENV CONFIG="/configs/config.json"
ADD src/* /
RUN pip3 install -r requirements.txt
CMD ["python", "./main.py"]
