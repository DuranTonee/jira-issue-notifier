# https://www.youtube.com/watch?v=vFENJpe6eJU
import psycopg2

def db_close():
    cur.close()
    conn.close()

def add_to_db(jira_username, tg_id):
    cur.execute(f"""INSERT INTO users (jira_username, tg_id) VALUES
                ('{jira_username}', {tg_id});
    """)
    conn.commit()

def check_if_in_db(jira_username, tg_id) -> bool:
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
                id serial PRIMARY KEY,
                jira_username VARCHAR(255),
                tg_id INT
    );
    """)
        
    cur.execute(f"SELECT COUNT(*) FROM users WHERE tg_id = {tg_id}")
    result = cur.fetchone()[0]
    if result > 0:
        return True
    else:
        add_to_db(jira_username, tg_id)
        return False


def delete_from_db(tg_id):
    cur.execute(f"DELETE FROM users WHERE tg_id = {tg_id}")
    conn.commit()


def get_id(jira_username) -> str:
    try:
        cur.execute(f"SELECT tg_id FROM users WHERE jira_username = '{jira_username}'")
        return cur.fetchone()[0]
    except:
        pass


def add_to_key_table(issue_key, assignee_id, creator_id):
    cur.execute("""CREATE TABLE IF NOT EXISTS keys (
                id serial PRIMARY KEY,
                issue_key VARCHAR,
                tg_assignee_id VARCHAR,
                tg_creator_id VARCHAR
    );
    """)
    conn.commit()
    
    cur.execute(f"""INSERT INTO keys (issue_key, tg_assignee_id, tg_creator_id) VALUES
                ('{issue_key}', '{assignee_id}', '{creator_id}')
    """)
    conn.commit()


def change_key_table(issue_key, assignee_id):
    cur.execute(f"""UPDATE keys
                SET tg_assignee_id = '{assignee_id}'
                WHERE issue_key = '{issue_key}';
    """)
    conn.commit()


def delete_from_key_table(issue_key):
    cur.execute(f"""DELETE FROM keys
                WHERE issue_key = '{issue_key}'
""")
    conn.commit()


def get_id_from_key_table(issue_key) -> int:
    cur.execute(f"SELECT tg_assignee_id FROM keys WHERE issue_key = '{issue_key}'")
    assignee_id = cur.fetchone()[0]
    cur.execute(f"SELECT tg_creator_id FROM keys WHERE issue_key = '{issue_key}'")
    creator_id = cur.fetchone()[0]
    return assignee_id, creator_id


conn = psycopg2.connect(host='localhost', dbname='postgres', user='postgres', password='damir123', port=5432)
cur = conn.cursor()

if __name__ == "__main__":
    get_id_from_key_table('piz-69')