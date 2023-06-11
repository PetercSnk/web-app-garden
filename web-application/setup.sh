pip install virtualenv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mv automated-garden.service /etc/systemd/system/
sudo systemctl enable automated-garden
sudo systemctl start automated-garden
