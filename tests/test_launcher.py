import re
from typing import Any

import pytest
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from twisted.logger import LogLevel, capturedLogs, eventAsText

from scrapyduler import __version__


GOOD = [
    None,
    (
        ("cron", "* * * * *"),
        ("project", "p1"),
        ("spider", "s1"),
        ("settings", "HTTPPROXY_ENABLED=True"),
        ("args", "foo=bar"),
    ),
    (
        ("interval", "weeks=0 days=0 hours=0 minutes=0 seconds=30"),
        ("project", "p1"),
        ("spider", "s2"),
    ),
]

BAD = [
    (("project", "p1"), ("spider", "s2")),
    (
        ("cron", "* * * * *"),
        ("interval", "weeks=0 days=0 hours=0 minutes=0 seconds=30"),
        ("project", "p1"),
        ("spider", "s1"),
    ),
]

IDS = ["default", "scheduler.cron", "scheduler.interval"]


def remove_debug_messages(captured):
    return [message for message in captured if message["log_level"] != LogLevel.debug]


def get_message(captured):
    return eventAsText(captured[0]).split(" ", 1)[1]


@pytest.mark.parametrize(
    "config, expected",
    zip(
        GOOD,
        (
            ["scrapyd", "services"],
            ["scrapyd", "services", "scheduler.cron"],
            ["scrapyd", "services", "scheduler.interval"],
        ),
    ),
    ids=IDS,
    indirect=["config"],
)
def test_start_service(config, launcher, expected):
    with capturedLogs() as captured:
        launcher.startService()
    captured = remove_debug_messages(captured)

    assert len(captured) == 2
    assert captured[1]["log_level"] == LogLevel.info
    assert re.search(
        f"\\[Launcher\\] Scrapyduler launcher {__version__} started",
        get_message(captured[1:]),
    )

    assert config.cp.sections() == expected


@pytest.mark.parametrize(
    "config, expected",
    zip(
        GOOD,
        (
            [
                0,
            ],
            [
                1,
                CronTrigger,
                {
                    "args": "foo=bar",
                    "cron": "* * * * *",
                    "project": "p1",
                    "settings": "HTTPPROXY_ENABLED=True",
                    "spider": "s1",
                },
            ],
            [
                1,
                IntervalTrigger,
                {
                    "interval": "weeks=0 days=0 hours=0 minutes=0 seconds=30",
                    "project": "p1",
                    "spider": "s2",
                },
            ],
        ),
    ),
    ids=IDS,
    indirect=["config"],
)
def test_start_service_scheduler_jobs(launcher, config, expected: Any):
    launcher.startService()
    jobs = launcher._scheduler.get_jobs()

    assert len(jobs) == expected[0]

    if jobs:
        assert isinstance(jobs[0].trigger, expected[1])
        assert jobs[0].kwargs == expected[2]


@pytest.mark.parametrize(
    "config, expected",
    zip(
        BAD,
        (
            [ValueError, "Required parameter 'cron' or 'interval' not set"],
            [ValueError, "Only one parameter 'cron' or 'interval' must be set"],
        ),
    ),
    ids=["scheduler.empty", "scheduler.both"],
    indirect=["config"],
)
def test_start_service_bad(launcher, config, expected):
    with pytest.raises(expected[0], match=expected[1]):
        launcher.startService()


@pytest.mark.parametrize("config", GOOD[1:], ids=IDS[1:], indirect=["config"])
def test_schedule_spider(launcher, config, mocker):
    kwargs = launcher.schedulers[0]

    mock_get = mocker.patch("scrapyduler.launcher.spider_list.get")
    mock_get.return_value = [kwargs["spider"]]
    mock_schedule = mocker.patch.object(launcher.scrapyd_scheduler, "schedule")

    launcher.schedule_spider(**kwargs)

    mock_schedule.assert_called_once()

    args_call, kwargs_call = mock_schedule.call_args

    assert args_call[0] == kwargs["project"]
    assert args_call[1] == kwargs["spider"]
    assert kwargs_call["priority"] == float(kwargs.get("priority", 0))
    assert "_job" in kwargs_call
    assert len(kwargs_call["_job"]) == 32


@pytest.mark.parametrize("config", GOOD[1:], ids=IDS[1:], indirect=["config"])
def test_schedule_spider_not_found(launcher, config, mocker):
    kwargs = launcher.schedulers[0]
    spider = kwargs["spider"]

    mock_get = mocker.patch("scrapyduler.launcher.spider_list.get")
    mock_get.return_value = []
    mock_schedule = mocker.patch.object(launcher.scrapyd_scheduler, "schedule")

    with capturedLogs() as captured:
        launcher.schedule_spider(**kwargs)
    captured = remove_debug_messages(captured)

    mock_schedule.assert_not_called()

    assert captured[0]["system"] == "Scrapyduler"
    assert re.search(f"spider '{spider}' not found", get_message(captured))
