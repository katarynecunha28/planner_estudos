# views/tab_materias.py
import pandas as pd
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView, QPushButton, QHeaderView, QMessageBox
from PyQt5.QtCore import Qt, QAbstractTableModel


# --- MODELO EDITÁVEL PARA A TABELA DE MATÉRIAS ---
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
        """Permite a alteração direta dos dados ao dar duplo clique."""
        if index.isValid() and role == Qt.EditRole:
            val_str = str(value).replace(',', '.').strip()
            
            # Converte para int/float se for um número válido
            try:
                if val_str.replace('.', '', 1).isdigit():
                    value = float(val_str) if '.' in val_str else int(val_str)
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


# --- CLASSE DA VIEW MATÉRIAS ---
class TabMaterias(QWidget):
    def __init__(self):
        super().__init__()
        self.arquivo_alvo = 'estudos_faculdade.xlsx'
        self.nome_aba = '📚 Matérias'
        self.carregando = False

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # 1. Configurando a Tabela
        self.tabela = QTableView()
        self.tabela.setAlternatingRowColors(True)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableView.SelectRows)
        self.tabela.setShowGrid(True)
        self.layout.addWidget(self.tabela)

        # 2. Botão de Ação
        self.btn_atualizar = QPushButton("🔄 Atualizar Minhas Matérias")
        self.btn_atualizar.clicked.connect(self.carregar_dados)
        self.layout.addWidget(self.btn_atualizar)

        self.carregar_dados()

    def carregar_dados(self):
        """Lê os dados da planilha e aplica o modelo editável."""
        self.carregando = True
        try:
            self.df = pd.read_excel(self.arquivo_alvo, sheet_name=self.nome_aba, header=1)
            self.df = self.df.loc[:, ~self.df.columns.str.contains('^Unnamed')]
            self.df.fillna("-", inplace=True)

            self.modelo = EditablePandasModel(self.df)
            self.tabela.setModel(self.modelo)
            
            # Conecta a alteração no modelo com a função de salvamento
            self.modelo.dataChanged.connect(self.ao_editar_celula)

        except Exception as e:
            print(f"Erro ao carregar a aba de Matérias: {e}")
        finally:
            self.carregando = False

    def ao_editar_celula(self, topLeft, bottomRight, roles):
        """Disparado após edições via duplo clique."""
        if self.carregando:
            return

        row = topLeft.row()
        col = topLeft.column()
        nome_coluna = str(self.df.columns[col]).strip()

        # Recalcula a média se houver alteração em notas de prova presentes nessa aba
        cols_notas = [c for c in self.df.columns if 'Nota' in str(c) or c in ['P1', 'P2', 'P3']]
        if nome_coluna in cols_notas and any('Média' in str(c) for c in self.df.columns):
            self.recalcular_media(row, cols_notas)

        self.salvar_dados()

    def recalcular_media(self, row, cols_notas):
        """Recalcula a média da matéria se houver notas numéricas."""
        try:
            soma = 0.0
            qtd = 0
            for col_name in cols_notas:
                val = self.df.at[row, col_name]
                try:
                    num = float(str(val).replace(',', '.'))
                    soma += num
                    qtd += 1
                except (ValueError, TypeError):
                    pass

            if qtd > 0:
                col_media = [i for i, c in enumerate(self.df.columns) if 'Média' in str(c)][0]
                nova_media = round(soma / qtd, 2)
                self.df.iat[row, col_media] = nova_media
                
                # Atualiza a exibição na tabela
                idx_media = self.modelo.index(row, col_media)
                self.modelo.dataChanged.emit(idx_media, idx_media, [Qt.DisplayRole])
        except Exception as e:
            print(f"Erro ao recalcular média: {e}")

    def salvar_dados(self):
        """Salva a aba no Excel com 'header=1' preservando a estrutura."""
        try:
            with pd.ExcelWriter(self.arquivo_alvo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                self.df.to_excel(writer, sheet_name=self.nome_aba, index=False, startrow=1)
        except Exception as e:
            print(f"Erro ao salvar Matérias no Excel: {e}")
