import os
import sqlite3
from pathlib import Path

from flask import Flask, flash, get_flashed_messages, redirect, render_template_string, request, url_for
from werkzeug.security import safe_join
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "messi_app.db"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__, static_folder=str(BASE_DIR), static_url_path="/")
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24).hex()
app.config.update(
    MAX_CONTENT_LENGTH=2 * 1024 * 1024,
    UPLOAD_FOLDER=str(UPLOAD_DIR),
)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def is_safe_upload_path(candidate_path: str) -> bool:
    upload_root = Path(app.config["UPLOAD_FOLDER"]).resolve()
    resolved_candidate = Path(candidate_path).resolve()
    try:
        resolved_candidate.relative_to(upload_root)
        return True
    except ValueError:
        return False


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                email TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                archivo TEXT,
                creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()

    with get_db() as conn:
        columns = [row[1] for row in conn.execute("PRAGMA table_info(mensajes)")]
        if "archivo" not in columns:
            conn.execute("ALTER TABLE mensajes ADD COLUMN archivo TEXT")
        conn.commit()

    with get_db() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO mensajes (nombre, email, mensaje) VALUES (?, ?, ?)",
            ("Ana", "ana@example.com", "Me encanta la trayectoria de Messi."),
        )
        conn.execute(
            "INSERT OR IGNORE INTO mensajes (nombre, email, mensaje) VALUES (?, ?, ?)",
            ("Luis", "luis@example.com", "Quiero ver más logros y datos."),
        )
        conn.commit()


init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang=\"es\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Lionel Messi</title>
    <link rel=\"stylesheet\" href=\"{{ url_for('static', filename='styles.css') }}\">
</head>
<body>
    <div class=\"page-shell\">
        <header class=\"hero\">
            <div class=\"hero-copy\">
                <h1>Lionel Messi</h1>
                <p class=\"hero-sub\">Biografía y trayectoria</p>
                <p class=\"hero-text\">Capitán de la selección argentina y delantero del Inter Miami.</p>
                <div class=\"hero-actions\">
                    <a class=\"button primary\" href=\"#biografia\">Biografía</a>
                    <a class=\"button secondary\" href=\"#clubes\">Clubes</a>
                </div>
            </div>
            <div class=\"hero-media\">
                <img src=\"{{ url_for('static', filename='Img/MessiCOPA.jpg') }}\" alt=\"Lionel Messi con la camiseta de Inter Miami\">
            </div>
        </header>

        <main>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    <section class=\"section\">
                        {% for category, message in messages %}
                            <p class=\"flash flash-{{ category }}\">{{ message|e }}</p>
                        {% endfor %}
                    </section>
                {% endif %}
            {% endwith %}

            <section id=\"biografia\" class=\"section biography\">
                <div class=\"section-header\">
                    <span>Biografía</span>
                    <h2>Una carrera construida en grande</h2>
                </div>
                <img class=\"biography-image\" src=\"{{ url_for('static', filename='Img/Messi2026.webp') }}\" alt=\"Lionel Messi en 2026\">
                <p>Lionel Andrés Messi (Rosario, 24 de junio de 1987) es un futbolista argentino, delantero y capitán de la selección.</p>
                <p>Jugó más de veinte años en el F.C. Barcelona, donde ganó múltiples títulos nacionales e internacionales.</p>
                <p>Ha recibido varios reconocimientos individuales, incluidos Balones de Oro y Botas de Oro.</p>
                <p>En 2021, se unió al Paris Saint-Germain y en 2023 al Inter Miami, continuando su legado en el fútbol mundial.</p>
            </section>

            <section class=\"section achievements\">
                <div class=\"section-header\">
                    <span>Logros</span>
                    <h2>Hazañas destacadas</h2>
                </div>
                <div class=\"cards\">
                    <article class=\"card\"><strong>8 Balones de Oro</strong><p>Récord histórico como mejor jugador del mundo.</p></article>
                    <article class=\"card\"><strong>4 Champions League</strong><p>Éxitos internacionales con el Barcelona.</p></article>
                    <article class=\"card\"><strong>10 Ligas españolas</strong><p>Dominio absoluto en la liga doméstica.</p></article>
                    <article class=\"card\"><strong>Copa Mundial 2022</strong><p>Campeón del mundo con Argentina.</p></article>
                </div>
            </section>

            <section id=\"clubes\" class=\"section clubs\">
                <div class=\"section-header\">
                    <span>Clubes</span>
                    <h2>Etapas de su trayectoria</h2>
                </div>
                <div class=\"club-grid\">
                    <figure><img src=\"{{ url_for('static', filename='Img/MessiN.jpg') }}\" alt=\"Lionel Messi en Newell's Old Boys\"><figcaption>Newell's Old Boys</figcaption></figure>
                    <figure><img src=\"{{ url_for('static', filename='Img/MessiB.jpg') }}\" alt=\"Lionel Messi en el FC Barcelona\"><figcaption>FC Barcelona</figcaption></figure>
                    <figure><img src=\"{{ url_for('static', filename='Img/MessiPSG.jpg') }}\" alt=\"Lionel Messi en el Paris Saint-Germain\"><figcaption>Paris Saint-Germain</figcaption></figure>
                    <figure><img src=\"{{ url_for('static', filename='Img/MessiM.jpg') }}\" alt=\"Lionel Messi en el Inter Miami\"><figcaption>Inter Miami</figcaption></figure>
                </div>
            </section>

            <section class=\"section contact-section\">
                <div class=\"section-header\">
                    <span>Contacto</span>
                    <h2>¿Quieres seguir la historia de Messi?</h2>
                </div>
                <div class=\"contact-grid\">
                    <div class=\"contact-copy\">
                        <p>Envía un mensaje y guardaremos tu comentario en la base de datos.</p>
                        <ul class=\"contact-list\">
                            <li>Últimas novedades</li>
                            <li>Logros y estadísticas</li>
                            <li>Momentos clave</li>
                        </ul>
                    </div>
                    <form class=\"contact-form\" method=\"post\" action=\"{{ url_for('crear_mensaje') }}\" enctype=\"multipart/form-data\">
                        <label for=\"nombre\">Nombre</label>
                        <input type=\"text\" id=\"nombre\" name=\"nombre\" placeholder=\"Tu nombre\" required>
                        <label for=\"email\">Correo</label>
                        <input type=\"email\" id=\"email\" name=\"email\" placeholder=\"tu@email.com\" required>
                        <label for=\"mensaje\">Mensaje</label>
                        <textarea id=\"mensaje\" name=\"mensaje\" rows=\"4\" placeholder=\"Cuéntanos qué te gustaría ver...\" required></textarea>
                        <label for=\"archivo\">Imagen opcional</label>
                        <input type=\"file\" id=\"archivo\" name=\"archivo\" accept=\"image/png, image/jpeg, image/webp\">
                        <button class=\"button primary\" type=\"submit\">Enviar</button>
                    </form>
                </div>
            </section>

            <section class=\"section\">
                <div class=\"section-header\">
                    <span>Mensajes</span>
                    <h2>Comentarios registrados</h2>
                </div>
                {% if mensajes %}
                    <div class=\"messages-list\">
                        {% for mensaje in mensajes %}
                            <article class=\"message-card\">
                                <div class=\"message-meta\">
                                    <strong>{{ mensaje['nombre']|e }}</strong>
                                    <span>{{ mensaje['email']|e }}</span>
                                </div>
                                <p>{{ mensaje['mensaje']|e }}</p>
                                {% if mensaje['archivo'] %}
                                    <img class=\"message-image\" src=\"{{ url_for('static', filename='uploads/' ~ mensaje['archivo']) }}\" alt=\"Imagen adjunta\">
                                {% endif %}
                                <form method=\"post\" action=\"{{ url_for('eliminar_mensaje', mensaje_id=mensaje['id']) }}\" class=\"inline-form\">
                                    <button type=\"submit\" class=\"button secondary\">Eliminar</button>
                                </form>
                            </article>
                        {% endfor %}
                    </div>
                {% else %}
                    <p>No hay mensajes registrados aún.</p>
                {% endif %}
            </section>
        </main>

        <footer>
            <p>© 2026 Página dedicada a Lionel Messi</p>
            <div class=\"social-links\">
                <a href=\"https://www.instagram.com/leomessi/\" target=\"_blank\" rel=\"noreferrer\">Instagram</a>
                <a href=\"https://www.facebook.com/leomessi/\" target=\"_blank\" rel=\"noreferrer\">Facebook</a>
            </div>
        </footer>
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return crear_mensaje()
    with get_db() as conn:
        mensajes = conn.execute("SELECT * FROM mensajes ORDER BY id DESC").fetchall()
    return render_template_string(HTML_TEMPLATE, mensajes=mensajes)


@app.route("/mensajes", methods=["POST"])
def crear_mensaje():
    nombre = request.form.get("nombre", "").strip()
    email = request.form.get("email", "").strip()
    mensaje = request.form.get("mensaje", "").strip()

    if not nombre or not email or not mensaje:
        flash("Completa todos los campos.", "error")
        return redirect(url_for("index"))

    archivo_nombre = None
    archivo = request.files.get("archivo")
    if archivo and archivo.filename:
        filename = secure_filename(archivo.filename)
        if filename:
            safe_path = safe_join(app.config["UPLOAD_FOLDER"], filename)
            if safe_path is None or not is_safe_upload_path(safe_path):
                flash("Nombre de archivo no válido.", "error")
                return redirect(url_for("index"))
            archivo.save(safe_path)
            archivo_nombre = filename

    with get_db() as conn:
        conn.execute(
            "INSERT INTO mensajes (nombre, email, mensaje, archivo) VALUES (?, ?, ?, ?)",
            (nombre, email, mensaje, archivo_nombre),
        )
        conn.commit()
    flash("Mensaje guardado correctamente.", "success")
    return redirect(url_for("index"))


@app.route("/mensajes/<int:mensaje_id>", methods=["POST"])
def eliminar_mensaje(mensaje_id: int):
    with get_db() as conn:
        mensaje = conn.execute("SELECT * FROM mensajes WHERE id = ?", (mensaje_id,)).fetchone()
        if mensaje and mensaje["archivo"]:
            archivo_path = Path(app.config["UPLOAD_FOLDER"]) / mensaje["archivo"]
            if archivo_path.exists():
                archivo_path.unlink()
        conn.execute("DELETE FROM mensajes WHERE id = ?", (mensaje_id,))
        conn.commit()
    flash("Mensaje eliminado.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
