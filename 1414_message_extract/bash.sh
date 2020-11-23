apt-get update \
    && apt-get install -y software-properties-common \
    && apt-get install -y build-essential tesseract-ocr \
    && apt-get update

apt-get install -y build-essential python3-pip
RUN apt-get install libpoppler-cpp-dev pkg-config -y && apt-get install poppler-utils -y

pip install psycopg2-binary && pip3 install opencv-contrib-python
pip install --no-cache-dir -r requirements.txt

COPY vie.traineddata /usr/share/tesseract-ocr/4.00/tessdata/vie.traineddata