from __future__ import print_function
#  IMPORTS PARA GOOGLE API incluyenod la de arriba.NO poner nada x encima de __future__
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from werkzeug.utils import secure_filename
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from oauth2client import file, client, tools
#  IMPORT FLASK
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, jsonify, g, jsonify, Response
from flask_mysqldb import MySQL, MySQLdb
import bcrypt
import os
import sys
import json
from datetime import datetime
from flask_restful import Resource, Api
import random
from random import choice
from os import remove
import time
import smtplib
import getpass
from time import gmtime, strftime
from datetime import date, time, timezone, timedelta, datetime
import datetime
from pytz import timezone
from flask_mail import Mail
from flask_mail import Message
import pdfkit
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#loggin
import logging
logging.basicConfig( level=logging.DEBUG, filename='logs/example.log')



sys.path.append(os.getcwd())
### LISTA DE EXT PERMITIDAS + CARPETA DONDE SE SUBEN LOS ARCHIVOS ##############
extensionesPermitidas = {'txt', 'pdf', 'png', 'jpg', 'jpeg'} #lista de formatos permitidos
UPLOAD_FOLDER =  environ.get('URL_FILES_UPLOAD')

app = Flask(__name__)


# MySQL Connection config
app.config['MYSQL_HOST'] = environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = environ.get('MYSQL_DB')
app.config['UPLOAD_FOLDER'] = environ.get('UPLOAD_FOLDER')
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024


mysql = MySQL(app)

###########HOME###############
@app.route('/')
def index():

  return render_template('index.html')


###########LOGIN###############

@app.route('/login', methods=["GET","POST"])
def login():
  if request.method == 'POST':
    nombUser = request.form['nombUser'] #nombre de usuario que se ingresa en el form de login
    passUser = request.form['passUser'].encode('utf-8') # Almacenamos la password del form de login en una variable+encode para q reconozca simbolos
    hashedpassword = bcrypt.hashpw(passUser, bcrypt.gensalt(19)) #hasheamos la pass ingresa con un gensalt14
    cur = mysql.connection.cursor() #creamos cursor p coenectarnos a la db
    cur.execute("SELECT * FROM usuario WHERE nom_usu =%s",(nombUser,)) #buscamos el  nombre de usuario ingresado en la DB
    try: #primero que intente encontrar algo
      User = cur.fetchone() #traemos toda la info de USUARIO aca
      print ('User encontrado', User)
      if bcrypt.checkpw(passUser, User[2].encode('utf-8')) and User[3] == 0: #comparamos las passwords hasheadas y que User[3] (estado usuario) sea 0, es decir,activo
          session['idUser'] = User [0], # si coincidn las pass de arriba, almacenamos en la session del usuario su id, nombre de usuario y tipo
          session['nombUser'] = User[1],
          session['tipoUser'] = User [4]
          print ('usuario ingresado->', nombUser)
          print ('pass ingresada ->', passUser)
          print ('pass ingresada hasheada ->', hashedpassword)
          flash ("Te has logueado exitosamente!", 'success') #mostramos un flash de logueo exitoso  
          return redirect(url_for('inicio')) #y lo redireccionamos al inicio          
      else: # si las pass  no coiniciden se los manda aca a un flash de error
          flash (' ERROR: usuario o password incorrecto!', 'danger') 
          return redirect(url_for('login')) # y se lo redirecciona a la pantalla de logi nde nuevo
    except: # aca si el usuario no existe en la db, tambien se le meustra error y se lo redirecciona al login
      flash (' ERROR: usuario o password incorrecto!', 'danger')
      print ('usuario ingresado->', nombUser)
      print ('pass ingresada ->', passUser)
      print ('pass ingresada hasheada ->', hashedpassword)
      return redirect(url_for('login'))       
  else:
    print ('else, no post request.method')
    return render_template("login.html")

###########LOGOUT###############
@app.route('/logout')
def logout():
    session.clear()
    flash ("Has cerrado sesión. Hasta luego", 'danger')
    return render_template("index.html")

###########INICIO###############
@app.route('/inicio')
def inicio():
  nombreUsuario= session['nombUser'][0]
  if session['tipoUser'] == 2:#Si el tipo de usuario es Empleador, puedo generar un pago, solo para mi(Empleador)
    idUsuario = session['idUser'][0]  #Obtengo el idUser con el que se logeo
    cur = mysql.connection.cursor() #Y busco los datos de empleador del usuario
    cur.execute(
        "SELECT email_emp,Id_emp FROM emp INNER JOIN usuario on emp.idusu_emp = usuario.id_usu where idusu_emp=%s", (str(idUsuario),))
    email = cur.fetchall()
   
    if email[0][0]==None:
      return render_template("registraremail.html", nombreUsuario=nombreUsuario)
    else:
      return render_template("inicio.html", nombreUsuario=nombreUsuario )
  else:
      return render_template("inicio.html", nombreUsuario=nombreUsuario)

###########INICIO###############
@app.route('/registerEmail',methods=["GET","POST"])
def registerEmail():
  nombreUsuario = session['nombUser'][0]
  if request.method == 'POST':
    if session['tipoUser'] == 2:#Si el tipo de usuario es Empleador, puedo generar un pago, solo para mi(Empleador)
      idUsuario = session['idUser'][0]  #Obtengo el idUser con el que se logeo
      cur = mysql.connection.cursor() #Y busco los datos de empleador del usuario
      cur.execute(
          "SELECT Id_emp FROM emp INNER JOIN usuario on emp.idusu_emp = usuario.id_usu where idusu_emp=%s", (str(idUsuario),))
      idUsuario = cur.fetchall()
      idEmp=idUsuario[0][0]
      emailEmp = str(request.form['email'])
      cur = mysql.connection.cursor()
      cur.execute('UPDATE emp SET email_emp=%s WHERE id_emp=%s',(emailEmp,idEmp,))
      cur.connection.commit()

      flash("Email Registrado Correctamente","success")
      return render_template("inicio.html", nombreUsuario=nombreUsuario)
    else:
      return render_template("inicio.html", nombreUsuario=nombreUsuario)
###########EMPLEADORES###############

@app.route('/empleadores')
def empleadores():

    #Obtengo el listado de Prestadores
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM emp")
    Empleadores = cur.fetchall()

    return render_template('empleadores.html',listaEmpleadores=Empleadores)

###########PERFIL EMPLEADOR###############
@app.route('/empleadores/<string:id_emp>')
def perfilEmpleador(id_emp):
    idemp=str(id_emp) #El id lo recibo desde la ruta
    #Obtengo los datos del Empleador seleccionado
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM emp where id_emp=%s", (idemp,))
    perfilEmpleador = cur.fetchall()
 
    return render_template('perfilEmpleador.html', perfilEmpleador=perfilEmpleador,id_emp=id_emp)


###########MI PERFIL###############
@app.route('/miperfil')
def miperfil():
    nombreUsuario = session['nombUser'][0]
    idUsuario = session['idUser'][0]
      
    cur = mysql.connection.cursor() #Y busco los datos de empleador del usuario
    if session['tipoUser'] == 2:
      cur.execute(
          "SELECT * FROM  usuario INNER JOIN emp on usuario.id_usu=emp.idusu_emp where id_usu=%s", (str(idUsuario),))
      perfilUsuario = cur.fetchall()
    else:
      cur.execute("SELECT * FROM  usuario where id_usu=%s", (str(idUsuario),))
      perfilUsuario = cur.fetchall()
    return render_template('miPerfil.html',perfilUsuario=perfilUsuario)


###########PAGOS EMPLEADOR###############
@app.route('/empleadores/pago/<string:id_emp>')
def pagosEmpleador(id_emp):
    idemp = str(id_emp) #recibo el parametro desde la ruta


    #Obtengo el NOMBRE del Empleador seleccionado
    cur = mysql.connection.cursor()
    cur.execute("SELECT rs_emp FROM emp where Id_emp=%s", (idemp,))
    nombreEmpleador = cur.fetchall()
    nombreEmpleador = nombreEmpleador[0][0]
    
    #Obtengo los PAGOS del Empleador seleccionado
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM boleta where Id_empbol=%s order by mliq_bol desc", (idemp,))
    pagosEmpleador = cur.fetchall()

    return render_template('pagosEmpleador.html', pagosEmpleador=pagosEmpleador, nombreEmpleador=nombreEmpleador, id_emp=id_emp)

###########PAGOS###############

@app.route('/pagos')
def pagos():
  if session['tipoUser'] == 2:  #Si el tipo de usuario es Empleador, puedo generar un pago, solo para mi(Empleador)

    idUsuario = session['idUser'][0]  #Obtengo el idUser con el que se logeo
    cur = mysql.connection.cursor() #Y busco los datos de empleador del usuario
    cur.execute(
        "SELECT * FROM emp INNER JOIN usuario on emp.idusu_emp = usuario.id_usu where idusu_emp=%s", (str(idUsuario),))
    nombreEmpleadorGenPago = cur.fetchall()
    nombreEmpleadorGenPago = nombreEmpleadorGenPago[0][1] #Necesito el nombre por lo que lo separo y lo envio como parametro
    
    ### BUSCO LOS PAGOS DEL EMPLEADOR ###
    cur = mysql.connection.cursor()  # Y busco los datos de empleador del usuario
    cur.execute(
        "SELECT Id_bol as NPago,Id_empbol as EmpBol,mliq_bol as MesLiq, fge_bol as FecGen, imp_bol as Monto,can_bol as CEmpl, est_bol as EstBol,otr_bol as Otros from boleta INNER JOIN emp on boleta.Id_empbol=emp.id_emp INNER JOIN usuario on emp.idusu_emp=usuario.id_usu where idusu_emp=%s order by mliq_bol desc", (str(idUsuario),))
    boletasUsuario = cur.fetchall()
    
    return render_template('pagos.html', nombreEmpleadorGenPago=nombreEmpleadorGenPago, boletasUsuario=boletasUsuario)

  if session['tipoUser'] == 1 or session['tipoUser'] == 3:

    ### BUSCO LOS PAGOS DEL EMPLEADOR ###
    cur = mysql.connection.cursor()  # Y busco los datos de empleador del usuario
    cur.execute(
        "SELECT Id_bol as NPago,Id_empbol as EmpBol,mliq_bol as MesLiq, fge_bol as FecGen, imp_bol as Monto,can_bol as CEmpl, est_bol as EstBol,rs_emp,bolr_bol as LinkBol, comr_bol as LinkPag,otr_bol as Otros  from boleta INNER JOIN emp on boleta.Id_empbol=emp.id_emp INNER JOIN usuario on emp.idusu_emp=usuario.id_usu WHERE mliq_bol BETWEEN CURDATE() - INTERVAL 15 MONTH AND CURDATE()  order by mliq_bol desc")
    boletasUsuario = cur.fetchall()
    

    return render_template('pagos.html', boletasUsuario=boletasUsuario)


###########CALCULO CUOTA###############


@app.route('/calcularCuota', methods=['GET', 'POST'])
def calcularCuota():
  if request.method == 'POST':
    
    data = request.get_json()
    data = data[0]
    totalRemuneracion = float(data['totalRemuneracion'])
    cuotaSind=totalRemuneracion*float(0.015)
    res1116 = totalRemuneracion*float(0.015)
    total=cuotaSind+res1116

    #Retorno los datos necesarios para la vista (Se utilizan en el success de AJAX)
    return jsonify({'Mensaje': 'Correcto','cuotaSind': cuotaSind,'res1116':res1116,'total':total})

###########GENERAR CUOTA###############


@app.route('/generarCuota', methods=['GET', 'POST'])
def generarCuota():
  if request.method == 'POST':
    idUsuario = session['idUser'][0]  # Obtengo el idUser con el que se logeo
    cur = mysql.connection.cursor()  # Y busco los datos de empleador del usuario
    cur.execute(
        "SELECT * FROM emp INNER JOIN usuario on emp.idusu_emp = usuario.id_usu where idusu_emp=%s", (str(idUsuario),))
    idEmpl = cur.fetchall()
    # Id del empleador, lo necesito para insertar el pago
    idEmpl = idEmpl[0][0]

    #Recibo los parametros
    data = request.get_json()
    data = data[0]
    fechaLiq = str(data['fechaLiq'])
    cantEmpl = str(data['cantEmpl'])
    montoBol = str(data['total'])
    otrosApor = str(data['otrosApor'])

    #Verifico que no exista pago generado para dicho periodo
    cur = mysql.connection.cursor()  # Y busco los datos de empleador del usuario
    cur.execute("SELECT * FROM boleta where Id_empbol=%s and mliq_bol=%s and est_bol!='1'",
                (str(idEmpl), str(fechaLiq),))
    pagLiq = cur.fetchall()
    ##Queda comentado, pero seguramente vuelve atras
    """ if len(pagLiq) > 0:  
      flash('Ya Existe un Pago Generado Para Dicho Periodo','danger')
      return jsonify({'Mensaje': 'Error'})
    else: """
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO boleta (Id_empbol,mliq_bol,imp_bol,can_bol,est_bol,otr_bol) VALUES (%s,%s,%s,%s,%s,%s)',
                (idEmpl, fechaLiq, montoBol, cantEmpl, '0', otrosApor))
    cur.connection.commit()
    flash('Pago Generado Con Exito', 'success')

    return jsonify({'Mensaje': 'Correcto'})

#Generar Cuota del Lado del Empleador


@app.route('/generarCuotaEmpleador', methods=['GET', 'POST'])
def generarCuotaEmpleador():
  if request.method == 'POST':
    data = request.get_json()
    data = data[0]

    idUsuario = str(data['id_emp'])  # Obtengo el idUser con el que se logeo
    print(idUsuario)
    cur = mysql.connection.cursor()  # Y busco los datos de empleador del usuario
    cur.execute(
        "SELECT * FROM emp INNER JOIN usuario on emp.idusu_emp = usuario.id_usu where id_emp=%s", (str(idUsuario),))
    idEmpl = cur.fetchall()
    # Id del empleador, lo necesito para insertar el pago
    idEmpl = idEmpl[0][0]

    #Recibo los parametros

    fechaLiq = str(data['fechaLiq'])
    cantEmpl = str(data['cantEmpl'])
    montoBol = str(data['total'])
    otrosApor = str(data['otrosApor'])

    #Verifico que no exista pago generado para dicho periodo
    cur = mysql.connection.cursor()  # Y busco los datos de empleador del usuario
    cur.execute("SELECT * FROM boleta where Id_empbol=%s and mliq_bol=%s and est_bol!='1'",
                (str(idEmpl), str(fechaLiq),))
    pagLiq = cur.fetchall()
    ##Queda comentado, pero seguramente vuelve atras
    """ if len(pagLiq) > 0:  
      flash('Ya Existe un Pago Generado Para Dicho Periodo','danger')
      return jsonify({'Mensaje': 'Error'})
    else: """
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO boleta (Id_empbol,mliq_bol,imp_bol,can_bol,est_bol,otr_bol) VALUES (%s,%s,%s,%s,%s,%s)',
                (idEmpl, fechaLiq, montoBol, cantEmpl, '0', otrosApor))
    cur.connection.commit()
    flash('Pago Generado Con Exito', 'success')

    return jsonify({'Mensaje': 'Correcto'})






    

    

###########NUEVO PAGO###############

@app.route('/nuevoPago/<string:id_bol>')
def nuevoPago(id_bol):
  
  cur = mysql.connection.cursor()  # Y busco los datos de empleador del usuario
  cur.execute("SELECT * from boleta where Id_bol=%s", (str(id_bol),))
  boleta = cur.fetchall()
 
  return render_template ('nuevoPago.html', boleta=boleta)


###########ESTADO BOLETAS###############

@app.route('/estadoboleta/<string:id_bol>', methods=["POST"])
def estadoboleta(id_bol):
  if request.method == 'POST':

    cur = mysql.connection.cursor()
    cur.execute("SELECT Id_empbol FROM boleta where Id_bol=%s", (id_bol,))
    id_empleador = cur.fetchall()
    id_empleador = id_empleador[0][0]

    estado_boleta = request.form['estado']
    if estado_boleta != '3':
      cur = mysql.connection.cursor()
      cur.execute('UPDATE boleta SET est_bol='+str(estado_boleta) +
                  ' WHERE Id_bol='+str(id_bol) + '')
      cur.connection.commit()
    else:
      pass

    if estado_boleta == '3':
      fechaHoy = str(date.today())
      print(fechaHoy)
      cur = mysql.connection.cursor()
      cur.execute(
          'UPDATE boleta SET est_bol=%s ,fec_pag=%s WHERE Id_bol=%s', ("3", fechaHoy, id_bol))
      cur.connection.commit()

    return redirect(url_for('pagosEmpleador', id_emp=id_empleador))


########### ELEGIR COMPROBANTE ###############    

def archivoPermitido(filename): #checkeamos que el archivo subido tenga una extension permitida
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensionesPermitidas

@app.route('/nuevoPago/elegirComprobante', methods=['GET', 'POST'])
def elegirComprobante():
  if request.method == 'POST': 
    fileComprobante = request.files["fileComprobante"]
    print ('filecomprobante filename antes del if  : ', fileComprobante.filename)
    if fileComprobante and archivoPermitido(fileComprobante.filename):
      fileComprobanteNombreCorregido = secure_filename(fileComprobante.filename)
      print ('fileComprobante ELEGIDA corregida->', fileComprobanteNombreCorregido)    
      print ('filename fileComprobante ELEGIDA->', fileComprobante.filename)
      return jsonify({'Mensaje': 'Correcto', 'nombreArchivo':fileComprobante.filename, 'fileComprobanteNombreCorregido':fileComprobanteNombreCorregido})
    


########### SUBIR COMPROBANTE ###############    

@app.route('/nuevoPago/subirComprobante', methods=['GET', 'POST'])
def subirComprobante():
  if request.method == 'POST':
    fileComprobante = request.files["fileComprobante"]
    print ('fileComprobante ELEGIDO->', fileComprobante)    
    print ('filename fileComprobante ELEGIDO->', fileComprobante.filename)    
    if fileComprobante.filename == '':
      print ('no se selecciono archivo?')
      return redirect(url_for('pagos'))
    if fileComprobante and archivoPermitido(fileComprobante.filename):
            filename = secure_filename(fileComprobante.filename)
            fileComprobante.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print ('Comprobante SUBIDO AL SERVER')    
            return jsonify({'Mensaje': 'Correcto', 'nombreArchivo':fileComprobante.filename})
                           
    else:
      print ('no se selecciono archivo o el formato es incorrecto') 
      return jsonify({'Mensaje': 'Error'})

    # print ('fileboleta/> ', fileBoleta.filename)
    #Retorno los datos necesarios para la vista (Se utilizan en el success de AJAX)



########### INFORMAR PAGO ###############   ME FALTA AGREGAR COMPROBANTE ACA

@app.route('/informarPago', methods=["POST"])
def informarPago():
  if request.method == 'POST':
    idBoleta = request.form['idBoleta']
    # nombreBoleta = request.form ['fileBoletaNombreHidden']    
    nombreComprobante = request.form ['fileComprobanteNombreHidden']
    # print ('nombre boleta file boleta->>>>>   ', nombreBoleta)
    print ('nombre comprobante file comprobante->>>>>   ', nombreComprobante)
    #recupero el mes par el flash
    cur = mysql.connection.cursor()
    cur.execute("SELECT mliq_bol FROM boleta where Id_bol=%s", (idBoleta,))
    mesLiquidacion = cur.fetchall()
    mesLiqFlash = str(mesLiquidacion[0][0].strftime('%m-%Y'))
    mesLiquidacion = str(mesLiquidacion[0][0])

    SCOPES = 'https://www.googleapis.com/auth/drive.file' #one or more scopes (strings)
    CLIENT_SECRET = '/home/alfonso/sindicatoCarneRioIV/testAPI/serviceAcc.json' # en este json se guarda la info 'secreta' de la GSA para darle permisos
    #aca almacenamos las credenciales
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
      CLIENT_SECRET, scopes=SCOPES)
      DRIVE = build('drive', 'v3', credentials=credentials)
    folder_id = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxx' 
  


    for filename, mimeType in FILECOMPROBANTE:
        metadata2 = {'name':nombreComprobante, 'parents': [folder_id]}
        if mimeType:
            metadata2['mimetype'] = mimeType
        res2 = DRIVE.files().create(body=metadata2,media_body = filename, fields='id,name,webViewLink,mimeType').execute() #aca ejecutamos todo y obtenemos la info q nos devuelve la query
        if res2:
            linkFileComprobante = res2.get('webViewLink')
            nombreComprobanteSubido = res2.get('name')
            print ('Uploaded "%s" (%s)' % (filename, res2['mimeType']))
            print ('webviewlink->   ',res2.get('webViewLink'))
            print ('guardado como (filename): ', filename)
            print ('metadata2: ', metadata2)
            


    #Actualizo el estado del a boleta
    cur = mysql.connection.cursor()
    
    # cur.execute('UPDATE boleta SET est_bol = %s, bolr_bol = %s, comr_bol = %s  WHERE Id_bol = %s', (2,linkFile,linkFileComprobante,idBoleta))
    cur.execute('UPDATE boleta SET est_bol = %s, comr_bol = %s  WHERE Id_bol = %s', (2,linkFileComprobante,idBoleta))
    cur.connection.commit()

    #Envio el Email del Pago
    nombreEmail = str(session['nombUser'][0])
    cur = mysql.connection.cursor()
    cur.execute("SELECT Id_bol,mliq_bol,imp_bol,cuit_emp,tel_emp,email_emp,otr_bol from boleta INNER JOIN emp on emp.id_emp=boleta.Id_empbol where Id_bol=%s", (idBoleta,))
    resultado = cur.fetchall()
    resultado=resultado[0]


    me = environ.get('ME_EMAIL')
    my_password = environ.get('PASSWORD_EMAIL')
    you = environ.get('YOU_EMAIL')

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Nuevo Pago Efectuado"
    msg['From'] = me
    msg['To'] = you

    html = '<html><body><h3><b>Se genero un nuevo pago de </b></h3><h4> ' + nombreEmail + ' </h4><h3><b>CUIT del Empleador </b></h3><h4> ' + str(resultado[3]) + ' </h4><h3><b>Mes Liquidado </b></h3><h4> ' + str(resultado[1]) + ' </h4><h3><b>Monto Abonado </b></h3><h4> $' + str(
        resultado[2]*3/100)+' <br></h4><h3><b>Otros Aportes: </b></h3><h4> ' + str(resultado[6]) + ' <br></h4><h3><b>Total: </b></h3><h4> ' + str(resultado[6]+resultado[2]*3/100) + ' </h4><h3><b>Telefono: </b></h3><h4> ' + str(resultado[4]) + ' </h4><h3><b>Email: </b></h3><h4> ' + resultado[5] + ' </h4>'
    part2 = MIMEText(html, 'html')
    msg.attach(part2)

    # Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
    s = smtplib.SMTP_SSL('smtp.gmail.com')
    # uncomment if interested in the actual smtp conversation
    # s.set_debuglevel(1)
    # do the smtp auth; sends ehlo if it hasn't been sent already
    s.login(me, my_password)

    s.sendmail(me, you, msg.as_string())
    s.quit()


    flash('Pago Perteneciente a ' + mesLiqFlash +
          ' Informado Correctamente', 'success')
    return redirect(url_for('pagos'))

########### CONFIRMAR  PAGO SOLO USUARIO 2 ###############

@app.route('/confirmarPago', methods=["POST"])
def confirmarPago():
  if request.method == 'POST':
    if session['tipoUser'] == 1 or session['tipoUser'] == 3:
      idBoleta = request.form['idBoleta']
      
      #Recupero el mes par el flash
      cur = mysql.connection.cursor()
      cur.execute("SELECT mliq_bol FROM boleta where Id_bol=%s", (idBoleta,))
      mesLiquidacion = cur.fetchall()
      mesLiqFlash = str(mesLiquidacion[0][0].strftime('%m-%Y'))
      mesLiquidacion = str(mesLiquidacion[0][0])

      #Actualizo el estado del a boleta y fecha
      fechaHoy = str(date.today())
      print(fechaHoy)
      cur = mysql.connection.cursor()
      cur.execute('UPDATE boleta SET est_bol=%s ,fec_pag=%s WHERE Id_bol=%s',
                  ("3", fechaHoy, idBoleta))
      cur.connection.commit()

      #Selecciono a quien pertenece la boleta, y verifico que posea Email para enviarle la confirmación
      #Verifico si posee email
      cur = mysql.connection.cursor()
      cur.execute("SELECT emp.email_emp FROM boleta INNER JOIN emp ON boleta.Id_empbol = emp.id_emp where Id_bol=%s", (idBoleta,))
      email = cur.fetchall()
      email = str(email[0][0])
      print (email)
      #Si encuentro email
      if len(email) > 0:
        #Envio el Email del Pago
        try:
          nombreEmail = 'Sindicato de la Carne Rio Cuarto'
          

          me = environ.get('ME_EMAIL')
          my_password = environ.get('PASSWORD_EMAIL')
          you = email

          msg = MIMEMultipart('alternative')
          msg['Subject'] = "Pago Confirmado"
          msg['From'] = me
          msg['To'] = you

          html = '<html><body><h3><b>Se confirmo un nuevo pago para el periodo </b></h3><h4> ' + \
              mesLiqFlash + '</h4><br><h2 style="color:blue;">Muchas Gracias Por Su Cumplimiento</h2>'
          part2 = MIMEText(html, 'html')
          msg.attach(part2)

          # Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
          s = smtplib.SMTP_SSL('smtp.gmail.com')
          # uncomment if interested in the actual smtp conversation
          # s.set_debuglevel(1)
          # do the smtp auth; sends ehlo if it hasn't been sent already
          s.login(me, my_password)

          s.sendmail(me, you, msg.as_string())
          s.quit()

          flash('Pago Perteneciente a ' + mesLiqFlash +' Informado Correctamente', 'success')

          return redirect(url_for('pagos'))
        except:
          flash('Pago Perteneciente a ' + mesLiqFlash +' Informado Correctamente', 'success')

          return redirect(url_for('pagos'))

###########NUEVO EMPLEADOR###############
@app.route('/nuevoEmpleador',  methods=["GET", "POST"])
def nuevoEmpleador():
  if request.method == 'POST':
    nomEmpleador = request.form['nombEmpleador']
    inicioCuit = str(request.form['inicioCuit'])
    cuit = str(request.form['cuit'])
    finCuit = str(request.form['finCuit'])
    cuitcompleto=inicioCuit+'-'+cuit+'-'+finCuit
    Domicilio = str(request.form['Domicilio'])
    Localidad = str(request.form['Localidad'])
    Telefono = str(request.form['Telefono'])
    TelefonoFijo = str(request.form['TelefonoFijo'])
    email = str(request.form['email'])

    nombUser = str(request.form['nombUser'])
    passuser = str(request.form['passUser']).encode('utf-8')
    hashedpassword = bcrypt.hashpw(passuser, bcrypt.gensalt(19))
    tipoUser = '2'


    #Verifico que el cuit no se encuentre registrado
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM emp where cuit_emp= %s", (cuitcompleto,))
    result = cur.fetchall()
    if len(result) > 0:
      flash('ERROR: CUIT ya registrado previamente', 'danger')
      return redirect(url_for('empleadores'))
    else:
      #Verifico que el usuario no se encuentre registrado
      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM usuario where nom_usu= %s", (nombUser,))
      result = cur.fetchall()
      if len(result) > 0:
        flash('ERROR: Usuario ya en uso', 'danger')
        return redirect(url_for('empleadores'))
      else: 
        #Inserto el Usuario
        cur.execute(
            'INSERT INTO usuario (nom_usu,con_usu,id_tusu)VALUES(%s,%s,%s)', (nombUser, hashedpassword, tipoUser))
        cur.connection.commit()
        
        #obtengo el id del ultimo usuario cargado para asignarselo al empleador
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_usu FROM usuario order by id_usu desc limit 1")
        result = cur.fetchall()
        idusuario=result[0][0]
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO emp (rs_emp,dom_emp,loc_emp,cuit_emp,cel_emp,email_emp,idusu_emp,tel_emp) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                    (nomEmpleador,  Domicilio, Localidad, cuitcompleto, Telefono, email, idusuario,TelefonoFijo))
        cur.connection.commit()

        flash('Empleador cargado correctamente', 'success')

        return redirect(url_for('empleadores'))



### EDITAR EMPLEADOR
@app.route('/modificarPerfil',  methods=["GET", "POST"])
def modificarPerfil():
  if request.method == 'POST':
    idEmp = request.form['idEmp']
    razonSocial = str(request.form['razonSocial'])
    cuit = str(request.form['cuit'])
    Domicilio = str(request.form['Domicilio'])
    Localidad = str(request.form['Localidad'])
    Telefono = str(request.form['Telefono'])
    TelefonoFijo = str(request.form['TelefonoFijo'])
    email = str(request.form['email'])
   

    cur = mysql.connection.cursor()
    cur.execute('UPDATE emp SET rs_emp=%s,dom_emp=%s,loc_emp=%s,cuit_emp=%s,cel_emp=%s,email_emp=%s,tel_emp=%s where id_emp=' +
                idEmp+'', (razonSocial, Domicilio, Localidad, cuit, Telefono, email, TelefonoFijo))
    cur.connection.commit()
    flash('Cambios realizados correctamente', 'success')


    return redirect(url_for('perfilEmpleador', id_emp=idEmp))

### Recuperar Contraseña
@app.route('/recuperarPass',  methods=["GET", "POST"])
def recuperarPass():
  if request.method == 'POST':
    email = request.form['email']

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT nom_usu,email_emp,con_usu,id_usu from usuario INNER JOIN emp on usuario.id_usu=emp.idusu_emp where email_emp= %s", (email,))
    result = cur.fetchall()
    if len(result) > 0:
      nameUsuario = result[0][0]
      emailUsuario = result[0][1]
      passUsuario = result[0][2]
      id_usu = result[0][3]
      print(id_usu)

      longitud = 8
      valores = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

      nuevaPass = ""
      nuevaPass = nuevaPass.join([choice(valores) for i in range(longitud)])
      print(nuevaPass)

      hashedpassword = bcrypt.hashpw(
          nuevaPass.encode('utf-8'), bcrypt.gensalt(19))
      print(hashedpassword)

      cur = mysql.connection.cursor()
      cur.execute('UPDATE usuario SET con_usu=%s WHERE id_usu=%s',
                  (hashedpassword, id_usu,))
      cur.connection.commit()

      mensaje = "ENVIAMOS A "+emailUsuario+" SU PASS"

      
      nombreEmail = str(nameUsuario)

      me = environ.get('ME_EMAIL')
      my_password = environ.get('MY_PASSWORD')
      you = emailUsuario

      msg = MIMEMultipart('alternative')
      msg['Subject'] = "Nuevo Contraseña"
      msg['From'] = me
      msg['To'] = you

      html = '<html><body><h3><b>Nuevo Contrasena para ingresar a Sindicato de la Carne</b></h3><h4> ' + nuevaPass + \
          ' </h4><br><h3><b>Usuario :</h3></b><h4> ' + nameUsuario + \
          '</h4><br> Ingrese desde : www.sindicarne.com.ar'
      part2 = MIMEText(html, 'html')
      msg.attach(part2)

      # Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
      s = smtplib.SMTP_SSL('smtp.gmail.com')
      # uncomment if interested in the actual smtp conversation
      # s.set_debuglevel(1)
      # do the smtp auth; sends ehlo if it hasn't been sent already
      s.login(me, my_password)

      s.sendmail(me, you, msg.as_string())
      s.quit()

    else:
      mensaje = "NO EXISTE USUARIO REGISTRADO CON EMAIL"

    return render_template("mensajePass.html", mensaje=mensaje)


@app.route('/resetearPass',  methods=["GET", "POST"])   #Es el reseteo del Pass del Sindicato a un Empleador
def resetearPass():
  if request.method == 'POST':
    data = request.get_json()
    data = data[0]

    idEmpl=str(data['idEmpl'])
    
    ##Obtengo el id del Usuario, que es donde tengo la contraseña
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT id_usu,nom_usu from usuario INNER JOIN emp on usuario.id_usu=emp.idusu_emp where id_emp= %s", (idEmpl,))
    result = cur.fetchall()
    idUsuario=result[0][0]
    Usuario=result[0][1]

    ##Regenero la Contraseña
    longitud = 8
    valores = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    nuevaPass = ""
    nuevaPass = nuevaPass.join([choice(valores) for i in range(longitud)])
    print(nuevaPass)

    ##Hasheo la Nueva Pass y Actualizo en la Base de Datos
    hashedpassword = bcrypt.hashpw(nuevaPass.encode('utf-8'), bcrypt.gensalt(19))
    print(hashedpassword)

    cur = mysql.connection.cursor()
    cur.execute('UPDATE usuario SET con_usu=%s WHERE id_usu=%s',
                (hashedpassword, idUsuario,))
    cur.connection.commit()

    return jsonify({'Mensaje': 'Correcto','Usuario':Usuario,'Pass':nuevaPass})



@app.route('/generaPdf/<string:id_bol>')
def generarPdf(id_bol):
   cur = mysql.connection.cursor()
   cur.execute(
       "SELECT * FROM boleta INNER JOIN emp on boleta.Id_empbol=emp.id_emp where Id_bol= %s", (id_bol,))
   result = cur.fetchall()
   result=result[0]

   empleador=result[15]
   periodo=result[4]
   empleados=result[9]
   importe=result[6]
   
   usuario = session['nombUser'][0]
   return render_template('pdf_template.html',empleador=empleador,boleta=id_bol.zfill(8),periodo=periodo,empleados=empleados,importe=importe,usuario=usuario,data=result)

### PERFIL USUARIO
@app.route('/cambioPass',  methods=["GET", "POST"])
def cambioPass():
  if request.method == 'POST':
    idUsuario = session['idUser'][0]
    actual_usuario = request.form['actual_usuario'].encode('utf-8')
    nueva_usuario = request.form['nueva_usuario']
    repite_usuario = request.form['repite_usuario']

    if nueva_usuario==repite_usuario: 
      hashedpassword = bcrypt.hashpw(actual_usuario, bcrypt.gensalt(19)) #hasheamos la pass ingresa con un gensalt14
      cur = mysql.connection.cursor() #creamos cursor p coenectarnos a la db
      cur.execute("SELECT * FROM usuario WHERE id_usu =%s",(str(idUsuario),)) #buscamos el  nombre de usuario ingresado en la DB
      try: #primero que intente encontrar algo
        User = cur.fetchone() #traemos toda la info de USUARIO aca
        # comparamos las passwords hasheadas y que User[3] (estado usuario) sea 0, es decir,activo
        if bcrypt.checkpw(actual_usuario, User[2].encode('utf-8')):
            hashednewpassword = bcrypt.hashpw(nueva_usuario.encode('utf-8'), bcrypt.gensalt(19))
            cur = mysql.connection.cursor()
            cur.execute('UPDATE usuario SET con_usu=%s WHERE id_usu=%s',
                        (hashednewpassword, idUsuario,))
            cur.connection.commit()
            session.clear()
            flash('Password Modificada Correctamente Inicie Sesión Para Continuar','success')
            return render_template("login.html")
        else: # si las pass  no coiniciden se los manda aca a un flash de error
            flash ('Error: Las Contraseñas no coinciden', 'danger') 
            return redirect(url_for('miperfil'))
      except:
        flash('No paso nada','danger')
        return redirect(url_for('miperfil'))
    else:
      flash ('Error: Las Contraseñas no coinciden', 'danger') 
      return redirect(url_for('miperfil'))

########## ANULAR BOLETA LADO EMPLEADOR #########
@app.route('/anularBoleta/<string:idEmpleador>/<string:idBoleta>')
def anularBoleta(idEmpleador,idBoleta):
  cur = mysql.connection.cursor()
  cur.execute('SELECT Id_empbol,est_bol FROM boleta WHERE id_bol=%s', (idBoleta,))
  estadoBoleta = cur.fetchone()
  cur.connection.commit()
  print ('estsado boleta',estadoBoleta)
  print ('estadoboleta 0->',estadoBoleta[0])
  print ('id empleador-> ',idEmpleador, 'idboleta->',idBoleta)
  if estadoBoleta and str(estadoBoleta[0]) == idEmpleador:
    if estadoBoleta[1] == 0:
      cur = mysql.connection.cursor()
      cur.execute('UPDATE boleta SET est_bol = %s  WHERE id_bol=%s', (0,idBoleta,))
      cur.connection.commit()
      flash("Boleta anulada correctamente","success")
      return redirect(url_for('pagos'))
    else :
      flash("No puedes anular esta boleta ahora, porque ya se encuentra  INFORMADA, ANULADA o CONFIRMADA. Contactate con la administración del Sindicato","danger")
      return redirect(url_for('pagos'))
  else :
      flash("No puedes anular esta boleta ahora, porque no existe o no tienes los permisos suficientes. Contactate con la administración del Sindicato si crees que esto es un error","danger")
      return redirect(url_for('pagos'))


@app.route('/filter')
def filter():
  if session['tipoUser'] == 1 or session['tipoUser'] == 3:
    cur = mysql.connection.cursor()
    cur.execute('SELECT * from emp order by rs_emp asc')
    empleador = cur.fetchall()
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * from boleta')
    boleta = cur.fetchall()
   

    return render_template("filter.html", empleador=empleador, boleta=boleta)


@app.route('/filtropersonalizado',  methods=["GET", "POST"])
def filtropersonalizado():
  if request.method == 'POST':
    Empleador = str(request.form['Empleador'])
    Desde = str(request.form['Desde'])
    Hasta = str(request.form['Hasta'])
    DesdePago = str(request.form['DesdePago'])
    HastaPago = str(request.form['HastaPago'])
    Estado = str(request.form['Estado'])
    mesLiqDesde = str(request.form['mesLiqDesde'])
    anioLiqDesde = str(request.form['anioLiqDesde'])
    mesLiqHasta = str(request.form['mesLiqHasta'])
    anioLiqHasta = str(request.form['anioLiqHasta'])

    if mesLiqDesde == "00":
      mesLiqDesde = "01"
    if mesLiqHasta == "00":
      mesLiqHasta = "12"
    if anioLiqDesde == "00":
      anioLiqDesde = "2000"
    if anioLiqHasta == "00":
      anioLiqHasta = "2050"

    if Desde == '':
      Desde = '2000-01-01'
    else:
      pass
    if Hasta == '':
      Hasta = '2050-01-01'
    else:
      pass

    if DesdePago == '':
      DesdePago = '2000-01-01'
    else:
      pass
    if HastaPago == '':
      HastaPago = '2050-01-01'
    else:
      pass

    ###Para La Base de Datos
    DesdeLiq = (anioLiqDesde+'-'+mesLiqDesde+'-01')
    HastaLiq = (anioLiqHasta)+'-'+mesLiqHasta+'-01'
    ###Para El Tempalte
    desdeLiq = mesLiqDesde+'-'+anioLiqDesde
    hastaLiq = mesLiqHasta+'-'+anioLiqHasta

    ###Si Selecciona TODOS Los empleadores y todas las boletas
    if Empleador == '0' and Estado == '99':
      Nombre = 'Todos'
      cur = mysql.connection.cursor()
      cur.execute(
          'SELECT * FROM boleta inner join emp on Id_empbol=id_emp where (fge_bol BETWEEN %s and %s) and (mliq_bol BETWEEN %s and %s)', (Desde, Hasta, DesdeLiq, HastaLiq,))
      datos = cur.fetchall()

    ###Si Selecciona A un proveedor en particular y todas las boletas
    if Empleador != '0' and Estado == '99':
      cur = mysql.connection.cursor()
      cur.execute(
          'SELECT * FROM boleta inner join emp on Id_empbol=id_emp where (fge_bol BETWEEN %s and %s) and (mliq_bol BETWEEN %s and %s) and (Id_empbol=%s)', (Desde, Hasta, DesdeLiq, HastaLiq, Empleador,))
      datos = cur.fetchall()

      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM emp where id_emp= %s", (Empleador,))
      Nombre = cur.fetchall()
      Nombre = Nombre[0][1]

    ###Si Selecciona TODOS Los empleadores y un estado en particular que no sea abonado
    if Empleador == '0' and Estado != '99' and Estado != '3':
      Nombre = 'Todos'
      cur = mysql.connection.cursor()
      cur.execute(
          'SELECT * FROM boleta inner join emp on Id_empbol=id_emp where (fge_bol BETWEEN %s and %s) and (mliq_bol BETWEEN %s and %s) and est_bol=%s', (Desde, Hasta, DesdeLiq, HastaLiq, Estado))
      datos = cur.fetchall()

    ###Si Selecciona A un proveedor en particular y un estado en particular que no sea abonado
    if Empleador != '0' and Estado != '99' and Estado != '3':
      cur = mysql.connection.cursor()
      cur.execute(
          'SELECT * FROM boleta inner join emp on Id_empbol=id_emp where (fge_bol BETWEEN %s and %s) and (mliq_bol BETWEEN %s and %s) and (Id_empbol=%s) and est_bol=%s', (Desde, Hasta, DesdeLiq, HastaLiq, Empleador, Estado,))
      datos = cur.fetchall()

      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM emp where id_emp= %s", (Empleador,))
      Nombre = cur.fetchall()
      Nombre = Nombre[0][1]

    ###Si Selecciona TODOS Los empleadores y estado abonado que no sea abonado
    if Empleador == '0' and Estado == '3':
      Nombre = 'Todos'
      cur = mysql.connection.cursor()
      cur.execute(
          'SELECT * FROM boleta inner join emp on Id_empbol=id_emp where (fec_pag BETWEEN %s and %s) and (mliq_bol BETWEEN %s and %s) and est_bol=%s', (DesdePago, HastaPago, DesdeLiq, HastaLiq, Estado))
      datos = cur.fetchall()

    ###Si Selecciona A un proveedor en particular y un estado en particular que no sea abonado
    if Empleador != '0' and Estado == '3':
      cur = mysql.connection.cursor()
      cur.execute(
          'SELECT * FROM boleta inner join emp on Id_empbol=id_emp where (fec_pag BETWEEN %s and %s) and (mliq_bol BETWEEN %s and %s) and (Id_empbol=%s) and est_bol=%s', (DesdePago, HastaPago, DesdeLiq, HastaLiq, Empleador, Estado,))
      datos = cur.fetchall()

      cur = mysql.connection.cursor()
      cur.execute("SELECT * FROM emp where id_emp= %s", (Empleador,))
      Nombre = cur.fetchall()
      Nombre = Nombre[0][1]

    return render_template("estadisticas.html", datos=datos, Nombre=Nombre, Estado=Estado, DesdeLiq=desdeLiq, HastaLiq=hastaLiq, Desde=Desde, Hasta=Hasta, DesdePago=DesdePago, HastaPago=HastaPago)

#Modificar Datos de Contacto
@app.route('/modificaDatos',  methods=["GET", "POST"])
def modificaDatos():
  if request.method == 'POST':
    idUsuario = session['idUser'][0]  # Obtengo el idUser con el que se logeo
    cur = mysql.connection.cursor()  # Y busco los datos de empleador del usuario
    cur.execute("SELECT * FROM emp INNER JOIN usuario on emp.idusu_emp = usuario.id_usu where idusu_emp=%s", (str(idUsuario),))
    idEmpl = cur.fetchall()
    # Id del empleador, lo necesito para insertar el pago
    idEmpl = str(idEmpl[0][0])
    print(idEmpl)
    LocalidadN = str(request.form['LocalidadN'])
    DomicilioN = str(request.form['DomicilioN'])
    TelefonoN = str(request.form['TelefonoN'])
    CelularN = str(request.form['CelularN'])
    EmailN = str(request.form['EmailN'])
   
   

    cur = mysql.connection.cursor()
    cur.execute('UPDATE emp SET dom_emp=%s,loc_emp=%s,tel_emp=%s,cel_emp=%s,email_emp=%s where id_emp='+idEmpl+'',(DomicilioN,LocalidadN,TelefonoN,CelularN,EmailN,))
    cur.connection.commit()

    flash('Cambios realizados correctamente', 'success')

    nombreUsuario = session['nombUser'][0]
    idUsuario = session['idUser'][0]

    cur = mysql.connection.cursor()  # Y busco los datos de empleador del usuario
    if session['tipoUser'] == 2:
      cur.execute(
          "SELECT * FROM  usuario INNER JOIN emp on usuario.id_usu=emp.idusu_emp where id_usu=%s", (str(idUsuario),))
      perfilUsuario = cur.fetchall()
    return render_template('miPerfil.html', perfilUsuario=perfilUsuario)




###local
# if __name__ == '__main__':
#     app.secret_key = "privatekeyMellitus"
#     app.run(port=3000, debug=True)

##server
if __name__ == '__main__':
    app.secret_key = "claveSindicatoCarneUltraSecretisimaKaniefskyiana"
    app.run(host='0.0.0.0')
