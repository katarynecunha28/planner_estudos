# views/grade.py
import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView, QPushButton, QHeaderView
from models import PandasModel

class TabGrade(QWidget):
    def __init__(self):
        super().__init__()
        # Aponta para o seu arquivo Excel que tem a grade completa
        self.arquivo_alvo = 'estudos_faculdade.xlsx' 
        self.nome_aba = '🎓 Grade Curricular'
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Configurando a Tabela para apenas visualização
        self.tabela = QTableView()
        self.tabela.setAlternatingRowColors(True)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableView.SelectRows)
        self.tabela.setShowGrid(False)
        
        # Como a grade não muda, podemos travar a edição direto na tabela
        self.tabela.setEditTriggers(QTableView.NoEditTriggers) 
        
        self.layout.addWidget(self.tabela)

        # Botão apenas para recarregar caso você altere o Status lá no Excel
        self.btn_atualizar = QPushButton("🔄 Atualizar Status da Grade")
        self.btn_atualizar.clicked.connect(self.carregar_dados)
        self.layout.addWidget(self.btn_atualizar)

        # Carrega os dados automaticamente ao abrir a aba
        self.carregar_dados()

    def carregar_dados(self):
        try:
            # Lendo a aba da Grade. 
            # Dica: Verifique se no seu Excel o cabeçalho (Período, Código, etc) está na linha 1 ou 2.
            # Se a linha 1 tiver o título roxo e a linha 2 for o cabeçalho, use header=1.
            self.df = pd.read_excel(self.arquivo_alvo, sheet_name=self.nome_aba, header=2)
            
            # Preenche espaços vazios com um tracinho
            self.df.fillna("-", inplace=True)
            
            # Salva o modelo no 'self' para não sumir da memória!
            self.modelo = PandasModel(self.df)
            self.tabela.setModel(self.modelo)
            
        except Exception as e:
            print(f"Erro ao carregar a Grade Curricular: {e}")
    # Em views/grade.py

    def formatar_linhas_divisoras(self):
        """Detecta linhas que indicam períodos e mescla/destaca visualmente na tabela."""
        num_colunas = self.df.shape[1]
    
        for row in range(self.df.shape[0]):
            # Pega o texto da primeira coluna
            valor_primeira_col = str(self.df.iat[row, 0]).strip()
        
             # Verifica se é uma linha de divisor de período (ex: "— 1º Período —")
            if "Período" in valor_primeira_col or "—" in valor_primeira_col:
                # Mescla as células da linha ao longo de todas as colunas
                self.tabela.setSpan(row, 0, 1, num_colunas)
