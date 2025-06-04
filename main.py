# Projeto: Global Solution: Queimadas
# Disciplina: Dynamic Programming
# Integrantes: Higor Batista - RM 558907 || Fabricio Bettarello - RM 554638 || Kauê Pires - RM 554403

import heapq
import random
import time
from collections import deque
from colorama import Fore, init

# Configura o colorama
init(autoreset=True)

# Nó pra guardar os registros do histórico
class NoHistorico:
    def __init__(self, info):
        self.info = info  # Guarda a string do registro
        self.proximo = None  # Próximo nó da lista

# Gerencia o histórico com lista encadeada
class ListaDeHistorico:
    def __init__(self):
        self.primeiro = None

    # Adiciona registro no fim
    def adicionar(self, info):
        novo_no = NoHistorico(info)
        if not self.primeiro:
            self.primeiro = novo_no
        else:
            atual = self.primeiro
            while atual.proximo:
                atual = atual.proximo
            atual.proximo = novo_no

    # Tira o último registro
    def tirar_ultimo(self):
        if not self.primeiro:
            return None
        if not self.primeiro.proximo:
            valor = self.primeiro.info
            self.primeiro = None
            return valor
        anterior = None
        atual = self.primeiro
        while atual.proximo:
            anterior = atual
            atual = atual.proximo
        valor = atual.info
        anterior.proximo = None
        return valor

    # Pega todos os registros
    def listar_todos(self):
        lista = []
        atual = self.primeiro
        while atual:
            lista.append(atual.info)
            atual = atual.proximo
        return lista

    # Busca registros com a palavra-chave
    def buscar(self, termo):
        resultados = []
        atual = self.primeiro
        while atual:
            if termo.lower() in atual.info.lower():
                resultados.append(atual.info)
            atual = atual.proximo
        return resultados

# Classe pra áreas com ocorrências e subáreas
class Area:
    def __init__(self, nome):
        self.nome = nome  # Nome da área
        self.ocorrencias = []  # Lista de ocorrências
        self.sub_areas = []  # Subáreas da área

    # Adiciona uma subárea
    def add_subarea(self, subarea):
        self.sub_areas.append(subarea)

    # Inclui uma ocorrência
    def add_ocorrencia(self, dados):
        self.ocorrencias.append(dados)

    # Remove ocorrência pelo código
    def remover_ocorrencia(self, cod):
        self.ocorrencias = [oc for oc in self.ocorrencias if oc['codigo'] != cod]
        for sub in self.sub_areas:
            sub.remover_ocorrencia(cod)

    # Lista todas as ocorrências
    def listar_ocorrencias(self):
        resultado = [(self.nome, oc) for oc in self.ocorrencias]
        for sub in self.sub_areas:
            resultado.extend(sub.listar_ocorrencias())
        return resultado

    # Conta ocorrências totais
    def total_ocorrencias(self):
        total = len(self.ocorrencias)
        for sub in self.sub_areas:
            total += sub.total_ocorrencias()
        return total

# Pilha pra ações realizadas
class PilhaAcoes:
    def __init__(self):
        self.acoes = []  # Simula uma pilha

    # Guarda uma ação
    def salvar(self, acao):
        self.acoes.append(acao)

    # Desfaz a última ação
    def desfazer(self):
        if self.acoes:
            return self.acoes.pop()
        return None

    # Lista ações em ordem inversa
    def mostrar_acoes(self):
        return list(reversed(self.acoes))

# Fila de prioridade pras ocorrências
class FilaDePrioridade:
    def __init__(self):
        self.fila = []  # Heap pra prioridades
        self.contador = 0  # Pra manter ordem estável

    # Adiciona ocorrência na fila
    def adicionar(self, area, severidade, texto, cod):
        item = {
            'codigo': cod,
            'descricao': texto,
            'severidade': severidade,
            'status': 'Aberta'
        }
        heapq.heappush(self.fila, (-severidade, self.contador, area, item))
        self.contador += 1

    # Processa a ocorrência mais grave
    def processar(self):
        if self.fila:
            return heapq.heappop(self.fila)
        return None

    # Mostra todas as ocorrências
    def mostrar_todas(self):
        lista = [(-sev, cont, area, item) for (sev, cont, area, item) in self.fila]
        return sorted(lista, key=lambda x: (-x[0], x[3]['codigo']))

    # Limpa a fila
    def resetar(self):
        self.fila.clear()
        self.contador = 0

    # Atualiza status de uma ocorrência
    def atualizar_status(self, cod, novo_status):
        for i, reg in enumerate(self.fila):
            _, _, area, item = reg
            if item['codigo'] == cod:
                item['status'] = novo_status
                self.fila[i] = (-item['severidade'], reg[1], area, item)
                heapq.heapify(self.fila)
                return True
        return False

# Remove ocorrência de todas as áreas
def remover_de_todas(areas, cod):
    for area in areas.values():
        area.remover_ocorrencia(cod)

# Gera relatório pra uma área
def gerar_relatorio(area):
    print(Fore.CYAN + f"\nOcorrências em {area.nome}:")
    total = 0
    lista = area.listar_ocorrencias()
    if not lista:
        print(Fore.YELLOW + "Sem ocorrências registradas.")
        return
    lista_ordenada = sorted(lista, key=lambda x: (-x[1]['severidade'], x[1]['codigo']))
    for nome_area, oc in lista_ordenada:
        print(f"{Fore.WHITE}[{nome_area}] Cód: {oc['codigo']} | {oc['descricao']} | Sev: {oc['severidade']} | Status: {oc['status']}")
        total += 1
    print(Fore.YELLOW + f"Total em {area.nome}: {total}")

# Mostra o menu
def exibir_menu():
    print(Fore.CYAN + """
--- Sistema de Ocorrências ---
1 - Nova ocorrência
2 - Simular registros
3 - Ver fila de ocorrências
4 - Processar ocorrência
5 - Mudar status
6 - Relatório por área
7 - Contagem por área
8 - Ver histórico
9 - Buscar no histórico
10 - Registrar ação
11 - Desfazer ação
12 - Zerar fila
13 - Exportar relatório
14 - Sair
-----------------------------
""")

# Gera código único pra ocorrência
def gerar_codigo_unico(areas):
    codigos = set()
    for area in areas.values():
        for oc in area.ocorrencias:
            codigos.add(oc['codigo'])
    while True:
        cod = random.randint(10000, 99999)
        if cod not in codigos:
            return cod

# Cadastra nova ocorrência
def cadastrar_ocorrencia(fila, areas):
    area = input("Área (Norte, Sul, Leste, Oeste): ").strip()
    if area not in areas:
        print(Fore.RED + f"Área inválida! Escolha: {', '.join(areas.keys())}")
        return
    try:
        sev = int(input("Severidade (1-10): ").strip())
        if not 1 <= sev <= 10:
            raise ValueError
    except ValueError:
        print(Fore.RED + "Severidade inválida!")
        return
    desc = input("Descrição: ").strip()
    
    cod = gerar_codigo_unico(areas)
    fila.adicionar(area, sev, desc, cod)
    areas[area].add_ocorrencia({
        'codigo': cod,
        'descricao': desc,
        'severidade': sev,
        'status': 'Aberta'
    })
    print(Fore.GREEN + f"Registrado! Código: {cod}")

# Processa ocorrência prioritária
def tratar_ocorrencia(fila, historico, acoes, areas):
    item = fila.processar()
    if item:
        _, _, area, dados = item
        cod = dados['codigo']
        desc = dados['descricao']
        registro = f"Processado em {area}: Cód {cod} - {desc}"
        historico.adicionar(registro)
        acoes.salvar(registro)
        remover_de_todas(areas, cod)
        print(Fore.GREEN + registro)
    else:
        print(Fore.RED + "Nenhuma ocorrência na fila.")

# Registra ação manual
def salvar_acao(historico, acoes):
    acao = input("Descreva a ação: ").strip()
    if acao:
        historico.adicionar(acao)
        acoes.salvar(acao)
        print(Fore.GREEN + "Ação salva.")
    else:
        print(Fore.RED + "Ação não pode ser vazia.")

# Desfaz última ação
def desfazer_acao(acoes, historico, areas):
    ultima = acoes.desfazer()
    if ultima:
        historico.tirar_ultimo()
        print(Fore.GREEN + f"Desfeito: {ultima}")
    else:
        print(Fore.RED + "Sem ações para desfazer.")

# Simula ocorrências aleatórias
def simular_dados(fila, areas, historico=None, acoes=None, qtd=10):
    descricoes = [
        "Fumaça avistada", "Incêndio rural", "Fogo perto da rodovia",
        "Sinal térmico", "Foco em reserva", "Alerta de moradores",
        "Calor extremo", "Drone detectou foco", "Chamas em mata"
    ]
    print(Fore.CYAN + f"\nGerando {qtd} ocorrências...")
    for _ in range(qtd):
        area = random.choice(list(areas.keys()))
        sev = random.randint(4, 10)
        desc = random.choice(descricoes)
        cod = gerar_codigo_unico(areas)
        fila.adicionar(area, sev, desc, cod)
        areas[area].add_ocorrencia({
            'codigo': cod,
            'descricao': desc,
            'severidade': sev,
            'status': 'Aberta'
        })
        if historico and acoes:
            registro = f"Simulação: Cód {cod} em {area} (Sev {sev}): {desc}"
            historico.adicionar(registro)
            acoes.salvar(registro)
        print(Fore.LIGHTGREEN_EX + f"[{area}] Cód: {cod} (Sev: {sev}) {desc}")
        time.sleep(0.2)
    print(Fore.GREEN + "\nSimulação finalizada.")

# Busca no histórico
def buscar_no_historico(historico):
    termo = input("Termo para busca: ").strip()
    resultados = historico.buscar(termo)
    if resultados:
        print(Fore.CYAN + "Resultados:")
        for res in resultados:
            print(f"- {res}")
    else:
        print(Fore.RED + "Nada encontrado.")

# Conta ocorrências por área
def contar_por_area(areas):
    print(Fore.CYAN + "\nOcorrências por área:")
    total_geral = 0
    for nome, area in areas.items():
        cont = area.total_ocorrencias()
        total_geral += cont
        print(Fore.YELLOW + f"{nome}: {cont} ocorrência(s)")
    print(Fore.GREEN + f"Total: {total_geral} ocorrência(s)")

# Lista fila de prioridade
def mostrar_fila(fila):
    lista = fila.mostrar_todas()
    if lista:
        print(Fore.CYAN + "\nOcorrências na fila:")
        for sev, _, area, dados in lista:
            print(f"{Fore.WHITE}[{area}] Cód: {dados['codigo']} (Sev: {sev}) {dados['descricao']} | Status: {dados['status']}")
    else:
        print(Fore.YELLOW + "Fila vazia.")

# Zera a fila
def zerar_fila(fila):
    fila.resetar()
    print(Fore.GREEN + "Fila zerada.")

# Salva relatório em arquivo
def exportar_relatorio(areas):
    nome_arq = input("Nome do arquivo (.txt): ").strip()
    try:
        with open(nome_arq, 'w', encoding='utf-8') as arq:
            for area in areas.values():
                arq.write(f"Área: {area.nome}\n")
                ocorrencias = sorted(area.ocorrencias, key=lambda o: (-o['severidade'], o['codigo']))
                for oc in ocorrencias:
                    arq.write(f" Cód: {oc['codigo']} | {oc['descricao']} | Sev: {oc['severidade']} | Status: {oc['status']}\n")
                arq.write("\n")
        print(Fore.GREEN + f"Relatório salvo em {nome_arq}")
    except Exception as e:
        print(Fore.RED + f"Erro ao salvar: {e}")

# Atualiza status de ocorrência
def mudar_status(areas, historico, acoes):
    try:
        cod = int(input("Código da ocorrência: ").strip())
    except ValueError:
        print(Fore.RED + "Código inválido!")
        return
    status = input("Novo status (Aberta, Em Atendimento, Concluída): ").strip()
    if status not in ['Aberta', 'Em Atendimento', 'Concluída']:
        print(Fore.RED + "Status inválido!")
        return
    mudou = False
    for area in areas.values():
        for oc in area.ocorrencias:
            if oc['codigo'] == cod:
                oc['status'] = status
                mudou = True
    if mudou:
        print(Fore.GREEN + f"Status do cód {cod} alterado para {status}.")
        registro = f"Status do cód {cod} mudado para {status}"
        historico.adicionar(registro)
        acoes.salvar(registro)
    else:
        print(Fore.RED + "Ocorrência não encontrada.")

# Função principal
def main():
    # Configura áreas
    areas = {
        'Norte': Area('Norte'),
        'Sul': Area('Sul'),
        'Leste': Area('Leste'),
        'Oeste': Area('Oeste'),
    }
    fila = FilaDePrioridade()
    historico = ListaDeHistorico()
    acoes = PilhaAcoes()

    # Loop do sistema
    while True:
        exibir_menu()
        opcao = input("Escolha: ").strip()
        if opcao == '1':
            cadastrar_ocorrencia(fila, areas)
        elif opcao == '2':
            simular_dados(fila, areas, historico, acoes)
        elif opcao == '3':
            mostrar_fila(fila)
        elif opcao == '4':
            tratar_ocorrencia(fila, historico, acoes, areas)
        elif opcao == '5':
            mudar_status(areas, historico, acoes)
        elif opcao == '6':
            area = input("Área do relatório: ").strip()
            if area in areas:
                gerar_relatorio(areas[area])
            else:
                print(Fore.RED + "Área não existe!")
        elif opcao == '7':
            contar_por_area(areas)
        elif opcao == '8':
            lista_acoes = acoes.mostrar_acoes()
            if lista_acoes:
                print(Fore.CYAN + "Histórico:")
                for ac in lista_acoes:
                    print(f"- {ac}")
            else:
                print(Fore.YELLOW + "Histórico vazio.")
        elif opcao == '9':
            buscar_no_historico(historico)
        elif opcao == '10':
            salvar_acao(historico, acoes)
        elif opcao == '11':
            desfazer_acao(acoes, historico, areas)
        elif opcao == '12':
            zerar_fila(fila)
        elif opcao == '13':
            exportar_relatorio(areas)
        elif opcao == '14':
            print(Fore.CYAN + "Encerrando sistema...")
            break
        else:
            print(Fore.RED + "Opção inválida!")

if __name__ == "__main__":
    main()