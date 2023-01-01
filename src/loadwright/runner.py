"""Functionality for running load tests"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import List

import panel as pn
import param
from playwright.async_api import async_playwright

from .logger import Logger
from .user import User

USERS = 10
USER_DELAY = 1
USER_CLICKS = 10


class LoadTestRunner(pn.viewable.Viewer):
    """Can run load tests a data apps using the Playwright framework"""

    host: str = param.String("http://localhost:5006")
    logger: Logger = param.ClassSelector(class_=Logger)
    headless: bool = param.Boolean(doc="If True the browser will be shown while running the test")
    n_users: int = param.Integer(default=USERS, doc="The number of users to access the page")
    user_delay: float = param.Number(
        default=USER_DELAY, doc="The delay to apply between users accessing the the page"
    )
    user: User = param.Selector(objects=[User()], doc="The user to use")

    def __panel__(self):
        raise NotImplementedError()

    def __init__(self, user: User | None = None, users: List[User] | None = None, **params):
        """_summary_

        Args:
            user (User | None, optional): A custom user or None. Defaults to None.
            users (List[User] | None, optional): A list of users to select from. Defaults to None.
        """
        params["logger"] = params.get("logger", Logger())
        super().__init__(**params)

        if user and not users:
            users = [user]
        if users:
            self.param.user.objects = users
        if user:
            self.user = self.param.user.default = user
        elif not self.param.user.default in self.param.user.objects and self.param.user.objects:
            self.user = self.param.user.default = self.param.user.objects[0]

    async def _create_task(self, index, browser, **kwargs):
        await asyncio.sleep(delay=index * self.user_delay)
        page = await browser.new_page()
        await self.user.clone(
            name=str(index), host=self.host, page=page, event=self.logger.event, **kwargs
        ).run()
        await asyncio.sleep(self.user.sleep_time)
        await page.close()

    def _create_tasks(self, browser):
        return [self._create_task(index=index, browser=browser) for index in range(self.n_users)]

    async def run(self):
        """Runs the test"""
        self.logger.reset()
        async with async_playwright() as pwright:
            browser = await pwright.chromium.launch(headless=self.headless)
            await asyncio.sleep(0.2)
            # Then()
            tasks = self._create_tasks(browser=browser)
            await asyncio.gather(*tasks)
            await browser.close()
        self.logger.save()
        self.logger.archive()

    @staticmethod
    @asynccontextmanager
    async def serve(panels, threaded=True, show=False, port: int | None = None, **kwargs):
        """Utility context manager for serving one or more panels in the context

        Parameters are the same as for pn.serve
        """
        server = pn.serve(panels, port=port, threaded=threaded, show=show, **kwargs)
        await asyncio.sleep(0.2)

        try:
            yield f"http://localhost:{port}"
        finally:
            server.stop()
