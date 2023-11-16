import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ttkbootstrap import Style

# Função para validar o formato da data
def validar_data(data):
    padrao_data = re.compile(r'^\d{2}/\d{2}/\d{4}$')
    return bool(padrao_data.match(data))

# Função para visualizar os gastos passados em um gráfico
def visualizar_gastos_passados():
    # Verificar se o arquivo CSV existe
    if not os.path.exists('historico_contas.csv'):
        messagebox.showinfo("Aviso", "Nenhum dado encontrado.")
        return

    try:
        # Carregar os dados do arquivo CSV usando Pandas
        df = pd.read_csv('historico_contas.csv')

        # Verificar se o DataFrame está vazio
        if df.empty:
            messagebox.showinfo("Aviso", "Nenhum dado encontrado.")
            return

        # Ajustar a leitura da coluna 'Data' para considerar o formato 'DD/MM/YYYY'
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce', format='%d/%m/%Y')

        # Filtrar linhas onde a conversão falhou (Valores incorretos ou 'Data' no cabeçalho)
        df = df.dropna(subset=['Data'])

        # Ordenar os dados por data
        df = df.sort_values(by='Data')

        # Agrupar por mês e ano
        df_agrupado = df.groupby(df['Data'].dt.to_period("M")).agg({'Valor': 'sum', 'kWh': 'sum'}).reset_index()

        # Criar gráfico
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Plotar Valor
        ax1.plot(df_agrupado['Data'].astype(str), df_agrupado['Valor'], marker='o', color='b', label='Valor')
        ax1.set_xlabel('Mês e Ano')
        ax1.set_ylabel('Valor Total', color='b')
        ax1.tick_params('y', colors='b')

        # Criar segundo eixo y para kWh
        ax2 = ax1.twinx()
        ax2.plot(df_agrupado['Data'].astype(str), df_agrupado['kWh'], marker='s', color='r', label='kWh')
        ax2.set_ylabel('kWh Total', color='r')
        ax2.tick_params('y', colors='r')

        # Configurar rótulos e título
        ax1.set_title('Gastos Mensais')

        # Ajustar rótulos do eixo x para melhor legibilidade
        ax1.set_xticks(df_agrupado['Data'].astype(str))
        ax1.set_xticklabels(df_agrupado['Data'].astype(str), rotation=45, ha='right')

        # Adicionar grade
        ax1.grid(True)

        # Adicionar legenda
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        # Exibir gráfico
        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showinfo("Erro", f"Erro ao visualizar gastos passados: {str(e)}")

# Função pra salvar 
def salvar_historico():
    data_conta = entry_data.get()
    valor_conta = caixa_valor.get()
    kWh_conta = caixa_kWh.get()

    if not validar_data(data_conta):
        messagebox.showinfo("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
        return

    try:
        # Criar o DataFrame se o arquivo CSV existir
        if os.path.exists('historico_contas.csv'):
            df = pd.read_csv('historico_contas.csv')
        else:
            df = pd.DataFrame(columns=['Data', 'Valor', 'kWh'])

        # Adicionar nova entrada ao DataFrame apenas se todos os valores estiverem presentes
        if data_conta and valor_conta and kWh_conta:
            nova_entrada = pd.DataFrame({'Data': [pd.to_datetime(data_conta, format='%d/%m/%Y', errors='coerce').strftime('%d/%m/%Y')],
                                          'Valor': [float(valor_conta)],
                                          'kWh': [float(kWh_conta)]})
            df = pd.concat([df, nova_entrada], ignore_index=True)

        # Salvar o DataFrame de volta ao arquivo CSV
        df.to_csv('historico_contas.csv', index=False)

        messagebox.showinfo("Sucesso", "Dados salvos com sucesso.")

        # Atualizar a tabela
        exibir_tabela()

        # Atualizar o gráfico
        visualizar_gastos_passados()

    except Exception as e:
        messagebox.showinfo("Erro", f"Erro ao salvar dados: {str(e)}")

# Função para exibir a tabela
def exibir_tabela():
    # Verificar se o arquivo CSV existe
    if not os.path.exists('historico_contas.csv'):
        messagebox.showinfo("Aviso", "Nenhum dado encontrado.")
        return

    try:
        # Carregar os dados do arquivo CSV usando Pandas
        df = pd.read_csv('historico_contas.csv')

        # Verificar se o DataFrame está vazio
        if df.empty:
            messagebox.showinfo("Aviso", "Nenhum dado encontrado.")
            return

        # Ajustar a leitura da coluna 'Data' para considerar o formato 'DD/MM/YYYY'
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce', format='%d/%m/%Y')

        # Filtrar linhas onde a conversão falhou (Valores incorretos ou 'Data' no cabeçalho)
        df = df.dropna(subset=['Data'])

        # Ordenar os dados por data
        df = df.sort_values(by='Data')

        # Criar a tabela no frame2
        tabela = ttk.Treeview(frame2, columns=['Data', 'Valor', 'kWh'], show='headings')

        # Definir cabeçalhos
        tabela.heading('Data', text='Data')
        tabela.heading('Valor', text='Valor')
        tabela.heading('kWh', text='kWh')

        # Adicionar os dados à tabela
        for index, row in df.iterrows():
            tabela.insert("", "end", values=(row['Data'].strftime('%d/%m/%Y'), row['Valor'], row['kWh']))

        # Adicionar a tabela ao frame
        tabela.pack(padx=10, pady=10)

        # Adicionar botões para excluir e alterar dados
        botao_excluir = tk.Button(frame2, text='Excluir Selecionado', command=lambda: excluir_dado(tabela, df))
        botao_excluir.pack(pady=10)

        botao_alterar = tk.Button(frame2, text='Alterar Selecionado', command=lambda: alterar_dado(tabela, df))
        botao_alterar.pack(pady=10)

    except Exception as e:
        messagebox.showinfo("Erro", f"Erro ao exibir tabela: {str(e)}")

# Função para excluir um dado da tabela
def excluir_dado(tabela, df):
    # Obter item selecionado na tabela
    item_selecionado = tabela.selection()
    if not item_selecionado:
        messagebox.showinfo("Aviso", "Nenhum item selecionado.")
        return

    # Obter índice do item selecionado
    index = tabela.index(item_selecionado)

    # Remover a linha correspondente no DataFrame
    df = df.drop(index, axis=0)

    # Salvar o DataFrame atualizado de volta ao arquivo CSV
    df.to_csv('historico_contas.csv', index=False)

    # Remover item da tabela
    tabela.delete(item_selecionado)

    messagebox.showinfo("Sucesso", "Item excluído com sucesso.")

# Função para alterar um dado na tabela
def alterar_dado(tabela, df):
    # Obter item selecionado na tabela
    item_selecionado = tabela.selection()
    if not item_selecionado:
        messagebox.showinfo("Aviso", "Nenhum item selecionado.")
        return

    # Obter índice do item selecionado
    index = tabela.index(item_selecionado)

    # Abrir janela para edição
    janela_edicao = tk.Toplevel(root)

    # Adicionar campos para edição
    tk.Label(janela_edicao, text="Nova Data:").grid(row=0, column=0)
    nova_data_entry = tk.Entry(janela_edicao)
    nova_data_entry.grid(row=0, column=1)

    tk.Label(janela_edicao, text="Novo Valor:").grid(row=1, column=0)
    novo_valor_entry = tk.Entry(janela_edicao)
    novo_valor_entry.grid(row=1, column=1)

    # Preencher os campos de edição com os valores atuais
    nova_data_entry.insert(0, df.at[index, 'Data'].strftime('%d/%m/%Y'))
    novo_valor_entry.insert(0, df.at[index, 'Valor'])

    # Função para aplicar as alterações
    def aplicar_alteracoes():
        # Obter os novos valores
        nova_data = nova_data_entry.get()
        novo_valor = novo_valor_entry.get()

        # Validar a data
        if not validar_data(nova_data):
            messagebox.showinfo("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
            return

        # Converter a nova data para datetime
        nova_data = pd.to_datetime(nova_data, format='%d/%m/%Y', errors='coerce')

        # Verificar se a conversão falhou
        if pd.isnull(nova_data):
            messagebox.showinfo("Erro", "Data inválida.")
            return

        # Atualizar os valores no DataFrame
        df.at[index, 'Data'] = nova_data
        df.at[index, 'Valor'] = float(novo_valor)

        # Atualizar a tabela
        tabela.item(item_selecionado, values=(nova_data.strftime('%d/%m/%Y'), novo_valor))

        # Salvar o DataFrame atualizado de volta ao arquivo CSV
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')  
        df.to_csv('historico_contas.csv', index=False)

        # Fechar a janela de edição
        janela_edicao.destroy()

        messagebox.showinfo("Sucesso", "Item alterado com sucesso.")

        # Adicionar botão para visualizar o gráfico após alterar o dado
        botao_visualizar_grafico = tk.Button(frame2, text='Visualizar Gastos Passados', command=visualizar_gastos_passados)
        botao_visualizar_grafico.pack(pady=10)

# Função para calcular a autonomia de painéis solares e o retorno financeiro
def calcular_autonomia_paineis_solares():
    try:
        # Obter dados de consumo e custo da energia elétrica
        consumo_mensal = float(entry_consumo.get())
        custo_kwh = float(entry_custo_kwh.get())

        # Obter dados de geração dos painéis solares
        producao_mensal_por_painel = float(entry_producao_painel.get())
        custo_painel = float(entry_custo_painel.get())

        # Calcular a quantidade de painéis solares necessários
        paineis_necessarios = consumo_mensal / producao_mensal_por_painel

        # Calcular o retorno financeiro em anos
        retorno_financeiro_anos = custo_painel * paineis_necessarios / (consumo_mensal * custo_kwh)

        messagebox.showinfo("Resultado", f"São necessários {round(paineis_necessarios, 2)} painéis solares para suprir o consumo. \n\n"
                                         f"O retorno financeiro estimado é em aproximadamente {round(retorno_financeiro_anos, 2)} anos.")
    except Exception as e:
        messagebox.showinfo("Erro", f"Erro ao calcular autonomia de painéis solares: {str(e)}")

# Criar uma instância do ttkbootstrap Style
style = Style()

# Criar a janela principal
root = style.master
style = Style(theme='superhero')

# Adquirir tamanho da tela
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

width = screen_width 
height = screen_height 
root.geometry(f"{width}x{height}")

root.title('Controle de Gastos Energéticos')

# Criando um notebook (Widget para manusear diferentes abas)
notebook = ttk.Notebook(root, height=screen_height, width=screen_width)
notebook.pack(pady=0, expand=False)

# Criando as abas
frame1 = ttk.Frame(notebook, width=width, height=height)
frame2 = ttk.Frame(notebook, width=width, height=height)
frame3 = ttk.Frame(notebook, width=width, height=height)
frame4 = ttk.Frame(notebook, width=width, height=height)

frame1.pack(fill='both', expand=True)  # Página Inicial
frame2.pack(fill='both', expand=True)  # Tabela de Gastos Passados
frame3.pack(fill='both', expand=True)  # Visualizar Gastos Passados
frame4.pack(fill='both', expand=True)  # Area Verde

# add frames to notebook
notebook.add(frame1, text='Página Inicial')
notebook.add(frame2, text='Tabela de Gastos Passados')
notebook.add(frame3, text='Visualizar Gastos Passados')
notebook.add(frame4, text='Area Verde')

# Adicione imagens às abas
img1 = tk.PhotoImage(file="Images/casa-com-certificado-energetico.png")
img2 = tk.PhotoImage(file="Images/5415790 (Telefone).png")
img3 = tk.PhotoImage(file="Images/5415790 (Telefone).png")
img4 = tk.PhotoImage(file="Images/5415790 (Telefone).png")

# Aba Página Inicial
label1 = tk.Label(frame1, image=img1, compound="top", text="Página Inicial").pack(pady=20)

# Campos de entrada
tk.Label(frame1, text='Data:').pack(pady=5)
entry_data = tk.Entry(frame1, width=15)
entry_data.pack(pady=5)

tk.Label(frame1, text='Valor:').pack(pady=5)
caixa_valor = tk.Entry(frame1, width=15)
caixa_valor.pack(pady=5)

tk.Label(frame1, text='kWh:').pack(pady=5)
caixa_kWh = tk.Entry(frame1, width=15)  # Certifique-se de criar a variável caixa_kWh
caixa_kWh.pack(pady=5)

# Botão para salvar dados
botao_salvar = tk.Button(frame1, text="Salvar Conta", command=salvar_historico)
botao_salvar.pack(pady=10)

# Aba Tabela de Gastos Passados
tk.Label(frame2, image=img2, compound="top", text="Tabela de Gastos Passados").pack(pady=20)

btn_exibir_tabela = tk.Button(frame2, text="Exibir Tabela", command=exibir_tabela)
btn_exibir_tabela.pack(pady=10)

# Aba Visualizar Gastos Passados
tk.Label(frame3, text="Visualizar Gastos Passados").pack(pady=20)

# Adicionar botão para visualizar o gráfico
btn_visualizar_grafico = tk.Button(frame3, text="Visualizar Gastos Passados", command=visualizar_gastos_passados)
btn_visualizar_grafico.pack(pady=10)

# Aba Area Verde
tk.Label(frame4, image=img4, compound="top", text="Area Verde").pack(pady=20)

# Adicionar widgets para entrada de dados
tk.Label(frame4, text="Consumo Mensal (kWh):").pack(pady=5)
entry_consumo = tk.Entry(frame4, width=15)
entry_consumo.pack(pady=5)

tk.Label(frame4, text="Custo por kWh (R$):").pack(pady=5)
entry_custo_kwh = tk.Entry(frame4, width=15)
entry_custo_kwh.pack(pady=5)

tk.Label(frame4, text="Produção Mensal por Painel (kWh):").pack(pady=5)
entry_producao_painel = tk.Entry(frame4, width=15)
entry_producao_painel.pack(pady=5)

tk.Label(frame4, text="Custo por Painel Solar (R$):").pack(pady=5)
entry_custo_painel = tk.Entry(frame4, width=15)
entry_custo_painel.pack(pady=5)

# Botão para calcular autonomia de painéis solares
botao_calcular_autonomia = tk.Button(frame4, text='Calcular Autonomia', command=calcular_autonomia_paineis_solares)
botao_calcular_autonomia.pack(padx=10, pady=10)

root.mainloop()
