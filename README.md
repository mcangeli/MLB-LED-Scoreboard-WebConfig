# MLB-LED-Scoreboard-WebConfig
Web Configuration Add in for MLB-LED-Scoreboard - https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard

This simple web configurator adds a simple web service that allows the user to edit config.json, colors/teams.json, colors/scoreboard.json and the wifi network
in a simple web based text editor.

<img width="1888" height="878" alt="image" src="https://github.com/user-attachments/assets/5053cfa8-425a-42a2-a245-8dbf84dd5e67" />


There is also a function to restart the mlb-led-scoreboard.service via systemctl. 

This configurator *DOES NOT* have any authentication required, only use this on systems that are not directly accessed from an outside network.

# To install:
```
cd mlb-led-scoreboard
git clone https://github.com/mcangeli/MLB-LED-Scoreboard-WebConfig.git
mv MLB-LED-Scoreboard-WebConfig webconfig
```
to run:
```
sudo venv/bin/python3 webconfig/config_editor.py
```

When running, the configurator can be accessed via webbrowser at http://<ip-address>:5000
(I start a screen session and run it in screen so I can disconnect from the pi)

# Optional Startup Script

To create a systemctl start up script...

```
sudo nano /lib/systemd/system/mlb-webconfig.service
```

Paste in to the file:
```
  [Unit]
  Description=MLB LED Scoreboard WebConfig
  Wants=network-online.target time-sync.target
  After=network.target network-online.target time-sync.target

  [Service]
  Environment=""
  WorkingDirectory=/home/HOMEDIR/mlb-led-scoreboard
  ExecStartPre=/bin/sleep 15
  ExecStart=/home/HOMEDIR/mlb-led-scoreboard/venv/bin/python /home/HOMEDIR/mlb-led-scoreboard/webconfig/config_editor.py $SCOREBOARD_ARGS
  Restart=always
  RestartSec=2

  [Install]
  WantedBy=multi-user.target
```

Change HOMEDIR to the user that you have the mlb-scoreboard setup under.

Then run:
```
$  sudo systemctl enable mlb-webconfig.service
```

This will now start the webconfig server when the pi boots.
You can run:
```
sudo systemctl start mlb-webconfig.service
```
to run it and test it.
The webconfig is available at http://scoreboard-IP-Address:5000/

