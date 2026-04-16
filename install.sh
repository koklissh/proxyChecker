#!/bin/bash
sudo chown -R $USER:$USER /opt/proxy-checker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "Done! Now run: nano config.py"