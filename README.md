# Realistic Battery
Control Android battery level realistically. What a cool party trick!

> [!WARNING]
> The quick run scripts only work on Linux and macOS. You will need to manually install Realistic Battery if yuo would like to use it on Windows.

> [!TIP]
> Install ADB and Python3 to your PATH before running, or it won't work!

# Features:

Gradual Battery Drain

Setable Percentage (Up to 9999, down to 0)

Supports charging and discharging status unlike most scripts

No Root Required

Linux, macOS, and Windows support

# Example Scenario

You can show your buddies that your phone is charged to 356 percent, or 9999 percent, or 2056 percent!

# How to run (UNIX Users/Quick Run)

GUI: ```curl -LO https://raw.githubusercontent.com/EmoticonYT/realistic_battery/refs/heads/main/gui.sh; bash gui.sh; rm -rf gui.sh```

CLI: ```curl -LO https://raw.githubusercontent.com/EmoticonYT/realistic_battery/refs/heads/main/cli.sh; bash cli.sh; rm -rf gui.sh```

STOP: ```https://raw.githubusercontent.com/EmoticonYT/realistic_battery/refs/heads/main/stop.sh; bash stop.sh; rm -rf stop.sh```

# How to download/install (Windows Users)

Download the contents of the "realisticbattery" folder and open a Terminal window inside it. Powershell is prefered. Next, run ```pip3 install -r requirements.txt```.

# How to run (Windows Users)

GUI: ```python3 realistic_battery.py --gui```

CLI: ```python3 realistic_battery.py```

STOP: ```python3 realistic_battery.py --stop```


