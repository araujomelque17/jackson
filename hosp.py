import pytest
from src.paciente import Paciente

# Uso de parametrização para testar múltiplos cenários de CPF inválido [21]
@pytest.mark.parametrize("cpf_invalido", [
    "1234567890", # 10 dígitos
    "123456789012", # 12 dígitos
    "12345abc789", # Não numérico
    "", # Vazio
], ids=["10_digitos", "12_digitos", "nao_numerico", "vazio"])
def test_paciente_cpf_invalido_deve_lancar_erro(cpf_invalido):
    # Uso de pytest.raises para verificar se o erro ValueError é lançado [14, 24]
    with pytest.raises(ValueError, match="CPF deve ter 11 dígitos numéricos."):
        # Act (Executar) [25]
        Paciente(nome="Teste", cpf=cpf_invalido)

def test_paciente_cpf_valido_deve_ser_criado():
    # Arrange (Preparar) [25]
    cpf_valido = "11122233344"
    
    # Act (Executar) [25]
    p = Paciente(nome="Joao", cpf=cpf_valido, ativo=False)
    
    # Assert (Verificar) [25, 26]
    assert p.nome == "Joao"
    assert p.cpf == cpf_valido
    assert p.ativo is False # Verifica atributo de instância [2, 18]

def test_paciente_ativo_por_padrao():
    p = Paciente(nome="Maria", cpf="99988877766")
    assert p.ativo is True
2.2. tests/test_medico.py

import pytest
from src.medico import Medico

HORARIO_1 = "2025-05-10 14:00"
HORARIO_2 = "2025-05-10 15:00"

# Fixture para criar um objeto Medico com um horário inicial [20, 23]
@pytest.fixture
def medico_com_agenda():
    m = Medico(nome="Dr. House", especialidade="Clínico Geral")
    m.adicionar_horario(HORARIO_1)
    return m

def test_adicionar_horario(medico_com_agenda):
    medico_com_agenda.adicionar_horario(HORARIO_2)
    # Asserção de pertencimento [27]
    assert HORARIO_1 in medico_com_agenda.agenda
    assert HORARIO_2 in medico_com_agenda.agenda
    assert len(medico_com_agenda.agenda) == 2

def test_adicionar_horario_duplicado_deve_lancar_erro(medico_com_agenda):
    # Regra: Não permitir horários duplicados [13]
    with pytest.raises(ValueError, match="Horário já existe na agenda."):
        medico_com_agenda.adicionar_horario(HORARIO_1)

def test_remover_horario(medico_com_agenda):
    medico_com_agenda.remover_horario(HORARIO_1)
    assert HORARIO_1 not in medico_com_agenda.agenda
    assert len(medico_com_agenda.agenda) == 0

def test_remover_horario_inexistente_deve_lancar_erro(medico_com_agenda):
    # Regra: Não permitir remoção de horários inexistentes [13]
    with pytest.raises(ValueError, match="Horário não encontrado na agenda."):
        medico_com_agenda.remover_horario(HORARIO_2)

def test_disponivel_retorna_corretamente(medico_com_agenda):
    # Teste de disponibilidade (True)
    assert medico_com_agenda.disponivel(HORARIO_1) is True
    # Teste de indisponibilidade (False)
    assert medico_com_agenda.disponivel(HORARIO_2) is False
2.3. tests/test_agendamento.py

# tests/test_agendamento.py
import pytest
from src.paciente import Paciente
from src.medico import Medico
from src.agendamento import Agendamento

HORARIO_DISP = "2025-10-20 10:00"
HORARIO_INDISP = "2025-10-20 11:00" # Não estará na agenda inicial

# Fixture para Paciente Ativo [20]
@pytest.fixture
def paciente_ativo():
    return Paciente(nome="Alice", cpf="11111111111", ativo=True)

# Fixture para Paciente Inativo
@pytest.fixture
def paciente_inativo():
    return Paciente(nome="Bob", cpf="22222222222", ativo=False)

# Fixture para Médico com horário disponível
@pytest.fixture
def medico_disponivel():
    m = Medico(nome="Dra. Eva", especialidade="Cardio")
    m.adicionar_horario(HORARIO_DISP)
    return m

# Fixture que cria um Agendamento no estado CRIADO
@pytest.fixture
def agendamento_criado(paciente_ativo, medico_disponivel):
    return Agendamento(paciente_ativo, medico_disponivel, HORARIO_DISP)

# --- Testes de Confirmação (Regras Complexas) ---

def test_confirmar_agendamento_sucesso(agendamento_criado, medico_disponivel):
    # Act
    agendamento_criado.confirmar()

    # Assert 1: Status mudou [17]
    assert agendamento_criado.status == Agendamento.STATUS_CONFIRMADO
    
    # Assert 2: Horário removido da agenda do médico (Efeito colateral obrigatório) [17]
    assert medico_disponivel.disponivel(HORARIO_DISP) is False

def test_confirmar_paciente_inativo_deve_lancar_erro(paciente_inativo, medico_disponivel):
    agendamento = Agendamento(paciente_inativo, medico_disponivel, HORARIO_DISP)
    
    # Regra: Paciente inativo não pode agendar [13, 17]
    with pytest.raises(ValueError, match="Paciente inativo não pode confirmar agendamento."):
        agendamento.confirmar()
    
    # Verifica que o status permaneceu CRIADO
    assert agendamento.status == Agendamento.STATUS_CRIADO

def test_confirmar_medico_indisponivel_deve_lancar_erro(paciente_ativo, medico_disponivel):
    # O agendamento usa um HORARIO_INDISP que não está na agenda do médico
    agendamento = Agendamento(paciente_ativo, medico_disponivel, HORARIO_INDISP)

    # Regra: Médico indisponível [17]
    with pytest.raises(ValueError, match="Médico não está disponível neste horário."):
        agendamento.confirmar()

# --- Testes de Transição de Status ---

def test_realizar_sucesso(agendamento_criado):
    agendamento_criado.confirmar()
    agendamento_criado.realizar() # Só pode ser chamado se CONFIRMADO [17]
    assert agendamento_criado.status == Agendamento.STATUS_REALIZADO

def test_realizar_falha_se_nao_confirmado(agendamento_criado):
    # Tenta realizar diretamente do estado CRIADO
    with pytest.raises(ValueError, match="CONFIRMADO"):
        agendamento_criado.realizar()

# --- Testes de Cancelamento ---

def test_cancelar_agendamento_e_liberar_horario(agendamento_criado, medico_disponivel):
    # 1. Confirma (horário é removido da agenda)
    agendamento_criado.confirmar()
    assert medico_disponivel.disponivel(HORARIO_DISP) is False
    
    # 2. Cancela (status anterior era CONFIRMADO, não REALIZADO)
    agendamento_criado.cancelar()
    
    # Assert 1: Status mudou
    assert agendamento_criado.status == Agendamento.STATUS_CANCELADO
    # Assert 2: Horário DEVE ser liberado [17]
    assert medico_disponivel.disponivel(HORARIO_DISP) is True

def test_cancelar_nao_libera_horario_se_ja_realizado(agendamento_criado, medico_disponivel):
    # 1. Prepara: Confirma e Realiza
    agendamento_criado.confirmar()
    agendamento_criado.realizar()
    assert medico_disponivel.disponivel(HORARIO_DISP) is False # Deve estar indisponível
