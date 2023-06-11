sudo apt-get install python3-venv
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
sudo cp automated-garden.service /etc/systemd/system/
sudo systemctl enable automated-garden
sudo systemctl start automated-garden
sudo apt-get install nginx
sudo cp automated-garden.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/automated-garden.conf /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx