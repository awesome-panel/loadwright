"""The base User class"""
from __future__ import annotations

import asyncio
from typing import Callable

import param
from playwright.async_api import Page

DEFAULT_SLEEP_TIME = 0.5


class User(param.Parameterized):
    """Base User class for interacting with a page

    Override the `run` method to implement custom user interactions
    """

    page: Page = param.ClassSelector(
        class_=Page, constant=True, doc="A Playwright page to interact with"
    )
    host: str = param.String("http://localhost:5006", doc="The host to interact with")
    event: Callable = param.Callable(default=print, doc="An event logger")
    sleep_time: float = param.Number(
        default=DEFAULT_SLEEP_TIME, doc="The duration between the user interacting with the page"
    )

    endpoint: str = param.String("/")

    @property
    def url(self):
        """Returns the url the user is interacting with"""
        return self.host + self.endpoint

    async def sleep(self):
        """Sleep for a duration of sleep_time"""
        await asyncio.sleep(self.sleep_time)

    async def run(self):
        """Override the `run` method to implement custom user interactions.

        The default is to go to self.url
        """
        with self.event(name="load", user=self.name):
            await self.page.goto(self.url)
        await self.sleep()

    def clone(self, **params) -> "User":
        """Makes a copy of the object sharing the same parameters.

        Any `params` specified will be set on the new user

        Returns:
            User: A new User
        """
        inherited = {p: v for p, v in self.param.values().items() if not self.param[p].readonly}
        return type(self)(**dict(inherited, **params))
