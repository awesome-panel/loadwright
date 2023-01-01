from __future__ import annotations
import asyncio
import param
from playwright.async_api import Page

DEFAULT_SLEEP_TIME = 0.5

class User(param.Parameterized):
    page: Page = param.ClassSelector(class_=Page, constant=True)
    host: str = param.String("http://localhost:5006")
    event: callable = param.Callable(default=print)
    sleep_time: float = param.Number(default=DEFAULT_SLEEP_TIME)

    endpoint: str = param.String("/")

    @property
    def url(self):
        return self.host + self.endpoint

    async def sleep(self):
        await asyncio.sleep(self.sleep_time)

    async def run(self):
        with self.event(name="load", user=self.name):
            await self.page.goto(self.url)
        await self.sleep()

    def clone(self, **params) -> 'User':
        """
        Makes a copy of the object sharing the same parameters.

        Arguments
        ---------
        params: Keyword arguments to override the parameters on the clone.

        Returns
        -------
        Cloned User object
        """
        inherited = {p: v for p, v in self.param.values().items()
                     if not self.param[p].readonly}
        return type(self)(**dict(inherited, **params))