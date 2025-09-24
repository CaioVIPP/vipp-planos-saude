# app.py
# Carrega detalhes das enrollments e installments
for e in tutor.enrollments:
e.plan = Plan.query.get(e.plan_id)
e.installments = Installment.query.filter_by(enrollment_id=e.id).all()
return render_template('tutor_detail.html', tutor=tutor)


# Form simples para criar tutor
@app.route('/tutor/new', methods=['GET','POST'])
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
t = Tutor(nome=nome, cpf=cpf, email=email, telefone=telefone, endereco=endereco)
db.session.add(t)
db.session.commit()
flash('Tutor criado com sucesso', 'success')
return redirect(url_for('index'))
return render_template('forms.html')


# Adicionar pet
@app.route('/pet/new', methods=['POST'])
def new_pet():
tutor_cpf = request.form['tutor_cpf']
tutor = Tutor.query.filter_by(cpf=tutor_cpf).first()
if not tutor:
flash('Tutor não encontrado para cadastrar pet', 'danger')
return redirect(url_for('index'))
pet = Pet(tutor_id=tutor.id, nome=request.form['nome'], especie=request.form.get('especie'), raca=request.form.get('raca'))
db.session.add(pet)
db.session.commit()
flash('Pet cadastrado', 'success')
return redirect(url_for('search', cpf=tutor_cpf))


# Criar enrollment (adesão)
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
enroll = Enrollment(tutor_id=tutor.id, plan_id=plan_id, forma_pagamento=forma_pag, valor_plano=valor, parcelas=parcelas, taxa_administracao=taxa)
db.session.add(enroll)
db.session.commit()
create_installments(enroll)
flash('Adesão criada', 'success')
return redirect(url_for('search', cpf=cpf))


# Marcar parcela como paga
@app.route('/installment/pay/<int:inst_id>', methods=['POST'])
def pay_installment(inst_id):
inst = Installment.query.get_or_404(inst_id)
inst.pago = True
inst.pago_em = datetime.utcnow()
db.session.commit()
flash('Parcela marcada como paga', 'success')
return redirect(url_for('search', cpf=inst.enrollment.tutor.cpf))


# Admin: upload Excel para importar planos
@app.route('/admin/import', methods=['GET','POST'])
def import_plans():
if request.method == 'POST':
file = request.files.get(