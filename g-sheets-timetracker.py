#!/usr/bin/python

import argparse
import signal
import time
import sys
import json
import gspread
from collections import namedtuple
from oauth2client.service_account import ServiceAccountCredentials
from datetime import tzinfo, timedelta, datetime
from gspread.urls import DRIVE_FILES_API_V2_URL


APP_NAME = 'GSheetsTimetracker'
APP_DESC = 'Tracking time and save it to Google Sheets'
API_SECRET_FILE = 'secret.json'


class GSheetsTimetracker:
  
  def __init__(self, sheet, project, task):
    self.sheet = sheet
    self.project = project
    self.task = task
    self.start_time = datetime.now()
    self.end_time = None
    self.working_duration = None
    self.row_id = None
    self.ended = False
    # start tracking
    self.start()

  def start(self):
    print('{} Tracking time for project: "{}" on task: "{}"'.format(self.start_time, self.project, self.task))

    # write to google sheet
    self.row_id = self.sheet.next_available_row()
    self.sheet.update_acell('A{}'.format(self.row_id), self.project)
    self.sheet.update_acell('B{}'.format(self.row_id), self.task)
    self.sheet.update_acell('C{}'.format(self.row_id), self.start_time)

  def end(self, signal, frame):
    if not self.ended:
      self.end_time = datetime.now()
      self.working_duration = self.end_time - self.start_time

      # # TODO remove
      # self.working_duration = timedelta(hours=2, minutes=10)
      # self.end_time = self.start_time + self.working_duration

      print('{} Stoping time tracking for project: "{}" on task: "{}". Duration: {:0.1f} hour(s)'.format(self.end_time, self.project, self.task, self.working_duration_hours()))
      print('Updating data..')
      
      # write to gogle sheet
      self.sheet.update_acell('D{}'.format(self.row_id), self.end_time)
      self.sheet.update_acell('E{}'.format(self.row_id), self.working_duration_hours())
      print('Update completed.')

    sys.exit(0)
  
  def working_duration_text(self):
    """
    Get working duration in textual format
    """
    days = self.working_duration.days
    hours, seconds = divmod(self.working_duration.seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return '{} day(s) {} hour(s) {} minute(s) {} second(s)'.format(days, hours, minutes, seconds)


  def working_duration_hours(self):
    """
    Get working duration in hours
    """
    return self.working_duration.days / 24.0 + self.working_duration.seconds / 3600.0
  

# Helpers

def delete(self, spreadsheet_id):
  r = self.session.delete(DRIVE_FILES_API_V2_URL + '/' + spreadsheet_id)
  return r

def next_available_row(self):
    str_list = filter(None, self.col_values(1))  # fastest
    return len(str_list) + 1

if __name__ == '__main__':
  
  # capture arguments
  parser = argparse.ArgumentParser(description=APP_DESC)
  parser.add_argument('project', metavar='PROJECT_NAME', help='Name of the project that you are going to work on')
  parser.add_argument('-t', '--task', metavar='TASK_DESCRIPTION', default='TBD', help='Short description of task(s) that you are going to do')
  args = parser.parse_args()

  # load config
  with open('config.json') as f:
      config_dict = json.load(f)
      config = namedtuple("Config", config_dict.keys())(*config_dict.values())

  # init google drive api client
  scopes = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.appdata',
    'https://www.googleapis.com/auth/drive.apps.readonly'
  ]

  # add delete methods
  delete.func_name = 'delete'
  gspread.Client.delete = delete
  next_available_row.func_name = 'next_available_row'
  gspread.models.Worksheet.next_available_row = next_available_row

  try:
    print('Connecting to Google Drive..')
    creds = ServiceAccountCredentials.from_json_keyfile_name(API_SECRET_FILE, scopes)
    client = gspread.authorize(creds)
    doc = client.open(config.GOOGLE_SHEET_DOC)
    print('Google sheet document found')
    sheet = doc.sheet1    
    # if sheet.next_available_row() == 1:
    #   print('Empty sheet. Deleting doc id={}..'.format(doc.id))
    #   print(client.delete(doc.id))
    #   raise gspread.exceptions.SpreadsheetNotFound('File has been deleted')
  except IOError:
    print('No {} found in this directory'.format(API_SECRET_FILE))
  except gspread.exceptions.SpreadsheetNotFound:
    print('Google sheet document not found. Creating new one..')
    doc = client.create(config.GOOGLE_SHEET_DOC)
    doc.share(config.GOOGLE_DRIVE_EMAIL, perm_type='user', role='writer')
    sheet = doc.sheet1
    # write header
    sheet.update_acell('A1', 'Project')
    sheet.update_acell('B1', 'Task')
    sheet.update_acell('C1', 'Start Time')
    sheet.update_acell('D1', 'End Time')
    sheet.update_acell('E1', 'Duration')
    sheet.update_acell('F1', 'Remarks')
    print('Google sheet document created "{}" and shared with "{}"'.format(config.GOOGLE_SHEET_DOC, config.GOOGLE_DRIVE_EMAIL))


  # init timetracker
  g = GSheetsTimetracker(sheet, args.project, args.task)

  # track end time
  signal.signal(signal.SIGINT, g.end)
  signal.signal(signal.SIGTERM, g.end)

  # wait until killed
  while True:
    time.sleep(1)


    