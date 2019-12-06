from python:3
ADD rssreader.py /
RUN pip install feedreader
CMD [ "python" , "./rssreader.py" ]
