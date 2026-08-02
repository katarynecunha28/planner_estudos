# views/cronograma.py
import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView, QPushButton, QHeaderView
from models import PandasModel

class TabCronograma(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Configurando a Tabela
        self.tabela = QTableView()
        self.tabela.setAlternatingRowColors(True)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableView.SelectRows)
        self.tabela.setShowGrid(False)
        self.layout.addWidget(self.tabela)

        # Botão de Ação
        self.btn_atualizar = QPushButton("🔄 Atualizar Cronograma")
        self.btn_atualizar.clicked.connect(self.carregar_dados)
        self.layout.addWidget(self.btn_atualizar)

        self.carregar_dados()

    def carregar_dados(self):
        try:
            # header=1 para pular o título da tabela no Excel
            df = pd.read_excel('estudos_faculdade.xlsx', sheet_name='📅 Cronograma', header=1)
            
            # Renomeia as colunas sem nome (que guardam os blocos de horário) para "Horário"
            if df.columns[0].startswith('Unnamed'):
                df.rename(columns={df.columns[0]: 'Bloco'}, inplace=True)
            if df.columns[1].startswith('Unnamed'):
                df.rename(columns={df.columns[1]: 'Horário'}, inplace=True)

            df.fillna("-", inplace=True)
            
            modelo = PandasModel(df)
            self.tabela.setModel(modelo)
        except Exception as e:
            print(f"Erro ao carregar o Cronograma: {e}")
