# views/progresso.py

import pandas as pd

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView, QPushButton, QHeaderView

from models import PandasModel

class TabProgresso(QWidget):

    def __init__(self):

        super().__init__()

        # Lembre-se de checar se o nome do arquivo está igual ao que você está usando agora

        self.arquivo_alvo = 'Planner_Estudos_Faculdade.xlsx'

        # SUBSTITUA AQUI pelo nome exato que está na aba do seu Excel (ex: '📊 Progresso')

        self.nome_aba = '📊 Progresso Mensal'

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

        self.btn_atualizar = QPushButton("🔄 Atualizar Progresso")

        self.btn_atualizar.clicked.connect(self.carregar_dados)

        self.layout.addWidget(self.btn_atualizar)

        self.carregar_dados()

    def carregar_dados(self):

        try:

            # 1. Lê o Excel e cria o self.df
            self.df = pd.read_excel(self.arquivo_alvo, sheet_name=self.nome_aba, header=2)

            # 2. A linha de limpeza das colunas invisíveis fica AQUI!
            self.df = self.df.loc[:, ~self.df.columns.str.contains('^Unnamed')]

            # 3. Preenche vazios com 0
            self.df.fillna(0, inplace=True)

            self.modelo = PandasModel(self.df)

            self.tabela.setModel(self.modelo)
        except Exception as e:

            print(f"Erro ao carregar o Progresso: {e}") 

