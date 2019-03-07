sudo apt-get update
sudo apt-get install -y git curl virtualenv
sudo groupadd docker
sudo gpasswd -a $USER docker
newgrp docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic test"
sudo apt update
sudo apt install -y docker-ce docker-compose
git clone https://github.com/crazyfrogspb/fast-cosine-similarity.git
cd fast-cosine-similarity
sudo apt install -y maven
mvn package
cd ..
git clone https://github.com/crazyfrogspb/docker-elk.git
mv fast-cosine-similarity/target/releases/staysense-cosine-sim-6.6.1.zip docker-elk/elasticsearch
cd docker-elk
docker-compose build
docker-compose up -d
sudo apt install -y python3-pip
sudo pip3 install virtualenvwrapper
echo "source /home/ubuntu/.local/bin/virtualenvwrapper.sh" >> ~/.bashrc
source ~/.bashrc
cd ..
git clone https://github.com/crazyfrogspb/elasticsmapp.git
cd elasticsmapp
mkvirtualenv --python=/usr/bin/python3 elastic
pip install -e .
pip install -r requirements.txt
wget https://files.pushshift.io/reddit/comments/RC_2008-01.bz2
python elasticsmapp/utils/put_data.py --filename RC_2008-01.bz2 \
--index_name reddit --calc_embeddings --compression bz2
