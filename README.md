# Simulação de Algoritmo de Substituição de Páginas: WSClock

## Sobre o Projeto
Este repositório contém a implementação de um simulador do algoritmo WSClock. O projeto foi desenvolvido como requisito prático para a disciplina de Sistemas Operacionais e
tem como objetivo demonstrar a mecânica de gerenciamento de memória em cenários onde um buffer limitado exige a substituição de páginas, considerando o tempo lógico e o conjunto de trabalho ativo.

## Referência e Conteúdo Base
A lógica do algoritmo implementado foi fundamentada na literatura clássica de ciência da computação e sistemas operacionais, especificamente:
*   **Sistemas Operacionais Modernos (Andrew S. Tanenbaum):** Capítulo referente ao Gerenciamento de Memória e Algoritmos de Substituição de Página.
*   **Conceitos implementados:** 
    *   Buffer em lista circular
    *   Controle por **Bit de Referência (R)** para a regra da "segunda chance"
    *   Controle por **Bit de Modificação (M / Dirty Bit)** para agendamento simulado de gravação em disco
    *   Janela de tempo de uso ativo

## Ambiente de Desenvolvimento
*   **Linguagem de Programação:** Python
*   **Bibliotecas:** Nenhuma biblioteca externa, a lógica circular e o gerenciamento de estado foram construídos puramente com as estruturas de dados nativas do Python
*   **Sistema Operacional:** O código é multiplataforma. O desenvolvimento e os testes foram realizados em ambiente Windows.

## Como Executar a Simulação
Por ser desenvolvido em Python, o projeto não exige um processo de compilação prévia gerando executáveis. O código é interpretado diretamente.

**1. Pré-requisitos:**
Certifique-se de ter o Python 3 instalado em sua máquina

**2. Execução:**
Abra o terminal de sua preferência, navegue até a pasta onde o arquivo se encontra e execute o script com o comando abaixo:
`python algoritmo_subst-pag_working-set-clock.py`

## ⚙️ O que o programa faz?
Ao rodar o script, ele não exige interação do usuário. Ele executa automaticamente um cenário de simulação programado no final do código

O console exibirá um relatório passo a passo contendo:
1. As configurações iniciais do buffer 
2. Uma lista de requisições sequenciais da CPU 
3. O diagnóstico de cada requisição: se houve um Page Hit ou um Page Fault 
4. As decisões do WSClock: detalhamento de qual página foi escolhida para ser substituída e o porquê 
5. O estado interno do buffer circular exibindo a posição do ponteiro após cada ciclo
6. O totalizador de Page Faults ao final do processo
