from __future__ import annotations

from django.contrib import admin
from django.db.models import Sum

from smartwash.admin_site import admin_site
from django.template.response import TemplateResponse
from .models import (
    Agendamento,
    Assinatura,
    Despesa,
    Horario,
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
            total = obj.calcular_total()
            if obj.total != total:
                Agendamento.objects.filter(pk=obj.pk).update(total=total)
        except Exception:
            pass

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)

        # Se foi POST e o admin decidiu redirecionar, não existe context_data
        if not isinstance(response, TemplateResponse):
            return response

        # A partir daqui é seguro mexer no contexto
        try:
            context = response.context_data
        except Exception:
            return response

        # ---- seu cálculo aqui ----
        # total = ...
        context["total_ganhos"] = total
        # context["outros_campos"] = ...

        return response


# OBS:
# O model Horario não é registrado no Admin de propósito.
# Os horários são gerados via comando "gerar_horarios".