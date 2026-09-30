"""TUI portátil do Gerenciador de Usuários (sem lib de teclado)."""
import os
import time

from .users import listar, login, registrar

VERMELHO = "\033[31m"
VERDE = "\033[32m"
AMARELO = "\033[33m"
RESET = "\033[0m"
CLEAR = "cls" if os.name == "nt" else "clear"

OPCOES = ["Registrar", "Login", "Sair"]


def menu():
    os.system(CLEAR)
    print("#" * 31)
    print("#   Gerenciador de Usuários   #")
    print("#" * 31)
    for i, op in enumerate(OPCOES, 1):
        print(f"  {i}. {op}")


def _pausa(msg="Pressione Enter para continuar..."):
    input(f"\n{AMARELO}{msg}{RESET}")


def _registrar():
    print("Registro de Usuário")
    nome = input("Digite seu nome: ")
    senha = input("Digite sua senha: ")
    cpf = input("Digite seu CPF (apenas números): ")
    try:
        registrar(nome, senha, cpf)
        print(f"{VERDE}Usuário registrado com sucesso!{RESET}")
    except ValueError as e:
        print(f"{VERDE if False else VERMELHO}{e}{RESET}")


def _login():
    print("Login de Usuário")
    nome = input("Digite seu nome: ")
    senha = input("Digite sua senha: ")
    usuario = login(nome, senha)
    if usuario:
        print(f"{VERDE}Login bem-sucedido!{RESET}")
        print(f"Nome: {usuario['nome']}")
        print(f"CPF:  {usuario['cpf'][:3]}.***.***-{usuario['cpf'][-2:]}")
    else:
        print(f"{VERMELHO}Nome ou senha incorretos!{RESET}")


def run():
    acoes = {"1": _registrar, "2": _login}
    while True:
        menu()
        escolha = input("Escolha [1-3]: ").strip()
        if escolha == "3":
            print(f"{AMARELO}Saindo...{RESET}")
            break
        if escolha in acoes:
            os.system(CLEAR)
            acoes[escolha]()
            _pausa()
        else:
            print(f"{VERMELHO}Opção inválida.{RESET}")
            _pausa()
