# DESENVOLVIDO POR GUSTAVO LAVINA E VITOR GOULART

from encoders import Encoder, Golomb, EliasGamma, FibonacciZeckendorf, Huffman
from typing import List

AVAILABLE_ENCODERS: List[Encoder] = [
    Golomb(Golomb.DEFAULT_K_VALUE, "Golomb"),
    EliasGamma("Elias-Gamma"),
    FibonacciZeckendorf("Fibonacci/Zeckendorf"),
    Huffman("Huffman")
]


def get_encoder():
    method_options_str = list(map(lambda x: f'{x[0]}: {x[1].name}', enumerate(AVAILABLE_ENCODERS)))
    method = -1
    while not (0 <= method < len(AVAILABLE_ENCODERS)):
        print("Qual método deseja usar?")
        for opt in method_options_str:
            print(opt)
        method = int(input())
    return AVAILABLE_ENCODERS[method]


def get_validated_str_to_encode(encoder: Encoder):
    valid_str = False
    str_to_encode = ''
    while not valid_str:
        str_to_encode = input("Insira a mensagem para codificar: ")
        valid_str = encoder.is_valid_str_to_encode(str_to_encode) and len(str_to_encode) > 0
    return str_to_encode


def get_validated_encoded_str():
    valid_str = False
    str_to_decode = ''
    while not valid_str:
        str_to_decode = input("Insira a mensagem para decodificar: ")
        valid_str = all([bit == '0' or bit == '1' for bit in str_to_decode]) and len(str_to_decode) > 0
    return str_to_decode


def should_decode_message():
    option = input("Deseja decodificar esta mesma codificação? (S/N)")
    return option == 'S' or option == 's'


def run():
    while True:
        action = input(
            """Insira:
1 para codificar
2 para decodificar
X para sair
""")
        if action == "1" or action == "2":
            encoder = get_encoder()
            if action == "1":
                try:
                    encoder.get_additional_parameters()
                    encoded_str = encoder.encode(get_validated_str_to_encode(encoder))
                    print(f"Input codificado:\n{encoded_str}")
                    if should_decode_message():
                        print(f'Mensagem decodificada:\n{encoder.decode(encoded_str)}')
                except:
                    print("Algo deu errado ao tentar codificar a mensagem, verifique se está usando caracteres inválidos")
            else:
                try:
                    encoder.get_additional_parameters()
                    encoded_str = get_validated_encoded_str()
                    decoded_str = encoder.decode(encoded_str)
                    print(f"Input decodificado:\n{decoded_str}")
                except:
                    print("Não foi possível decodificar a mensagem, tem certeza que está usando o método correto para essa mensagem?")
        else:
            break


if __name__ == '__main__':
    run()
