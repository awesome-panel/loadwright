from loadwright import LoadTestViewer, read_loadwright_file

if __name__.startswith("bokeh"):
    data = read_loadwright_file()
    viewer =  LoadTestViewer(data=data).servable()