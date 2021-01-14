#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from datetime import datetime, timedelta
from typing import List

from cdp_backend.database.constants import EventMinutesItemDecision, MatterStatusDecision, VoteDecision
from cdp_backend.pipeline.ingestion_models import (
    Body,
    EventIngestionModel,
    EventMinutesItem,
    Matter,
    MinutesItem,
    Person,
    Role,
    Seat,
    Session,
    SupportingFile,
    Vote,
)
from cdp_backend.utils.constants_utils import get_all_class_attr_values

###############################################################################


def get_events() -> List[EventIngestionModel]:
    return [_get_example_event()]


###############################################################################


NUM_COUNCIL_SEATS = 10
RAND_BODY_RANGE = (1, 100)
RAND_EVENT_MINUTES_ITEMS_RANGE = (5, 15)
RAND_MATTER_RANGE = (1, 100)

ALL_EVENT_MINUTES_ITEM_DECISION = get_all_class_attr_values(EventMinutesItemDecision)
ALL_MATTER_STATUS_DECISION = get_all_class_attr_values(MatterStatusDecision)
ALL_VOTE_DECISION = get_all_class_attr_values(VoteDecision)

SESSIONS = [
    (
        "https://youtu.be/BkWNBqlZjGk",
        "https://www.seattlechannel.org/documents/seattlechannel/closedcaption/2020/council_101220_2022077.vtt",
    ),
    (
        "https://youtu.be/DU1pycy73yI",
        "https://www.seattlechannel.org/documents/seattlechannel/closedcaption/2020/council_113020_2022091.vtt",
    ),
    (
        "https://youtu.be/ePTZs5ZxCnc",
        "https://www.seattlechannel.org/documents/seattlechannel/closedcaption/2020/brief_112320_2012089.vtt",
    ),
    (
        "https://youtu.be/51jNLMQ3qB8",
        "https://www.seattlechannel.org/documents/seattlechannel/closedcaption/2020/council_110920_2022085.vtt",
    ),
    ("https://youtu.be/fgr2sYYJy0Q", None),
]


def _get_example_person(seat_num: int) -> Person:
    "Create a fake example person"
    # Create a list of roles
    roles = [
        Role(title="Councilmember", body=Body(name="Example Committee")),
        Role(title="Chair", body=Body(name=f"Example Committee {seat_num}")),
    ]
    if seat_num == 1:
        # Add Council President role for seat position 1
        roles.append(
            Role(title="Council President", body=Body(name="Example Committee"))
        )
    return Person(
        name=f"Example Person {seat_num}",
        email="person@example.com",
        phone="123-456-7890",
        website="www.example.com",
        picture_uri="https://councildataproject.github.io/imgs/public-speaker-light-purple.svg",
        seat=Seat(
            name=f"Example Seat Position {seat_num}",
            electoral_area=f"Example Electoral Area {seat_num}",
            electoral_type=f"Example Electoral Type {1 if seat_num <= NUM_COUNCIL_SEATS / 2 else 2 }",
            image_uri="https://councildataproject.github.io/imgs/seattle.jpg",
        ),
        roles=roles,
    )


def _get_example_event() -> EventIngestionModel:
    "Create a fake example event data"
    # Create a body for the event
    body = Body(
        name=f"Example Committee {random.randint(*RAND_BODY_RANGE)}",
        description="Example Description",
    )
    # Create sessions for the event
    sessions = [
        Session(
            session_datetime=datetime.utcnow() + (i * timedelta(hours=3)),
            video_uri=session[0],
            caption_uri=session[1],
        )
        for session in random.sample(SESSIONS, random.randint(1, 3))
    ]
    # Get a number of event minutes items for the event
    num_event_minutes_items = random.randint(*RAND_EVENT_MINUTES_ITEMS_RANGE)
    # Get a matter number for each event minutes item
    matter_nums = random.sample(range(RAND_MATTER_RANGE[0], RAND_MATTER_RANGE[1] + 1), num_event_minutes_items)
    # Get a number of sponsors for each event minutes item
    nums_sponsors = random.choices(range(1, 4), k=num_event_minutes_items)
    # Specify the seat position for each sponsor
    sponsors_seats = [
        random.sample(range(1, NUM_COUNCIL_SEATS + 1), num_sponsors)
        for num_sponsors in nums_sponsors
    ]
    # Create a list of event minutes item for the event
    event_minutes_items = [
        EventMinutesItem(
            minutes_item=MinutesItem(
                name=f"Example Minutes Item {matter_nums[i]}",
                description="Example Description",
            ),
            matter=Matter(
                name=f"Example Matter {matter_nums[i]}",
                matter_type=f"Example Matter Type {matter_nums[i]//10}",
                title="Example Matter Title",
                result_status=random.choice(ALL_MATTER_STATUS_DECISION),
                sponsors=[
                    _get_example_person(seat_num) for seat_num in sponsors_seats[i]
                ],
            ),
            supporting_files=[
                SupportingFile(
                    name=f"Example Supporting File Name {file_num}",
                    uri="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
                )
                for file_num in range(1, random.randint(1, 5) + 1)
            ],
            decision=random.choice(ALL_EVENT_MINUTES_ITEM_DECISION),
            votes=[
                Vote(
                    person=_get_example_person(seat_num),
                    decision=random.choice(ALL_VOTE_DECISION),
                )
                for seat_num in range(1, NUM_COUNCIL_SEATS + 1)
            ],
        )
        for i in range(num_event_minutes_items)
    ]
    # Insert a non-matter event minutes item
    event_minutes_items.insert(
        0,
        EventMinutesItem(
            minutes_item=MinutesItem(
                name="Approval of Agenda", description="Example Description"
            )
        ),
    )
    return EventIngestionModel(
        body=body,
        sessions=sessions,
        event_minutes_items=event_minutes_items,
        agenda_uri="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        minutes_uri="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
    )
