import json
from datetime import date, timedelta

from django.contrib.admin import AdminSite
from django.db.models import Q, Sum
from django.utils import timezone

from agendamento.models import Agendamento, Assinatura, Despesa, Servico


def _parse_date(value: str | None) -> date | None:
    """Parse YYYY-MM-DD (from <input type=date>) to date."""
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


class SmartWashAdminSite(AdminSite):
    site_header = "SmartRoutine | Barber SaaS"
    site_title = "SmartRoutine Barber"
    index_title = "Dashboard"
    index_template = "admin/index.html"

    def index(self, request, extra_context=None):
        # ===== Base dates
        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)
        week_end = today + timedelta(days=7)

        # ===== Read filters
        # If no explicit filter is provided, default to TODAY.
        f_de = request.GET.get("de")
        f_ate = request.GET.get("ate")
        f_servico = request.GET.get("servico")
        f_q = (request.GET.get("q") or "").strip()

        d_de = _parse_date(f_de) or today
        d_ate = _parse_date(f_ate) or today
        if d_ate < d_de:
            d_de, d_ate = d_ate, d_de

        # Normalized values back to template
        f_de_norm = d_de.isoformat()
        f_ate_norm = d_ate.isoformat()

        # ===== Queryset (base)
        qs = (
            Agendamento.objects
            .select_related("horario", "plano_mensal")
            .prefetch_related("servicos")
            .filter(horario__data__gte=d_de, horario__data__lte=d_ate)
        )

        if f_servico:
            qs = qs.filter(servicos__id=f_servico)

        if f_q:
            qs = qs.filter(
                Q(nome__icontains=f_q)
                | Q(cpf__icontains=f_q)
                | Q(whatsapp__icontains=f_q)
                | Q(email__icontains=f_q)
            )

        qs = qs.order_by("horario__data", "horario__hora")

        # ===== KPIs
        total_agendamentos = qs.count()
        total_faturamento = qs.filter(status_pagamento=Agendamento.StatusPagamento.PAGO).aggregate(total=Sum("total"))["total"] or 0
        total_pendente = qs.filter(status_pagamento=Agendamento.StatusPagamento.PENDENTE).aggregate(total=Sum("total"))["total"] or 0

        # ===== Agenda blocks (intuitive view)
        base_agenda = (
            Agendamento.objects
            .select_related("horario", "plano_mensal")
            .prefetch_related("servicos")
            .order_by("horario__data", "horario__hora")
        )

        # Apply only "tipo" and "q" to the daily blocks, so the admin can
        # still see the day view consistent with what they searched.
        if f_servico:
            base_agenda = base_agenda.filter(servicos__id=f_servico)
        if f_q:
            base_agenda = base_agenda.filter(
                Q(nome__icontains=f_q)
                | Q(cpf__icontains=f_q)
                | Q(whatsapp__icontains=f_q)
                | Q(email__icontains=f_q)
            )

        agenda_hoje = base_agenda.filter(horario__data=today)
        agenda_amanha = base_agenda.filter(horario__data=tomorrow)
        agenda_prox7 = base_agenda.filter(horario__data__gte=tomorrow, horario__data__lte=week_end)

        # ===== Recent list (within current filter)
        recent_agendamentos = qs.order_by("-horario__data", "-horario__hora", "-criado_em")[:20]

        # ===== Chart: faturamento por dia
        # If user filtered a range, use it; else show last 14 days.
        if request.GET.get("de") or request.GET.get("ate"):
            chart_start = d_de
            chart_end = d_ate
        else:
            chart_end = today
            chart_start = today - timedelta(days=13)

        agg = (
            Agendamento.objects
            .select_related("horario")
            .filter(horario__data__gte=chart_start, horario__data__lte=chart_end)
        )
        if f_servico:
            agg = agg.filter(servicos__id=f_servico)
        if f_q:
            agg = agg.filter(
                Q(nome__icontains=f_q)
                | Q(cpf__icontains=f_q)
                | Q(whatsapp__icontains=f_q)
                | Q(email__icontains=f_q)
            )

        by_day = {
            row["horario__data"]: float(row["total"] or 0)
            for row in agg.filter(status_pagamento=Agendamento.StatusPagamento.PAGO)
            .values("horario__data").annotate(total=Sum("total")).order_by("horario__data")
        }

        labels: list[str] = []
        totals: list[float] = []
        cur = chart_start
        while cur <= chart_end:
            labels.append(cur.strftime("%d/%m"))
            totals.append(by_day.get(cur, 0.0))
            cur += timedelta(days=1)

        servicos = Servico.objects.filter(ativo=True).order_by("categoria", "nome")

        # Financeiro (período do filtro)
        despesas_periodo = Despesa.objects.filter(data__gte=d_de, data__lte=d_ate).aggregate(total=Sum("valor"))["total"] or 0
        lucro_periodo = (total_faturamento or 0) - (despesas_periodo or 0)

        # Assinaturas ativas
        assinaturas_ativas = Assinatura.objects.filter(ativa=True).count()

        extra_context = extra_context or {}
        extra_context.update({
            # dates
            "today": today,
            "tomorrow": tomorrow,
            "week_end": week_end,

            # filters (normalized)
            "f_de": f_de_norm,
            "f_ate": f_ate_norm,
            "f_servico": f_servico or "",
            "f_q": f_q,
            "servicos": servicos,

            # dashboard content
            "agenda_hoje": agenda_hoje,
            "agenda_amanha": agenda_amanha,
            "agenda_prox7": agenda_prox7,
            "recent_agendamentos": recent_agendamentos,

            # KPIs
            "total_agendamentos": total_agendamentos,
            "total_faturamento": total_faturamento,
            "total_pendente": total_pendente,
            "total_despesas": despesas_periodo,
            "lucro_periodo": lucro_periodo,
            "assinaturas_ativas": assinaturas_ativas,

            # chart
            "chart_start": chart_start,
            "chart_end": chart_end,
            "chart_labels": json.dumps(labels, ensure_ascii=False),
            "chart_totals": json.dumps(totals, ensure_ascii=False),
        })

        return super().index(request, extra_context=extra_context)


admin_site = SmartWashAdminSite(name="smartwash_admin")
