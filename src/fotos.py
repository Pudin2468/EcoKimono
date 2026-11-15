"""Tratamento da foto do kimono.

Por que não só salvar o arquivo que chegou?
- O nome e a "extensão" podem mentir (um .jpg que na verdade é outra coisa).
  Por isso abrimos a imagem de verdade com o Pillow e vemos o que ela é.
- Fotos de celular guardam dados escondidos (EXIF), como a localização GPS.
  Como o público é de crianças, regravamos a imagem sem nenhum desses dados.
- Fotos enormes deixariam o site lento: reduzimos para no máximo 900 pixels.
"""
import os
import secrets

from PIL import Image, ImageOps, UnidentifiedImageError

FORMATOS_ACEITOS = {"JPEG", "PNG", "WEBP"}
LADO_MAXIMO = 900            # pixels
LIMITE_PIXELS = 40_000_000   # recusa imagens gigantes (proteção contra "bomba de imagem")


def abrir_foto(arquivo):
    """Recebe o arquivo enviado (do request.files). Devolve a imagem pronta (RGB, reduzida),
    ou levanta ValueError com uma frase em português para mostrar à pessoa."""
    if arquivo is None or not arquivo.filename:
        raise ValueError("Escolha uma foto do kimono.")
    try:
        imagem = Image.open(arquivo.stream)
        if imagem.format not in FORMATOS_ACEITOS:
            raise ValueError("Use uma foto JPG, PNG ou WEBP.")
        if imagem.width * imagem.height > LIMITE_PIXELS:
            raise ValueError("A foto é grande demais. Tire outra em resolução menor.")
        imagem.load()                                   # lê tudo: pega arquivo quebrado
    except ValueError:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise ValueError("Não consegui abrir essa foto. Tente outra.")

    imagem = ImageOps.exif_transpose(imagem)            # endireita fotos de celular
    if imagem.mode in ("RGBA", "LA", "P"):              # fundo branco no lugar da transparência
        imagem = imagem.convert("RGBA")
        fundo = Image.new("RGB", imagem.size, (255, 255, 255))
        fundo.paste(imagem, mask=imagem.split()[-1])
        imagem = fundo
    else:
        imagem = imagem.convert("RGB")
    imagem.thumbnail((LADO_MAXIMO, LADO_MAXIMO))        # só diminui, nunca aumenta
    return imagem


def gravar_foto(imagem, pasta):
    """Grava a imagem em JPEG numa pasta, com nome aleatório (ninguém adivinha o endereço).
    Devolve o caminho relativo à pasta static, por exemplo 'uploads/ab12cd.jpg'."""
    os.makedirs(pasta, exist_ok=True)
    nome = secrets.token_hex(12) + ".jpg"               # nome nosso, nunca o que a pessoa mandou
    imagem.save(os.path.join(pasta, nome), "JPEG", quality=85, optimize=True)  # sem EXIF
    return "uploads/" + nome
