# GSheets Timetracker

Tracking time using command line and save it to Google Sheets

## Prerequisites

1. Python >= 2.7.x

## Setup

1. Go to [Google API console](https://console.developers.google.com), register a Google project, enable Google Drive API and save the private key as `secret.json` in the same directory as this app
1. Update your email (attribute `GOOGLE_DRIVE_EMAIL`) in `config.json`. This email will get invited to edit timetracker sheet
1. Install dependencies `pip install -r requirements.txt`

## Running

Run `g-sheets-timetracker.py` from command line. Example:

```
$ python g-sheets-timetracker.py "GSheets Timetracker" -t "Updating README"

```

Usage:

```
usage: g-sheets-timetracker.py [-h] [-t TASK_DESCRIPTION] PROJECT_NAME
```

Argument and options:

```
Positional arguments:
  PROJECT_NAME          Name of the project that you are going to work on

optional arguments:
  -h, --help            show this help message and exit
  -t TASK_DESCRIPTION, --task TASK_DESCRIPTION
                        Short description of task(s) that you are going to do
```