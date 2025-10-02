import re
import plotly.graph_objects as go

if __name__=='__main__':
    dir = '../outputs/'
    fc_names = ['250W', 'ps6', 'h-12', 'scribner_850e_1_25']

    data=[]

    for fname in fc_names:
        lines=[]
        with open(dir+fname+'.txt') as f:
            lines = f.readlines()

        flt_str = '[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?'
        int_str= '\d+'
        loup_scan=False

        uplos=[]
        loups=[]

        cur_loup={}
        for line in lines:
            if re.search('^\['+flt_str,line):
                # print(line)
                m = re.search(flt_str,line)
                # print('t:',m[0])
                # t = float(m.group(0)[1:])
                t = float(m[0])
                m = re.search('/'+int_str,line)
                # print('nb:',m[0][1:])
                nb = int(m[0][1:])
                m = re.search('uplo= '+flt_str,line)
                # print('uplo:',m[0][6:])
                uplo = float(m[0][6:])
                loup_scan=False
                uplos.append({'uplo': uplo, 'nb_cells':  nb, 'time': t })
            elif re.search('^\{'+flt_str,line):
                m = re.search('^\{'+flt_str,line)
                loup_scan=True
                # print('t:',m[0][1:])
                t = float(m[0][1:])
                m = re.search('/'+int_str,line)
                nb = int(m[0][1:])
                cur_loup = {'nb_cells':  nb, 'time': t }
            elif loup_scan and re.search('loup= '+flt_str,line):
                m = re.search('loup= '+flt_str,line)
                cur_loup['loup']=float(m[0][6:])
                loups.append(cur_loup)
            else:
                print('Unknown line type:',line)
                loup_scan=False
        data.append({'name':fname, 'loup': loups, 'uplo': uplos})

    fig = go.Figure()
    for dat in data:
        fname = dat['name'] if dat['name'] != 'scribner_850e_1_25' else 'scribner'
        fig.add_trace(
            go.Scatter(mode='lines',
                x=[item['time'] for item in dat['loup']],
                y=[item['loup'] for item in dat['loup']],
                name='UB '+fname))
        fig.add_trace(
            go.Scatter(mode='lines',
                x=[item['time'] for item in dat['uplo']],
                y=[item['uplo'] for item in dat['uplo']],
                name='LB '+fname,line=dict(dash='dash')))
        fig.update_yaxes(type="log")
        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        ))
    fig.update_yaxes(title="SSE")
    fig.update_xaxes(title="Time (s)")
    fig.update_layout(template="plotly_white") # ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))
    fig.show()
    fig.write_image("all_res.svg")
