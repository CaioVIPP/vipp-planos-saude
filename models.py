from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Tutor(db.Model):
    __tablename__ = "tutor"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(120))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))

    pets = db.relationship("Pet", backref="tutor", lazy=True)
    enrollments = db.relationship("Enrollment", backref="tutor", lazy=True)


class Pet(db.Model):
    __tablename__ = "pet"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    especie = db.Column(db.String(50))
    raca = db.Column(db.String(50))
    microchip = db.Column(db.String(50))

    tutor_id = db.Column(db.Integer, db.ForeignKey("tutor.id"), nullable=False)


class Plan(db.Model):
    __tablename__ = "plan"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)


class Enrollment(db.Model):
    __tablename__ = "enrollment"
    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey("tutor.id"), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey("plan.id"))
    valor_plano = db.Column(db.Float, nullable=False)
    parcelas = db.Column(db.Integer, default=1)
    forma_pagamento = db.Column(db.String(50))
    taxa_adm = db.Column(db.Float, default=0.0)

    installments = db.relationship("Installment", backref="enrollment", lazy=True)


class Installment(db.Model):
    __tablename__ = "installment"
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    vencimento = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    pago = db.Column(db.Boolean, default=False)
    pago_em = db.Column(db.Date)

    enrollment_id = db.Column(db.Integer, db.ForeignKey("enrollment.id"), nullable=False)
