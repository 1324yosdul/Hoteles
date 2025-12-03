from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "clave_super_secreta"

DB_NAME = "hospedajes.db"


# ==================================================
# CREAR BASE DE DATOS (SOLO UNA VEZ)
# ==================================================
def crear_bd():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        # Tabla clientes
        cur.execute("""
        CREATE TABLE clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            telefono TEXT,
            reserva TEXT
        );
        """)

        # Tabla hoteles
        cur.execute("""
        CREATE TABLE hospedajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            direccion TEXT,
            telefono TEXT,
            tipo TEXT,
            habitaciones INTEGER,
            camas INTEGER
        );
        """)

        hoteles = [
            ('Hotel Chaquenoda Frontino', 'Carrera 32 29 34', '3217735850', 'Hotel', 32, 62),
            ('Hotel El Paisa de Frontino', 'Carrera 30A 31-44', '3148896756', 'Hotel', 21, 27),
            ('Hotel Casa Vieja Frontino', 'Carrera 32 30 45', '3117710060', 'Hotel', 23, 26),
            ('Hotel La Casona', 'Calle 30 # 30-20', '3122872384', 'Hotel', 12, 22),
            ('Hotel Nacho', 'Cr30 27A 07', '6048595403', 'Hotel', 20, 27),
            ('Hotel La Montaña', 'Vía Frontino – Nutibara', '3005567832', 'Hostal', 15, 30),
            ('Hotel Amanecer', 'Carrera 29 # 27-14', '3149982345', 'Hotel', 18, 25),
            ('Hotel Vista Hermosa', 'Sector Alto de Cuevas', '3124567809', 'Cabañas', 10, 20)
        ]

        cur.executemany("""
        INSERT INTO hospedajes(nombre,direccion,telefono,tipo,habitaciones,camas)
        VALUES (?, ?, ?, ?, ?, ?)
        """, hoteles)

        conn.commit()
        conn.close()


crear_bd()


# ==================================================
# ADMIN LOGIN
# ==================================================
ADMIN_USER = "admin"
ADMIN_PASS = "12345"


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        if usuario == ADMIN_USER and password == ADMIN_PASS:
            session["admin"] = True
            return redirect(url_for("panel"))

        return render_template("login_admin.html", error="❌ Usuario o contraseña incorrectos")

    return render_template("login_admin.html")


# ==================================================
# PANEL ADMIN – LISTADO DE HOTELES
# ==================================================
@app.route("/panel")
def panel():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM hospedajes")
    lista = cur.fetchall()
    conn.close()

    return render_template("admin_panel.html", hoteles=lista)


# ==================================================
# AGREGAR HOTEL (ADMIN)
# ==================================================
@app.route("/agregar_hotel", methods=["GET", "POST"])
def agregar_hotel():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        nombre = request.form["nombre"]
        direccion = request.form["direccion"]
        telefono = request.form["telefono"]
        tipo = request.form["tipo"]
        habitaciones = request.form["habitaciones"]
        camas = request.form["camas"]

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO hospedajes (nombre, direccion, telefono, tipo, habitaciones, camas)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre, direccion, telefono, tipo, habitaciones, camas))

        conn.commit()
        conn.close()

        return redirect(url_for("panel"))

    return render_template("agregar_hotel.html")


# ==================================================
# ELIMINAR HOTEL
# ==================================================
@app.route("/eliminar_hotel/<int:id>")
def eliminar_hotel(id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM hospedajes WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("panel"))


# ==================================================
# INICIO PÚBLICO
# ==================================================
@app.route("/")
def inicio():
    return render_template("inicio.html")


# ==================================================
# LISTA DE HOTELES PARA CLIENTES
# ==================================================
@app.route("/hoteles")
def hoteles():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM hospedajes")
    lista = cur.fetchall()
    conn.close()

    return render_template("hoteles.html", hoteles=lista)


# ==================================================
# REGISTRO DE CLIENTES
# ==================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        telefono = request.form["telefono"]

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO clientes (nombre,email,telefono) VALUES (?,?,?)",
                        (nombre, email, telefono))
            conn.commit()
            conn.close()
            return redirect(url_for("reserva"))
        except:
            return render_template("register.html", error="⚠ Ese correo ya está registrado")

    return render_template("register.html")


# ==================================================
# RESERVA
# ==================================================
@app.route("/reserva", methods=["GET", "POST"])
def reserva():
    if request.method == "POST":
        email = request.form["email"]
        reserva = request.form["reserva"]

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("UPDATE clientes SET reserva=? WHERE email=?", (reserva, email))
        conn.commit()
        conn.close()

        return render_template("reserva.html", ok="✔ Reserva registrada correctamente")

    return render_template("reserva.html")


# ==================================================
# LOGOUT ADMIN
# ==================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin_login"))


# ==================================================
# EJECUCIÓN
# ==================================================
if __name__ == "__main__":
    app.run(debug=True)
