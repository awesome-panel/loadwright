from __future__ import annotations
import asyncio
import param
from playwright.async_api import Page

USER_REACTION_TIME = 0.5

class User(param.Parameterized):
    page: Page = param.ClassSelector(class_=Page, constant=True)
    host: str = param.String("http://localhost:5006")
    event: callable = param.Callable(default=print)
    reaction_time: float = param.Number(default=USER_REACTION_TIME)

    endpoint: str = param.String("/")

    @property
    def url(self):
        return self.host + self.endpoint

    async def delay_reaction(self):
        await asyncio.sleep(self.reaction_time)

    async def run(self):
        with self.event(name="load", user=self.name):
            await self.page.goto(self.url)
        await self.delay_reaction()