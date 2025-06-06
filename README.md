# Simple Encoding Algorithms

Desenvolvido por Gustavo Lavina e Vitor Goulart como primeiro **e segundo** trabalho avaliativo da disciplina de Teoria da Informação: Compressão e Criptografia da Unisinos, ministrada pelo professor Elvandi da Silva Junior.

**Os algoritmos desenvolvidos para o Grau B (Repetição, CRC e Hamming(7, 4)) estão posicionados na parte inicial do arquivo encoders.py, após as classes abstratas.** O restante dos algoritmos foram desenvolvidos para a entrega anterior (exceto o Ascii, adicionado para facilitar os testes).

## Como executar

Basta executar o arquivo main.py e inserir as informações necessárias após os prompts no console.

Para utilizar o método de Huffman, a árvore utilizada para decodificar será a mesma utilizada na última codificação. Portanto, não é possível fazer duas decodificações distintas consecutivas utilizando a codificação de Huffman, é necessário fazer uma codificação e decodificação de cada vez. Também não é possível decodificar uma mensagem com codificação de Huffman que **não tenha sido codificada na mesma instância de execução do programa**, pois não foi implementada persitência.

Para utilizar o método Hamming(7, 4), é necessário desconsiderar eventuais zeros de padding após a decodificação. Zeros de padding são inseridos para que a mensagem tenha um tamanho múltiplo de 4, necessário para a codificação.