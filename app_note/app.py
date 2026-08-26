from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# Configurazione del database SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///note.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modello del database per le Note
class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(100), nullable=False)
    contenuto = db.Column(db.Text, nullable=False)
    data_scadenza = db.Column(db.Date, nullable=True)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)

# Crea il database al primo avvio
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # Recupera tutte le note ordinate dalla più recente
    note = Nota.query.order_by(Nota.data_creazione.desc()).all()
    oggi = datetime.utcnow().date()
    return render_template('index.html', note=note, oggi=oggi)

@app.route('/aggiungi', methods=['POST'])
def aggiungi_nota():
    titolo = request.form.get('titolo')
    contenuto = request.form.get('contenuto')
    data_scadenza_str = request.form.get('data_scadenza')

    # Converti la stringa in un oggetto Date se presente
    data_scadenza = datetime.strptime(data_scadenza_str, '%Y-%m-%d').date() if data_scadenza_str else None

    nuova_nota = Nota(titolo=titolo, contenuto=contenuto, data_scadenza=data_scadenza)
    db.session.add(nuova_nota)
    db.session.commit()
    
    return redirect(url_for('index'))

@app.route('/elimina/<int:id>')
def elimina_nota(id):
    nota = Nota.query.get_or_404(id)
    db.session.delete(nota)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/modifica/<int:id>', methods=['GET', 'POST'])
def modifica_nota(id):
    nota = Nota.query.get_or_404(id)
    
    if request.method == 'POST':
        nota.titolo = request.form.get('titolo')
        nota.contenuto = request.form.get('contenuto')
        data_scadenza_str = request.form.get('data_scadenza')
        
        nota.data_scadenza = datetime.strptime(data_scadenza_str, '%Y-%m-%d').date() if data_scadenza_str else None
        
        db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('edit.html', nota=nota)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)