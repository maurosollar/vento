#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask, json
from flask import request, jsonify
import sys, os, time
import importlib
from datetime import datetime
import mariadb, tzlocal
from calendar import monthrange

importlib.reload(sys)

app = flask.Flask(__name__)
app.config["DEBUG"] = False


@app.route('/', methods=['GET'])
def home():
    return 'Utilizar http://10.0.0.100:95/vento'


@app.route('/vento', methods=['GET'])
def ambiente():
    if not 'periodo' in request.args:
        return "A solicitação de dados do anemômetro pode ser pedido das seguintes formas: <br><br> - http://10.0.0.100:8080/vento?periodo=20200101  <--- Ano Mês Dia <br> - http://10.0.0.100:8080/vento?periodo=202001  <--- Ano Mês <br> - http://10.0.0.100:8080/vento?periodo=2020  <--- Ano"
    tempo = request.args.get('periodo')
    if len(tempo) < 4 and len(tempo) > 8:
        return "Erro na solicitação, verifique a sintaxe"
    if len(tempo) == 4:
        xtempo = tempo + '0101 000000'
        datai = time.mktime(datetime.strptime(xtempo, "%Y%m%d %H%M%S").timetuple())
        xtempo = tempo + '1231 235959'
        dataf = time.mktime(datetime.strptime(xtempo, "%Y%m%d %H%M%S").timetuple())
    if len(tempo) == 6:
        ano = tempo[:4]
        mes = tempo[4:6]
        ult_dia_mes = str(monthrange(int(ano), int(mes))[1])
        xtempo = tempo + '01 000000'
        print(xtempo)
        datai = time.mktime(datetime.strptime(xtempo, "%Y%m%d %H%M%S").timetuple())
        xtempo = tempo + ult_dia_mes + ' 235959'
        print(xtempo)
        dataf = time.mktime(datetime.strptime(xtempo, "%Y%m%d %H%M%S").timetuple())
    if len(tempo) == 8:
        xtempo = tempo + ' 000000'
        print(xtempo)
        datai = time.mktime(datetime.strptime(xtempo, "%Y%m%d %H%M%S").timetuple())
        xtempo = tempo + ' 235959'
        print(xtempo)
        dataf = time.mktime(datetime.strptime(xtempo, "%Y%m%d %H%M%S").timetuple())

    db = mariadb.connect(host='localhost', user='zabbix', passwd='????????', db='zabbix')
    cursor = db.cursor()
    sql = "select name, hostid from hosts where left(name,10) = 'Anemometro'"
    cursor.execute(sql)
    hosts = cursor.fetchone()
    sql = "select itemid, name, key_ from items where hostid = '" + str(hosts[1]) + "' and name = 'Anemometro'"
    cursor.execute(sql)
    sensor_anemometro = cursor.fetchone()
    sql = "select itemid, name, key_ from items where hostid = '" + str(hosts[1]) + "' and name = 'Direcao'"
    cursor.execute(sql)
    sensor_direcao = cursor.fetchone()
    print('Anemometro:', sensor_anemometro)
    print('Direcao:', sensor_direcao)
    resultado = '['
    sql = "select itemid, clock, value from history where (itemid = '" + str(sensor_anemometro[0]) + "' or itemid = '" + str(sensor_direcao[0]) + "') and (clock >= " + str(int(datai)) + " and clock <= " + str(int(dataf)) + ') order by clock'
    print("####################", sql)
    cursor.execute(sql)
    graficos = cursor.fetchone()
    local_tz = tzlocal.get_localzone()
    dados = []
    anemometro_ok = False
    direcao_ok = False
    anemometro_minuto = 0
    direcao_minuto = 0
    if graficos == None:
        return jsonify(json.loads('[{}]'))
    while graficos is not None:
        #print(graficos[0], graficos[1], datetime.fromtimestamp(int(graficos[1]), local_tz).strftime('%Y-%m-%-d %H:%M:%S'), graficos[2])
        minuto = datetime.fromtimestamp(int(graficos[1]), local_tz).strftime('%M')
        if graficos[0] == sensor_anemometro[0]:
            anemometro_ok = True
            anemometro = graficos[2]
            anemometro_minuto = minuto
        if graficos[0] == sensor_direcao[0]:
            direcao_ok = True
            direcao = graficos[2]
            direcao_minuto = minuto
        if anemometro_ok and direcao_ok and anemometro_minuto == direcao_minuto:
            dados.append([datetime.fromtimestamp(int(graficos[1]), local_tz).strftime('%Y-%m-%-d %H:%M:%S'), anemometro, direcao])
            anemometro_ok = False
            anemometro_ok = False
        graficos = cursor.fetchone()

    for xdados in dados:
        #print(xdados[0], xdados[1], xdados[2])
        resultado = resultado + '{"hora" : "' + xdados[0] + '", '
        resultado = resultado + '"velocidade" : "' + str(xdados[1]) + '", '
        resultado = resultado + '"direcao" : "' + str(xdados[2]) + '"'
        resultado = resultado + '}, '
    resultado = resultado[0:len(resultado)-2] + ']'
    cursor.close()
    db.close()
    return jsonify(json.loads(resultado))


app.config['JSON_AS_ASCII'] = False
app.run(host='0.0.0.0', port=8080)
