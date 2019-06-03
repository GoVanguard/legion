FROM ubuntu:18.04
ENV	DISPLAY :0
RUN     apt-get update && apt-get install -y \
        python \
        python-pip \
        python3 \
        python3-pip \
	nmap \
	hydra \ 
	git
RUN 	git clone https://github.com/GoVanguard/legion.git
RUN	cd legion && chmod +x ./startLegion.sh && chmod +x ./deps/* -R && chmod +x ./scripts/* -R && mkdir /legion/tmp
RUN	cd legion && pip3 install -r requirements.txt --upgrade
RUN	pip3 install service_identity --upgrade
RUN     cd legion && chmod a+x ./deps/primeExploitDb.py && ./deps/primeExploitDb.py
RUN     cd legion && ./deps/Ubuntu-18.sh
RUN	cd legion && ./startLegion.sh setup
WORKDIR	/legion
CMD 	["python3", "legion.py"]
