class Pagina:
    def __init__(self, id_pagina, tempo_virtual, modo_escrita=False):
        self.id = id_pagina
        self.bit_referencia = 1      # (R) 1 quando acessada, 0 quando varrida pelo ponteiro
        self.bit_modificacao = 1 if modo_escrita else 0 # (M) 1 se sofreu escrita (dirty)
        self.ultimo_acesso = tempo_virtual # Tempo do último uso

    def __repr__(self):
        return f"[ID:{self.id}|R:{self.bit_referencia}|M:{self.bit_modificacao}|T:{self.ultimo_acesso}]"

class MemoriaWSClock:
    def __init__(self, capacidade_buffer, tau):
        self.capacidade = capacidade_buffer
        self.tau = tau # Tempo limite que define o Working Set (se idade <= tau, está no WS)
        self.buffer = [] # Lista circular de páginas
        self.ponteiro = 0 # Ponteiro do relógio (hand)
        self.tempo_virtual = 0 # Relógio lógico da CPU
        self.page_faults = 0

    def acessar_pagina(self, id_pagina, modo_escrita=False):
        self.tempo_virtual += 1
        
        # 1. Verifica se a página já está no buffer (Hit)
        for i, pagina in enumerate(self.buffer):
            if pagina.id == id_pagina:
                pagina.bit_referencia = 1
                pagina.ultimo_acesso = self.tempo_virtual
                if modo_escrita:
                    pagina.bit_modificacao = 1
                print(f"Tempo {self.tempo_virtual:02d}: HIT -> Página {id_pagina} acessada.")
                return

        # 2. Page Fault (Página não está no buffer)
        self.page_faults += 1
        nova_pagina = Pagina(id_pagina, self.tempo_virtual, modo_escrita)

        # Se houver espaço livre no buffer, apenas adiciona
        if len(self.buffer) < self.capacidade:
            self.buffer.append(nova_pagina)
            print(f"Tempo {self.tempo_virtual:02d}: FAULT -> Página {id_pagina} carregada. (Buffer não cheio)")
            return

        # 3. Buffer cheio: Executa o algoritmo WSClock para substituição
        self._substituir_pagina(nova_pagina)

    def _substituir_pagina(self, nova_pagina):
        varreduras = 0
        limite_varreduras = self.capacidade * 2 # Evita loop infinito caso todas estejam no WS ou modificadas

        while True:
            pagina_atual = self.buffer[self.ponteiro]
            idade = self.tempo_virtual - pagina_atual.ultimo_acesso

            if pagina_atual.bit_referencia == 1:
                # Recebeu uma 2ª chance: zera o bit R e atualiza o tempo
                pagina_atual.bit_referencia = 0
                pagina_atual.ultimo_acesso = self.tempo_virtual
            else:
                # bit_referencia == 0
                if idade > self.tau:
                    # Página não faz mais parte do Working Set
                    if pagina_atual.bit_modificacao == 0:
                        # Página limpa (Clean): Substituição ideal
                        print(f"Tempo {self.tempo_virtual:02d}: FAULT -> Substituindo pág {pagina_atual.id} (Limpa/Fora do WS) pela pág {nova_pagina.id}.")
                        self.buffer[self.ponteiro] = nova_pagina
                        self._avancar_ponteiro()
                        return
                    else:
                        # Página suja (Dirty): Agenda escrita no disco. 
                        # Na simulação, limpamos o bit M para fingir que a gravação terminou.
                        print(f"Tempo {self.tempo_virtual:02d}: SC -> Agendando gravação no disco pág {pagina_atual.id} e limpando bit M.")
                        pagina_atual.bit_modificacao = 0

            self._avancar_ponteiro()
            varreduras += 1

            # Fallback (Margem de erro realista): Se varrermos o relógio inteiro e todas as páginas 
            # estiverem em uso intenso (dentro do tau) ou aguardando disco, forçamos a troca
            # da página atual apontada para não travar o sistema.
            if varreduras >= limite_varreduras:
                alvo = self.buffer[self.ponteiro]
                print(f"Tempo {self.tempo_virtual:02d}: FAULT -> Fallback forçado. Substituindo pág {alvo.id} pela pág {nova_pagina.id}.")
                self.buffer[self.ponteiro] = nova_pagina
                self._avancar_ponteiro()
                return

    def _avancar_ponteiro(self):
        self.ponteiro = (self.ponteiro + 1) % self.capacidade

    def exibir_estado(self):
        estado = "\nEstado atual do Buffer (Ponteiro no índice {}):\n".format(self.ponteiro)
        for i, pag in enumerate(self.buffer):
            marcador = " -> " if i == self.ponteiro else "    "
            estado += f"{marcador}Índice {i}: {pag}\n"
        print(estado + "-"*40)


# ==========================================
# Simulação de Uso
# ==========================================
if __name__ == "__main__":
    # Inicializa memória com capacidade para 4 páginas e tau (janela do WS) igual a 3 tempos lógicos
    memoria = MemoriaWSClock(capacidade_buffer=4, tau=3)

    # Sequência de operações: (ID da Página, É Escrita?)
    operacoes = [
        (1, False), # Tempo 1: Carrega pág 1 (Leitura)
        (2, True),  # Tempo 2: Carrega pág 2 (Escrita - M=1)
        (3, False), # Tempo 3: Carrega pág 3
        (4, True),  # Tempo 4: Carrega pág 4 (Escrita - M=1) - Buffer enche aqui
        (1, False), # Tempo 5: Acessa pág 1 (Hit)
        (5, False), # Tempo 6: Falta de página! Requer substituição.
        (2, False), # Tempo 7: Tenta acessar a pág 2
        (6, True),  # Tempo 8: Falta de página! (Escrita)
    ]

    print("Iniciando simulação do WSClock...")
    print(f"Capacidade: {memoria.capacidade} páginas | Janela (Tau): {memoria.tau}\n")

    for id_pag, modo_esc in operacoes:
        acao = "Escrita" if modo_esc else "Leitura"
        print(f"\n--- Requisição: Página {id_pag} ({acao}) ---")
        memoria.acessar_pagina(id_pag, modo_escrita=modo_esc)
        memoria.exibir_estado()

    print(f"\nResumo: Total de Page Faults na simulação: {memoria.page_faults}")