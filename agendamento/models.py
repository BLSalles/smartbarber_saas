from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone


class Servico(models.Model):
    """Serviços da barbearia (corte, barba, sobrancelha, etc.)."""

    class Categoria(models.TextChoices):
        CABELO = "CABELO", "Cabelo"
        BARBA = "BARBA", "Barba"
        ESTETICA = "ESTETICA", "Estética"
        QUIMICA = "QUIMICA", "Química/Tratamento"
        PACOTE = "PACOTE", "Pacote/Combo"

    nome = models.CharField(max_length=120, unique=True)
    categoria = models.CharField(max_length=20, choices=Categoria.choices, default=Categoria.CABELO)
    duracao_min = models.PositiveIntegerField(default=30)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    ativo = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.nome} (R$ {self.valor})"


class PlanoMensal(models.Model):
    """Plano de assinatura mensal (ex.: ilimitado, 2 visitas/mês, etc.)."""

    nome = models.CharField(max_length=120, unique=True)
    descricao = models.TextField(blank=True)
    valor_mensal = models.DecimalField(max_digits=10, decimal_places=2)
    # Para simplificar: 0 = ilimitado
    limite_visitas_mes = models.PositiveIntegerField(default=0)
    ativo = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.nome} (R$ {self.valor_mensal}/mês)"


class Horario(models.Model):
    """Slot de agenda."""

    data = models.DateField()
    hora = models.TimeField()
    disponivel = models.BooleanField(default=True)

    class Meta:
        unique_together = ("data", "hora")

    def __str__(self) -> str:
        return f"{self.data} {self.hora}"


class Assinatura(models.Model):
    """Assinatura ativa vinculada ao cliente (por WhatsApp + e-mail)."""

    nome = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    whatsapp = models.CharField(max_length=30)
    cpf = models.CharField(max_length=14, blank=True)

    plano = models.ForeignKey(PlanoMensal, on_delete=models.PROTECT)
    inicio = models.DateField(default=timezone.localdate)
    ativa = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["whatsapp", "ativa"]),
            models.Index(fields=["email", "ativa"]),
        ]

    def __str__(self) -> str:
        return f"{self.nome} - {self.plano.nome}"


class Agendamento(models.Model):
    """Agendamento do cliente."""

    class FormaPagamento(models.TextChoices):
        PIX = "PIX", "PIX"
        CARTAO = "CARTAO", "Cartão"
        DINHEIRO = "DINHEIRO", "Dinheiro"

    class StatusPagamento(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        PAGO = "PAGO", "Pago"
        CANCELADO = "CANCELADO", "Cancelado"

    nome = models.CharField(max_length=120)
    email = models.EmailField()
    whatsapp = models.CharField(max_length=30)
    cpf = models.CharField(max_length=14, blank=True)

    # Seleção de serviços (multi)
    servicos = models.ManyToManyField(Servico, blank=True)

    # Se o cliente optou por adquirir/usar um plano mensal
    plano_mensal = models.ForeignKey(PlanoMensal, null=True, blank=True, on_delete=models.PROTECT)
    assinatura = models.ForeignKey(Assinatura, null=True, blank=True, on_delete=models.SET_NULL)

    horario = models.OneToOneField(Horario, on_delete=models.CASCADE)

    forma_pagamento = models.CharField(max_length=20, choices=FormaPagamento.choices, default=FormaPagamento.PIX)
    status_pagamento = models.CharField(max_length=20, choices=StatusPagamento.choices, default=StatusPagamento.PENDENTE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.nome} - {self.horario.data} {self.horario.hora}"

    def calcular_total(self) -> Decimal:
        """Soma serviços + (se houver) plano mensal."""
        total = Decimal("0.00")
        total += sum((s.valor for s in self.servicos.all()), Decimal("0.00"))
        if self.plano_mensal_id:
            total += self.plano_mensal.valor_mensal
        return total


class Despesa(models.Model):
    """Controle simples de despesas para o financeiro."""

    class Categoria(models.TextChoices):
        INSUMOS = "INSUMOS", "Insumos"
        ALUGUEL = "ALUGUEL", "Aluguel"
        SALARIOS = "SALARIOS", "Salários"
        MARKETING = "MARKETING", "Marketing"
        OUTROS = "OUTROS", "Outros"

    descricao = models.CharField(max_length=160)
    categoria = models.CharField(max_length=20, choices=Categoria.choices, default=Categoria.OUTROS)
    data = models.DateField(default=timezone.localdate)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.descricao} (R$ {self.valor})"


class Mensagem(models.Model):
    """Mensagens enviadas pelo cliente (ex.: dúvidas no agendamento)."""

    nome = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    assunto = models.CharField(max_length=120, blank=True)
    conteudo = models.TextField()
    lida = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.nome} - {self.assunto or 'Mensagem'}"
