# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from models import db, Tutor, Pet, Plan, Enrollment, Installment
from utils import create_installments

# -------------------------------
# Configuração inicial
# -------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta'  # troque por algo seguro

# Banco de dados (local = SQLite | Render = PostgreSQL)
# Para rodar localmente:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vipp_plans.db'

# Se for usar PostgreSQL no Render, comente a linha acima e use algo assim:
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://usuario:senha@host:porta/banco'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


# -------------------------------
# Página de detalhes de um tutor
# -------------------------------
@app.route('/tutor/<int:id>')
def tutor_detail(id):
    tutor = Tutor.query.get_or_404(id)

    for e in tutor.enrollments:
        e.plan = Plan.query.get(e.plan_id)
        e.installments = Installment.query.filter_by(enrollment_id=e.id).all()

    return render_template('tutor_detail.html', tutor=tutor)


# -------------------------------
# Criar novo tutor
# -------------------------------
@app.route('/tutor/new', methods=['GET', 'POST'])
def new_tutor():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        endereco = request.form.get('endereco')

        if Tutor.query.filter_by(cpf=cpf).first():
            flash('CPF já cadastrado', 'danger')
            return redirect(url_for('new_tutor'))

        t = Tutor(
            nome=nome,
            cpf=cpf,
            email=email,
            telefone=telefone,
            endereco=endereco
        )
        db.session.add(t)
        db.session.commit()
        flash('Tutor criado com sucesso', 'success')
        return redirect(url_for('index'))

    return render_template('forms.html')


# -------------------------------
# Adicionar pet
# -------------------------------
@app.route('/pet/new', methods=['POST'])
def new_pet():
    tutor_cpf = request.form['tutor_cpf']
    tutor = Tutor.query.filter_by(cpf=tutor_cpf).first()

    if not tutor:
        flash('Tutor não encontrado para cadastrar pet', 'danger')
        return redirect(url_for('index'))

    pet = Pet(
        tutor_id=tutor.id,
        nome=request.form['nome'],
        especie=request.form.get('especie'),
        raca=request.form.get('raca')
    )
    db.session.add(pet)
    db.session.commit()
    flash('Pet cadastrado', 'success')
    return redirect(url_for('search', cpf=tutor_cpf))


# -------------------------------
# Criar enrollment (adesão)
# -------------------------------
@app.route('/enrollment/new', methods=['POST'])
def new_enrollment():
    cpf = request.form['cpf']
    plan_id = int(request.form['plan_id'])
    forma_pag = request.form.get('forma_pagamento', 'boleto')
    parcelas = int(request.form.get('parcelas', 1))
    valor = float(request.form.get('valor', 0))
    taxa = float(request.form.get('taxa', 0))

    tutor = Tutor.query.filter_by(cpf=cpf).first()
    if not tutor:
        flash('Tutor não encontrado', 'danger')
        return redirect(url_for('index'))

    enroll = Enrollment(
        tutor_id=tutor.id,
        plan_id=plan_id,
        forma_pagamento=forma_pag,
        valor_plano=valor,
        parcelas=parcelas,
        taxa_administracao=taxa
    )
    db.session.add(enroll)
    db.session.commit()

    # Gera parcelas automaticamente
    create_installments(enroll)

    flash('Adesão criada com sucesso', 'success')
    return redirect(url_for('search', cpf=cpf))


# -------------------------------
# Marcar parcela como paga
# -------------------------------
@app.route('/installment/pay/<int:inst_id>', methods=['POST'])
def pay_installment(inst_id):
    inst = Installment.query.get_or_404(inst_id)
    inst.pago = True
    inst.pago_em = datetime.utcnow()
    db.session.commit()
    flash('Parcela marcada como paga', 'success')
    return redirect(url_for('search', cpf=inst.enrollment.tutor.cpf))


# -------------------------------
# Admin: importar planos via Excel
# -------------------------------
@app.route('/admin/import', methods=['GET', 'POST'])
def import_plans():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            flash('Nenhum arquivo enviado', 'danger')
            return redirect(url_for('import_plans'))

        # TODO: implementar leitura do Excel com pandas/openpyxl
        # Exemplo:
        # df = pd.read_excel(file)
        # for _, row in df.iterrows():
        #     plan = Plan(nome=row['nome'], valor=row['valor'], ...)
        #     db.session.add(plan)
        # db.session.commit()

        flash('Planos importados com sucesso', 'success')
        return redirect(url_for('index'))

    return render_template('import.html')


# -------------------------------
# Rota inicial
# -------------------------------
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
