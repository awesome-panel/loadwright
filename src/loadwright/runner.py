# load_tester.py
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
    host: str = param.String("http://localhost:5006")
    logger: Logger = param.ClassSelector(class_=Logger)
    headless: bool = param.Boolean()
    n_users: int = param.Integer(default=USERS)
    user_delay: float = param.Number(default=USER_DELAY)
    user: User = param.Selector(objects=[User()])

    def __init__(self, user: User|None=None, users: List[User] | None=None, **params):
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
        await self.user.clone(name=str(index), host=self.host, page=page, event=self.logger.event, **kwargs).run()
        await asyncio.sleep(self.user.sleep_time)
        await page.close()

    def _create_tasks(self, browser):
        return [self._create_task(index=index, browser=browser) for index in range(self.n_users)]


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
        self.logger.archive()

    @staticmethod
    @asynccontextmanager
    async def serve(panels, threaded=True, show=False, port: int=None, **kwargs)->str:
        server = pn.serve(panels, port=port, threaded=threaded, show=show, **kwargs)
        await asyncio.sleep(0.2)
        
        try:
            yield f"http://localhost:{port}"
        except:
            raise
        finally:
            server.stop()
