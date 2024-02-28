FROM python:3.9 
ADD src/* /asellibot
ADD requirements.txt / 
RUN pip3 install -r requirements.txt
CMD ["python", "/asellibot/main.py"] 
