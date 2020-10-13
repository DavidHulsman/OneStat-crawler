import time

import requests
import sys
from lxml import html
import sqlite3

STARTID = 397021
ENDID = 1000000

TIMEOUT = 0.25
conn = sqlite3.connect('Crawler.db')
c = conn.cursor()

for userid in range(STARTID, ENDID):
    if userid % 10 == 0:
        print(userid)
    try:
        head = requests.head('http://www.onestat.com/aspx/login.aspx?sid=' + str(userid), timeout=TIMEOUT, allow_redirects=False)
        if head.status_code == 302:
            page = requests.get('http://www.onestat.com/aspx/login.aspx?sid=' + str(userid), timeout=TIMEOUT)
            page_tree = html.fromstring(page.content)

            # Extract info
            user_id = page_tree.xpath('//span[@id="ctl00_Header1_Account"]/text()')
            user_website = page_tree.xpath('//td/child::a/@href')

            if len(user_id) > 0:
                # Get user's website and its response code (404, 200, 500, etc)
                user_page = requests.get(user_website[0], timeout=TIMEOUT)
                user_reponse_code = user_page.status_code

                c.execute("INSERT INTO found VALUES (?,?,?)", (user_id[0], user_reponse_code, user_website[0]))
                conn.commit()
    except requests.exceptions.InvalidURL:
        c.execute("INSERT INTO error VALUES (?,?)", (userid, 'InvalidURL'))
        conn.commit()
        print("InvalidURL")
    except requests.exceptions.ConnectionError:
        c.execute("INSERT INTO error VALUES (?,?)", (userid, 'ConnectionError'))
        conn.commit()
        print("ConnectionError")
    except TimeoutError:
        c.execute("INSERT INTO error VALUES (?,?)", (userid, 'TimeoutError'))
        conn.commit()
        print("TimeoutError")
    except requests.exceptions.ReadTimeout:
        c.execute("INSERT INTO error VALUES (?,?)", (userid, 'ReadTimeout'))
        conn.commit()
        print("ReadTimeout")
    except :
        s = 'Other:'
        s += str(sys.exc_info())
        c.execute("INSERT INTO error VALUES (?,?)", (userid, s))
        conn.commit()
        print("OtherException")
