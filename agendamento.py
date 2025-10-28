class Agendamento:
    STATUS_CRIADO = "CRIADO"
    STATUS_CONFIRMADO = "CONFIRMADO"
    STATUS_REALIZADO = "REALIZADO"
    STATUS_CANCELADO = "CANCELADO"

  def __init__(self, paciente, medico, horario):
        self.paciente = paciente
        self.medico = medico
        self.horario = horario
        self.status = Agendamento.STATUS_CRIADO

  def confirmar(self):
        if not self.paciente.ativo:
            raise ValueError("Paciente inativo não pode confirmar agendamento.")
        if not self.medico.disponivel(self.horario):
            raise ValueError("Médico não está disponível neste horário.")
        self.status = Agendamento.STATUS_CONFIRMADO
        self.medico.remover_horario(self.horario)

  def realizar(self):
        if self.status != Agendamento.STATUS_CONFIRMADO:
            raise ValueError("Agendamento só pode ser realizado se estiver CONFIRMADO.")
        self.status = Agendamento.STATUS_REALIZADO

  def cancelar(self):
        status_anterior = self.status
        self.status = Agendamento.STATUS_CANCELADO
        # Se estava confirmado, libera o horário
        if status_anterior == Agendamento.STATUS_CONFIRMADO:
            self.medico.adicionar_horario(self.horario)
