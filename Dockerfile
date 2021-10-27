FROM python:3.9-buster
WORKDIR /vrf-initializer
ADD main.py .

ENV VRF_INITIALIZER_CONFIG=/vrf-initializer/config.json
ENV VRF_INITIALIZER_TIMEOUT=5

ENTRYPOINT python main.py -f ${VRF_INITIALIZER_CONFIG} -d -t ${VRF_INITIALIZER_TIMEOUT}