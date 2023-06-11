sudo apt-get install python3-venv
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
mv automated-garden.service /etc/systemd/system/
sudo systemctl enable automated-garden
sudo systemctl start automated-garden
