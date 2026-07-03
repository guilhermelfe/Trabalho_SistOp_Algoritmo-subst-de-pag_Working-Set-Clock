
# Algoritmo de Substituição de Páginas: WSClock (Working Set Clock)

# Este código simula o gerenciamento de memória de um Sistema Operacional.
# O objetivo do WSClock é decidir qual página deve ser removida da memória principal (RAM)
# quando ela está cheia e uma nova página precisa ser carregada do disco. Ele faz isso de forma eficiente usando uma lista circular

class Pagina:
    """
    Representa um bloco de dados (página) armazenado na memória física (RAM).
    """
    def __init__(self, id_pagina, tempo_virtual, modo_escrita=False):
        self.id = id_pagina # Identificador único da página
        
        # O bit de referência (R) indica se a página foi acessada recentemente.
        # Inicializa como 1 (acabou de ser carregada/acessada).
        self.bit_referencia = 1      
        
        # O bit de modificação (M), indica se a página foi alterada.
        # Se for 1, a página sofreu escrita e precisa ser salva no disco antes de ser removida.
        self.bit_modificacao = 1 if modo_escrita else 0 
        
        # Registra o tempo exato (relógio lógico) em que a página foi utilizada.
        self.ultimo_acesso = tempo_virtual 

    def __repr__(self):
        # Formata a impressão da página no console para facilitar a visualização do estado.
        return f"[ID:{self.id}|R:{self.bit_referencia}|M:{self.bit_modificacao}|T:{self.ultimo_acesso}]"

class MemoriaWSClock:
    """
    Gerenciador da memória que implementa a lógica do algoritmo circular WSClock.
    """
    def __init__(self, capacidade_buffer, tau):
        self.capacidade = capacidade_buffer # Quantidade máxima de páginas que cabem na RAM
        self.tau = tau # Tempo limite do Working Set (janela de tempo de uso ativo)
        self.buffer = [] # Estrutura que funciona como a memória RAM (lista circular)
        self.ponteiro = 0 # Ponteiro do relógio que varre as páginas para substituição
        self.tempo_virtual = 0 # Relógio lógico da CPU que avança a cada operação
        self.page_faults = 0 # Contador de falhas de página (quando a página não está na RAM)

    def acessar_pagina(self, id_pagina, modo_escrita=False):
        """
        Simula a CPU solicitando leitura ou escrita em uma página específica.
        """
        # A cada requisição, o tempo lógico do sistema avança um "tick".
        self.tempo_virtual += 1
        
        # 1. VERIFICAÇÃO DE HIT: A página já está na memória?
        for i, pagina in enumerate(self.buffer):
            if pagina.id == id_pagina:
                # HIT: A página foi encontrada. Atualiza os status para indicar uso recente.
                pagina.bit_referencia = 1
                pagina.ultimo_acesso = self.tempo_virtual
                if modo_escrita:
                    pagina.bit_modificacao = 1
                print(f"Tempo {self.tempo_virtual:02d}: HIT -> Página {id_pagina} acessada.")
                return

        # 2. PAGE FAULT: A página não está na memória e precisa vir do disco.
        self.page_faults += 1
        nova_pagina = Pagina(id_pagina, self.tempo_virtual, modo_escrita)

        # Se ainda há espaço vazio no buffer (RAM não está cheia), apenas insere no final.
        if len(self.buffer) < self.capacidade:
            self.buffer.append(nova_pagina)
            print(f"Tempo {self.tempo_virtual:02d}: FAULT -> Página {id_pagina} carregada. (Buffer não cheio)")
            return

        # 3. BUFFER CHEIO: Aciona o WSClock para escolher quem será removido.
        self._substituir_pagina(nova_pagina)

    def _substituir_pagina(self, nova_pagina):
        """
        Núcleo do Algoritmo WSClock: Varrer a lista circular e encontrar uma vítima.
        """
        varreduras = 0
        # Define um limite de varreduras para evitar que o SO trave em um loop infinito.
        limite_varreduras = self.capacidade * 2 

        while True:
            # Pega a página que está na posição atual do ponteiro do relógio
            pagina_atual = self.buffer[self.ponteiro]
            
            # Calcula o tempo que a página está sem ser acessada (idade)
            idade = self.tempo_virtual - pagina_atual.ultimo_acesso

            # REGRA 1: O bit de referência é 1?
            if pagina_atual.bit_referencia == 1:
                # Segunda Chance: A página foi usada recentemente. 
                # O SO dá uma nova chance zerando o bit R e atualizando o tempo, e não a remove agora.
                pagina_atual.bit_referencia = 0
                pagina_atual.ultimo_acesso = self.tempo_virtual
            
            # REGRA 2: O bit de referência é 0.
            else:
                # Verifica se a página ainda faz parte do Working Set.
                if idade > self.tau:
                    # A página é mais velha que o tau, está fora do Working Set. É uma candidata.
                    
                    if pagina_atual.bit_modificacao == 0:
                        # Página Limpa (M=0): Não precisa ser salva no disco. 
                        # É a vítima perfeita. Remove a antiga e insere a nova no lugar.
                        print(f"Tempo {self.tempo_virtual:02d}: FAULT -> Substituindo pág {pagina_atual.id} (Limpa/Fora do WS) pela pág {nova_pagina.id}.")
                        self.buffer[self.ponteiro] = nova_pagina
                        self._avancar_ponteiro() # Move o ponteiro para a próxima casa
                        return
                    
                    else:
                        # Página Suja (M=1): Foi modificada e precisa ser gravada no disco antes de sair.
                        # O SO agenda a gravação. Na simulação, limpamos o bit M simulando que gravou.
                        print(f"Tempo {self.tempo_virtual:02d}: SC -> Agendando gravação no disco pág {pagina_atual.id} e limpando bit M.")
                        pagina_atual.bit_modificacao = 0

            # Avança o ponteiro do relógio para analisar a próxima página
            self._avancar_ponteiro()
            varreduras += 1

            # FALLBACK DE SEGURANÇA: Se varreu a memória inteira e não achou uma página adequada para substituição
            # (todas em uso ou aguardando disco), força a substituição da página atual para não travar.
            if varreduras >= limite_varreduras:
                alvo = self.buffer[self.ponteiro]
                print(f"Tempo {self.tempo_virtual:02d}: FAULT -> Fallback forçado. Substituindo pág {alvo.id} pela pág {nova_pagina.id}.")
                self.buffer[self.ponteiro] = nova_pagina
                self._avancar_ponteiro()
                return

    def _avancar_ponteiro(self):
        """
        Avança o ponteiro simulando o comportamento circular de um relógio.
        O operador módulo (%) faz com que, ao chegar no final da lista, o ponteiro volte a zero.
        """
        self.ponteiro = (self.ponteiro + 1) % self.capacidade

    def exibir_estado(self):
        """
        Imprime o estado atual do buffer de memória para acompanhamento da simulação.
        """
        estado = "\nEstado atual do Buffer (Ponteiro no índice {}):\n".format(self.ponteiro)
        for i, pag in enumerate(self.buffer):
            # Adiciona uma seta '->' apontando exatamente onde o ponteiro do relógio está parado
            marcador = " -> " if i == self.ponteiro else "    "
            estado += f"{marcador}Índice {i}: {pag}\n"
        print(estado + "-"*40)



### Simulação de Execução ###

if __name__ == "__main__":
    # Configura um hardware simulado: 4 espaços na memória RAM e janela WS de 3 ciclos.
    memoria = MemoriaWSClock(capacidade_buffer=4, tau=3)

    # Lista de processos que a CPU tentará executar (ID da Página, Requer Escrita?)
    operacoes = [
        (1, False), # Tempo 1: Carrega pág 1 para Leitura (M=0)
        (2, True),  # Tempo 2: Carrega pág 2 para Escrita (M=1)
        (3, False), # Tempo 3: Carrega pág 3 para Leitura
        (4, True),  # Tempo 4: Carrega pág 4 para Escrita (M=1) - A memória fica cheia aqui!
        (1, False), # Tempo 5: CPU tenta ler a pág 1 (Já está na memória -> HIT)
        (5, False), # Tempo 6: Falta de página! Pág 5 não está na RAM, força substituição.
        (2, False), # Tempo 7: CPU tenta ler a pág 2.
        (6, True),  # Tempo 8: Falta de página para a Pág 6. Requer gravação no buffer.
    ]

    print("Iniciando simulação do WSClock...")
    print(f"Capacidade: {memoria.capacidade} páginas | Janela (Tau): {memoria.tau}\n")

    # Percorre as operações simulando os ciclos de trabalho
    for id_pag, modo_esc in operacoes:
        acao = "Escrita" if modo_esc else "Leitura"
        print(f"\n Requisição: Página {id_pag} ({acao})")
        
        # Chama a função de acesso principal
        memoria.acessar_pagina(id_pag, modo_escrita=modo_esc)
        
        # Mostra o resultado visual após a operação
        memoria.exibir_estado()

    # Ao final, exibe a contagem total de falhas de página que ocorreram.
    print(f"\nResumo: Total de Page Faults na simulação: {memoria.page_faults}")