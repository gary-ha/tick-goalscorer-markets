from metric_api import MetricAPI
from google_sheets_api import GoogleSheetsAPI

metric_api = MetricAPI()
google_sheets_api = GoogleSheetsAPI()

if __name__ == "__main__":
    metric_api.get_events_for_goalscorers()
    metric_api.tick_goalscorers()
