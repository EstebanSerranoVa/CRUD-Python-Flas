from flask import Flask
from flask import render_template, request, redirect, url_for,flash
from flaskext.mysql import MySQL
from flask import send_from_directory
from datetime import datetime
import os




app = Flask(__name__)
app.secret_key="Valijas"

#Conexión a BD
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']= 'localhost'
app.config['MYSQL_DATABASE_USER']= 'root'
app.config['MYSQL_DATABASE_PASSWORD']= ''
app.config['MYSQL_DATABASE_DB']= 'sistema'
mysql.init_app(app)


CARPETA= os.path.join('uploads')
app.config['CARPETA']=CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)



@app.route('/')
def index():
    
    sql = "SELECT * FROM `valijas`;"
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql)
    valijas=cursor.fetchall()
    conn.commit()
    return render_template('valijas/index.html',valijas=valijas)

#Eliminar registro
@app.route('/destroy/<int:id>')
def destroy(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    
    cursor.execute("SELECT imagen FROM valijas WHERE id=%s",id)
    fila=cursor.fetchall()
        
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
    
    cursor.execute("DELETE FROM valijas WHERE id=%s",(id))
    conn.commit()
    return redirect('/')



@app.route('/editar/<int:id>')
def editar(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM valijas WHERE id=%s", (id))
    valijas=cursor.fetchall()
    conn.commit()
    return render_template('valijas/editar.html',valijas=valijas)


@app.route('/update', methods=['POST'])
def update():
    
    _nombre = request.form['txtNombre']
    _foto = request.files['txtFoto']
    _descripcion = request.form['txtDescripcion']     
    id= request.form['txtID']
    
    sql = "UPDATE valijas SET nombre=%s,descripcion=%s WHERE id=%s ;"
    
    datos = (_nombre,_descripcion,id)
    
    conn = mysql.connect()
    cursor = conn.cursor()
    
    now = datetime.now()
    tiempo=now.strftime("%Y%H%M%S")
    
    if _foto.filename!='':
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
        
        cursor.execute("SELECT imagen FROM valijas WHERE id=%s",id)
        fila=cursor.fetchall()
        
        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("UPDATE valijas SET imagen=%s WHERE id=%s",(nuevoNombreFoto,id))
        conn.commit()
    
    
    cursor.execute(sql, datos)
    conn.commit()
    

    return redirect('/') 


@app.route('/crear')
def crear():
    
    return render_template('valijas/crear.html')
    
@app.route('/store', methods=['POST'])
def storage():
    _nombre = request.form['txtNombre']
    _foto = request.files['txtFoto']
    _descripcion = request.form['txtDescripcion']
    
    ##Validacion de formulario
    if _nombre=='' or _descripcion=='' or _foto=='':
        flash("Recuerda llenar los campos con datos")
        return redirect(url_for('crear'))
        
    now = datetime.now()
    tiempo=now.strftime("%Y%H%M%S")
    
    if _foto.filename!='':
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)
    
    sql = "INSERT INTO `valijas` (`id`, `nombre`, `imagen`, `descripcion`) VALUES (NULL, %s, %s, %s); "
    
    #Orden de Datos a ingresar a la BD
    datos = (_nombre,nuevoNombreFoto,_descripcion)
    
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute(sql, datos)
    conn.commit()
    return redirect('/')



if __name__ == '__main__':
    app.run(debug=True)