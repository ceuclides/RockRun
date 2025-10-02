import re

"""Formata números de telefone brasileiros (11 dígitos)"""
def formatar_tel(telefone):
    numeros = re.sub(r'\D','', telefone)
    if len(numeros) == 11:
        return f"({numeros[0:2]}) {numeros[2:7]}-{numeros[7:]}"  # Formato (99) 99999-9999
    else:
        return None