from __future__ import annotations

from django.contrib import admin
from django.db.models import Sum
from django.template.response import TemplateResponse

from smartwash.admin_site import admin_site
from .models import (
    Agendamento,
    Assinatura,
    Despesa,
    Mensagem,
    PlanoMensal,
    Servico,
)


@admin.register(Servico, site=admin_site)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "duracao_min", "valor", "ativo")
    list_filter = ("categoria", "ativo")
    search_fields = ("nome",)


@admin.register(PlanoMensal, site=admin_site)
class PlanoMensalAdmin(admin.ModelAdmin):
    list_display = ("nome", "valor_mensal", "limite_visitas_mes", "ativo")
    list_filter = ("ativo",)
    search_fields = ("nome",)


@admin.register(Assinatura, site=admin_site)
class AssinaturaAdmin(admin.ModelAdmin):
    list_display = ("criado_em", "nome", "whatsapp", "plano", "inicio", "ativa")
    list_filter = ("ativa", "plano")
    search_fields = ("nome", "email", "whatsapp", "cpf")
    date_hierarchy = "criado_em"


@admin.register(Despesa, site=admin_site)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ("data", "descricao", "categoria", "valor")
    list_filter = ("categoria",)
    search_fields = ("descricao",)
    date_hierarchy = "data"


@admin.register(Mensagem, site=admin_site)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ("criado_em", "nome", "assunto", "lida")
    list_filter = ("lida",)
    search_fields = ("nome", "email", "whatsapp", "assunto", "conteudo")
    date_hierarchy = "criado_em"


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
    # editar rápido na listagem
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
        # M2M só existe após salvar; recalcula e atualiza
        try:
            total_calc = obj.calcular_total()
            if obj.total != total_calc:
                Agendamento.objects.filter(pk=obj.pk).update(total=total_calc)
        except Exception:
            pass

    def changelist_view(self, request, extra_context=None):
        """Adiciona KPIs no contexto da changelist sem quebrar POST/redirect."""
        response = super().changelist_view(request, extra_context=extra_context)

        # POST geralmente redireciona -> HttpResponseRedirect (sem context_data)
        if not isinstance(response, TemplateResponse):
            return response
        if not hasattr(response, "context_data") or response.context_data is None:
            return response

        context = response.context_data

        # QuerySet com filtros do admin aplicados
        cl = context.get("cl")
        qs = cl.queryset if cl else self.get_queryset(request)

        total_geral = qs.aggregate(v=Sum("total")).get("v") or 0
        receita_paga = qs.filter(status_pagamento="PAGO").aggregate(v=Sum("total")).get("v") or 0
        receita_pendente = qs.filter(status_pagamento="PENDENTE").aggregate(v=Sum("total")).get("v") or 0

        context["total_ganhos"] = total_geral
        context["receita_paga"] = receita_paga
        context["receita_pendente"] = receita_pendente

        return response


# OBS:
# O model Horario não é registrado no Admin de propósito.
# Os horários são gerados via comando "gerar_horarios".
