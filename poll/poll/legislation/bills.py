from enum import Enum
import logging
import datetime
from typing import ClassVar, Iterator, Optional

import requests
from pydantic import BaseModel, Field


BILL_COUNT_CAP = 500
BILL_URL_PREFIX = "https://bills.parliament.uk/bills/"


class BillSortEnum(str, Enum):
    title_ascending = "TitleAscending"
    title_descending = "TitleDescending"
    date_updated_ascending = "DateUpdatedAscending"
    date_updated_descending = "DateUpdatedDescending"


class Stage(BaseModel):
    id: int = Field(alias="stageId")
    description: str = Field(alias="description")
    house: str = Field(alias="house")


class Bill(BaseModel):
    id: int = Field(alias="billId")
    title: str = Field(alias="shortTitle")
    current_house: str = Field(alias="currentHouse")
    originating_house: str = Field(alias="originatingHouse")
    updated_timestamp: datetime.datetime | None = Field(alias="lastUpdate")
    withdrawn_timestamp: datetime.datetime | None = Field(alias="billWithdrawn")
    defeated: bool = Field(alias="isDefeated")
    act: bool = Field(alias="isAct")
    current_stage: Stage
    link: str

    # Each house has 1R, 2R, committee stage, report stage, 3R
    # After both houses have approved, there's consideration and RA
    progress_stage_ids: ClassVar[dict[str, list[int]]] = {
        "commons": [6, 7, 8, 9, 10],
        "lords": [1, 2, 3, 4, 5],
        "unassigned": [11],  # Royal Assent
    }

    def progress(self) -> int:
        """
        Returns a percentage of progress based on the current stage.
        """
        stage_ids = []
        if self.originating_house.lower() == "commons":
            stage_ids = (
                Bill.progress_stage_ids["commons"]
                + Bill.progress_stage_ids["lords"]
                + Bill.progress_stage_ids["unassigned"]
            )
        elif self.originating_house.lower() == "lords":
            stage_ids = (
                Bill.progress_stage_ids["lords"]
                + Bill.progress_stage_ids["commons"]
                + Bill.progress_stage_ids["unassigned"]
            )
        else:
            raise ValueError("originating_house must be 'Lords' or 'Commons'")

        return int(
            (stage_ids.index(self.current_stage.id) / (len(stage_ids) - 1))
            * 100
        )


def fetch_most_recent_session() -> int:
    """
    Fetch the session ID of the most recent session (e.g. 2022-2023 is ID 37).
    """
    logging.info("Fetching the most recent session ID...")
    res = requests.get(
        url="https://bills-api.parliament.uk/api/v1/Bills",
        params={
            "SortOrder": "DateUpdatedDescending",
        },
    )
    session_id = max(res.json()["items"][0]["includedSessionIds"])
    logging.info(f"Most recent session ID is {session_id}")
    return session_id


def fetch_bills(
    session: Optional[int] = None,
    current_house: Optional[str] = None,
    originating_house: Optional[str] = None,
    bill_stages: Optional[list[int]] = None,
    bill_stages_excluded: Optional[list[int]] = None,
    is_defeated: Optional[bool] = None,
    is_withdrawn: Optional[bool] = None,
    sort: Optional[BillSortEnum] = None,
) -> Iterator[Bill]:
    """
    Fetch all bills matching the provided, optional criteria, up to bills.BILL_COUNT_CAP.
    """
    bills_count = 0
    params = {
        "Session": session,
        "CurrentHouse": current_house,
        "OriginatingHouse": originating_house,
        "BillStage": bill_stages,
        "BillStagesExcluded": bill_stages_excluded,
        "IsDefeated": is_defeated,
        "IsWithdrawn": is_withdrawn,
        "SortOrder": sort,
    }
    params = {k: v for k, v in params.items() if v is not None}
    logging.info(f"Fetching bills using params {params}...")

    res = requests.get(
        url="https://bills-api.parliament.uk/api/v1/Bills", params=params
    )
    if res.status_code != 200:
        logging.error("Failed to fetch first page of bills")
        return

    resjson = res.json()
    for b in resjson["items"]:
        try:
            yield Bill(
                **b,
                link=f"{BILL_URL_PREFIX}{b['billId']}",
                current_stage=Stage(**b["currentStage"]),
            )
            bills_count += 1
        except Exception as e:
            logging.error(e)

    logging.debug(f"Response: {resjson}")

    total_results = max(resjson["totalResults"], BILL_COUNT_CAP)
    logging.debug(f"{total_results} bills will be fetched in total.")

    while bills_count < total_results:
        res = requests.get(
            url="https://bills-api.parliament.uk/api/v1/Bills",
            params={
                **params,
                "Skip": bills_count,
            },
        )
        if res.status_code != 200:
            logging.error("Failed to fetch first page of bills")
            return

        resjson = res.json()
        logging.debug(f"Response: {resjson}")

        if len(resjson["items"]) == 0:
            logging.debug("End of pages.")
            break

        for b in resjson["items"]:
            try:
                yield Bill(
                    **b,
                    link=f"{BILL_URL_PREFIX}{b['billId']}",
                    current_stage=Stage(**b["currentStage"]),
                )
                bills_count += 1
            except Exception as e:
                logging.error(e)


def fetch_bills_up_to_date(dt: datetime.datetime) -> list[Bill]:
    """
    Fetch bills up to a certain datetime, in DateUpdatedDescending order.
    """
    bills = []
    for b in fetch_bills(sort=BillSortEnum.date_updated_descending):
        # If we're out of our datetime range, return
        if b.updated_timestamp is None or b.updated_timestamp < dt:
            break

        bills.append(b)
    
    return bills
