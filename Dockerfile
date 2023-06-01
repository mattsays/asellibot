FROM python:3.9 
# Or any preferred Python version.
ENV CONFIG="/configs/config.json"
ENV SSL_CERT="/configs/pub.cert"
ENV SSL_KEY="/configs/key.priv"
ADD src/* /
ADD requirements.txt / 
RUN pip3 install -r requirements.txt
CMD ["python", "./main.py"] 
