FROM ubuntu:18.04
ENV	DISPLAY :0
RUN     apt-get update && apt-get install -y \
        python3 \
        python3-pip \
	nmap \
	hydra \ 
	git
RUN 	git clone https://github.com/GoVanguard/legion.git
RUN	cd legion; chmod +x ./startLegion.sh; chmod +x ./deps/ -R; chmod +x ./scripts/ -R; mkdir /legion/tmp;./startLegion.sh setup
WORKDIR	/legion
CMD 	["python3", "legion.py"]
