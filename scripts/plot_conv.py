import os

import plotly.graph_objects as go
from plotly.subplots import make_subplots

if __name__=='__main__':
    dir = '../outputs/'
    fc_names = ['250W', 'ps6', 'h-12', 'scribner_1']

    data=[]

    abs_str='absolute precision on f*:'
    time_str='cpu time used:'
    cells_str='number of cells:'

    for fc_name in fc_names:
        expo = 1
        prec = 10**(-expo)
        filename = dir+fc_name+'_r'+"{:.9f}".format(prec).rstrip('0')+'.txt'
        while os.path.isfile(filename):
            lines=[]
            with open(filename) as f:
                lines = f.readlines()

            line_data={'name': fc_name, 'r_prec':prec,'expo':expo}

            for line in lines:
                if line.find(abs_str)>=0:
                    start=line.find(abs_str)+len(abs_str)
                    line_data['a_prec']=float(line[start:])
                elif line.find(time_str)>=0:
                    start=line.find(time_str)+len(time_str)
                    line_data['time']=float(line[start:len(line)-2])
                elif line.find(cells_str)>=0:
                    start=line.find(cells_str)+len(cells_str)
                    line_data['cells']=int(line[start:])

            print(line_data)
            expo += 1
            prec = 10**(-expo)
            filename = dir+fc_name+'_r'+"{:.9f}".format(prec).rstrip('0')+'.txt'
            data.append(line_data)


    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for fc_name in fc_names:
        fig.add_trace(go.Scatter(mode='lines',
            x=[item['expo'] for item in filter(lambda d: d['name']==fc_name, data)],
            y=[item['time'] for item in filter(lambda d: d['name']==fc_name, data)],
            name='time '+fc_name),
            secondary_y=False)
        fig.add_trace(go.Scatter(mode='lines',
            x=[item['expo'] for item in filter(lambda d: d['name']==fc_name, data)],
            y=[item['cells'] for item in filter(lambda d: d['name']==fc_name, data)],
            name='nodes '+fc_name,
            line=dict(dash='dash')),
            secondary_y=True)
    fig.update_yaxes(type="log")
    fig.update_layout(xaxis_title="Relative precision")
    fig.update_layout(xaxis_tickvals=[item['expo'] for item in data])
    fig.update_layout(xaxis_ticktext=[item['r_prec'] for item in data])
    fig.update_layout(yaxis_title="Time (s)")
    fig.update_layout(yaxis2_title="Number of nodes")
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    fig.update_layout(template="plotly_white") # ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
    fig.show()
    fig.write_image("all_conv.svg")
