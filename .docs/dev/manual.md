# Manual para desenvolvimento
Orientacoes para a correta utilizacao desse template

# 1. Arquivos padrao
Jamais apague estes arquivos, eles sao essenciais para a execucao do código

- [.env](../../.env):
Aqui guardamos variavie globais de sistema e *sensiveis* como credenciais, estas devem ser importadas no arquivo settings.py com a biblioteca [python-decouple](https://pypi.org/project/python-decouple/).

- [source/main.py](../../source/main.py):
A lógica principal de seu código deve estar contida aqui, importe módulos, bibliotecas, funções e etc.

- [source/settings.py](../../source/settings.py):
As principais variaveis globais estão neste local para configurar o comportamento do código.