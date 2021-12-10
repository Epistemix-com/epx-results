# You can build this image locally by running
#   docker build -t epistemix-py .
# You can run `tox` in a container by then running
#   docker run --rm -it epistemix-py

# Image based on 335566905560.dkr.ecr.us-east-1.amazonaws.com/fred-core:latest
# See https://github.com/Epistemix-com/FRED-tools/ for details
FROM 335566905560.dkr.ecr.us-east-1.amazonaws.com/fred-tools

WORKDIR /epx-results

COPY ./requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

COPY ./ ./

CMD tox
