import sys
import os
import ctypes
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtSvg import QSvgRenderer  # Suporte a SVG nativo

# Importando todas as abas modulares
from views.tab_tarefas import TabTarefas
from views.tab_materias import TabMaterias
from views.grade import TabGrade
from views.cronograma import TabCronograma
from views.progresso import TabProgresso
from views.notas import TabNotas

# Força o Windows a exibir o ícone personalizado na barra de tarefas
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('planner.estudos.faculdade')
except Exception:
    pass


class PlannerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configurações da Janela Principal
        self.setWindowTitle("Meu Planner de Estudos")
        self.resize(1000, 600)
        
        # Resolvendo o caminho do ícone SVG
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_icone = os.path.join(diretorio_atual, "assets", "icone_app.svg")
        self.setWindowIcon(QIcon(caminho_icone))

        # Criando o gerenciador de abas
        self.abas = QTabWidget()
        self.setCentralWidget(self.abas)

        # Instanciando as abas
        self.aba_tarefas = TabTarefas()
        self.aba_materias = TabMaterias()
        self.aba_grade = TabGrade()
        self.aba_cronograma = TabCronograma()
        self.aba_progresso = TabProgresso()
        self.aba_notas = TabNotas()
        
        # Adicionando as abas ao gerenciador
        self.abas.addTab(self.aba_tarefas, "✅ Tarefas")
        self.abas.addTab(self.aba_materias, "📚 Matérias")
        self.abas.addTab(self.aba_grade, "🎓 Grade")
        self.abas.addTab(self.aba_cronograma, "📅 Cronograma")
        self.abas.addTab(self.aba_progresso, "📊 Progresso")
        self.abas.addTab(self.aba_notas, "🧮 Notas")

        # Conecta a mudança de aba ao trocador de temas
        self.abas.currentChanged.connect(self.mudar_cor_tema)
        
        # Aplica o tema inicial
        self.mudar_cor_tema(0)

    def mudar_cor_tema(self, index):
        # Paletas Pastel personalizadas por aba
        temas = [
            {"clara": "#E8F5E9", "media": "#C8E6C9", "escura": "#81C784"},  # 0: ✅ Tarefas (Verde)
            {"clara": "#E3F2FD", "media": "#BBDEFB", "escura": "#64B5F6"},  # 1: 📚 Matérias (Azul)
            {"clara": "#F3E5F5", "media": "#E1BEE7", "escura": "#BA68C8"},  # 2: 🎓 Grade (Roxo/Lilás)
            {"clara": "#FFFDE7", "media": "#FFF59D", "escura": "#F6D552"},  # 3: 📅 Cronograma (Amarelo)
            {"clara": "#FFF0F5", "media": "#FFD1DC", "escura": "#FFB6C1"},  # 4: 📊 Progresso (Rosa)
            {"clara": "#FFF5E6", "media": "#FFDAB9", "escura": "#FFA07A"}   # 5: 🧮 Notas (Coral)
        ]
        
        # Fallback se o índice extrapolar
        if index < len(temas):
            tema = temas[index]
        else:
            tema = {"clara": "#F5F5F5", "media": "#E0E0E0", "escura": "#BDBDBD"}

        # Estilo Dinâmico QSS
        estilo = f"""
        /* Cor de fundo da janela principal */
        QMainWindow {{
            background-color: #FAFAFA;
        }}

        /* Estilo da caixa das Abas */
        QTabWidget::pane {{
            border: 2px solid {tema['media']};
            background: white;
            border-radius: 10px;
        }}
        
        /* Botões superiores das abas (inativos) */
        QTabBar::tab {{
            background: #F0F0F0;
            border: 1px solid #DCDCDC;
            padding: 10px 20px;
            margin-right: 4px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            color: #777777;
            font-weight: bold;
            font-size: 13px;
        }}
        
        /* Aba SELECIONADA (recebe a cor do tema ativo) */
        QTabBar::tab:selected {{
            background: {tema['media']};
            border-color: {tema['media']};
            color: #333333;
        }}
        
        QTabBar::tab:hover {{
            background: {tema['clara']};
        }}

        /* Estilo das Tabelas */
        QTableView {{
            background-color: white;
            alternate-background-color: {tema['clara']};
            gridline-color: #F0F0F0;
            border: none;
            selection-background-color: {tema['media']};
            selection-color: black;
            font-size: 12px;
        }}
        
        QHeaderView::section {{
            background-color: {tema['media']};
            color: #333333;
            font-weight: bold;
            border: none;
            padding: 6px;
            border-right: 1px solid #FFFFFF;
        }}

        /* Estilo dos Botões de Ação */
        QPushButton {{
            background-color: {tema['escura']};
            color: white;
            border-radius: 12px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 13px;
        }}
        QPushButton:hover {{
            background-color: {tema['media']}; 
            color: #333333;
        }}
        
        /* Estilo dos Inputs */
        QLineEdit, QComboBox {{
            border: 1px solid #DCDCDC;
            border-radius: 5px;
            padding: 5px;
            background-color: #FFFFFF;
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 1px solid {tema['media']};
        }}
        """
        
        self.setStyleSheet(estilo)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    
    # Resolvendo o caminho do ícone para a aplicação
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_icone = os.path.join(diretorio_atual, "assets", "icone_app.svg")
    
    icon_obj = QIcon(caminho_icone)
    app.setWindowIcon(icon_obj)
    
    janela = PlannerApp()
    janela.setWindowIcon(icon_obj)
    janela.show()
    
    sys.exit(app.exec_())
