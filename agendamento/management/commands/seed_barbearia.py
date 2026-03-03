from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand

from agendamento.models import PlanoMensal, Servico


class Command(BaseCommand):
    help = "Cria serviços e planos padrão (demo) para a barbearia."

    def handle(self, *args, **kwargs):
        servicos = [
            # Valores inspirados em tabelas públicas e práticas comuns no BR
            # (ajuste livremente no Admin)
            ("Corte social", "CABELO", 30, Decimal("35.00")),
            ("Degradê", "CABELO", 40, Decimal("45.00")),
            ("Corte + lavagem", "CABELO", 45, Decimal("55.00")),
            ("Barba", "BARBA", 30, Decimal("35.00")),
            ("Barba + toalha quente", "BARBA", 40, Decimal("45.00")),
            ("Sobrancelha", "ESTETICA", 15, Decimal("15.00")),
            ("Pezinho / Acabamento", "ESTETICA", 15, Decimal("15.00")),
            ("Pigmentação", "QUIMICA", 30, Decimal("35.00")),
            ("Hidratação", "QUIMICA", 30, Decimal("30.00")),
            ("Combo completo (cabelo + barba + sobrancelha)", "PACOTE", 70, Decimal("85.00")),
        ]

        planos = [
            ("Mensal Essencial", "1 corte por semana (até 4/mês).", Decimal("99.90"), 4),
            ("Mensal Premium", "Cortes ilimitados (seg a sáb).", Decimal("139.90"), 0),
            ("Mensal VIP", "Cabelo + barba ilimitados (consulte regras).", Decimal("199.90"), 0),
        ]

        created_s = 0
        for nome, cat, dur, valor in servicos:
            obj, created = Servico.objects.get_or_create(
                nome=nome,
                defaults={"categoria": cat, "duracao_min": dur, "valor": valor, "ativo": True},
            )
            if created:
                created_s += 1

        created_p = 0
        for nome, desc, valor, lim in planos:
            obj, created = PlanoMensal.objects.get_or_create(
                nome=nome,
                defaults={"descricao": desc, "valor_mensal": valor, "limite_visitas_mes": lim, "ativo": True},
            )
            if created:
                created_p += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed concluído. Serviços criados: {created_s}. Planos criados: {created_p}."
        ))
