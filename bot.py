# required libraries
import praw
import prawcore
import time
import re
import os
import random
from configparser import ConfigParser

# path of current directory
directory = os.path.dirname(os.path.realpath(__file__))

# access contents of "config.cfg" file
config = os.path.join(directory, "config.cfg")
parser = ConfigParser()
parser.read(config)

# reddit API instance
reddit = praw.Reddit(
    username = parser.get("API", "username"),
    password = parser.get("API", "password"),
    client_id = parser.get("API", "client_id"),
    client_secret = parser.get("API", "client_secret"),
    # requestor_kwargs = {"session": session},
    user_agent = parser.get("API", "user_agent")
)

def get_ratelimit(ex_msg = None):
    """
    get the rate-limit given by Reddit API and convert
    it into seconds
    """

    try:
        msg = ex_msg.lower()
        search = re.search(r"""\b(minutes)\b""", msg)
        msg = msg[search.start()-3] + msg[search.start()-2]
        minutes = int(msg.replace(" ", "")) + 1
        return minutes * 60
    
    except:
        return 60

def on_comments():
	"""
	comment on comments of a post in a subreddit
	"""

	with open(os.path.join(directory, "subreddits.txt"), "r") as file:
		subs = file.read().splitlines()
	subreddit = reddit.subreddit("+".join(subs))

	# use "stream" to fetch new comments
	for comment in subreddit.stream.submissions(skip_existing = True):

		with open(os.path.join(directory, "comments.txt"), "r") as file:
			comms = file.read()

		try:
			if comment.author not in [reddit.user.me(), "AutoModerator"]:

				url = comment.reply(comms)
				print(f"Link to comment: https://reddit.com{url.permalink}")
				INTERVALS = [x for x in range(300, 601, 60)]
				random.seed(a = None)
				time.sleep(random.choice(INTERVALS))

		except praw.exceptions.APIException as e:
			# print(get_ratelimit(str(e)))
			ratelimit = get_ratelimit(str(e))
			time.sleep(ratelimit)

		except prawcore.exceptions.ResponseException:
			time.sleep(900)

		except Exception as error:
			print(error)

while True:
	on_comments()
