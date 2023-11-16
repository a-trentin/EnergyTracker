import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import re

# Função para validar o formato da data
def validar_data(data):
    padrao_data = re.compile(r'^\d{2}/\d{2}/\d{4}$')
    return bool(padrao_data.match(data))

# Função para salvar o histórico no arquivo CSV
def salvar_historico():
    data_conta = entry_data.get()
    valor_conta = entry_valor.get()

    if not validar_data(data_conta):
        messagebox.showinfo("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
        return

    try:
        # Criar o DataFrame se o arquivo CSV existir
        if os.path.exists('historico_contas.csv'):
            df = pd.read_csv('historico_contas.csv')
        else:
            df = pd.DataFrame(columns=['Data', 'Valor'])

        # Adicionar nova entrada ao DataFrame apenas se ambos os valores estiverem presentes
        if data_conta and valor_conta:
            nova_entrada = pd.DataFrame({'Data': [data_conta], 'Valor': [float(valor_conta)]})
            df = pd.concat([df, nova_entrada], ignore_index=True)

        # Salvar o DataFrame de volta ao arquivo CSV
        df.to_csv('historico_contas.csv', index=False)

        messagebox.showinfo("Sucesso", "Dados salvos com sucesso.")
    except Exception as e:
        messagebox.showinfo("Erro", f"Erro ao salvar dados: {str(e)}")

    data_conta = entry_data.get()
    valor_conta = caixa_valor.get()  # Corrigido de entry_valor para caixa_valor

    if not validar_data(data_conta):
        messagebox.showinfo("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
        return

    try:
        # Criar o DataFrame se o arquivo CSV existir
        if os.path.exists('historico_contas.csv'):
            df = pd.read_csv('historico_contas.csv')
        else:
            df = pd.DataFrame(columns=['Data', 'Valor'])

        # Adicionar nova entrada ao DataFrame
        nova_entrada = pd.DataFrame({'Data': [data_conta], 'Valor': [float(valor_conta)]})
        df = pd.concat([df, nova_entrada], ignore_index=True)

        # Salvar o DataFrame de volta ao arquivo CSV
        df.to_csv('historico_contas.csv', mode='a', header=not os.path.exists('historico_contas.csv'), index=False)

        messagebox.showinfo("Sucesso", "Dados salvos com sucesso.")
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
        df = pd.read_csv('historico_contas.csv', names=['Data', 'Valor'], header=None)

        # Verificar se o DataFrame está vazio
        if df.empty:
            messagebox.showinfo("Aviso", "Nenhum dado encontrado.")
            return

        # Tentar converter a coluna 'Data' para o formato de data
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce', format='%d/%m/%Y')

        # Filtrar linhas onde a conversão falhou (Valores incorretos ou 'Data' no cabeçalho)
        df = df.dropna(subset=['Data'])

        # Ordenar os dados por mês e ano
        df = df.sort_values(by='Data')

        # Criar a tabela no frame2
        tabela = ttk.Treeview(frame2, columns=['Data', 'Valor'], show='headings')

        # Definir cabeçalhos
        tabela.heading('Data', text='Data')
        tabela.heading('Valor', text='Valor')

        # Adicionar os dados à tabela
        for index, row in df.iterrows():
            tabela.insert("", "end", values=(row['Data'].strftime('%d/%m/%Y'), row['Valor']))

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

    # Função para aplicar as alterações
    def aplicar_alteracoes():
        # Obter os novos valores
        nova_data = nova_data_entry.get()
        novo_valor = novo_valor_entry.get()

        # Validar a data
        if not validar_data(nova_data):
            messagebox.showinfo("Erro", "Formato de data inválido. Use DD/MM/AAAA.")
            return

        # Atualizar os valores no DataFrame
        df.at[index, 'Data'] = nova_data
        df.at[index, 'Valor'] = float(novo_valor)

        # Atualizar a tabela
        tabela.item(item_selecionado, values=(nova_data, novo_valor))

        # Salvar o DataFrame atualizado de volta ao arquivo CSV
        df.to_csv('historico_contas.csv', index=False)

        # Fechar a janela de edição
        janela_edicao.destroy()

        messagebox.showinfo("Sucesso", "Item alterado com sucesso.")

    # Adicionar botão para aplicar alterações
    botao_aplicar = tk.Button(janela_edicao, text='Aplicar Alterações', command=aplicar_alteracoes)
    botao_aplicar.grid(row=2, column=0, columnspan=2)
    # Limpar a tabela
    tabela.delete(*tabela.get_children())

    # Adicionar os dados atualizados à tabela
    for index, row in df.iterrows():
        tabela.insert("", "end", values=(row['Data'].strftime('%d/%m/%Y'), row['Valor']))

# root window
root = tk.Tk()
root.iconbitmap('Images/imagem.jpeg')

# Adquirir tamanho da tela
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

width = screen_width - 650
height = screen_height - 250
root.geometry(f"{width}x{height}")

root.configure(bg="white")
root.title('Controle de Gastos Energéticos')

# Criando um notebook (Widget para manusear diferentes abas)
notebook = ttk.Notebook(root, height=screen_height, width=screen_width)
notebook.pack(pady=0, expand=False)

# Criando as abas
frame1 = ttk.Frame(notebook, width=800, height=600)
frame2 = ttk.Frame(notebook, width=800, height=600)
frame3 = ttk.Frame(notebook, width=800, height=600)
frame4 = ttk.Frame(notebook, width=800, height=600)

frame1.pack(fill='both', expand=True)  # Página Inicial
frame2.pack(fill='both', expand=True)  # Tabela de Gastos Passados
frame3.pack(fill='both', expand=True)  # Visualizar Gastos Passados
frame4.pack(fill='both', expand=True)  # Alertas Gastos Futuros

# add frames to notebook
notebook.add(frame1, text='Página Inicial')
notebook.add(frame2, text='Tabela de Gastos Passados')
notebook.add(frame3, text='Visualizar Gastos Passados')
notebook.add(frame4, text='Alertas Gastos Futuros')

# Aba Página Inicial
tk.Label(frame1, text="Página Inicial").pack(pady=20)

# Campos de entrada
tk.Label(frame1, text='Data:').pack(pady=5)
entry_data = tk.Entry(frame1, width=15)
entry_data.pack(pady=5)

tk.Label(frame1, text='Valor:').pack(pady=5)
caixa_valor = tk.Entry(frame1, width=15)
caixa_valor.pack(pady=5)

#Botão para salvar dados
# Supondo que você tenha um botão chamado "botao_salvar" na sua interface gráfica
botao_salvar = tk.Button(frame1, text="Salvar Histórico", command=salvar_historico)
botao_salvar.pack(pady=10)


# Aba Tabela de Gastos Passados
tk.Label(frame2, text="Tabela de Gastos Passados").pack(pady=20)

btn_exibir_tabela = tk.Button(frame2, text="Exibir Tabela", command=exibir_tabela)
btn_exibir_tabela.pack(pady=10)

# Aba Visualizar Gastos Passados
tk.Label(frame3, text="Visualizar Gastos Passados").pack(pady=20)

# Aba Alertas Gastos Futuros
tk.Label(frame4, text="Alertas Gastos Futuros").pack(pady=20)

root.mainloop()
