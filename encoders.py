from abc import ABC, abstractmethod
import math
import bisect


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
