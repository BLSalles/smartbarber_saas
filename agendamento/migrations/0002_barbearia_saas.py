from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("agendamento", "0001_initial"),
    ]

    operations = [
        # Remove old car-wash models
        migrations.DeleteModel(name="Agendamento"),
        migrations.DeleteModel(name="TipoLavagem"),

        # New models (barbearia SaaS)
        migrations.CreateModel(
            name="Servico",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=120, unique=True)),
                (
                    "categoria",
                    models.CharField(
                        choices=[
                            ("CABELO", "Cabelo"),
                            ("BARBA", "Barba"),
                            ("ESTETICA", "Estética"),
                            ("QUIMICA", "Química/Tratamento"),
                            ("PACOTE", "Pacote/Combo"),
                        ],
                        default="CABELO",
                        max_length=20,
                    ),
                ),
                ("duracao_min", models.PositiveIntegerField(default=30)),
                ("valor", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("ativo", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="PlanoMensal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=120, unique=True)),
                ("descricao", models.TextField(blank=True)),
                ("valor_mensal", models.DecimalField(decimal_places=2, max_digits=10)),
                ("limite_visitas_mes", models.PositiveIntegerField(default=0)),
                ("ativo", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Assinatura",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=120)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("whatsapp", models.CharField(max_length=30)),
                ("cpf", models.CharField(blank=True, max_length=14)),
                ("inicio", models.DateField(default=django.utils.timezone.localdate)),
                ("ativa", models.BooleanField(default=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                (
                    "plano",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="agendamento.planomensal"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Despesa",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("descricao", models.CharField(max_length=160)),
                (
                    "categoria",
                    models.CharField(
                        choices=[
                            ("INSUMOS", "Insumos"),
                            ("ALUGUEL", "Aluguel"),
                            ("SALARIOS", "Salários"),
                            ("MARKETING", "Marketing"),
                            ("OUTROS", "Outros"),
                        ],
                        default="OUTROS",
                        max_length=20,
                    ),
                ),
                ("data", models.DateField(default=django.utils.timezone.localdate)),
                ("valor", models.DecimalField(decimal_places=2, max_digits=10)),
                ("observacoes", models.TextField(blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Mensagem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=120)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("whatsapp", models.CharField(blank=True, max_length=30)),
                ("assunto", models.CharField(blank=True, max_length=120)),
                ("conteudo", models.TextField()),
                ("lida", models.BooleanField(default=False)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Agendamento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("whatsapp", models.CharField(max_length=30)),
                ("cpf", models.CharField(blank=True, max_length=14)),
                (
                    "forma_pagamento",
                    models.CharField(
                        choices=[("PIX", "PIX"), ("CARTAO", "Cartão"), ("DINHEIRO", "Dinheiro")],
                        default="PIX",
                        max_length=20,
                    ),
                ),
                (
                    "status_pagamento",
                    models.CharField(
                        choices=[("PENDENTE", "Pendente"), ("PAGO", "Pago"), ("CANCELADO", "Cancelado")],
                        default="PENDENTE",
                        max_length=20,
                    ),
                ),
                ("total", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("observacoes", models.TextField(blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                (
                    "assinatura",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="agendamento.assinatura"),
                ),
                (
                    "horario",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to="agendamento.horario"),
                ),
                (
                    "plano_mensal",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="agendamento.planomensal"),
                ),
            ],
        ),
        migrations.AddField(
            model_name="agendamento",
            name="servicos",
            field=models.ManyToManyField(blank=True, to="agendamento.servico"),
        ),

        migrations.AddIndex(
            model_name="assinatura",
            index=models.Index(fields=["whatsapp", "ativa"], name="agendamento__whatsapp_ativa"),
        ),
        migrations.AddIndex(
            model_name="assinatura",
            index=models.Index(fields=["email", "ativa"], name="agendamento__email_ativa"),
        ),
    ]
