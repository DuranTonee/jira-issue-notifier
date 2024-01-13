import json
import requests
from dotenv import load_dotenv
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from jira_notifications_app.db import get_id, add_to_key_table, get_id_from_key_table, change_key_table, delete_from_key_table
from urllib.parse import urlparse
import os

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

#admin_id = "YOUR TG ID HERE AS AN ADMIN"
admin_id = 978888377

def send_message(assignee_id, creator_id, admin_id, message):
    apiURL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    tg_ids = []
    tg_ids.append(assignee_id)
    tg_ids.append(creator_id)
    if assignee_id == None:
        params = {
            'chat_id': admin_id,
            'text': f'UNASSIGNED ISSUE\n{message}',
            'parse_mode': 'html',
            'disable_web_page_preview': True
        }
        requests.get(apiURL, params)
        print(f"Sent to admin {admin_id}")
    elif assignee_id != creator_id:
        for id in tg_ids:
            params = {
                'chat_id': id,
                'text': message,
                'parse_mode': 'html',
                'disable_web_page_preview': True
            }
            requests.get(apiURL, params)
            print(f"Sent to {id}")
    else:
        params = {
            'chat_id': assignee_id,
            'text': message,
            'parse_mode': 'html',
            'disable_web_page_preview': True
        }
        requests.get(apiURL, params)
        print(f"Sent to {assignee_id}")


def get_username_by_id(tg_id) -> str or None:
    apiURL = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat?chat_id={tg_id}"
    response = requests.get(apiURL)
    try: 
        username = f"@{response.json()['result']['username']}"
        return username
    except Exception:
        return None


@csrf_exempt
def index(request):
    if request.method == 'POST':
        try: 
            response = request.body
            data = json.loads(response)  # Parse the response as JSON
            print(data)
            issue_key = data['issue']['key']
            domain = urlparse(data['issue']['self']).netloc

            if data['webhookEvent'] == 'comment_created':
                comment_author = data['comment']['author']['displayName']
                comment_body = data['comment']['body']
                issue_name = data['issue']['fields']['summary']
                tg_author_username = get_username_by_id(get_id(comment_author))
                tg_assignee_id, tg_creator_id = get_id_from_key_table(issue_key)
                message = f'A comment was left on issue <a href="https://{domain}/browse/{issue_key}">{issue_key}</a> "{issue_name}".\nAuthor: {comment_author} ({tg_author_username})\nComment: {comment_body}'
                apiURL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                if tg_assignee_id == "None":
                    params = {
                        'chat_id': tg_creator_id,
                        'text': message,
                        'parse_mode': 'html',
                        'disable_web_page_preview': True
                    }
                    requests.get(apiURL, params)

                else:
                    if tg_assignee_id != tg_creator_id:
                        tg_ids = []
                        tg_ids.append(tg_assignee_id)
                        tg_ids.append(tg_creator_id)
                        for id in tg_ids:
                            params = {
                                'chat_id': id,
                                'text': message,
                                'parse_mode': 'html',
                                'disable_web_page_preview': True
                            }
                            requests.get(apiURL, params)
                            print(f"Sent to {id}")
                    else:
                        params = {
                            'chat_id': tg_assignee_id,
                            'text': message,
                            'parse_mode': 'html',
                            'disable_web_page_preview': True
                        }
                        requests.get(apiURL, params)
                        print(f"Sent to {tg_assignee_id}")


            if data['webhookEvent'] == 'jira:issue_created' or data['webhookEvent'] == 'jira:issue_updated':
                issue_name = data['issue']['fields']['summary']
                issue_status = data['issue']['fields']['status']['name']
                issue_creator = data['issue']['fields']['creator']['displayName']

                issue_assignee = data['issue']['fields']['assignee']

                if issue_assignee != None:
                    issue_assignee = data['issue']['fields']['assignee']['displayName']
                    # print(issue_assignee)
                tg_assignee_id = get_id(issue_assignee)
                tg_assignee_username = get_username_by_id(tg_assignee_id)

                tg_creator_id = get_id(issue_creator)
                tg_creator_username = get_username_by_id(tg_creator_id)

                if data['webhookEvent'] == 'jira:issue_created':
                    message = f'ISSUE CREATED.\nIssue: <a href="https://{domain}/browse/{issue_key}">{issue_key}</a> "{issue_name}"\nStatus: {issue_status}\nAssignee: {issue_assignee} ({tg_assignee_username})\nCreator: {issue_creator} ({tg_creator_username})'
                    send_message(tg_assignee_id, tg_creator_id, admin_id, message)

                    add_to_key_table(issue_key, tg_assignee_id, tg_creator_id)
                    print('added to db')
                elif data['webhookEvent'] == 'jira:issue_updated':
                    changelog_items = data['changelog']['items']
                    for item in changelog_items:
                        # Accessing the specific parameters within each item
                        changed_field = item['field']
                        changed_from = item['fromString']
                        changed_to = item['toString']

                    message = f'ISSUE UPDATED.\nIssue: <a href="https://{domain}/browse/{issue_key}">{issue_key}</a> "{issue_name}"\nStatus: {issue_status}\nAssignee: {issue_assignee} ({tg_assignee_username})\nCreator: {issue_creator} ({tg_creator_username})\n\nCHANGES:\n{changed_field}. {changed_from} → {changed_to}'
                    send_message(tg_assignee_id, tg_creator_id, admin_id, message)

                    change_key_table(issue_key, tg_assignee_id)
                    print('changed db')
            elif data['webhookEvent'] == 'jira:issue_deleted':
                delete_from_key_table(issue_key)
                print("deleted from db")
        except Exception as ex:
            print(f"An error occurred: {ex}")


    else:
        print("Wrong method")

    return HttpResponse('<html><body><a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ" style="font-size: 69px;">Check out that thing!</a></body></html>')
