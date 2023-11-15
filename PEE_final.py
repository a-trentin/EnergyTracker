import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import calendar as cal
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

historico_gastos = []

data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

import calendar


# Carregar dados existentes do arquivo CSV (se existir)
historico_csv_path = "historico_contas.csv"

try:
    with open(historico_csv_path, mode='r') as file:
        reader = csv.reader(file)
        historico_gastos = [tuple(row) for row in reader]
except FileNotFoundError:
    historico_gastos = [] 
    
def calcular_gastos():
    try:
        consumo = float(entry_consumo.get())
        tarifa = float(entry_tarifa.get())
        mes_nome = mes_var.get()
        mes_numero = meses.index(mes_nome) + 1
        ano = ano_var.get()
        ultimo_dia_mes = cal.monthrange(int(ano), mes_numero)[1]
        data_atual_global = datetime(int(ano), mes_numero, ultimo_dia_mes, 0, 0, 0)
        mes_ano = f"{ano}-{mes_numero:02d}"
        print(f"Data Atual: {data_atual_global.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Mês/Ano: {mes_ano}")
        gastos = consumo * tarifa
        historico_gastos.append((data_atual_global.strftime('%d/%m/%Y %H:%M:%S'), mes_ano, gastos))
        with open(historico_csv_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([data_atual_global.strftime('%d/%m/%Y %H:%M:%S'), mes_ano, gastos])
        resultado.config(text=f"Gastos: R$ {gastos:.2f} para {mes_ano}")
        entry_consumo.delete(0, tk.END)
        entry_tarifa.delete(0, tk.END)
        atualizar_tabela()  # Updated to reflect changes in the table
    except ValueError as e:
        handle_error("Digite valores válidos.")

def abrir_janela_edicao(idx):
    janela_edicao = tk.Toplevel(janela)
    janela_edicao.title("Editar Gastos")

    # Adicione widgets para edição, como Entry, Combobox, etc.
    # Certifique-se de preencher os widgets com os valores atuais do item no índice idx

    # Adicione um botão para salvar as alterações
    btn_salvar = tk.Button(janela_edicao, text="Salvar", command=lambda: salvar_edicao(idx))
    btn_salvar.pack()

def salvar_edicao(idx):
    # Esta função deve ser chamada ao clicar no botão "Salvar" na janela de edição
    # idx é o índice do item na lista historico_gastos
    # Implemente conforme necessário para salvar as alterações
    # Certifique-se de atualizar o gráfico e a tabela após salvar as alterações

def abrir_janela_confirmacao_exclusao(idx):
    # Esta função será chamada ao clicar no botão de exclusão
    # idx é o índice do item na lista historico_gastos
    resposta = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir este item?")
    if resposta:
        excluir_item(idx)

def excluir_item(idx):
    # Esta função exclui um item do histórico pelo índice idx
    del historico_gastos[idx]
    atualizar_grafico()
    atualizar_tabela()

def atualizar_tabela():
    # Atualiza a tabela de histórico na interface
    # (Esta função deve ser chamada sempre que o histórico é modificado)
    # Implemente conforme necessário para sua interface gráfica

def abrir_segunda_janela():
    segunda_janela = tk.Toplevel(janela)
    segunda_janela.title("Acompanhamento de Gastos")

    # Configurar tabela para exibir histórico
    tree = ttk.Treeview(segunda_janela)
    tree["columns"] = ("Data", "Mês/Ano", "Gastos", "Editar", "Excluir")

    tree.column("#0", width=0, stretch=tk.NO)  # Ocultar coluna vazia
    tree.column("Data", anchor=tk.W, width=120)
    tree.column("Mês/Ano", anchor=tk.W, width=80)
    tree.column("Gastos", anchor=tk.W, width=80)
    tree.column("Editar", anchor=tk.W, width=50)
    tree.column("Excluir", anchor=tk.W, width=60)

    tree.heading("#0", text="", anchor=tk.W)
    tree.heading("Data", text="Data", anchor=tk.W)
    tree.heading("Mês/Ano", text="Mês/Ano", anchor=tk.W)
    tree.heading("Gastos", text="Gastos", anchor=tk.W)
    tree.heading("Editar", text="Editar", anchor=tk.W)
    tree.heading("Excluir", text="Excluir", anchor=tk.W)

    for i, (data, mes_ano, gastos) in enumerate(historico_gastos):
        tree.insert("", i, values=(data, mes_ano, f"R$ {gastos:.2f}"), tags=(i,))

        # Adicionar botões de edição e exclusão
        editar_button = tk.Button(segunda_janela, text="Editar", command=lambda i=i: abrir_janela_edicao(i))
        excluir_button = tk.Button(segunda_janela, text="Excluir", command=lambda i=i: abrir_janela_confirmacao_exclusao(i))

        tree.window_create(tree.identify_region(i, 4), window=editar_button)
        tree.window_create(tree.identify_region(i, 5), window=excluir_button)

    tree.pack()

def calcular_instalacao():
    try:
        # Obter valores dos widgets de entrada
        custo_instalacao = float(entry_custo_instalacao.get())
        tempo_recuperacao = float(entry_tempo_recuperacao.get())

        # Calcular custo mensal
        gasto_mensal = sum([gasto for _, _, gasto in historico_gastos])
        custo_mensal = gasto_mensal * 12  # Supondo gasto médio mensal multiplicado por 12 meses

        # Calcular economia anual
        economia_anual = custo_mensal * tempo_recuperacao

        # Calcular tempo total até a recuperação do investimento
        tempo_total = tempo_recuperacao * 12  # Convertendo para meses

        # Verificar se o tempo total é maior que o tempo de vida útil da instalação
        vida_util_instalacao = 25  # Supondo uma vida útil de 25 anos para a instalação
        if tempo_total > vida_util_instalacao * 12:
            messagebox.showwarning("Aviso", "O tempo total é maior que a vida útil da instalação.")

        # Exibir resultados
        resultado_instalacao.config(text=f"Custo Mensal Atual: R$ {custo_mensal:.2f}\n"
                                         f"Economia Anual: R$ {economia_anual:.2f}\n"
                                         f"Tempo Total até Recuperação do Investimento: {tempo_total:.2f} meses")

    except ValueError as e:
        print(f"Erro: {e}")
        resultado_instalacao.config(text="Digite valores válidos.")
        messagebox.showerror("Erro", "Digite valores válidos.")

def abrir_terceira_janela():
    if not historico_gastos:
        messagebox.showinfo("Aviso", "Não há dados para exibir na projeção.")
        return

    terceira_janela = tk.Toplevel(janela)
    terceira_janela.title("Projeção de Gastos Mensais")

    # Obter os dados para a projeção
    meses_anos, gastos = zip(*[(mes_ano, gasto) for _, mes_ano, gasto in historico_gastos])

    # Calcular projeção linear com +/- 5% do gasto dos meses anteriores
    gastos_projetados = [gastos[0]]  # O primeiro valor não é projetado, é o valor real
    for i in range(1, len(gastos)):
        gasto_proj = gastos[i - 1] * np.random.uniform(0.95, 1.05)
        gastos_projetados.append(gasto_proj)

    # Adicionar gastos projetados ao histórico
    mes_ano_proj = f"{ano_var.get()}-{mes_var.get()}"
    historico_gastos.append((datetime.now().strftime("%d/%m/%Y %H:%M:%S"), mes_ano_proj, gastos_projetados[-1]))

    # Configurar gráfico para exibir gastos e projeção
    meses_numeros = [int(m.split('-')[1]) if "-" in m else datetime.strptime(m, "%d/%m/%Y %H:%M:%S").month for m in meses_anos]
    plt.plot(np.array(meses_numeros), gastos, marker='o', linestyle='-', color='b', label='Gastos Reais')
    plt.plot(np.array(meses_numeros)[1:], gastos_projetados[1:], marker='x', linestyle='--', color='r', label='Projeção')
    plt.title('Projeção de Gastos Mensais')
    plt.xlabel('Mês/Ano')
    plt.ylabel('Gastos (R$)')
    plt.xticks(range(1, 13), calendar.month_abbr[1:])  # Usar abreviações de meses para rótulos do eixo x
    plt.legend()

    # Atualizar gráfico na interface
    canvas = FigureCanvasTkAgg(plt.gcf(), master=terceira_janela)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()

    # Exibir a projeção
    resultado.config(text=f"Gastos Projetados: R$ {gastos_projetados[-1]:.2f} para {mes_ano_proj}")

def atualizar_grafico():
    # Criar gráfico de evolução mensal
    meses_anos, gastos = zip(*[(mes_ano, gasto) for _, mes_ano, gasto in historico_gastos])

    # Converter todas as datas para objetos datetime
    datas = [datetime.strptime(mes_ano, "%Y-%m") if "-" in mes_ano else datetime.strptime(mes_ano, "%d/%m/%Y %H:%M:%S") for mes_ano in meses_anos]

    # Ordenar os dados pela ordem dos meses
    dados_ordenados = sorted(zip(datas, meses_anos, gastos), key=lambda x: x[0])

    # Extrair os dados ordenados
    datas, meses_anos, gastos = zip(*dados_ordenados)

    # Plotar o gráfico ordenado
    plt.plot(meses_anos, gastos, marker='o', linestyle='-', color='b')
    plt.title('Evolução Mensal dos Gastos')
    plt.xlabel('Mês/Ano')
    plt.ylabel('Gastos (R$)')
    plt.xticks(rotation=45, ha='right')  # Rotacionar rótulos do eixo x para melhor visualização

    # Adicionar rótulos de data aos pontos no gráfico
    for i, (_, mes_ano, gasto) in enumerate(dados_ordenados):
        plt.text(mes_ano, gasto, f'  {gasto:.2f}', rotation=45, ha='right', va='bottom')

    # Atualizar gráfico na interface
    canvas.draw()

def adicionar_gastos_mensais():
    try:
        # Obter o mês e ano selecionados nos menus suspensos
        mes_nome = mes_var.get()

        # Verificar se o mês está no formato numérico ou nome completo
        if mes_nome.isdigit():
            mes_numero = int(mes_nome)
        else:
            mes_numero = meses.index(mes_nome) + 1  # +1 porque os índices começam em 1 no calendário

        ano = ano_var.get()

        # Obter o último dia do mês
        ultimo_dia_mes = cal.monthrange(int(ano), mes_numero)[1]

        # Formatar a data no formato desejado (brasileiro)
        data_atual_global = datetime(int(ano), mes_numero, ultimo_dia_mes, 0, 0, 0)
        mes_ano = f"{ano}-{mes_numero:02d}"

        print(f"Data Atual: {data_atual_global.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Mês/Ano: {mes_ano}")

        # Verificar se já existem gastos para esse mês
        for data, mes, gasto in historico_gastos:
            if mes == mes_ano:
                # Já existem gastos para esse mês
                resposta = messagebox.askyesno("Atualizar Gastos", f"Já existem gastos registrados para {mes_ano}. Deseja atualizar o valor?")
                if not resposta:
                    return
                else:
                    # Atualizar o valor existente
                    historico_gastos.remove((data, mes, gasto))
                    break

        # Calcular gastos energéticos
        consumo = float(entry_consumo.get())
        tarifa = float(entry_tarifa.get())
        gastos = consumo * tarifa

        # Adicionar gastos, data e mês/ano ao histórico
        historico_gastos.append((data_atual_global.strftime('%d/%m/%Y %H:%M:%S'), mes_ano, gastos))

        # Atualizar rótulo de resultado
        resultado.config(text=f"Gastos: R$ {gastos:.2f} para {mes_ano}")

        # Limpar campos de entrada
        entry_consumo.delete(0, tk.END)
        entry_tarifa.delete(0, tk.END)

        # Atualizar o gráfico
        atualizar_grafico()

        # Exibir mensagem de confirmação
        messagebox.showinfo("Sucesso", f"Gastos para {mes_ano} adicionados com sucesso!")

    except ValueError as e:
        print(f"Erro: {e}")
        messagebox.showerror("Erro", "Digite valores válidos.")
    except Exception as e:
        print(f"Erro: {e}")
        messagebox.showerror("Erro", "Ocorreu um erro. Verifique os dados inseridos.")

def handle_error(message):
    print(f"Erro: {message}")
    messagebox.showerror("Erro", message)

# Criar a janela principal
janela = tk.Tk()
janela.title("Controle de Gastos Energéticos")
resultado = tk.Label(janela, text="")
resultado.pack()

# Criar widgets
tk.Label(janela, text="Consumo (kWh):").pack()
entry_consumo = tk.Entry(janela)
entry_consumo.pack()

tk.Label(janela, text="Tarifa (R$/kWh):").pack()
entry_tarifa = tk.Entry(janela)
entry_tarifa.pack()

# Adicionar menus suspensos para seleção de mês e ano
frame_data = tk.Frame(janela)
frame_data.pack()

tk.Label(frame_data, text="Selecione o Mês:").pack(side=tk.LEFT)
mes_var = tk.StringVar(janela)
meses = [cal.month_name[i] for i in range(1, 13)]
mes_menu = ttk.Combobox(frame_data, textvariable=mes_var, values=meses)
mes_menu.pack(side=tk.LEFT)
mes_menu.set(cal.month_name[datetime.now().month])  # Definir o mês atual como padrão

tk.Label(frame_data, text="   Selecione o Ano:").pack(side=tk.LEFT)  # Adicionei alguns espaços para separar os menus
ano_var = tk.StringVar(janela)
anos = [str(i) for i in range(datetime.now().year, datetime.now().year - 10, -1)]  # Anos recentes
ano_menu = ttk.Combobox(frame_data, textvariable=ano_var, values=anos)
ano_menu.pack(side=tk.LEFT)
ano_menu.set(str(datetime.now().year))  # Definir o ano atual como padrão

# Botão para calcular gastos
btn_calcular = tk.Button(janela, text="Calcular Gastos", command=calcular_gastos)
btn_calcular.pack()

# Botão para abrir a segunda janela
btn_abrir_segunda_janela = tk.Button(janela, text="Ver Gastos Mensais", command=abrir_segunda_janela)
btn_abrir_segunda_janela.pack()

# Configurações adicionais para o gráfico
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=janela)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack()

# Botão para abrir a terceira janela
btn_abrir_terceira_janela = tk.Button(janela, text="Projeção de Gastos Mensais", command=abrir_terceira_janela)
btn_abrir_terceira_janela.pack()

# Adicionar botão para abrir a quarta janela
btn_adicionar_gastos = tk.Button(janela, text="Adicionar Gastos Mensais", command=adicionar_gastos_mensais)
btn_adicionar_gastos.pack()

# Adicionar uma nova janela para o cálculo de instalação
frame_instalacao = tk.Frame(janela)
frame_instalacao.pack()

tk.Label(frame_instalacao, text="Custo de Instalação (R$):").pack(side=tk.LEFT)
entry_custo_instalacao = tk.Entry(frame_instalacao)
entry_custo_instalacao.pack(side=tk.LEFT)

tk.Label(frame_instalacao, text="Tempo até Recuperar Investimento (anos):").pack(side=tk.LEFT)
entry_tempo_recuperacao = tk.Entry(frame_instalacao)
entry_tempo_recuperacao.pack(side=tk.LEFT)

btn_calcular_instalacao = tk.Button(janela, text="Calcular Instalação", command=calcular_instalacao)
btn_calcular_instalacao.pack()

resultado_instalacao = tk.Label(janela, text="")
resultado_instalacao.pack()

# Iniciar o loop de eventos
janela.mainloop()