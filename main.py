# DESENVOLVIDO POR GUSTAVO LAVINA E VITOR GOULART

from encoders import Encoder, Golomb, EliasGamma, FibonacciZeckendorf, Huffman, RepetitionCode, Crc, Hamming74, Ascii
from typing import List

AVAILABLE_ENCODERS: List[Encoder] = [
    Ascii("Ascii"),
    Golomb(Golomb.DEFAULT_K_VALUE, "Golomb"),
    EliasGamma("Elias-Gamma"),
    FibonacciZeckendorf("Fibonacci/Zeckendorf"),
    Huffman("Huffman"),
    RepetitionCode("Código de Repetição"),
    Crc("CRC"),
    Hamming74("Hamming(7, 4)")
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


def get_follow_up_action(output_str: str, previous_encoder: Encoder):
    action = input(
        """O que deseja fazer com o resultado da operação? Insira:
1 para codificar com outro algoritmo
2 para decodificar com o mesmo algoritmo sem alterações
3 para decodificar com o mesmo algoritmo com alterações
4 para decodificar com outro algoritmo sem alterações
5 para decodificar com outro algoritmo com alterações
X para voltar ao menu principal
""")
    if action == '1':
        try:
            encoder = get_encoder()
            encoder.get_additional_parameters()
            encoded_str = encoder.encode(output_str)
            print(f"Input codificado:\n{encoded_str}")
            get_follow_up_action(encoded_str, encoder)
        except Exception as error:
            print("Algo deu errado ao tentar codificar a mensagem, verifique se está usando caracteres inválidos.")
            print(error)
            return
    elif action == '2' or action == '3':
        try:
            str_to_decode = output_str if action == '2' else get_validated_encoded_str()
            decoded_str = previous_encoder.decode(str_to_decode)
            print(f'Mensagem decodificada:\n{decoded_str}')
            get_follow_up_action(decoded_str, previous_encoder)
        except Exception as error:
            print("Houve um erro durante a decodificação:")
            print(error)
            return
    elif action == '4' or action == '5':
        try:
            encoder = get_encoder()
            encoder.get_additional_parameters()
            str_to_decode = output_str if action == '4' else get_validated_encoded_str()
            decoded_str = encoder.decode(str_to_decode)
            print(f'Mensagem decodificada:\n{decoded_str}')
            get_follow_up_action(decoded_str, encoder)
        except Exception as error:
            print(error)
            print("Não foi possível decodificar a mensagem, tem certeza que está usando o método correto para essa mensagem?")
            return


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
                    get_follow_up_action(encoded_str, encoder)
                except Exception as error:
                    print(error)
                    print("Algo deu errado ao tentar codificar a mensagem, verifique se está usando caracteres inválidos")
            else:
                try:
                    encoder.get_additional_parameters()
                    encoded_str = get_validated_encoded_str()
                    decoded_str = encoder.decode(encoded_str)
                    print(f"Input decodificado:\n{decoded_str}")
                    get_follow_up_action(decoded_str, encoder)
                except Exception as error:
                    print(error)
                    print("Não foi possível decodificar a mensagem, tem certeza que está usando o método correto para essa mensagem?")
        else:
            break


if __name__ == '__main__':
    run()

