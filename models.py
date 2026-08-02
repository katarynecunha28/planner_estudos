# models.py
import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtGui import QColor, QFont

class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame()):
        super().__init__()
        self._df = df

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        valor = self._df.iat[row, col]
        primeira_col_texto = str(self._df.iat[row, 0])

        # 1. Exibição do Texto
        if role in (Qt.DisplayRole, Qt.EditRole):
            if pd.isna(valor):
                return ""
            return str(valor)

        # 2. Cor de Fundo para Linhas de Período (Roxo/Lilás)
        if role == Qt.BackgroundRole:
            if "Período" in primeira_col_texto or "—" in primeira_col_texto:
                return QColor("#8A2BE2")  # Cor roxa/violeta de destaque

        # 3. Cor do Texto para Linhas de Período (Branco)
        if role == Qt.ForegroundRole:
            if "Período" in primeira_col_texto or "—" in primeira_col_texto:
                return QColor("#FFFFFF")  # Texto em branco

        # 4. Alinhamento ao Centro para Linhas de Período
        if role == Qt.TextAlignmentRole:
            if "Período" in primeira_col_texto or "—" in primeira_col_texto:
                return Qt.AlignCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        # 5. Fonte em Negrito para os Períodos
        if role == Qt.FontRole:
            if "Período" in primeira_col_texto or "—" in primeira_col_texto:
                font = QFont()
                font.setBold(True)
                return font

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and role == Qt.EditRole:
            row = index.row()
            col = index.column()

            val_limpo = str(value).replace(',', '.').strip()
            try:
                if val_limpo.replace('.', '', 1).isdigit():
                    value = float(val_limpo) if '.' in val_limpo else int(val_limpo)
            except ValueError:
                pass

            self._df.iat[row, col] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True

        return False

    def flags(self, index):
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
