# MLB-LED-Scoreboard-WebConfig
Web Configuration Add in for MLB-LED-Scoreboard - https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard

This simple web configurator adds a simple web service that allows the user to edit config.json, colors/teams.json, colors/scoreboard.json and the wifi network
in a simple web based text editor.

<img width="1888" height="878" alt="image" src="https://github.com/user-attachments/assets/5053cfa8-425a-42a2-a245-8dbf84dd5e67" />


There is also a function to restart the mlb-led-scoreboard.service via systemctl. 

This configurator *DOES NOT* have any authentication required, only use this on systems that are not directly accessed from an outside network.

To install:
```
cd mlb-led-scoreboard
sudo venv/bin/pip3 install flask
```
Once Flask is installed:
```
git clone https://github.com/mcangeli/MLB-LED-Scoreboard-WebConfig.git
mv MLB-LED-Scoreboard-WebConfig webconfig
```
to run:
```
sudo venv/bin/python3 webconfig/config_editor.py
```

When running, the configurator can be accessed via webbrowser at http://<ip-address>:5000
(I start a screen session and run it in screen so I can disconnect from the pi)
