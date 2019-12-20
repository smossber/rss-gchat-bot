from registry.access.redhat.com/ubi8/python-27
ADD rssread.py ./
RUN pip install feedparser requests
CMD [ "python" , "./rssread.py" ]
