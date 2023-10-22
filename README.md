# ✨ Loadwright

We want to

- Make it really easy to load test data apps in Python and get useful insights

We provide

- A `LoadTestRunner` that can record complex `User` interactions with your data app
- A `LoadTestViewer` that can show you the results of the recording.

The framework is based on [Playwright](https://playwright.dev/python/) and [Panel](https://panel.holoviz.org).

You can install and use the package as simple as.

```bash
pip install loadwright
```

See the [`tests`](tests) folder for examples or the [Panel test operating capacity howto](https://panel.holoviz.org/how_to/test/loadtests.html).

![Project Intro](https://user-images.githubusercontent.com/42288570/210130957-92dee566-4fcf-4a02-a8ee-830af6297307.gif)

Please note this project is at a **very early stage an the api and functionality will change**!

## Why not Locust

I love Locust. But Locust and Playwright just does not work well for me. See [locust-plugins #101](https://github.com/SvenskaSpel/locust-plugins/issues/101#issuecomment-1367216919). And this gave me an oppportunity to play with Panel+Async+Streaming.

## ⭐ Support

Please support [Panel](https://panel.holoviz.org) and
[awesome-panel](https://awesome-panel.org) by giving the projects a star on Github:

- [holoviz/panel](https://github.com/holoviz/panel).
- [awesome-panel/awesome-panel](https://github.com/awesome-panel/awesome-panel).

Thanks

## ❤️ Contribute

If you are looking to contribute to this project you can find ideas in the [issue tracker](https://github.com/awesome-panel/loadwright/issues). To get started check out the [DEVELOPER_GUIDE](DEVELOPER_GUIDE.md).

I would love to support and receive your contributions. Thanks.

[![Hacktober Fest](https://github.blog/wp-content/uploads/2022/10/hacktoberfestbanner.jpeg?fit=1200%2C630)](https://github.com/awesome-panel/loadwright/issues).

## Monitor

[![PyPI version](https://badge.fury.io/py/loadwright.svg)](https://pypi.org/project/loadwright/)
[![Downloads](https://pepy.tech/badge/loadwright/month)](https://pepy.tech/project/loadwright)
![Python Versions](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue)
[![License](https://img.shields.io/badge/License-MIT%202.0-blue.svg)](https://opensource.org/licenses/MIT)
![Test Results](https://github.com/awesome-panel/loadwright/actions/workflows/tests.yaml/badge.svg?branch=main)
