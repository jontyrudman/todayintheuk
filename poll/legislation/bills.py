import logging
import datetime
from typing import Optional
from os import PathLike
import json

import requests
from pydantic import BaseModel, Field


BILL_COUNT_CAP = 500
BILL_URL_PREFIX = "https://bills.parliament.uk/bills/"


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
) -> list[Bill]:
    """
    Fetch all bills matching the provided, optional criteria, up to bills.BILL_COUNT_CAP.
    """
    bills = []
    params = {
        "Session": session,
        "CurrentHouse": current_house,
        "OriginatingHouse": originating_house,
        "BillStage": bill_stages,
        "BillStagesExcluded": bill_stages_excluded,
        "IsDefeated": is_defeated,
        "IsWithdrawn": is_withdrawn,
        "SortOrder": "DateUpdatedDescending",
    }
    logging.info(f"Fetching bills using params {params}...")

    res = requests.get(
        url="https://bills-api.parliament.uk/api/v1/Bills", params=params
    )
    if res.status_code != 200:
        logging.error("Failed to fetch first page of bills")
        return bills

    resjson = res.json()
    bills += resjson["items"]
    logging.debug(f"Response: {resjson}")

    total_results = max(resjson["totalResults"], BILL_COUNT_CAP)
    logging.debug(f"{total_results} bills will be fetched in total.")

    while len(bills) < total_results:
        res = requests.get(
            url="https://bills-api.parliament.uk/api/v1/Bills",
            params={
                **params,
                "Skip": len(bills),
            },
        )
        if res.status_code != 200:
            logging.error("Failed to fetch first page of bills")
            return bills

        resjson = res.json()
        logging.debug(f"Response: {resjson}")

        if len(resjson["items"]) == 0:
            logging.debug("End of pages.")
            break

        bills += resjson["items"]

    bill_objs = []
    for b in bills:
        try:
            bill_objs.append(
                Bill(
                    **b,
                    link=f"{BILL_URL_PREFIX}{b['billId']}",
                    current_stage=Stage(**b["currentStage"]),
                )
            )
        except Exception as e:
            logging.error(e)

    return bill_objs


def write_bill_list_as_json(path: PathLike, data: list[Bill]):
    if not isinstance(data, list):
        raise TypeError("Must provide a list of bills")
    with open(path, "w") as file:
        file.write(json.dumps([x.model_dump_json() for x in data]))
