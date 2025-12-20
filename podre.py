# testar_ruff.py - Script para testar o linter Ruff em português
import sys  # importação não utilizada (será detectada)
import os   # outra importação não utilizada

def calcular(primeiro_numero, segundo_numero):
    """
    Função com problemas de formatação e estilo.
    """
    # Problema de espaçamento em operador
    resultado=primeiro_numero+segundo_numero  # E225: falta espaço em torno do operador
    
    # Variável não utilizada
    variavel_inutil = "não usada"  # F841: variável definida mas não utilizada
    
    return resultado

def saudacao(nome):
    # Usando variável não definida
    mensagem = f"Olá, {variavel_indefinida}!"  # F821: nome não definido
    return mensagem

# Linha muito longa (>88 caracteres - padrão do Ruff)
def exemplo_linha_longa():
    print("Esta linha é extremamente longa e com certeza vai exceder o limite de caracteres padrão do Ruff configurado pela formatação Black.")

# Comparação com None usando == (não recomendado)
if sys.argv[0] == None:  # E711: comparação com None deve usar 'is'
    print("Isso será marcado pelo Ruff.")

# Problema de ordenação de imports (regra do isort)
from datetime import datetime  # este import deveria estar no topo
import json  # ordem incorreta de importação

# Código que nunca será executado
x = 10
if False:
    print("Nunca será impresso")

# Chamando a função com parâmetros incorretos
calcular(1)  # F821: falta argumento obrigatório

# Exemplo de f-string mal formatada
nome = "Maria"
idade = 30
print(f"{nome} tem {idade} anos.")

# Função muito complexa (demasiados branches)
def funcao_complexa(valor):
    if valor > 0:
        if valor < 10:
            if valor % 2 == 0:
                if valor == 4:
                    return "quatro"
                else:
                    return "par pequeno"
            else:
                return "ímpar pequeno"
        else:
            return "positivo grande"
    else:
        return "não positivo"

# Dict com chaves duplicadas
meu_dict = {"chave": 1, "chave": 2}  # F601: chave de dict duplicada

print("Script para testar Ruff em português!")