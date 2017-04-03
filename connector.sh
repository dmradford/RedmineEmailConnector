#!/bin/bash
cd /home/user/Connector # Directory to connector.py
nice -n -15 nohup python connector.py
disown $!
