"""We can run load tests on data apps"""
from __future__ import annotations

import asyncio

import panel as pn
import param
import pytest

from loadwright import LoadTest, User

from .app import App


class LoadAndClickUser(User):
    n_clicks = param.Integer(bounds=(0,None))
    
    async def run(self):
        with self.event(name="load", user=self.name):
            await self.page.goto(self.url)
            await self.page.get_by_role("button", name="Run").wait_for()
        await self.delay_reaction()

        for click_index in range(self.n_clicks):
            with self.event(name="interact", user=self.name):
                await self.page.get_by_role("button", name="Run").first.click()
                await self.page.get_by_text(f"Finished run {click_index+1}").wait_for()
            await self.delay_reaction()

@pytest.mark.asyncio
async def test_component(port=6001):
    # When
    # Given
    component = App
    host = f"http://localhost:{port}"
    server = pn.serve(component, port=port, threaded=True, show=False)
    await asyncio.sleep(0.2)

    try:
        test = LoadTest(host=host, headless=False, user=LoadAndClickUser)
        await test.run()
    except Exception as ex:
        server.stop()
        raise Exception("Test failed") from ex
    finally:
        # Clean up
        server.stop()


if __name__ == "__main__":
    asyncio.run(test_component())
