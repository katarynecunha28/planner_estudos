# views/notas.py
import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView, QPushButton, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt, QAbstractTableModel


# --- MODELO ADAPTADO DO PANDAS COM SUPORTE A EDIÇÃO ---
class EditablePandasModel(QAbstractTableModel):
    def __init__(self, df):
        super().__init__()
        self._df = df

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        
        if role in (Qt.DisplayRole, Qt.EditRole):
            valor = self._df.iat[index.row(), index.column()]
            return str(valor)
            
        return None

    def setData(self, index, value, role=Qt.EditRole):
        """Permite que o duplo clique altere o dado diretamente no DataFrame."""
        if index.isValid() and role == Qt.EditRole:
            col_name = self._df.columns[index.column()]
            
            # Tenta converter para número se for nota/média, caso contrário mantém string
            try:
                if str(value).replace('.', '', 1).isdigit():
                    value = float(value)
            except ValueError:
                pass

            self._df.iat[index.row(), index.column()] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
            
        return False

    def flags(self, index):
        """Habilita a edição via duplo clique nas células."""
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._df.columns[section])
            if orientation == Qt.Vertical:
                return str(self._df.index[section])
        return None


# --- CLASSE DA VIEW NOTAS ---
class TabNotas(QWidget):
    def __init__(self):
        super().__init__()
        
        self.arquivo_alvo = 'estudos_faculdade.xlsx' 
        self.nome_aba = '🧮 Notas' 
        self.carregando = False  # Evita loops ao carregar a tabela
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Configurando a Tabela
        self.tabela = QTableView()
        self.tabela.setAlternatingRowColors(True)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableView.SelectRows)
        self.tabela.setShowGrid(True)
        
        self.layout.addWidget(self.tabela)

        # Botão de Ação (Recarregar/Atualizar)
        self.btn_atualizar = QPushButton("🔄 Atualizar Notas")
        self.btn_atualizar.clicked.connect(self.carregar_dados)
        self.layout.addWidget(self.btn_atualizar)

        self.carregar_dados()

    def carregar_dados(self):
        """Lê os dados da planilha e preenche a tabela."""
        self.carregando = True
        try:
            # 1. Lê o Excel e cria o self.df
            self.df = pd.read_excel(self.arquivo_alvo, sheet_name=self.nome_aba, header=2)
            
            # 2. Limpeza das colunas invisíveis
            self.df = self.df.loc[:, ~self.df.columns.str.contains('^Unnamed')]
            
            # 3. Preenche vazios
            self.df.fillna("-", inplace=True)
            
            # Instancia o modelo editável e atribui à tabela
            self.modelo = EditablePandasModel(self.df)
            self.tabela.setModel(self.modelo)
            
            # Conecta o evento de edição ao salvamento automático
            self.modelo.dataChanged.connect(self.ao_editar_celula)
            
        except Exception as e:
            print(f"Erro ao carregar Notas: {e}")
        finally:
            self.carregando = False

    def ao_editar_celula(self, topLeft, bottomRight, roles):
        """Disparado após o usuário editar um dado com duplo clique + Enter."""
        if self.carregando:
            return

        row = topLeft.row()
        col = topLeft.column()
        col_name = self.df.columns[col]

        # Se alterar P1, P2 ou P3 e existir a coluna Média, recalcula automaticamente
        if col_name in ['P1', 'P2', 'P3'] and 'Média' in self.df.columns:
            self.recalcular_media(row)

        # Salva as alterações na planilha Excel
        self.salvar_dados()

    def recalcular_media(self, row):
        """Recalcula a Média da linha se as notas forem numéricas."""
        try:
            p1 = float(self.df.at[row, 'P1']) if str(self.df.at[row, 'P1']).replace('.', '', 1).isdigit() else 0
            p2 = float(self.df.at[row, 'P2']) if str(self.df.at[row, 'P2']).replace('.', '', 1).isdigit() else 0
            p3 = float(self.df.at[row, 'P3']) if str(self.df.at[row, 'P3']).replace('.', '', 1).isdigit() else 0
            
            # Média simples das notas digitadas
            media = round((p1 + p2 + p3) / 3, 2) if (p1 or p2 or p3) else 0.0
            self.df.at[row, 'Média'] = media
            
            # Notifica a tabela para atualizar a exibição da Média na tela
            col_media = self.df.columns.get_loc('Média')
            idx_media = self.modelo.index(row, col_media)
            self.modelo.dataChanged.emit(idx_media, idx_media, [Qt.DisplayRole])
        except Exception as e:
            print(f"Erro ao recalcular média: {e}")

    def salvar_dados(self):
        """Escreve o DataFrame atualizado de volta na aba do Excel."""
        try:
            with pd.ExcelWriter(self.arquivo_alvo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                # Mantém o cabeçalho na linha 3 (startrow=2) conforme sua estrutura de leitura (header=2)
                self.df.to_excel(writer, sheet_name=self.nome_aba, index=False, startrow=2)
        except Exception as e:
            print(f"Erro ao salvar alterações no Excel: {e}")
