from bs4 import BeautifulSoup
import requests
import json


def get_all_workout_links(stop_date):
  athlete_id = 33095
  break_bool = True
  step_count = -1

  json_data = {"data": []}
  while break_bool:
    url = f'http://www.running-log.com/calendar/step_calendar?athleteid={athlete_id}&step={step_count}'
    print('running with ', step_count)
    response = requests.post(url, cookies = {
      '_runlog_session': 'BAh7EDoPc2Vzc2lvbl9pZCIlYjJmMjNjODE4YTUzOTZiODEwMTdlODljOTM4MGY1YTdJIhJjYWxlbmRhcl95ZWFyBjoGRUZpAuAHSSITY2FsZW5kYXJfbW9udGgGOwZGaRFJIhFjYWxlbmRhcl9kYXkGOwZGaRBJIhZuYXZfY2FsZW5kYXJfZGF0ZQY7BkZVOglEYXRlWwtpAGkDSYAlaQBpAGkAZgwyMjk5MTYxSSISY2FsZW5kYXJfbW9kZQY7BkYiCm1vbnRoSSISY2FsZW5kYXJfdmlldwY7BkZJIg1jYWxlbmRhcgY7BkZJIgxhdGhsZXRlBjsGRm86DEF0aGxldGUHOhBAYXR0cmlidXRlc3sXIgdpZCIKMzMwOTUiCmxvZ2luIhlqc2hvd2FzaWFuQGdtYWlsLmNvbSIUc2FsdGVkX3Bhc3N3b3JkIi1hZWY2YmVlY2JlMGJkOTJkYWRmMDA1NzE1OTZlZjk3NWE2N2MzNzYxIg5maXJzdG5hbWUiCUpvc2giDWxhc3RuYW1lIg5TaG93YWx0ZXIiFGRlZmF1bHRfc2hvZV9pZCIKMzM2NzkiCXNhbHQiLTlkYTA5ZTQ5YjY3MWJmOTc1ODFmN2I0MTlmODg1MTY0ODM4ZmY0YTciDXZlcmlmaWVkIgYxIglyb2xlMCITc2VjdXJpdHlfdG9rZW4iLWZjYTViZjQ0ZDU1Yjk0NDgwNGQ0NGNkYzdhMTkzNWMxYjEzNDZkNzkiEXRva2VuX2V4cGlyeSIYMjAxMy0wNS0xMCAxMzozNzozMSIMZGVsZXRlZCIGMCIRZGVsZXRlX2FmdGVyMCILcHVibGljIgYxIgxoYXNfaHJtIgYwIg5maXJzdF9kYXkiBjEiFHByZWZlcnJlZF91bml0cyIGMSIVYXV0b19sb2dpbl90b2tlbiItODRjNWRhYTg0ZDRkYzEzNTNlNGNiOWFjNzdjY2FiYTQ4YTg1MTBmMDoWQGF0dHJpYnV0ZXNfY2FjaGV7AEkiCmZsYXNoBjsGRklDOidBY3Rpb25Db250cm9sbGVyOjpGbGFzaDo6Rmxhc2hIYXNoewAGOgpAdXNlZHsASSIYY2FsZW5kYXJfbW9udGhfeWVhcgY7BkZpAuAHSSIZY2FsZW5kYXJfbW9udGhfbW9udGgGOwZGaQ8%3D--4b5deef92240746f845a643d309fd9b988f5e9b7'
    })
    soup = BeautifulSoup(response.content, 'html.parser')
    days = soup.findAll('td', {'class': 'month_calendar_day_in_month'})

    date_text = soup.find('div', {'id': 'date_range'}).text
    date_text = date_text.split('\n')
    date_text = date_text[3]
    print(date_text)

    for day in days:
      date = day['id'] # d2019-12-1
      workouts = day.findAll('div', {'class': 'month_calendar_workout'})
      for w in workouts:
        link = 'http://www.running-log.com' + w.a['href']
        json_data['data'].append(link)

    step_count -= 1
    if stop_date in date_text:
      with open('workout-links.json', 'a') as outfile:
        json.dump(json_data, outfile)
      break
    
    # fallback break
    if step_count < -100:
      break


def get_workout_data():
  with open('workout-links.json', 'r') as file:
    json_data = json.load(file)

  workouts = []
  for link in json_data['data']:
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    content = soup.find('div', {'class': 'page_Content'})
    title = content.find('h3').text.replace('\n', '').strip()
    p = content.findAll('p')
    date = p[2].text.replace('\n', '').strip()
    print(date, '\n')
    comment = '' if 'Share on Facebook' in p[4].text else p[4].text
    body = content.find('tbody')
    
    workout = {}
    workout['date'] = date
    workout['title'] = title
    workout['comment'] = comment
    workout['splits'] = []

    if body:
      rows = body.findAll('tr')
      for row in rows:
        row_data = row.findAll('td')
        data = {}
        data['distance'] = row_data[0].text
        data['duration'] = row_data[1].text
        data['pace'] = row_data[2].text
        data['interval_type'] = row_data[3].text.replace('\n', '').strip()
        workout['splits'].append(data)
    workouts.append(workout)

  output_json = {"data": workouts}
  with open('workouts.json', 'a') as outfile:
    json.dump(output_json, outfile)


# get_all_workout_links('April 2011')
get_workout_data()