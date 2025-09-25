from datetime import datetime, timedelta
from models import db, Installment

def create_installments(enrollment):
    """
    Gera parcelas para uma adesão de plano.
    - enrollment: objeto Enrollment já salvo no banco
    """
    hoje = datetime.utcnow().date()
    valor = (enrollment.valor_plano + (enrollment.taxa_administracao or 0)) / enrollment.parcelas

    for i in range(1, enrollment.parcelas + 1):
        vencimento = hoje + timedelta(days=30 * i)
        inst = Installment(
            enrollment_id=enrollment.id,
            numero=i,
            vencimento=vencimento,
            valor=valor,
            pago=False
        )
        db.session.add(inst)

    db.session.commit()
