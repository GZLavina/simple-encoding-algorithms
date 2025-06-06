# DESENVOLVIDO POR GUSTAVO LAVINA E VITOR GOULART

from abc import ABC, abstractmethod
import math
import bisect
from textwrap import wrap
from functools import reduce

# CLASSES ABSTRATAS PARA FACILITAR O DESENVOLVIMENTO DA UI

class Encoder(ABC):
    def __init__(self, name_: str):
        self.name = name_

    @abstractmethod
    def encode(self, str_to_encode: str):
        pass

    @abstractmethod
    def decode(self, encoded_str: str):
        pass

    @abstractmethod
    def get_additional_parameters(self):
        pass

    def is_valid_str_to_encode(self, str_to_encode: str):
        return True


# ------------------------------ CODIFICAÇÕES DO TRABALHO 2 ------------------------------

class ErrorCorrectionEncoder(Encoder):
    def __init__(self, name_: str):
        super().__init__(name_)

    @abstractmethod
    def encode(self, str_to_encode: str):
        pass

    @abstractmethod
    def decode(self, encoded_str: str):
        pass

    @abstractmethod
    def get_additional_parameters(self):
        pass

    def is_valid_str_to_encode(self, str_to_encode: str):
        return all([c == "1" or c == "0" for c in str_to_encode]) and len(str_to_encode) > 0


class RepetitionCode(ErrorCorrectionEncoder):
    DEFAULT_R_VALUE = 3
    r: int

    def __init__(self, name_: str):
        super().__init__(name_)
        self.r = self.DEFAULT_R_VALUE

    def encode(self, str_to_encode: str):
        encoded_str = ''
        for i in range(len(str_to_encode)):
            """Multiplica o caracter atual por r e adiciona no valor de retorno"""
            encoded_str += str_to_encode[i] * self.r
        return encoded_str

    def decode(self, encoded_str: str):
        decoded_str = ''
        for i in range(len(encoded_str) // self.r):
            """obtem o deslocamento multiplicando o indice atual por r"""
            shift = i * self.r
            substring = encoded_str[shift : shift + self.r]
            """Conta o número de bits 0 e 1"""
            bit_count_dict = {bit: substring.count(bit) for bit in substring}
            """Determina qual o bit prevalente"""
            max_count = max(bit_count_dict.values())
            prevalent_bits = [i for i, count in bit_count_dict.items() if count == max_count]
            """Se houve empate no caso de um valor r par, retorna a mensagem de erro e descarta a mensagem"""
            if len(prevalent_bits) > 1:
                return f"Múltiplos erros no segmento de número {i}: {substring} causaram empate entre os bits, impossível corrigir"
            """Adiciona o bit correto na string de retorno"""
            correct_bit = prevalent_bits[0]
            decoded_str += correct_bit
            """Se houve erro (ambos 0 e 1 estavam presente no segmento), avisa o usuario"""
            if len(bit_count_dict) > 1:
                error_index = substring.index("1") if correct_bit == "0" else substring.index("0")
                print(f"Erro encontrado no bit número {error_index + shift + 1} (da esquerda para a direita, iniciando em 1): {get_error_highlight(substring, error_index)}")
        return decoded_str

    def get_additional_parameters(self):
        try:
            r_ = int(input(
                f"Insira um valor válido para R (caso inválido, r = {self.DEFAULT_R_VALUE} ou qualquer valor configurado anteriormente): "))
            if r_ <= 0:
                raise ValueError
            self.r = r_
        except ValueError:
            pass


class Crc(ErrorCorrectionEncoder):
    DEFAULT_GENERATOR = "1001"
    generator: str
    d: int

    def __init__(self, name_: str):
        super().__init__(name_)
        self.set_generator(self.DEFAULT_GENERATOR)

    def get_rest(self, data: str):
        """Pega a substring inicial"""
        substring = data[:self.d]
        for i in range(len(substring), len(data) + 1):
            """Transforma o gerador em número e zera se o primeiro caracter da substring for 0"""
            xor_value = int(self.generator, 2) * int(substring[0])
            """Aplica o XOR"""
            xor_sum = int(substring, 2) ^ xor_value
            """Converte o resultado de volta para binário e descarta o primeiro caracter"""
            substring = format(xor_sum, f'0{self.d}b')[1:]
            if i < len(data):
                """Se ainda não acabou, puxa o próximo bit da string"""
                substring += data[i]
        return substring

    def encode(self, str_to_encode: str):
        """Adicionando zeros ao final"""
        str_with_zeros = str_to_encode + ('0' * (self.d - 1))
        return str_to_encode + self.get_rest(str_with_zeros)

    def decode(self, encoded_str: str):
        expected_rest = '0' * (self.d - 1)
        rest = self.get_rest(encoded_str)
        if rest == expected_rest:
            print(f"Resto = {rest}, mensagem recebida corretamente.")
            return encoded_str[:-self.d + 1]
        else:
            print(f"Resto = {rest}, mensagem recebida com erro.")
            return encoded_str[:-self.d + 1] + rest

    def get_additional_parameters(self):
        generator_ = input("Insira o polinômio gerador em formato binário (caso inválido, o valor padrão é 1001): ")
        if all([c == "1" or c == "0" for c in generator_]) and len(generator_) > 0:
            self.set_generator(generator_)

    def set_generator(self, generator_):
        self.generator = generator_
        self.d = len(generator_)


def get_error_highlight(sequence: str, error_index: int):
    return sequence[:error_index] + '>' + sequence[error_index] + '<' + sequence[error_index+1:]


class Hamming74(ErrorCorrectionEncoder):
    # Matriz geradora:
    # 1 0 0 0 | 1 0 1 -> 5
    # 0 1 0 0 | 1 1 0 -> 6
    # 0 0 1 0 | 1 1 1 -> 7
    # 0 0 0 1 | 0 1 1 -> 3
    CODE_SEQUENCE = [5, 6, 7, 3]

    # Ordem do cálculo de paridade para cada bit de paridade:
    XOR_ORDER = {
        4: [0, 2, 1],
        5: [1, 2, 3],
        6: [0, 2, 3]
    }

    def __init__(self, name_: str):
        super().__init__(name_)

    # DDDDPPP
    def encode(self, str_to_encode: str):
        """Adiciona zeros ao final para que o tamanho seja multiplo de 4"""
        if len(str_to_encode) % 4 != 0:
            padding_zeros = '0' * ((-len(str_to_encode)) % 4)
            str_to_encode += padding_zeros
            print(f"Foi necessário adicionar {len(padding_zeros)} zeros de padding ao final da mensagem. Por favor, desconsidere-os após a decodificação.")
        sequences = wrap(str_to_encode, 4)
        encoded_str = ''
        for sequence in sequences:
            """Pega o código pela lista e multiplica por 1 ou 0 de acordo com o bit da posição"""
            codes_to_use = [self.CODE_SEQUENCE[i] * int(sequence[i]) for i in range(4)]
            """Reduz a lista de códigos com XOR"""
            reduced_code = reduce(lambda x, y: x ^ y, codes_to_use)
            """Formata em binário com zeros à esquerda e adiciona tudo ao valor de retorno"""
            encoded_str += sequence + format(reduced_code, f'0{3}b')
        return encoded_str

    def decode(self, encoded_str: str):
        """Verifica se o número de bits é múltiplo de 7"""
        if not self.is_valid_str_to_decode(encoded_str):
            return "Mensagem com um número incorreto de caracteres!"

        """Divide as strings em um lista a cada 7 caracteres"""
        decoded_str = ''
        sequences = wrap(encoded_str, 7)
        for n, sequence in enumerate(sequences):
            """Inicializa um dicionário que mantém o número de cálculos corretos para cada bit"""
            check_count_dict = {i: 0 for i in range(7)}
            bits = list(map(int, sequence))
            sequence_correct = True
            for parity_bit_index in range(4, 7):
                """Pega a ordem dos bits de dados que compoe o calculo de paridade"""
                data_index_list = self.XOR_ORDER[parity_bit_index]
                """Calculo da paridade"""
                expected_parity_bit = bits[data_index_list[0]] ^ bits[data_index_list[1]] ^ bits[data_index_list[2]]
                """Se o resultado estiver correto, adicionamos no dicionário para cada bit de dados e para o bit de paridade"""
                if expected_parity_bit == bits[parity_bit_index]:
                    check_count_dict[parity_bit_index] += 1
                    for index in data_index_list:
                        check_count_dict[index] += 1
                else:
                    sequence_correct = False
            """Se não houve erro, concatena na string de retorno"""
            if sequence_correct:
                decoded_str += sequence[:4]
            else:
                """Monta uma lista com True para os bits de dados que participaram de calculos corretos e False para os outros"""
                bool_indices = [check_count_dict[i] > 0 for i in range(4)]
                if all(bool_indices[:4]):
                    """Se todos participaram de cálculos corretos, o erro está no bit de paridade que não participou de um cálculo correto"""
                    wrong_parity_bit = min(check_count_dict, key=check_count_dict.get)
                    print(f'Erro no bit de paridade número {wrong_parity_bit - 3} do segmento de número {n + 1}: {get_error_highlight(sequence, wrong_parity_bit)}')
                    decoded_str += sequence[:4]
                elif sum(bool_indices[:4]) == 3:
                    """Se apenas 3 bits de dados participaram de cálculos corretos, o erro está naquele que não participou"""
                    wrong_data_bit_index = bool_indices.index(False)
                    correction_bit = (int(sequence[wrong_data_bit_index]) + 1) % 2  # Transforma 1 em 0 e 0 em 1
                    print(f'Erro no bit de dados número {wrong_data_bit_index + 1} do segmento de número {n + 1}: {get_error_highlight(sequence, wrong_data_bit_index)}')
                    decoded_str += sequence[:wrong_data_bit_index] + str(correction_bit) + sequence[wrong_data_bit_index + 1 : 4]
                elif sum(bool_indices) == 0:
                    """Se todos os calculos falharam, o bit do meio está errado"""
                    correction_bit = (int(sequence[2]) + 1) % 2
                    print(f'Erro no bit de dados número 3 do segmento de número {n + 1}: {get_error_highlight(sequence, 2)}')
                    decoded_str += sequence[:2] + str(correction_bit) + sequence[3:4]
                else:
                    """Guard apenas para debug"""
                    print("Algo deu errado!")
                    return
        return decoded_str

    def get_additional_parameters(self):
        pass

    def is_valid_str_to_decode(self, encoded_str: str):
        return len(encoded_str) % 7 == 0


# ------------------------------ CODIFICAÇÕES DO PRÉVIAS (TRABALHO 1) ------------------------------

class Golomb(Encoder):
    DEFAULT_K_VALUE = 64
    k: int
    suffix_len: int

    def __init__(self, k_, name_: str):
        super().__init__(name_)
        self.k = k_
        self.set_suffix_len()

    def encode(self, str_to_encode: str):
        encoded_str = ''
        for c in str_to_encode:
            ascii_value = ord(c)

            """Adding prefix"""
            prefix_length = int(ascii_value / self.k)
            encoded_str += '0' * prefix_length

            """Adding stop-bit"""
            encoded_str += '1'

            """Adding suffix with necessary padding zeros to the left"""
            suffix_value = ascii_value % self.k
            encoded_str += format(suffix_value, f'0{self.suffix_len}b')
        return encoded_str

    def decode(self, encoded_str: str):
        decoded_str = ''
        index = 0
        while index < len(encoded_str):
            """Prefix reading"""
            zero_count = 0
            while encoded_str[index] == '0':
                zero_count += 1
                index += 1
            symbol_sum_value = self.k * zero_count
            """Suffix reading"""
            index += 1
            suffix_substring = encoded_str[index:(index+self.suffix_len)]
            symbol_sum_value += int(suffix_substring, 2)
            index += self.suffix_len
            decoded_str += chr(symbol_sum_value)
        return decoded_str

    def get_additional_parameters(self):
        try:
            k_ = int(input(f"Insira um valor válido para K (caso inválido, k = {self.DEFAULT_K_VALUE} ou qualquer valor configurado anteriormente): "))
            if k_ <= 0:
                raise ValueError
            self.k = k_
        except ValueError:
            pass
        finally:
            self.set_suffix_len()

    def set_suffix_len(self):
        self.suffix_len = math.ceil(math.log2(self.k))


class EliasGamma(Encoder):
    def __init__(self, name_: str):
        super().__init__(name_)

    def encode(self, str_to_encode: str):
        encoded_str = ''
        for character in str_to_encode:
            char_value = ord(character)
            """Calculate prefix and suffix length"""
            n = int(math.log2(char_value))
            """Append prefix and stop bit"""
            encoded_str += ('0' * n) + '1'
            """Append suffix"""
            if n > 0:
                encoded_str += format(char_value - (2 ** n), f'0{n}b')
        return encoded_str

    def decode(self, encoded_str: str):
        decoded_str = ''
        index = 0
        while index < len(encoded_str):
            """Prefix reading"""
            zero_count = 0
            while encoded_str[index] == '0':
                zero_count += 1
                index += 1
            symbol_sum_value = 2 ** zero_count
            """Suffix reading"""
            index += 1
            suffix_substring = encoded_str[index:index + zero_count]
            if len(suffix_substring) > 0:
                symbol_sum_value += int(suffix_substring, 2)
                decoded_str += chr(symbol_sum_value)
            index += zero_count
        return decoded_str

    def get_additional_parameters(self):
        pass

    def is_valid_str_to_encode(self, str_to_encode: str):
        return has_no_zeros(str_to_encode)


def has_no_zeros(str_to_encode):
    """True if no character are 0"""
    return all([ord(c) != 0 for c in str_to_encode])


class FibonacciZeckendorf(Encoder):

    def __init__(self, name_: str):
        super().__init__(name_)
        self.fibonacci_seq = [1, 2]

    def encode(self, str_to_encode: str):
        encoded_str = ''
        for character in str_to_encode:
            """Adding bits from right to left - starting with stop bit"""
            code = '1'
            """Ascii code"""
            char_value = ord(character)
            """Starting from the index of the largest fibonacci value that is lesser than char_value and decreasing"""
            for i in range(self.get_index_of_nearest_fibonacci(char_value), -1, -1):
                fibo_val = self.get_nth_fibonacci_val(i)
                """If fibonacci value fits, subtract it from remainder and add 1 to encoding"""
                if char_value - fibo_val >= 0:
                    char_value -= fibo_val
                    code = '1' + code
                else:
                    code = '0' + code
            encoded_str += code
        return encoded_str

    def decode(self, encoded_str: str):
        decoded_str = ''
        index = 0
        while index < len(encoded_str):
            last_read = '0'
            sum_value = 0
            current_symbol_index = 0
            """Until reads the second of two consecutive 1's"""
            while last_read != (curr_bit := encoded_str[current_symbol_index + index]) or last_read == '0':
                """Add Nth fibonacci value if read 1 where N is the current index in the current symbol"""
                if curr_bit == '1':
                    sum_value += self.get_nth_fibonacci_val(current_symbol_index)
                current_symbol_index += 1
                last_read = curr_bit
            """Use ascii table to turn value into symbol"""
            decoded_str += chr(sum_value)
            """increase the outer index by the inner index plus 1 to skip the stop bit"""
            index += current_symbol_index + 1
        return decoded_str

    def get_additional_parameters(self):
        pass

    def get_index_of_nearest_fibonacci(self, value):
        """Example: input value 15 returns index of 13, the nearest fibonacci value to 15"""
        index = 0
        while (fibo_val := self.get_nth_fibonacci_val(index)) < value:
            index += 1
        return index if fibo_val == value else index - 1

    def get_nth_fibonacci_val(self, n: int):
        """Compute fibonacci sequence as needed and store it for future reference"""
        if (curr_size := len(self.fibonacci_seq)) <= n:
            for _ in range(n - (curr_size - 1)):
                self.fibonacci_seq.append(self.fibonacci_seq[-1] + self.fibonacci_seq[-2])
        return self.fibonacci_seq[n]

    def is_valid_str_to_encode(self, str_to_encode: str):
        return has_no_zeros(str_to_encode)


class Ascii(Encoder):
    def __init__(self, name_):
        super().__init__(name_)

    def encode(self, str_to_encode: str):
        return ''.join([format(ord(c), f'0{8}b') for c in str_to_encode])

    def decode(self, encoded_str: str):
        char_list = wrap(encoded_str, 8)
        return ''.join([chr(int(c, 2)) for c in char_list])

    def get_additional_parameters(self):
        pass




class Huffman(Encoder):
    def __init__(self, name_):
        super().__init__(name_)
        self.root: Node | None = None
        self.codes_dict: dict = {}

    def encode(self, str_to_encode: str):
        frequency_dict = {symbol: str_to_encode.count(symbol) for symbol in str_to_encode}
        sorted_nodes_list = sorted([Node(frequency_dict[symbol], symbol) for symbol in frequency_dict], key=get_value)
        while len(sorted_nodes_list) > 1:
            left_node = sorted_nodes_list.pop(0)
            right_node = sorted_nodes_list.pop(0)
            new_node = Node(left_node.value + right_node.value, symbol_=None, left_=left_node, right_=right_node)
            bisect.insort(sorted_nodes_list, new_node, key=get_value)
        self.root = sorted_nodes_list[0]
        self.build_codes_dict(self.root, '')
        return ''.join([self.codes_dict[c] for c in str_to_encode])

    def decode(self, encoded_str: str):
        decoded_str = ''
        index = 0
        while index < len(encoded_str):
            symbol, index = self.find_symbol(self.root, encoded_str, index)
            decoded_str += symbol
        return decoded_str

    def find_symbol(self, node, encoded_str, index):
        if node.symbol:
            return node.symbol, index
        next_node = node.left if encoded_str[index] == '0' else node.right
        return self.find_symbol(next_node, encoded_str, index + 1)

    def build_codes_dict(self, node, code_str: str):
        if node.symbol:
            self.codes_dict[node.symbol] = code_str
        else:
            self.build_codes_dict(node.left, code_str + '0')
            self.build_codes_dict(node.right, code_str + '1')

    def get_additional_parameters(self):
        pass


def get_value(node):
    return node.value


class Node:
    def __init__(self, value_, symbol_=None, left_=None, right_=None):
        self.value: int = value_
        self.symbol: str | None = symbol_
        self.left: Node | None = left_
        self.right: Node | None = right_
