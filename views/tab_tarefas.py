# views/tab_tarefas.py
import pandas as pd
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableView, QPushButton, 
                             QHeaderView, QHBoxLayout, QDialog, QLineEdit, 
                             QComboBox, QLabel, QMessageBox)
from models import PandasModel

class DialogNovaTarefa(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("✨ Nova Tarefa")
        self.setFixedSize(300, 250)
        
        layout = QVBoxLayout(self)
        
        # Campos de entrada (Inputs)
        self.input_materia = QLineEdit()
        self.input_materia.setPlaceholderText("Ex: Cálculo I")
        
        self.input_desc = QLineEdit()
        self.input_desc.setPlaceholderText("Ex: Lista 5 - Integrais")
        
        self.input_tipo = QComboBox()
        self.input_tipo.addItems(["Lista", "Trabalho", "Prova"])
        
        self.input_data = QLineEdit()
        self.input_data.setPlaceholderText("DD/MM/AAAA")
        
        btn_salvar = QPushButton("💾 Salvar Tarefa")
        btn_salvar.clicked.connect(self.accept) # O "accept" fecha o dialog com sucesso
        
        layout.addWidget(QLabel("📚 Matéria:"))
        layout.addWidget(self.input_materia)
        layout.addWidget(QLabel("📝 Descrição:"))
        layout.addWidget(self.input_desc)
        layout.addWidget(QLabel("📌 Tipo:"))
        layout.addWidget(self.input_tipo)
        layout.addWidget(QLabel("📅 Data de Entrega:"))
        layout.addWidget(self.input_data)
        layout.addWidget(btn_salvar)

    def obter_dados(self):
        # Retorna um dicionário com os dados digitados
        return {
            'Matéria': self.input_materia.text(),
            'Descrição': self.input_desc.text(),
            'Tipo': self.input_tipo.currentText(),
            'Entrega / Data': self.input_data.text(),
            'Prioridade': 'Média', 
            'Status': 'Pendente',
            'Observações': '-',
            '⏳ Dias Restantes': '-'
        }

class TabTarefas(QWidget):
    def __init__(self):
        super().__init__()
        self.arquivo_alvo = 'estudos_faculdade.xlsx'
        self.nome_aba = '✅ Tarefas'
        self.df = None # Vai guardar o DataFrame atual
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Tabela
        self.tabela = QTableView()
        self.tabela.setAlternatingRowColors(True)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableView.SelectRows)
        self.tabela.setShowGrid(False)
        self.layout.addWidget(self.tabela)

        # Botões
        layout_botoes = QHBoxLayout()
        self.btn_atualizar = QPushButton("🔄 Atualizar")
        self.btn_atualizar.clicked.connect(self.carregar_dados)
        
        self.btn_adicionar = QPushButton("➕ Nova Tarefa")
        self.btn_adicionar.clicked.connect(self.adicionar_tarefa)
        
        layout_botoes.addWidget(self.btn_atualizar)
        layout_botoes.addWidget(self.btn_adicionar)
        self.layout.addLayout(layout_botoes)

        self.carregar_dados()

    def carregar_dados(self):
        try:
            self.df = pd.read_excel(self.arquivo_alvo, sheet_name=self.nome_aba, header=1)
            self.df.fillna("-", inplace=True)
            self.modelo = PandasModel(self.df)
            self.tabela.setModel(self.modelo)
        except Exception as e:
            print(f"Erro ao carregar: {e}")

    def adicionar_tarefa(self):
        dialog = DialogNovaTarefa()
        if dialog.exec_() == QDialog.Accepted:
            novos_dados = dialog.obter_dados()
            
            # 1. Adiciona a nova linha no DataFrame do Pandas
            self.df.loc[len(self.df)] = novos_dados
            
            # 2. Salva no Excel atualizando APENAS a aba de Tarefas
            try:
                with pd.ExcelWriter(self.arquivo_alvo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    # header=True salva os nomes das colunas. Como você tinha um título na linha 0, 
                    # talvez precisemos ajustar o índice, mas o padrão já escreve certinho.
                    self.df.to_excel(writer, sheet_name=self.nome_aba, index=False)
                
                # 3. Recarrega a visualização
                self.carregar_dados()
                QMessageBox.information(self, "Sucesso", "Tarefa adicionada com sucesso! ✨")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar: {e}\n\nFeche a planilha no Excel antes de salvar!")
