import datetime
import logging
from pathlib import Path

import azure.functions as func

from methane.earth_engine import authenticate_google_service_account
from methane.methane_hotspots import run


def main(mytimer: func.TimerRequest) -> None:
    authenticate_google_service_account(
        Path("/mounted") / "data" / "hacktheclimate-308416-d1d36f96dfcf.json"
    )
    fmt = "%Y-%m-%d"
    date_now = datetime.datetime.now().date()
    two_days_ago = date_now - datetime.timedelta(days=2)
    two_weeks_before = two_days_ago - datetime.timedelta(days=14)

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info(
        run(
            two_weeks_before.strftime(fmt),
            two_days_ago.strftime(fmt),
            fdir="/mounted/",
        )
    )
