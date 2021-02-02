from flask import Flask, render_template, url_for, redirect, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import flash, session
from flask_login import LoginManager
from flask_login import login_user, logout_user, login_required, current_user


app = Flask(__name__)
app.debug = True
Bootstrap(app)
bcrypt = Bcrypt()
bcrypt.init_app(app)
# Configuración de la app  para manejar  sesión
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.log_view='login'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.config['SQLALCHEMY_DATABASE_URI']='postgres://rpoyxmqswdbprt:5be3fb76ea32b776d55dc782ef47d320fb99e5a383acbbcb1183df8dd9c6c3b6@ec2-3-208-168-0.compute-1.amazonaws.com:5432/dcm0291acll69h'
#app.config['SQLALCHEMY_DATABASE_URI']='postgresql+psycopg2://postgres:14122016@localhost:5432/Notas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__='usuario'
    
    id_usuario= db.Column(db.Integer,primary_key=True)
    nombre_user = db.Column(db.String(500))
    email = db.Column(db.String(500), unique=True,nullable= False, index=True)
    pwd= db.Column(db.String(500))

    def __init__(self,nombre_user,email,pwd):
        self.nombre_user=nombre_user
        self.email=email
        self.pwd=pwd
    
    def is_authenticated(self):
        return True
	
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
	
    def get_id(self):
        return str(self.id_usuario)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.filter_by(id_usuario=user_id).first()

class Categoria(db.Model):
    __tablename__='categoria'

    id_categoria= db.Column(db.Integer,primary_key=True)
    nombre_categoria = db.Column(db.String(30), nullable= False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'))

    def __init__(self,nombre_categoria,id_usuario):
        self.nombre_categoria = nombre_categoria
        self.id_usuario = id_usuario
        
   


class Nota(db.Model):
    __tablename__='nota'

    id_nota= db.Column(db.Integer,primary_key=True)
    titulo = db.Column(db.String(80), nullable= False, index=True)
    contenido = db.Column(db.String(1000))
    fecha_creacion = db.Column(db.DateTime)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categoria.id_categoria'))

    def __init__(self,titulo,contenido,fecha_creacion,id_categoria):
        self.titulo = titulo
        self.contenido = contenido
        self.fecha_creacion = fecha_creacion
        self.id_categoria = id_categoria

@app.route('/')
def index():
    return render_template("home.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/loginin', methods=['GET','POST'])
def loginin():
    if request.method == 'POST':
        email = request.form["email"]
        pwd = request.form["pwd"]
        usuario_existe = Usuario.query.filter_by(email=email).first()
        if usuario_existe != None and bcrypt.check_password_hash(usuario_existe.pwd, pwd) :
            mensaje = 'Bienvenido...sesión iniciada'
            #session['email'] = email
            login_user(usuario_existe)	
            if current_user.is_authenticated:
                return redirect(url_for('inicio',mensaje=mensaje))
        else:
            mensaje = 'Usuario o contraseña invalidos'

    print("Login in...")
    return render_template("login.html",mensaje=mensaje)

@app.route('/registro', methods=['GET','POST'])
def registro():
    mensaje = ""
    if request.method=='POST':
        pwd = request.form["pwd"]
        password = request.form["password"]
        if pwd != password:
            mensaje = "Contraseñas no coinciden, vuelva a intentar"
            return render_template("registro.html", mensaje = mensaje)
        else:
            nombre=request.form["nombre_usuario"]
            correo=request.form["email"]
            pwd=request.form["pwd"]

            usuario = Usuario(
                nombre_user =nombre,
                email=correo,
                pwd = bcrypt.generate_password_hash(pwd).decode('utf-8')
            )
            db.session.add(usuario)
            db.session.commit()

            mensaje = "Usuario resgistrado"
            return render_template("registro.html", mensaje = mensaje)

    return render_template("registro.html", mensaje = mensaje)

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/inicio')
@login_required
def inicio():
    return render_template('inicio.html')

@app.route('/categoria', methods=['GET','POST'])
@login_required
def categoria():
    if request.method == 'POST':
        print("request")
        nombre_categoria = request.form['nom_categoria']
        print(current_user.get_id())
        categoria = Categoria(nombre_categoria=nombre_categoria,id_usuario=current_user.get_id())
        db.session.add(categoria)
        db.session.commit()
        mensaje = "Categoria registrada"
        return render_template("categoria.html", mensaje = mensaje)
    
    return  render_template('categoria.html')

@app.route('/crearNota', methods=['GET','POST'])
@login_required
def crearNota():
    if request.method == 'POST':
        print("request")
        titulo = request.form['titulo']
        contenido = request.form['contenido']
        fecha_creacion = request.form['fecha']
        nota = Nota(titulo=titulo,contenido=contenido,fecha_creacion=fecha_creacion, id_categoria=current_user.get_id())
        db.session.add(nota)
        db.session.commit()
        mensaje = "Nota registrada"
        return render_template("nuevaNota.html", mensaje = mensaje)
        
    return render_template('nuevaNota.html')

@app.route('/verNotas') 
@login_required
def verNotas():
    consulta = Nota.query.all()
    print(consulta)
    return render_template("verNota.html", variable = consulta)

@app.route('/editar/<id>') 
@login_required
def editar(id):
    a= Nota.query.filter_by(id_nota=int(id)).first()
    return render_template("editar.html", nota = a)

@app.route('/actualizar', methods=['GET','POST'])
@login_required
def actualizar():
    if request.method == 'POST':
        qry = Nota.query.get(request.form['id'])
        qry.titulo = request.form['tituloE']
        qry.contenido = request.form['contenidoE']
        db.session.commit()
        return redirect(url_for('verNotas'))

@app.route('/eliminar/<id>')
@login_required
def eliminar(id):
    q= Nota.query.filter_by(id_nota=int(id)).delete()
    db.session.commit()
    return redirect(url_for('verNotas'))





if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
