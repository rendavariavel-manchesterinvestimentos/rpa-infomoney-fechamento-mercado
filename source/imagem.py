"""Faz a troca do tipo de arquivo do Fechamento do Mercado do PDF de PPT para PNG"""

from pathlib import Path
import win32com.client as win32com

def transforma_em_png(modelo: Path, salvar_como: Path) -> None:
    """Tranforma o arquivo do PPT para PNG. 'VBA'"""

    # Tranforma o arquivo da pasta tmp para PNG
    ppt = win32com.Dispatch("PowerPoint.Application")
    active_presentation = ppt.Presentations.Open(modelo)
    active_presentation.Slides(1).Export(salvar_como, "PNG")
    active_presentation.Close()
    ppt.Quit()
