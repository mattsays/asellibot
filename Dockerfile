FROM python:3.9-alpine
ADD requirements.txt / 
RUN pip3 install --no-cache -r requirements.txt
ADD src/* /asellibot/
CMD ["python", "/asellibot/main.py"] 