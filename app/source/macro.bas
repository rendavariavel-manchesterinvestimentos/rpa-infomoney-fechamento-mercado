Sub Export()
Set Presentation = ActivePresentation
caminho = Presentation.Path

ActivePresentation.Slides(1).Export caminho & "/Fechamento de mercado.png", "PNG"

End Sub