Step 1:

Launch EC2 (Ubuntu 20.04 or 22.04 LTS)

Set Inbound Rules in the security group:

HTTP → Port 80

HTTPS → Port 443

SSH → Port 22 (your IP)

Connect using PuTTY or VS Code SSH

Step 2: intall Required packages

sudo apt update
sudo apt install apache2 libapache2-mod-wsgi-py3 python3-venv git python3-pip -y


Step 3: git clone

cd /var/www/html
sudo git clone -b reyaz11 https://github.com/Sri-Karthick-S/Music-Subscription.git
sudo mv Music-Subscription MusicApp
sudo chown -R ubuntu:www-data MusicApp
cd MusicApp

if any error : 
git config --global --add safe.directory /var/www/html/MusicApp
sudo chown -R $USER:$USER .git


Step 4: Set Up Python Environment

python3 -m venv venv
source venv/bin/activate

pip install flask boto3 requests
pip freeze > requirements.txt

pip install -r requirements.txt

Step 5: Configure WSGI

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/html/MusicApp")

from app import app as application


Step 6: Apache Config for HTTP

sudo nano /etc/apache2/sites-available/music.conf

<VirtualHost *:80>
    ServerName YOUR_PUBLIC_DNS

    WSGIDaemonProcess music python-home=/var/www/html/MusicApp/venv python-path=/var/www/html/MusicApp
    WSGIProcessGroup music
    WSGIScriptAlias / /var/www/html/MusicApp/wsgi.py

    <Directory /var/www/html/MusicApp>
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/music_error.log
    CustomLog ${APACHE_LOG_DIR}/music_access.log combined
</VirtualHost>


sudo a2ensite music.conf
sudo a2dissite 000-default.conf
sudo systemctl reload apache2


Step 7: Enable SSL (HTTPS)

sudo a2enmod ssl
sudo systemctl restart apache2

Step 8: Apache Config for HTTPS

sudo nano /etc/apache2/sites-available/music-ssl.conf

<VirtualHost *:443>
    ServerName YOUR_PUBLIC_DNS

    WSGIDaemonProcess music_ssl python-home=/var/www/html/MusicApp/venv python-path=/var/www/html/MusicApp
    WSGIProcessGroup music_ssl
    WSGIScriptAlias / /var/www/html/MusicApp/wsgi.py

    <Directory /var/www/html/MusicApp>
        Require all granted
    </Directory>

    SSLEngine on
    SSLCertificateFile /etc/apache2/ssl/apache-selfsigned.crt
    SSLCertificateKeyFile /etc/apache2/ssl/apache-selfsigned.key

    ErrorLog ${APACHE_LOG_DIR}/ssl_error.log
    CustomLog ${APACHE_LOG_DIR}/ssl_access.log combined
</VirtualHost>


sudo a2ensite music-ssl.conf
sudo systemctl reload apache2


Step 9: Access the App

Open your browser:

HTTP: http://ec2-xx-xx-xx-xx.compute-1.amazonaws.com

HTTPS: https://ec2-xx-xx-xx-xx.compute-1.amazonaws.com





to Restart the server.:

1. Restart Your EC2 Instance

Go to EC2 Console

Select your instance

Click Actions > Instance State > Start


Step 2:  SSH Into the EC2 Instance


Step 3: Start Apache


 Step 4: Pull Latest Code (if you've updated Git)

cd /var/www/html/MusicApp
sudo git pull origin reyaz11


Step 5: Activate Virtual Environment and Install Dependencies

cd /var/www/html/MusicApp
source venv/bin/activate
pip install -r requirements.txt

Step  6. Reload Apache (if app or WSGI changed)
sudo systemctl reload apache2

Step 7: Check Logs (if there's an error)

sudo tail -n 50 /var/log/apache2/error.log
