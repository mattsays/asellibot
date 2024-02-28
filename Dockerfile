FROM python:3.9 
ADD requirements.txt / 
RUN pip3 install -r requirements.txt
ADD src/* /asellibot/
CMD ["python", "/asellibot/main.py"] 