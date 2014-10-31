FROM hjacobs/flask

ADD pequod.xml /
ADD run.py /

CMD ["/run.py"]
