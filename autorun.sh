screen -d -m -S GardenPi
screen -S GardenPi -X stuff "cd ~Documents/repo/Automated-Garden"$(echo -ne "\015")
screen -S GardenPi -X stuff "python pi.py"$(echo -ne "\015")
