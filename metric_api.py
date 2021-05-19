import requests
import datetime
from decouple import config
from google_sheets_api import GoogleSheetsAPI
import pandas as pd


class MetricAPI(GoogleSheetsAPI):
    def __init__(self):
        super().__init__()
        self.category_id = config('CATEGORY_ID').split(",")
        self.metric_ids = []
        self.gameweb = config('GAME_WEB')
        self.betpumpweb = config('BETPUMPWEB')
        self.data = self.pull_participants_data()
        self.df = pd.DataFrame(self.data[1:], columns=self.data[0])
        self.teams_data = self.df.to_dict("records")

    def get_events_for_goalscorers(self):
        print(datetime.datetime.now())
        print("Gathering events for Goalscorers...")

        for i in self.category_id:
            try:
                parameters = {
                    "fn": "events",
                    "org": "snabbis",
                    "lang": "en",
                    "categoryid": f"{i}",
                    "status": "Live"
                }
                response = requests.get(url=self.gameweb, params=parameters)
                response.raise_for_status()
                events_data = response.json()

                for event in events_data["data"]:
                    if not event["scorers"] and event["state"]["periodId"] == "PreGame" and self.check_teams(event):
                        time_delta = datetime.datetime.strptime(event["startTime"], "%Y-%m-%d %H:%M:%S") - \
                                     (datetime.datetime.now() - datetime.timedelta(hours=1))
                        difference_minutes = int(time_delta.total_seconds() / 60)
                        if 3600 > difference_minutes > 60:
                            self.metric_ids.append(event["id"])
            except KeyError:
                continue
        print(self.metric_ids)

    def check_teams(self, event):
        home_team_exist = False
        away_team_exist = False
        for team in self.teams_data:
            if event["participants"][0]["id"] == team["Team ID"].split(";")[0]:
                home_team_exist = True
            if event["participants"][1]["id"] == team["Team ID"].split(";")[0]:
                away_team_exist = True
        if home_team_exist and away_team_exist:
            return True

    def tick_goalscorers(self):
        parameters = {
            "fn": "loginadmin",
            "org": "BetPump",
            "uid": config('BO_USERNAME'),
            "pwd": config('BO_PASSWORD'),
        }

        response = requests.get(url=self.betpumpweb, params=parameters)
        response.raise_for_status()
        session_id = response.json()["data"]["session"]

        print("Ticking Goalscorers...")
        for i in self.metric_ids:
            parameters = {
                "fn": "setpricingparam",
                "org": "Betpump",
                "lang": "en",
                "eventid": i,
                "prop": "pricePlayers",
                "val": True,
                "sessid": session_id
            }

            response = requests.post(url=self.betpumpweb, params=parameters)
            response.raise_for_status()
        print("Finished ticking Goalscorers.")
