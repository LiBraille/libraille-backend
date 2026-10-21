"""
Módulo: braille_translator.py
Descrição: Motor de conversão de texto em Português para Braille Grau 1 (Norma Brasileira / ABNT).
Não possui dependências externas.

Mapeamento de Bits (0 a 63):
Pino 1 -> Bit 0 (1 << 0 = 1)   | Pino 4 -> Bit 3 (1 << 3 = 8)
Pino 2 -> Bit 1 (1 << 1 = 2)   | Pino 5 -> Bit 4 (1 << 4 = 16)
Pino 3 -> Bit 2 (1 << 2 = 4)   | Pino 6 -> Bit 5 (1 << 5 = 32)
"""

from typing import List, Dict, Union


def _calc_dots(*pins: int) -> int:
    """Calcula o valor inteiro (0-63) a partir dos números dos pontos Braille (1 a 6)."""
    val = 0
    for p in pins:
        val |= (1 << (p - 1))
    return val


# Sinais prefixos da Grafia Braille da Língua Portuguesa
CAPITAL_SIGN = _calc_dots(4, 6)          # 40 
NUMBER_SIGN = _calc_dots(3, 4, 5, 6)     # 60 
RESTORE_SIGN = _calc_dots(5)             # 16 

# Tabela base pré-computada para máxima performance
BRAILLE_MAP: Dict[str, int] = {
    # Espaço vazio (célula rebaixada)
    " ": 0,

    # Letras do alfabeto base (1ª, 2ª e 3ª séries)
    "a": _calc_dots(1),
    "b": _calc_dots(1, 2),
    "c": _calc_dots(1, 4),
    "d": _calc_dots(1, 4, 5),
    "e": _calc_dots(1, 5),
    "f": _calc_dots(1, 2, 4),
    "g": _calc_dots(1, 2, 4, 5),
    "h": _calc_dots(1, 2, 5),
    "i": _calc_dots(2, 4),
    "j": _calc_dots(2, 4, 5),
    "k": _calc_dots(1, 3),
    "l": _calc_dots(1, 2, 3),
    "m": _calc_dots(1, 3, 4),
    "n": _calc_dots(1, 3, 4, 5),
    "o": _calc_dots(1, 3, 5),
    "p": _calc_dots(1, 2, 3, 4),
    "q": _calc_dots(1, 2, 3, 4, 5),
    "r": _calc_dots(1, 2, 3, 5),
    "s": _calc_dots(2, 3, 4),
    "t": _calc_dots(2, 3, 4, 5),
    "u": _calc_dots(1, 3, 6),
    "v": _calc_dots(1, 2, 3, 6),
    "w": _calc_dots(2, 4, 5, 6),
    "x": _calc_dots(1, 3, 4, 6),
    "y": _calc_dots(1, 3, 4, 5, 6),
    "z": _calc_dots(1, 3, 5, 6),

    # Caracteres acentuados da língua portuguesa
    "á": _calc_dots(1, 2, 3, 5, 6),
    "é": _calc_dots(1, 2, 3, 4, 5, 6),
    "í": _calc_dots(3, 4),
    "ó": _calc_dots(3, 4, 6),
    "ú": _calc_dots(2, 3, 4, 5, 6),
    "à": _calc_dots(1, 2, 4, 6),
    "â": _calc_dots(1, 6),
    "ê": _calc_dots(1, 2, 6),
    "ô": _calc_dots(1, 4, 5, 6),
    "ã": _calc_dots(3, 4, 5),
    "õ": _calc_dots(2, 4, 6),
    "ç": _calc_dots(1, 2, 3, 4, 6),
    "ü": _calc_dots(1, 2, 5, 6),

    # Pontuação comum (Norma Brasileira)
    ",": _calc_dots(2),
    ";": _calc_dots(2, 3),
    ":": _calc_dots(2, 5),
    ".": _calc_dots(3),
    "?": _calc_dots(2, 6),
    "!": _calc_dots(2, 3, 5),
    "-": _calc_dots(3, 6),
    '"': _calc_dots(2, 3, 6),
    "'": _calc_dots(3),
    "(": _calc_dots(2, 3, 5, 6),
    ")": _calc_dots(2, 3, 5, 6),
}

# Dígitos de 1 a 0 mapeados para as letras 'a' a 'j'
DIGIT_MAP: Dict[str, str] = {
    "1": "a", "2": "b", "3": "c", "4": "d", "5": "e",
    "6": "f", "7": "g", "8": "h", "9": "i", "0": "j"
}


class BrailleTranslator:
    """Motor de tradução de texto em Português para Braille Grau 1."""

    @staticmethod
    def text_to_bytes(text: str) -> List[int]:
        """
        Converte uma string em uma lista de inteiros (0 a 63).
        Aplica regras oficiais:
        - Prefixo maiúscula (40) antes de cada letra maiúscula.
        - Prefixo de número (60) no início de blocos numéricos contínuos.
        - Ponto 5 (16) se uma letra de 'a' a 'j' seguir imediatamente um número sem espaço.
        """
        if not text:
            return []

        # Normaliza espaços múltiplos e quebras de linha em espaço único
        clean_text = " ".join(text.split())
        result_bytes: List[int] = []
        in_number_mode = False

        for char in clean_text:
            # 1. Tratamento de dígitos numéricos
            if char.isdigit():
                if not in_number_mode:
                    result_bytes.append(NUMBER_SIGN)
                    in_number_mode = True
                target_letter = DIGIT_MAP[char]
                result_bytes.append(BRAILLE_MAP[target_letter])
                continue

            # 2. Tratamento de letras (com acentos ou maiúsculas)
            if char.isalpha():
                lower_char = char.lower()

                # Caso ocorra "1a" sem espaço, o restituidor evita a leitura como "11"
                if in_number_mode and char.islower() and lower_char in DIGIT_MAP.values():
                    result_bytes.append(RESTORE_SIGN)

                in_number_mode = False

                if lower_char not in BRAILLE_MAP:
                    # Caractere sem correspondente Braille cadastrado é ignorado
                    continue

                if char.isupper():
                    result_bytes.append(CAPITAL_SIGN)

                result_bytes.append(BRAILLE_MAP[lower_char])
                continue

            # 3. Espaços e pontuações
            in_number_mode = False
            if char in BRAILLE_MAP:
                result_bytes.append(BRAILLE_MAP[char])

        return result_bytes

    @staticmethod
    def byte_to_unicode(byte_val: int) -> str:
        """Converte um byte (0-63) no caractere visual Braille Unicode (0x2800..0x283F)."""
        return chr(0x2800 + (byte_val & 0x3F))

    @classmethod
    def text_to_unicode(cls, text: str) -> str:
        """Retorna a string visual em Braille Unicode correspondente ao texto."""
        raw_bytes = cls.text_to_bytes(text)
        return "".join(cls.byte_to_unicode(b) for b in raw_bytes)

    @staticmethod
    def byte_to_pins(byte_val: int) -> List[int]:
        """Informa quais pinos físicos (1 a 6) devem subir para acionar o atuador."""
        return [pin for pin in range(1, 7) if (byte_val & (1 << (pin - 1)))]


if __name__ == "__main__":
    # Teste rápido manual para execução direta no terminal
    sample = "Olá, Mundo 2026!"
    output_bytes = BrailleTranslator.text_to_bytes(sample)
    output_unicode = BrailleTranslator.text_to_unicode(sample)

    print(f"Texto original: {sample}")
    print(f"Bytes para o ESP32 (0-63): {output_bytes}")
    print(f"Braille visual (Unicode): {output_unicode}")