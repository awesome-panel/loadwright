# load_test_viewer.py
from __future__ import annotations
import pandas as pd
import hvplot.pandas
import holoviews as hv
from holoviews import opts
import panel as pn
import param
from bokeh.models import HoverTool


pn.extension(sizing_mode="stretch_width", template="fast")
hv.extension("bokeh")

def do_nothing():
    pass

class LoadTestViewer(pn.viewable.Viewer):
    max_load_duration = param.Number(2, bounds=(0.1, 5.0), step=0.1)
    max_interaction_duration = param.Number(1.0, bounds=(0.1, 5.0), step=0.1)
    aggregation = param.Selector(objects=["None", "Median", "Mean", "Min", "Max"])
    data = param.DataFrame()
    periodic_callback = param.Parameter()
    file = param.String("test_results/load_test.csv")

    def __init__(self, add_periodic_callback: bool=False, **params):
        super().__init__(**params)
        if not "data" in params:
            self.read()
        
        # self.data = self.clean(data=self.data)

        self._view = pn.Column(
            pn.Param(self, parameters=["max_load_duration", "max_interaction_duration"]),
            self.segment_plot,
            pn.widgets.RadioButtonGroup.from_param(self.param.aggregation),
            self.mean_duration_plot,
            self.active_users,
        )

        if not self.periodic_callback:
            self.periodic_callback = pn.state.add_periodic_callback(self.read, period=2000, start=add_periodic_callback)

    def __panel__(self):
        return self._view

    def read(self):
        try:
            self.data = pd.read_csv(self.file, parse_dates=["start", "stop"], dtype={"user": "str"}, index_col=0)
        except Exception as ex:
            print(ex)
            raise Exception() from ex

    @staticmethod
    def clean(data):
        data = data.copy(deep=True)
        data["start_seconds"]=(data["start"]-data["start"].min()).dt.total_seconds()
        data["stop_seconds"]=(data["stop"]-data["start"].min()).dt.total_seconds()

        return data

    @pn.depends("max_load_duration", "max_interaction_duration", "data")
    def segment_plot(self):
        data: pd.DataFrame = self.data[["user", "event", "start_seconds", "stop_seconds", "duration"]].copy()
        # sort indirectly by user, start_seconds
        min_start_by_user = data.groupby("user")["start_seconds"].min()
        data = data.join(min_start_by_user, on="user", rsuffix="_min")
        data = data.sort_values(by=["start_seconds_min", "start_seconds"])
        
        data["color"]="green"
        data.loc[(data["event"]=="load") & (data["duration"]>=self.max_load_duration),"color"]="red"
        data.loc[(data["event"]=="interact") & (data["duration"]>=self.max_interaction_duration),"color"]="red"
        plot = hv.Segments(data, [hv.Dimension('start_seconds', label='Time in seconds'), 
                         hv.Dimension('user', label='User'), 'stop_seconds', 'user'])
        hover = HoverTool(tooltips=[("event", "@event"), ("user", "@user"), ("start", "@start_seconds"), ("end", "@stop_seconds"), ("duration", "@duration")])
        plot.opts(color="color", line_width=20, tools=[hover], xlim=self._xlim)
        return plot

    @pn.depends("max_load_duration", "max_interaction_duration", "data")
    def mean_duration_plot(self):
        data = self.data.copy()
        data = data.sort_values("start_seconds")
        tmp = data.groupby(['event']).expanding().duration
        if self.aggregation=="Median":
            data["value"]=tmp.median().reset_index().set_index("level_1")["duration"]
        elif self.aggregation=="Mean":
            data["value"]=tmp.mean().reset_index().set_index("level_1")["duration"]
        elif self.aggregation=="Min":
            data["value"]=tmp.min().reset_index().set_index("level_1")["duration"]
        elif self.aggregation=="Max":
            data["value"]=tmp.max().reset_index().set_index("level_1")["duration"]
        else:
            data["value"]=data.duration
        data["color"]=data["event"].map({"load": "#0072B5", "interact": "#DF9F1F"})
        data=data.sort_values("start_seconds")
        
        plot = data.hvplot(x="start_seconds", y="value", by="event", xlabel="Time in seconds", ylabel="Duration in seconds", hover=False, color="color", ylim=(0,None), xlim=self._xlim, height=400).opts(legend_position='bottom') *\
            data.hvplot(x="start_seconds", y="value", by="event", xlabel="Time in seconds", ylabel="Duration in seconds", kind="scatter", hover=True, color="color")

        plot = plot * hv.HLine(self.max_load_duration).opts(color="red", line_width=1)
        plot = plot * hv.HLine(self.max_interaction_duration).opts(color="red", line_width=1)
        return plot

    @property
    def _xlim(self):
        return (self.data["start_seconds"].min(), self.data["stop_seconds"].max())

    @pn.depends("data")
    def active_users(self):
        data = self.data.copy()
        timestamps = sorted(set(data.start_seconds.unique()).union(set(data.stop_seconds.unique())))
        user_start = data.groupby("user")["start_seconds"].min()
        user_stop = data.groupby("user")["stop_seconds"].max()
        results = []
        for timestamp in timestamps:
            active_users = sum((user_start<=timestamp) & (user_stop>=timestamp))
            results.append({"start_seconds": timestamp, "active_users": active_users})
        data = pd.DataFrame(results)
        max_users = data["active_users"].max()
        return data.hvplot(x="start_seconds", y="active_users", xlabel="Time in seconds", ylabel="Active users", color="#0072B5", hover=False, yticks=list(range(0, max_users+1))) *\
        data.hvplot(x="start_seconds", y="active_users", xlabel="Time in seconds", ylabel="Active users", color="#0072B5", kind="scatter", ylim=(0,None), yticks=list(range(0, max_users+1)))

if __name__.startswith("bokeh"):
    app = LoadTestViewer(add_periodic_callback=True)
    pn.panel(app).servable()