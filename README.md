# Jira Issue Notifications Telegram Bot
If for some reason you can't use [Telegram Integration For Jira](https://marketplace.atlassian.com/apps/1218556/telegram-integration-for-jira), it is possible to use [webhooks](https://developer.atlassian.com/server/jira/platform/webhooks/) to notify team members in Telegram. This Django project allows it and serves as a Telegram bot to receive notifications from Atlassian Jira and forward them to users providing the necessary data. The bot allows users to register with their Jira username, and it sends notifications about issue updates and comments with PostgreSQL integration. 
## Features
1. **User registration**
   - Users can register with the bot using the _/register_ command, providing their Jira username. The data is stored in the database (check [dp.py](https://github.com/DuranTonee/jira-issue-notifier/blob/main/jira_notifications/jira_notifications_app/db.py))

     ![image](https://github.com/DuranTonee/jira-issue-notifier/assets/95922080/df15efc5-1c71-4f58-b19d-024ee6e92947)
     
   - It is possible to unregister.

      ![image](https://github.com/DuranTonee/jira-issue-notifier/assets/95922080/b30e6e5a-17bd-4ea8-90ee-9595bdf00657)

2. **Notification types**
   - Issue creation and updates. (*Unassigned issue is sent to an admin)
  
     ![image](https://github.com/DuranTonee/jira-issue-notifier/assets/95922080/4f5e6cee-fbc3-4a5f-8b3d-fc04721e8731)

   - Comment creation on an issue.
  
     ![image](https://github.com/DuranTonee/jira-issue-notifier/assets/95922080/b036e148-160a-470c-842a-92c546c0f659)

   *Issue overview in Jira.
    ![image](https://github.com/DuranTonee/jira-issue-notifier/assets/95922080/0dadcfc6-8322-4211-aaa4-18543f2c5577)
   
3. **Customized Notifications**
   - Notifications include details such as issue key, summary, status, assignee, and creator.
   - Differentiates between unassigned issues and those with assignees.
   - Provides a direct link to the Jira issue for quick access.
   - Provides creator's and assignee's Telegram username for better communication.
     
## How to deploy
1. Create your [Django project and application](https://docs.djangoproject.com/en/5.0/intro/tutorial01/) (in this case jira_notifications and jira_notifications_app respectively).
  > [!NOTE]
  > Refer to [views.py](https://github.com/DuranTonee/jira-issue-notifier/blob/main/jira_notifications/jira_notifications_app/views.py) and [urls.py](https://github.com/DuranTonee/jira-issue-notifier/blob/main/jira_notifications/jira_notifications/urls.py)

2. [Ngrok](https://ngrok.com/) is used to create a public URL for your local development server.
   - Refer to [Ngrok setup](https://dashboard.ngrok.com/get-started/setup) and obtain your authtoken from [here](https://dashboard.ngrok.com/get-started/your-authtoken).
   - `ngrok http 8000`
   - Ngrok URL will be provided:

   ![image](https://github.com/DuranTonee/jira-issue-notifier/assets/95922080/c84d8332-8e52-4458-b485-696f3c2fd1d7)

3. Create a webhook at https://YOURDOMAIN.atlassian.net/plugins/servlet/webhooks# and change the URL to Ngrok URL.
   ![image](https://github.com/DuranTonee/jira-issue-notifier/assets/95922080/241f3edb-5e23-48a0-bf9c-c8e4db6bee9a)


   Options:
   ![image](https://github.com/DuranTonee/jira-issue-notifier/assets/95922080/edfe8973-4b1f-48dd-beec-39e6e9d2495e)
   
4. Navigate to the project directory:
   - `cd jira_notifications`
     
5. Run [Gunicorn](https://gunicorn.org/) to host your server:
   - `gunicorn jira_notifications.wsgi`

   Or for development:
   - `python manage.py runserver`
6. Run **main.py** (optional, to enable registration)

## Database Setup
The project uses PostgreSQL as the database. Update the database connection details in [dp.py](https://github.com/DuranTonee/jira-issue-notifier/blob/main/jira_notifications/jira_notifications_app/db.py) if needed.

