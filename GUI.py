import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import calendar as cal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime

historico_gastos = []
data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")


# ...

def calcular_gastos():
    try:
        # Obter valores dos widgets de entrada
        consumo = float(entry_consumo.get())
        tarifa = float(entry_tarifa.get())

        # Obter o mês e ano selecionados nos menus suspensos
        mes_nome = mes_var.get()
        mes_numero = meses.index(mes_nome) + 1  # +1 porque os índices começam em 1 no calendário
        ano = ano_var.get()

        # Obter o último dia do mês
        ultimo_dia_mes = cal.monthrange(int(ano), mes_numero)[1]

        # Formatar a data no formato desejado (brasileiro)
        data_atual_global = datetime(int(ano), mes_numero, ultimo_dia_mes, 0, 0, 0)
        mes_ano = f"{ano}-{mes_numero:02d}"

        print(f"Data Atual: {data_atual_global.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Mês/Ano: {mes_ano}")

        # Calcular gastos energéticos
        gastos = consumo * tarifa

        print(f"Gastos Calculados: {gastos}")

        # Adicionar gastos, data e mês/ano ao histórico
        historico_gastos.append((data_atual_global.strftime('%d/%m/%Y %H:%M:%S'), mes_ano, gastos))

        # Atualizar rótulo de resultado
        resultado.config(text=f"Gastos: R$ {gastos:.2f} para {mes_ano}")

        # Limpar campos de entrada
        entry_consumo.delete(0, tk.END)
        entry_tarifa.delete(0, tk.END)

        # Atualizar o gráfico
        atualizar_grafico()

    except ValueError as e:
        print(f"Erro: {e}")
        resultado.config(text="Digite valores válidos.")
        messagebox.showerror("Erro", "Digite valores válidos.")


def abrir_segunda_janela():
    segunda_janela = tk.Toplevel(janela)
    segunda_janela.title("Acompanhamento de Gastos")

    # Configurar gráfico
    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=segunda_janela)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()

    # Atualizar o gráfico na nova janela
    atualizar_grafico()

    # Configurar gráfico na interface
    canvas.draw()

import calendar

# ...

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

# ...

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
    for i, (_, mes_ano, gasto) in enumerate(historico_gastos):
        plt.text(mes_ano, gasto, f'  {gasto:.2f}', rotation=45, ha='right', va='bottom')

    # Atualizar gráfico na interface
    canvas.draw()

# Criar a janela principal
janela = tk.Tk()
janela.title("Controle de Gastos Energéticos")

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

btn_calcular = tk.Button(janela, text="Calcular", command=calcular_gastos)
btn_calcular.pack()

resultado = tk.Label(janela, text="")
resultado.pack()


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

# Iniciar o loop de eventos
janela.mainloop()