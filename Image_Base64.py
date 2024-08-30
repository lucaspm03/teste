import base64

# Caminho para a imagem no seu PC
image_path = "O-que-e-ITIL-300x288.png"  # Certifique-se de incluir a extensão

# Ler a imagem em formato binário
with open(image_path, "rb") as image_file:
    # Converter para base64
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

# Exibir a string base64
print(encoded_string)
