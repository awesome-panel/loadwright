"""We can run load tests on data apps"""
import param
import pytest

from loadwright import LoadTestRunner, User

from .app import App


class LoadAndClickUser(User):
    """A custom User that loads a page and clicks a button n_clicks times"""

    n_clicks = param.Integer(
        default=1, bounds=(0, None), doc="The number of times to click the button"
    )

    async def run(self):
        with self.event(name="load", user=self.name):
            await self.page.goto(self.url)
            await self.page.get_by_role("button", name="Run").wait_for()
        await self.sleep()

        for click_index in range(self.n_clicks):
            with self.event(name="interact", user=self.name):
                await self.page.get_by_role("button", name="Run").first.click()
                await self.page.get_by_text(f"Finished run {click_index+1}").wait_for()
            await self.sleep()


def test_custom_user():
    """We can use a custom user"""
    org_user = LoadTestRunner.param.user.default
    assert not isinstance(org_user, LoadAndClickUser)

    user = LoadAndClickUser()
    runner = LoadTestRunner(user=user)
    assert runner.user == user

    assert LoadTestRunner.param.user.default == org_user


@pytest.mark.asyncio
async def test_component_2(port=6001):
    """We can run the LoadTestRunner with 2 users"""
    async with LoadTestRunner.serve(App, port=port) as host:
        await LoadTestRunner(host=host, headless=False, user=LoadAndClickUser(), n_users=2).run()
