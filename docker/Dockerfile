FROM ubuntu:18.04
ENV	DISPLAY :0
RUN     apt-get update && apt-get install -y \
	nmap \
	hydra \ 
	git
RUN 	git clone https://github.com/GoVanguard/legion.git
RUN	cd legion; chmod +x ./startLegion.sh; mkdir /legion/tmp
WORKDIR	/legion
CMD 	["python3", "legion.py"]
