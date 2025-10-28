class Medico:
    def __init__(self, nome: str, especialidade: str):
        self.nome = nome
        self.especialidade = especialidade
        self.agenda = []

  def adicionar_horario(self, horario: str):
        if horario in self.agenda:
            raise ValueError("Horário já existe na agenda.")
        self.agenda.append(horario)

  def remover_horario(self, horario: str):
        if horario not in self.agenda:
            raise ValueError("Horário não encontrado na agenda.")
        self.agenda.remove(horario)

   def disponivel(self, horario: str) -> bool:
        return horario in self.agenda
