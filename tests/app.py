# app.py
import time

import panel as pn
import param

class App(pn.viewable.Viewer):
    run = param.Event(doc="Runs for click_delay seconds when clicked")
    runs = param.Integer(doc="The number of runs")
    status = param.String("No runs yet")

    load_delay = param.Number(0.5)
    run_delay = param.Number(0.5)
    
    def __init__(self, **params):
        super().__init__(**params)
        
        result = self._load()
        self._time = time.time()


        self._status_pane = pn.pane.Markdown(self.status, height=40, align="start", margin=(0,5,10,5))
        self._result_pane = pn.Column(result)
        self._view = pn.Column(
            pn.Row(pn.widgets.Button.from_param(self.param.run, sizing_mode="fixed"), self._status_pane),
            self._result_pane
        )

    def __panel__(self):
        return self._view

    def _start_run(self):
        self.status = f"Running ..."
        self._time = time.time()

    def _stop_run(self):
        now = time.time()
        duration = round(now-self._time,3)
        self._time = now
        self.runs+=1
        self.status=f"Finished run {self.runs} in {duration}sec"

    @pn.depends("run", watch=True)
    def _run_with_status_update(self):
        self._start_run()
        self._result_pane[:] = [self._run()]
        self._stop_run()

    @pn.depends("status", watch=True)
    def _update_status_pane(self):
        self._status_pane.object = self.status

    def _load(self):
        time.sleep(self.load_delay)
        return "Loaded"

    def _run(self):
        time.sleep(self.run_delay)
        return f"Result {self.runs+1}"
    
if __name__.startswith("bokeh"):
    pn.extension(sizing_mode="stretch_width")
    App().servable()