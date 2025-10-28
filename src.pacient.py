class Paciente:
    def __init__(self, nome: str, cpf: str, ativo: bool = True):
        if not cpf.isdigit() or len(cpf) != 11:
            raise ValueError("CPF deve ter 11 dígitos numéricos.")
        self.nome = nome
        self.cpf = cpf
        self.ativo = ativo
