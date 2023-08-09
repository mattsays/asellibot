FROM python:3.9 
ADD src/* /
ADD requirements.txt / 
RUN pip3 install -r requirements.txt
CMD ["python", "./main.py"] 
