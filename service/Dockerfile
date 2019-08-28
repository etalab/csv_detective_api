FROM continuumio/miniconda3

COPY . /app

WORKDIR /app

RUN  apt-get update -y

RUN  apt-get install build-essential -y

RUN  apt-get install unzip

RUN  conda env update --file environment.yml

RUN  wget https://codeload.github.com/psorianom/csv_detective/zip/parse_table_modified

RUN  unzip parse_table_modified

EXPOSE 5000

ENTRYPOINT ["/opt/conda/envs/csv_deploy/bin/python"]

ENV PYTHONPATH ./csv_detective-parse_table_modified

CMD ["api.py"]
