sudo apt-get update
sudo apt-get install -y git curl python3-pip
pip3 install virtualenvwrapper
echo "source /home/ubuntu/.local/bin/virtualenvwrapper.sh" >> ~/.bashrc
source ~/.bashrc
git clone https://github.com/crazyfrogspb/elasticsmapp.git
cd elasticsmapp
mkvirtualenv --python=/usr/bin/python3 elastic
pip install -e .
pip install -r requirements.txt
