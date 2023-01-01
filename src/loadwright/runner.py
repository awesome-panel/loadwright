# load_tester.py
from __future__ import annotations
import asyncio
import time
from typing import Dict, List, Type
import datetime
import pandas as pd
import panel as pn
import param
from playwright.async_api import async_playwright
from pathlib import Path
from .user import User

USERS = 10
USER_DELAY = 1
USER_CLICKS = 10
TEST_RESULTS_PATH = Path("test_results")

from contextlib import contextmanager


class Logger(param.Parameterized):
    results: Dict = param.List(class_=dict)
    path: str = param.String("test_results")
    file: str = param.String("load_test.csv")
    archive: str = param.Boolean(True)

    def __init__(self, **params):
        super().__init__(**params)

        self.reset()

    @contextmanager
    def event(self, name: str, user: str, **kwargs):
        start = time.time()
        if not self._start:
            self._start = start
        yield
        stop = time.time()
        result = {
            "event": name,
            "user": user,
            "start": pd.to_datetime(start, unit="s"),
            "stop": pd.to_datetime(stop, unit="s"),
            "start_seconds": start - self._start,
            "stop_seconds": stop - self._start,
            "duration": stop - start,
            **kwargs,
        }
        self.results.append(result)
        self.save()

    @property
    def data(self) -> pd.DataFrame:
        return pd.DataFrame(self.results)

    def reset(self):
        self.results = []
        self._start = None

    def _save(self):
        path = Path(self.path)
        path.mkdir(parents=True, exist_ok=True)
        file = path / self.file
        self.data.to_csv(file, index=True)

    def save(self):
        self._save()
        if self.archive:
            path = Path(self.path)
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M")
            filename, extension = self.file.split(".")
            file = path/"archive"/f"{filename}_{timestamp}.{extension}"
            file.parent.mkdir(parents=True, exist_ok=True)
            self.data.to_csv(file, index=True)


class LoadTest(pn.viewable.Viewer):
    host: str = param.String("http://localhost:5006")
    logger: Logger = param.ClassSelector(class_=Logger)
    headless: bool = param.Boolean()
    user_count: int = param.Integer(default=USERS)
    user_delay: float = param.Number(default=USER_DELAY)
    user: Type[User] = param.Selector(objects=[User])

    def __init__(self, user: Type[User]|None=None, users: List[Type[User]] | None=None, **params):
        if user and not users:
            users=[user]
        if users:
            self.param.user.objects=users
        if user:
            self.param.user.default=user
        if not self.param.user.default in self.param.user.objects and self.param.user.objects:
            self.param.user.default = self.param.user.objects[0]
        params["logger"]=params.get("logger", Logger())
        super().__init__(**params)

    async def _create_task(self, index, browser, **kwargs):
        await asyncio.sleep(delay=index*self.user_delay)
        page = await browser.new_page()
        await self.user(name=str(index), host=self.host, page=page, event=self.logger.event, **kwargs).run()
        await asyncio.sleep(self.user.reaction_time)
        await page.close()

    def _create_tasks(self, browser):
        return [self._create_task(index=index, browser=browser) for index in range(self.user_count)]


    async def run(self):
        self.logger.reset()
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            await asyncio.sleep(0.2)
            # Then()
            tasks = self._create_tasks(browser=browser)
            await asyncio.gather(*tasks)
            await browser.close()
        self.logger.save()



# Todo: Be able to run seperately
# Todo: Save report to test folder
# Todo:
