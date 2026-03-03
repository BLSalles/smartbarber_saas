from django.core.management.base import BaseCommand
from agendamento.models import Horario
from datetime import datetime, date, time, timedelta


class Command(BaseCommand):
    help = 'Gera horários de segunda a sábado das 08:00 às 17:30'

    def handle(self, *args, **kwargs):

        data_inicio = date.today()
        dias = 60  # quantos dias no futuro gerar

        for i in range(dias):

            data_atual = data_inicio + timedelta(days=i)

            # 0=segunda, 6=domingo
            if data_atual.weekday() == 6:
                continue  # pula domingo

            hora_atual = datetime.combine(data_atual, time(8, 0))
            hora_fim = datetime.combine(data_atual, time(17, 30))

            while hora_atual <= hora_fim:

                hora = hora_atual.time()

                Horario.objects.get_or_create(
                    data=data_atual,
                    hora=hora,
                    defaults={'disponivel': True}
                )

                hora_atual += timedelta(minutes=30)

        self.stdout.write(self.style.SUCCESS('Horários gerados com sucesso!'))