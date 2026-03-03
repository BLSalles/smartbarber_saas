from __future__ import annotations

from django.db import transaction
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_date
from django.utils import timezone

from .models import Agendamento, Assinatura, Horario, PlanoMensal, Servico


def agendar(request):
    """Tela pública de agendamento (mobile-first)."""

    data_str = request.GET.get("data")
    data = parse_date(data_str) if data_str else None

    servicos = Servico.objects.filter(ativo=True).order_by("categoria", "nome")
    planos = PlanoMensal.objects.filter(ativo=True).order_by("valor_mensal")

    horarios = Horario.objects.none()
    if data:
        today = timezone.localdate()
        now_t = timezone.localtime().time()

        if data < today:
            horarios = Horario.objects.none()
        else:
            qs_h = Horario.objects.filter(data=data, disponivel=True)
            if data == today:
                qs_h = qs_h.filter(hora__gt=now_t)
            horarios = qs_h.order_by("hora")

    if request.method == "POST":
        horario_id = request.POST.get("horario")
        servicos_ids = request.POST.getlist("servicos")
        plano_id = request.POST.get("plano_mensal") or None

        # Pagamento
        forma = request.POST.get("forma_pagamento") or Agendamento.FormaPagamento.PIX
        obs = (request.POST.get("observacoes") or "").strip()

        with transaction.atomic():
            # trava o horário pra evitar duplicar
            horario = Horario.objects.select_for_update().get(id=horario_id)
            # não permite agendar horário no passado
            today = timezone.localdate()
            now_t = timezone.localtime().time()
            if horario.data < today or (horario.data == today and horario.hora <= now_t):
                return render(request, "agendar.html", {
                    "servicos": servicos,
                    "planos": planos,
                    "horarios": horarios,
                    "erro": "Esse horário já passou. Escolha outro.",
                })

            if not horario.disponivel:
                return render(request, "agendar.html", {
                    "servicos": servicos,
                    "planos": planos,
                    "horarios": horarios,
                    "erro": "Esse horário já foi agendado. Escolha outro.",
                })

            plano = PlanoMensal.objects.filter(id=plano_id, ativo=True).first() if plano_id else None

            ag = Agendamento.objects.create(
                nome=request.POST["nome"].strip(),
                email=request.POST["email"].strip(),
                whatsapp=request.POST["whatsapp"].strip(),
                cpf=(request.POST.get("cpf") or "").strip(),
                plano_mensal=plano,
                horario=horario,
                forma_pagamento=forma,
                observacoes=obs,
            )

            if servicos_ids:
                ag.servicos.set(Servico.objects.filter(id__in=servicos_ids, ativo=True))

            # Se escolheu plano, cria assinatura (ou reutiliza ativa) para o mesmo WhatsApp
            if plano:
                assinatura = (
                    Assinatura.objects.filter(whatsapp=ag.whatsapp, ativa=True)
                    .select_related("plano")
                    .first()
                )
                if not assinatura or assinatura.plano_id != plano.id:
                    assinatura = Assinatura.objects.create(
                        nome=ag.nome,
                        email=ag.email,
                        whatsapp=ag.whatsapp,
                        cpf=ag.cpf,
                        plano=plano,
                    )
                ag.assinatura = assinatura
                ag.save(update_fields=["assinatura"])

            # Total
            ag.total = ag.calcular_total()
            ag.save(update_fields=["total"])

            # ocupa o horário
            horario.disponivel = False
            horario.save(update_fields=["disponivel"])

        return redirect("sucesso")

    return render(request, "agendar.html", {"servicos": servicos, "planos": planos, "horarios": horarios})


def sucesso(request):
    return render(request, "sucesso.html")
