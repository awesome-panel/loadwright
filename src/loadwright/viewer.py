"""The LoadTestViewer can be used to view the Loadwright results"""
from __future__ import annotations

from pathlib import Path

import holoviews as hv
import hvplot.pandas  # pylint: disable=unused-import
import pandas as pd
import panel as pn
import param
from bokeh.models import HoverTool

from loadwright.io import read_loadwright_file
from loadwright.logger import DEFAULT_LOADWRIGHT_FILE


class LoadTestViewer(pn.viewable.Viewer):
    """A component for viewing Loadwright DataFrames or files"""

    max_load_duration = param.Number(
        2, bounds=(0.1, 5.0), step=0.1, doc="The maximum alloweable time for the load event"
    )
    max_interaction_duration = param.Number(
        1.0, bounds=(0.1, 5.0), step=0.1, doc="The maxium allowable time for the interaction event"
    )
    aggregation = param.Selector(objects=["None", "Median", "Mean", "Min", "Max"])
    data = param.DataFrame()

    def __init__(self, data: str | Path | pd.DataFrame | None = None, **params):
        if data is None:
            data = DEFAULT_LOADWRIGHT_FILE
        if isinstance(data, (str, Path)):
            data = read_loadwright_file(data)
        super().__init__(data=data, **params)

        self._view = pn.Column(
            pn.Param(self, parameters=["max_load_duration", "max_interaction_duration"]),
            self.segment_plot,
            pn.widgets.RadioButtonGroup.from_param(self.param.aggregation),
            self.duration_plot,
            self.active_users_plot,
        )

    def __panel__(self):
        return self._view

    @pn.depends("max_load_duration", "max_interaction_duration", "data")
    def segment_plot(self):
        """Returns a HoloViews segment plot"""
        data: pd.DataFrame = self.data[
            ["user", "event", "start_seconds", "stop_seconds", "duration"]
        ].copy()
        # sort indirectly by user, start_seconds
        min_start_by_user = data.groupby("user")["start_seconds"].min()
        data = data.join(min_start_by_user, on="user", rsuffix="_min")
        data = data.sort_values(by=["start_seconds_min", "start_seconds"])

        data["color"] = "green"
        data.loc[
            (data["event"] == "load") & (data["duration"] >= self.max_load_duration), "color"
        ] = "red"
        data.loc[
            (data["event"] == "interact") & (data["duration"] >= self.max_interaction_duration),
            "color",
        ] = "red"
        plot = hv.Segments(
            data,
            [
                hv.Dimension("start_seconds", label="Time in seconds"),
                hv.Dimension("user", label="User"),
                "stop_seconds",
                "user",
            ],
        )
        hover = HoverTool(
            tooltips=[
                ("event", "@event"),
                ("user", "@user"),
                ("start", "@start_seconds"),
                ("end", "@stop_seconds"),
                ("duration", "@duration"),
            ]
        )
        plot.opts(color="color", line_width=20, tools=[hover], xlim=self._xlim)
        return plot

    @pn.depends("max_load_duration", "max_interaction_duration", "aggregation", "data")
    def duration_plot(self):
        """Returns a HoloViews plot of time vs event duration"""
        data = self.data.copy()
        data = data.sort_values("start_seconds")
        tmp = data.groupby(["event"]).expanding().duration
        if self.aggregation == "Median":
            data["value"] = tmp.median().reset_index().set_index("level_1")["duration"]
        elif self.aggregation == "Mean":
            data["value"] = tmp.mean().reset_index().set_index("level_1")["duration"]
        elif self.aggregation == "Min":
            data["value"] = tmp.min().reset_index().set_index("level_1")["duration"]
        elif self.aggregation == "Max":
            data["value"] = tmp.max().reset_index().set_index("level_1")["duration"]
        else:
            data["value"] = data.duration
        data["color"] = data["event"].map({"load": "#0072B5", "interact": "#DF9F1F"})
        data = data.sort_values("start_seconds")

        plot = data.hvplot(
            x="start_seconds",
            y="value",
            by="event",
            xlabel="Time in seconds",
            ylabel="Duration in seconds",
            hover=False,
            color="color",
            ylim=(0, None),
            xlim=self._xlim,
            height=400,
        ).opts(legend_position="bottom") * data.hvplot(
            x="start_seconds",
            y="value",
            by="event",
            xlabel="Time in seconds",
            ylabel="Duration in seconds",
            kind="scatter",
            hover=True,
            color="color",
        )

        plot = plot * hv.HLine(self.max_load_duration).opts(color="red", line_width=1)
        plot = plot * hv.HLine(self.max_interaction_duration).opts(color="red", line_width=1)
        return plot

    @property
    def _xlim(self):
        return (self.data["start_seconds"].min(), self.data["stop_seconds"].max())

    @pn.depends("data")
    def active_users_plot(self):
        """Returns a plot of time vs the number of active users"""
        data = self.data.copy()
        timestamps = sorted(set(data.start_seconds.unique()).union(set(data.stop_seconds.unique())))
        user_start = data.groupby("user")["start_seconds"].min()
        user_stop = data.groupby("user")["stop_seconds"].max()
        results = []
        for timestamp in timestamps:
            active_users = sum((user_start <= timestamp) & (user_stop >= timestamp))
            results.append({"start_seconds": timestamp, "active_users": active_users})
        data = pd.DataFrame(results)
        max_users = data["active_users"].max()
        return data.hvplot(
            x="start_seconds",
            y="active_users",
            xlabel="Time in seconds",
            ylabel="Active users",
            color="#0072B5",
            hover=False,
            yticks=list(range(0, max_users + 1)),
        ) * data.hvplot(
            x="start_seconds",
            y="active_users",
            xlabel="Time in seconds",
            ylabel="Active users",
            color="#0072B5",
            kind="scatter",
            ylim=(0, None),
            yticks=list(range(0, max_users + 1)),
        )
