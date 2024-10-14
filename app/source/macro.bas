Sub Export()
Set Presentation = ActivePresentation
caminho = Presentation.Path

Presentation.Slides(1).Shapes("Variação IBOV").TextFrame.TextRange.Paragraphs.ParagraphFormat.Alignment = ppAlignRight
Presentation.Slides(1).Shapes("Data").TextFrame.TextRange.Paragraphs.ParagraphFormat.Alignment = ppAlignRight
Presentation.Slides(1).Shapes("Cotação IBOV").TextFrame.TextRange.Paragraphs.ParagraphFormat.Alignment = ppAlignRight
Presentation.Slides(1).Shapes("Variação NASDAQ").TextFrame.TextRange.Paragraphs.ParagraphFormat.Alignment = ppAlignRight
Presentation.Slides(1).Shapes("Variação S&P 500").TextFrame.TextRange.Paragraphs.ParagraphFormat.Alignment = ppAlignRight
Presentation.Slides(1).Shapes("Variação EUROSTOXX").TextFrame.TextRange.Paragraphs.ParagraphFormat.Alignment = ppAlignRight
Presentation.Slides(1).Shapes("Cotação DÓLAR").TextFrame.TextRange.Paragraphs.ParagraphFormat.Alignment = ppAlignRight
Presentation.Slides(1).Shapes("Variação maior alta 1").TextFrame.TextRange.Paragraphs.ParagraphFormat.Alignment = ppAlignRight
Presentation.Slides(1).Shapes("Variação maior alta 2").TextFrame.TextRange.Paragraphs.ParagraphFormat.Alignment = ppAlignRight
Presentation.Slides(1).Shapes("Variação maior queda 1").TextFrame.TextRange.Paragraphs.ParagraphFormat.Alignment = ppAlignRight
Presentation.Slides(1).Shapes("Variação maior queda 2").TextFrame.TextRange.Paragraphs.ParagraphFormat.Alignment = ppAlignRight

ActivePresentation.Slides(1).Export caminho & "/Fechamento de mercado.png", "PNG"

End Sub