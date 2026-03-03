from __future__ import annotations

from django.contrib import admin
from django.db.models import Sum
from django.template.response import TemplateResponse

from smartwash.admin_site import admin_site
from .models import Agendamento, Assinatura, Despesa, Mensagem, PlanoMensal, Servico


@admin.register(Agendamento, site=admin_site)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = (
        "criado_em",
        "nome",
        "whatsapp",
        "resumo_servicos",
        "plano_mensal",
        "forma_pagamento",
        "status_pagamento",
        "total",
        "horario",
    )
    list_editable = ("status_pagamento",)
    list_filter = ("status_pagamento", "forma_pagamento", "plano_mensal")
    date_hierarchy = "criado_em"
    search_fields = ("nome", "email", "whatsapp", "cpf")
    filter_horizontal = ("servicos",)

    @admin.display(description="Serviços")
    def resumo_servicos(self, obj: Agendamento):
        nomes = list(obj.servicos.values_list("nome", flat=True)[:3])
        extra = obj.servicos.count() - len(nomes)
        if extra > 0:
            return ", ".join(nomes) + f" (+{extra})"
        return ", ".join(nomes) if nomes else "—"

    def save_model(self, request, obj, form, change):
        """Garante total coerente ao salvar pelo admin."""
        super().save_model(request, obj, form, change)
        try:
            total_calc = obj.calcular_total()
            if obj.total != total_calc:
                Agendamento.objects.filter(pk=obj.pk).update(total=total_calc)
        except Exception:
            pass

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)

        # POST geralmente redireciona -> HttpResponseRedirect (sem context_data)
        if not isinstance(response, TemplateResponse):
            return response

        if not hasattr(response, "context_data") or response.context_data is None:
            return response

        context = response.context_data

        # QuerySet com os filtros que o admin aplicou (status_pagamento, plano, busca etc.)
        cl = context.get("cl")
        qs = cl.queryset if cl else self.get_queryset(request)

        # Somatórios
        total_geral = (qs.aggregate(v=Sum("total"))["v"] or 0)

        receita_paga = (
            qs.filter(status_pagamento="PAGO").aggregate(v=Sum("total"))["v"] or 0
        )
        receita_pendente = (
            qs.filter(status_pagamento="PENDENTE").aggregate(v=Sum("total"))["v"] or 0
        )

        # Injeta no contexto para usar no template (seu dashboard/custom)
        context["total_ganhos"] = total_geral
        context["receita_paga"] = receita_paga
        context["receita_pendente"] = receita_pendente

        return response