#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from math import pi
import json, requests, flask
from flask import request, Flask, render_template
from windrose import WindroseAxes
import datetime

app = flask.Flask(__name__)
app.config['DEBUG'] = False

@app.route('/', methods =["GET", "POST"])
def gfg():
    if request.method == "POST":
        xdata = request.form.get("date")
        xperiodo = request.form.get("periodo")
        if xperiodo == 'ano':
            periodo = xdata[0:4]
        if xperiodo == 'mes':
            periodo = xdata[0:4] + xdata[5:7]
        if xperiodo == 'dia':
            periodo = xdata[0:4] + xdata[5:7] + xdata[8:10]
        json_data = requests.get('http://10.0.0.100:8085/vento?periodo=' + periodo)
        json_data = json_data.json()
        if len(json_data) == 1:
            return "Sem dados no período"
        plt.switch_backend('agg')
        df = pd.DataFrame(json_data)

        df['velocidade'] = df['velocidade'].astype(float)
        df['direcao'] = df['direcao'].astype(float)

        ax = WindroseAxes.from_ax()
        ax.bar(df.direcao, df.velocidade, normed=True, opening=0.8, edgecolor='white')
        ax.set_legend()
        plt.suptitle('(Anemômetro / Direção do Vento)')
        plt.savefig("/usr/local/sbin/windrose/static/images/windrose.png", dpi = 100)
        plt.close('all')
        arqsai = open('/usr/local/sbin/windrose/static/images/dados.csv','w')
        for linha in json_data:
            arqsai.write(linha['hora'] + ';' + linha['velocidade'] + ';' + linha['direcao'] + '\n')
        arqsai.close()
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        return render_template("resultado.html", periodo = periodo, timestamp = timestamp)
    else:
        return render_template("form.html")

app.run(host='0.0.0.0', port=8085)
