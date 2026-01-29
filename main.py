import pygame, sys, random, json, os
pygame.init()

LARGURA, ALTURA = 640, 800
FPS = 60

TAM_JOGADOR = 40
PASSO_X = TAM_JOGADOR
PASSO_Y = 70
JOGADOR_POS_INICIAL = (LARGURA // 2, ALTURA - TAM_JOGADOR - 10)
COR_JOGADOR = (50, 200, 50)

QTD_FAIXAS = 7
FAIXA_ALTURA = PASSO_Y
TOPO_FAIXA = 80
ESPACAMENTO_FAIXA = 0

CARRO_LARGURA = TAM_JOGADOR
CARRO_ALTURA = TAM_JOGADOR
CARRO_COR = (220, 50, 50)

ESPACAMENTO_GRUPO = 6

BRANCO = (255,255,255)
PRETO = (0,0,0)
CINZA = (120,120,120)
AZUL_ESCURO = (10,10,50)
FUNDO = (30,160,200)

ESTADO_MENU = "menu"
ESTADO_JOGANDO = "jogando"
ESTADO_INFO = "info"
ESTADO_VITORIA = "vitoria"
ESTADO_RANKING = "ranking"
ESTADO_GAMEOVER = "gameover"
ESTADO_PAUSADO = "pausado"

estado = ESTADO_MENU

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 56)

inicio_tempo_ms = None
pausa_inicio_ms = None

BTN_W, BTN_H = 220, 56
BTN_SPACING = 24
center_x = LARGURA // 2

PASTA_RANKING = "ranking.json"
PADROES_FAIXA_POR_FASE = {
    1: [
        [(4, 1000), (2, 1000), (2, 1000)],
        [(3, 2000), (4, 2200), (3,2400)],
        [(0,0)],
        [(3,1300), (2,1300)],
        [(0,0)],
        [(3,2000), (3,2000)],
        [(4,1250), (2,2500)]
    ],
    2: [
        [(2,1000), (4,1000), (2,1000)],
        [(4,1000), (2,1500)],
        [(0,0)],
        [(3,1100), (4,2000)],
        [(4,1200), (3,1200)],
        [(0,0)],
        [(4,1000), (2,1800)],
        [(3,1500), (2,1500)],
        [(2,1200), (2,1200), (2,1200), (2,1000)]
    ]
}

VELOCIDADES_FAIXA_POR_FASE = {
    1: [200, 180, 160, 140, 120, 100, 80],
    2: [240, 240, 220, 200, 180, 160, 160, 140, 120]
}

class Botao:
    def __init__(self, rect, texto):
        self.rect = pygame.Rect(rect)
        self.texto = texto
    def desenhar(self, surf):
        pygame.draw.rect(surf, CINZA, self.rect)
        txt = font.render(self.texto, True, PRETO)
        surf.blit(txt, (self.rect.centerx - txt.get_width() // 2, self.rect.centery - txt.get_height() // 2))
    def clicado(self, mx, my):
        return self.rect.collidepoint(mx,my)

class Jogador(pygame.sprite.Sprite):
    def __init__(self, start_pos):
        super().__init__()
        self.surf = pygame.Surface((TAM_JOGADOR, TAM_JOGADOR))
        self.surf.fill(COR_JOGADOR)
        self.rect = self.surf.get_rect(center=start_pos)
        self.vidas = 3

    def movimentacao(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(LARGURA, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(ALTURA, self.rect.bottom)

    def reseta_comeco(self):
        self.rect.midbottom = (LARGURA // 2, ALTURA - 30)

class Carro(pygame.sprite.Sprite):
    def __init__(self, centro_y, direcao, vel):
        super().__init__()
        self.surf = pygame.Surface((CARRO_LARGURA, CARRO_ALTURA))
        self.surf.fill(CARRO_COR)
        self.rect = self.surf.get_rect()
        self.rect.centery = centro_y
        self.direcao = direcao
        self.vel = vel
        if direcao == 1:
            self.rect.left = -CARRO_LARGURA - 10
        else:
            self.rect.right = LARGURA + 10

    def update(self, dt):
        self.rect.x += int(self.vel * self.direcao * dt)
        if self.direcao == 1 and self.rect.left > LARGURA + 200:
            self.kill()
        if self.direcao == -1 and self.rect.right < -200:
            self.kill()

class FaixaController:
    def __init__(self, faixa_index, topo_y, direcao, vel, formato_grupo):
        self.faixa_index = faixa_index
        self.centro_y = topo_y + FAIXA_ALTURA // 2
        self.direcao = direcao
        self.vel = vel
        self.formato = formato_grupo
        self.formato_idx = 0
        self.estado = "waiting"
        self.prox_acao = pygame.time.get_ticks()

    def update(self, agora_ms, grupo_carros):
        if self.estado == "waiting":
            if agora_ms >= self.prox_acao:
                self.estado = "spawning_group"
        elif self.estado == "spawning_group":
            conta, espera = self.formato[self.formato_idx]
            for i in range(conta):
                novo_carro = Carro(self.centro_y, self.direcao, self.vel)
                if self.direcao == 1:
                    novo_carro.rect.left = -CARRO_LARGURA - 10 - i * (CARRO_LARGURA + ESPACAMENTO_GRUPO)
                else:
                    novo_carro.rect.right = LARGURA + 10 + i * (CARRO_LARGURA + ESPACAMENTO_GRUPO)
                grupo_carros.add(novo_carro)
            self.prox_acao = agora_ms + espera
            self.formato_idx = (self.formato_idx + 1) % len(self.formato)
            self.estado = "waiting"

def criacao_inicial_grupos(grupo_carros, controladores):
    for ctrl in controladores:
        conta, espera = ctrl.formato[ctrl.formato_idx]
        if conta <= 0:
            ctrl.prox_acao = pygame.time.get_ticks() + espera
            continue
        total_group_largura = conta * CARRO_LARGURA + max(0, (conta - 1)) * ESPACAMENTO_GRUPO
        min_cx = int(LARGURA * 0.2)
        max_cx = int(LARGURA * 0.8)
        alvo_cx = random.randint(min_cx, max_cx)
        primeira_esquerda = alvo_cx - total_group_largura // 2
        for i in range(conta):
            novo_carro = Carro(ctrl.centro_y, ctrl.direcao, ctrl.vel)
            if ctrl.direcao == 1:
                novo_carro.rect.left = int(primeira_esquerda + i * (CARRO_LARGURA + ESPACAMENTO_GRUPO))
            else:
                direita_desejada = primeira_esquerda + total_group_largura
                novo_carro.rect.right = int(direita_desejada - i * (CARRO_LARGURA + ESPACAMENTO_GRUPO))
            grupo_carros.add(novo_carro)
        ctrl.prox_acao = pygame.time.get_ticks() + espera

def construir_controladores_por_fase(fase):
    controladores = []
    if fase == 1:
        qtd_faixas = 7
        padroes = PADROES_FAIXA_POR_FASE.get(1, [])
        velocidades = VELOCIDADES_FAIXA_POR_FASE.get(1, [])
    else:
        qtd_faixas = 9
        padroes = PADROES_FAIXA_POR_FASE.get(2, [])
        velocidades = VELOCIDADES_FAIXA_POR_FASE.get(2, [])

    for i in range(qtd_faixas):
        y_top = TOPO_FAIXA + i * (FAIXA_ALTURA + ESPACAMENTO_FAIXA)
        direcao = 1 if (i % 2 == 0) else -1
        if random.random() < 0.5:
            direcao *= -1

        if i < len(velocidades):
            base_vel = velocidades[i]
        else:
            base_vel = 120 + i * 25

        if i < len(padroes):
            formato = padroes[i]
        else:
            formato = [(3,1500)]

        ctrl = FaixaController(i, y_top, direcao, base_vel, formato)
        ctrl.prox_acao = pygame.time.get_ticks() + random.randint(0,1500)
        controladores.append(ctrl)
    return controladores

def resetar_estado_fase(fase):
    global carros, faixa_controladores
    carros.empty()
    faixa_controladores = construir_controladores_por_fase(fase)
    criacao_inicial_grupos(carros, faixa_controladores)
    jog.reseta_comeco()

def verificar_colisoes_e_reset(jogador, carros, controladores):
    colisao = pygame.sprite.spritecollideany(jogador, carros)
    if colisao:
        jogador.reseta_comeco()
        carros.empty()
        novas_controladores = construir_controladores_por_fase(fase)
        criacao_inicial_grupos(carros, novas_controladores)
        controladores[:] = novas_controladores
        return True
    return False

def carregar_ranking():
    if not os.path.exists(PASTA_RANKING):
        return []
    try:
        with open(PASTA_RANKING, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                data_sorted = sorted(data, key=lambda x: x.get("time", float("inf")))
                return data_sorted[:10]
    except Exception:
        pass
    return []

def salvar_ranking(entries):
    try:
        entries_sorted = sorted(entries, key=lambda x: x.get("time", float("inf")))[:10]
        with open(PASTA_RANKING, "w", encoding="utf-8") as f:
            json.dump(entries_sorted, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Erro salvando ranking:", e)

jog = Jogador(JOGADOR_POS_INICIAL)
jog.reseta_comeco()

carros = pygame.sprite.Group()
fase = 1
faixa_controladores = construir_controladores_por_fase(fase)
criacao_inicial_grupos(carros, faixa_controladores)

btn_jogar = Botao((center_x - BTN_W//2, 320+ (BTN_H + 28)/20, BTN_W, BTN_H), "Jogar")
btn_info = Botao((center_x - BTN_W//2, 320 + BTN_H + 28, BTN_W, BTN_H), "Informações")
btn_sair = Botao((center_x - BTN_W//2, 320 + (BTN_H + 28)*2, BTN_W, BTN_H), "Sair")

btn_reiniciar_ranking = Botao((60, ALTURA - 120, 200, 48), "Reinício rápido (R)")
btn_voltar_menu_ranking = Botao((LARGURA - 260, ALTURA - 120, 200, 48), "Voltar ao Menu (ESC)")

btn_reiniciar_gameover = Botao((center_x - 240, 360, 200, 56), "Reinício rápido (R)")
btn_voltar_menu_gameover = Botao((center_x + 40, 360, 200, 56), "Voltar ao Menu (ESC)")

btn_continuar = Botao((center_x - BTN_W//2, 300, BTN_W, BTN_H), "Continuar (ESC)")
btn_voltar_menu_pausa = Botao((center_x - BTN_W//2, 300 + BTN_H + 20, BTN_W, BTN_H), "Voltar ao Menu")

tempo_vitoria_secs = 0.0
nome_input = ""

running = True
while running:
    dt_ms = clock.tick(FPS)
    dt = dt_ms / 1000.0
    agora_ms = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if estado == ESTADO_RANKING:
                if event.key == pygame.K_ESCAPE:
                    estado = ESTADO_MENU
                    continue
                if event.key == pygame.K_r:
                    fase = 1
                    jog.vidas = 3
                    resetar_estado_fase(fase)
                    jog.reseta_comeco()
                    estado = ESTADO_JOGANDO
                    inicio_tempo_ms = pygame.time.get_ticks()
                    continue

            if estado == ESTADO_GAMEOVER:
                if event.key == pygame.K_ESCAPE:
                    estado = ESTADO_MENU
                    continue
                if event.key == pygame.K_r:
                    fase = 1
                    jog.vidas = 3
                    resetar_estado_fase(fase)
                    jog.reseta_comeco()
                    estado = ESTADO_JOGANDO
                    inicio_tempo_ms = pygame.time.get_ticks()
                    continue

            if estado == ESTADO_VITORIA:
                if event.key == pygame.K_BACKSPACE:
                    nome_input = nome_input[:-1]
                elif event.key == pygame.K_RETURN:
                    entries = carregar_ranking()
                    entries.append({"name": nome_input if nome_input.strip() != "" else "Anon", "time": round(tempo_vitoria_secs, 3)})
                    salvar_ranking(entries)
                    nome_input = ""
                    estado = ESTADO_RANKING
                else:
                    if len(nome_input) < 16:
                        ch = event.unicode
                        if ch.isprintable():
                            nome_input += ch
                continue

            if estado == ESTADO_PAUSADO:
                if event.key == pygame.K_ESCAPE:
                    if pausa_inicio_ms is not None and inicio_tempo_ms is not None:
                        delta = agora_ms - pausa_inicio_ms
                        inicio_tempo_ms += delta
                    pausa_inicio_ms = None
                    estado = ESTADO_JOGANDO
                    continue
                if event.key == pygame.K_r:
                    fase = 1
                    jog.vidas = 3
                    resetar_estado_fase(fase)
                    jog.reseta_comeco()
                    inicio_tempo_ms = pygame.time.get_ticks()
                    pausa_inicio_ms = None
                    estado = ESTADO_JOGANDO
                    continue
                if event.key == pygame.K_m:
                    pausa_inicio_ms = None
                    inicio_tempo_ms = None
                    estado = ESTADO_MENU
                    continue

            if estado == ESTADO_JOGANDO:
                if event.key == pygame.K_ESCAPE:
                    estado = ESTADO_PAUSADO
                    pausa_inicio_ms = agora_ms
                    continue
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    jog.movimentacao(-PASSO_X, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    jog.movimentacao(PASSO_X, 0)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    jog.movimentacao(0, -PASSO_Y)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    jog.movimentacao(0, PASSO_Y)
            elif estado == ESTADO_MENU:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif estado == ESTADO_INFO:
                if event.key == pygame.K_ESCAPE:
                    estado = ESTADO_MENU

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx,my = event.pos
            if estado == ESTADO_MENU:
                if btn_jogar.clicado(mx,my):
                    fase = 1
                    resetar_estado_fase(fase)
                    jog.reseta_comeco()
                    jog.vidas = 3
                    estado = ESTADO_JOGANDO
                    inicio_tempo_ms = pygame.time.get_ticks()
                elif btn_info.clicado(mx,my):
                    estado = ESTADO_INFO
                elif btn_sair.clicado(mx,my):
                    running = False
            elif estado == ESTADO_INFO:
                estado = ESTADO_MENU
            elif estado == ESTADO_RANKING:
                if btn_reiniciar_ranking.clicado(mx, my):
                    fase = 1
                    jog.vidas = 3
                    resetar_estado_fase(fase)
                    jog.reseta_comeco()
                    estado = ESTADO_JOGANDO
                    inicio_tempo_ms = pygame.time.get_ticks()
                if btn_voltar_menu_ranking.clicado(mx, my):
                    estado = ESTADO_MENU
            elif estado == ESTADO_GAMEOVER:
                if btn_reiniciar_gameover.clicado(mx, my):
                    fase = 1
                    jog.vidas = 3
                    resetar_estado_fase(fase)
                    jog.reseta_comeco()
                    estado = ESTADO_JOGANDO
                    inicio_tempo_ms = pygame.time.get_ticks()
                if btn_voltar_menu_gameover.clicado(mx, my):
                    estado = ESTADO_MENU
            elif estado == ESTADO_PAUSADO:
                if btn_continuar.clicado(mx, my):
                    if pausa_inicio_ms is not None and inicio_tempo_ms is not None:
                        delta = pygame.time.get_ticks() - pausa_inicio_ms
                        inicio_tempo_ms += delta
                    pausa_inicio_ms = None
                    estado = ESTADO_JOGANDO
                if btn_voltar_menu_pausa.clicado(mx, my):
                    pausa_inicio_ms = None
                    inicio_tempo_ms = None
                    estado = ESTADO_MENU

    if estado == ESTADO_JOGANDO:
        for ctrl in faixa_controladores:
            ctrl.update(agora_ms, carros)
        for c in list(carros):
            c.update(dt)
        houve_colisao = verificar_colisoes_e_reset(jog, carros, faixa_controladores)
        if houve_colisao:
            jog.vidas -= 1
            if jog.vidas <= 0:
                estado = ESTADO_GAMEOVER
                inicio_tempo_ms = None

        if jog.rect.top <= TOPO_FAIXA:
            if fase == 1:
                fase = 2
                resetar_estado_fase(fase)
            else:
                if inicio_tempo_ms is None:
                    tempo_vitoria_secs = 0.0
                else:
                    tempo_vitoria_secs = (pygame.time.get_ticks() - inicio_tempo_ms) / 1000.0
                nome_input = ""
                estado = ESTADO_VITORIA
                inicio_tempo_ms = None

    tela.fill(FUNDO)

    if estado == ESTADO_MENU:
        titulo = big_font.render("CROSSY CLONE", True, BRANCO)
        tela.blit(titulo, ((LARGURA - titulo.get_width()) // 2, 120))
        btn_jogar.desenhar(tela)
        btn_info.desenhar(tela)
        btn_sair.desenhar(tela)

    elif estado == ESTADO_INFO:
        linhas = [
            "Como jogar:",
            "- Use as setas ou WASD para mover por passos (um passo por tecla).",
            "- Pressione ESC durante o jogo para pausar.",
            "- Objetivo: evitar os carros e atravessar as faixas.",
            "- Clique para voltar ao Menu."
        ]
        y = 120
        for ln in linhas:
            txt = font.render(ln, True, BRANCO)
            tela.blit(txt, (40,y))
            y += 36

    elif estado == ESTADO_JOGANDO:
        num_faixas_para_desenhar = len(faixa_controladores) if 'faixa_controladores' in globals() else QTD_FAIXAS

        topo = pygame.Rect(0, 0, LARGURA, TOPO_FAIXA)
        pygame.draw.rect(tela, AZUL_ESCURO, topo)

        for i in range(num_faixas_para_desenhar):
            r = pygame.Rect(0, TOPO_FAIXA + i*(FAIXA_ALTURA+ESPACAMENTO_FAIXA), LARGURA, FAIXA_ALTURA)
            pygame.draw.rect(tela, CINZA, r)
            pygame.draw.line(tela, PRETO, (0, r.top), (LARGURA, r.top), 2)

        for c in carros:
            tela.blit(c.surf, c.rect)
        tela.blit(jog.surf, jog.rect)

        texto_vidas = font.render(f"Vidas: {jog.vidas}  Fase: {fase}", True, BRANCO)
        tela.blit(texto_vidas, (10, 10))

        if inicio_tempo_ms is None:
            tempo_decorrido = 0.0
        else:
            tempo_decorrido = (pygame.time.get_ticks() - inicio_tempo_ms) / 1000.0

        texto_tempo = font.render(f"Tempo: {tempo_decorrido:.2f}s", True, BRANCO)
        x_tempo = LARGURA - texto_tempo.get_width() - 10
        tela.blit(texto_tempo, (x_tempo, 10))

    elif estado == ESTADO_PAUSADO:
        topo = pygame.Rect(0, 0, LARGURA, TOPO_FAIXA)
        pygame.draw.rect(tela, AZUL_ESCURO, topo)
        num_faixas_para_desenhar = len(faixa_controladores) if 'faixa_controladores' in globals() else QTD_FAIXAS
        for i in range(num_faixas_para_desenhar):
            r = pygame.Rect(0, TOPO_FAIXA + i*(FAIXA_ALTURA+ESPACAMENTO_FAIXA), LARGURA, FAIXA_ALTURA)
            pygame.draw.rect(tela, CINZA, r)
            pygame.draw.line(tela, PRETO, (0, r.top), (LARGURA, r.top), 2)
        for c in carros:
            tela.blit(c.surf, c.rect)
        tela.blit(jog.surf, jog.rect)

        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s.fill((0,0,0,140))
        tela.blit(s, (0,0))

        titulo = big_font.render("PAUSADO", True, BRANCO)
        tela.blit(titulo, ((LARGURA - titulo.get_width()) // 2, 120))

        btn_continuar.desenhar(tela)
        btn_voltar_menu_pausa.desenhar(tela)

        instr = font.render("Pressione ESC para continuar, R para reiniciar, ou clique nos botões.", True, BRANCO)
        tela.blit(instr, ((LARGURA - instr.get_width()) // 2, 480))

    elif estado == ESTADO_VITORIA:
        titulo = big_font.render("VOCÊ VENCEU!", True, BRANCO)
        tela.blit(titulo, ((LARGURA - titulo.get_width()) // 2, 120))

        t = font.render(f"Seu tempo: {tempo_vitoria_secs:.3f}s", True, BRANCO)
        tela.blit(t, ((LARGURA - t.get_width()) // 2, 200))

        prompt = font.render("Digite seu nome e pressione Enter:", True, BRANCO)
        tela.blit(prompt, ((LARGURA - prompt.get_width()) // 2, 260))

        box = pygame.Rect((LARGURA//2 - 200, 320, 400, 40))
        pygame.draw.rect(tela, (240,240,240), box)
        pygame.draw.rect(tela, PRETO, box, 2)
        name_surf = font.render(nome_input, True, PRETO)
        tela.blit(name_surf, (box.x + 8, box.y + 8))

    elif estado == ESTADO_RANKING:
        titulo = big_font.render("RANKING", True, BRANCO)
        tela.blit(titulo, ((LARGURA - titulo.get_width()) // 2, 20))

        entries = carregar_ranking()
        y = 100
        rank = 1
        for e in entries:
            line = f"{rank}. {e['name']} - {e['time']:.3f}s"
            t = font.render(line, True, BRANCO)
            tela.blit(t, (60, y))
            y += 28
            rank += 1

        btn_reiniciar_ranking.desenhar(tela)
        btn_voltar_menu_ranking.desenhar(tela)

    elif estado == ESTADO_GAMEOVER:
        titulo = big_font.render("GAME OVER", True, BRANCO)
        tela.blit(titulo, ((LARGURA - titulo.get_width()) // 2, 120))

        mensagem = font.render("Você perdeu todas as vidas.", True, BRANCO)
        tela.blit(mensagem, ((LARGURA - mensagem.get_width()) // 2, 200))

        btn_reiniciar_gameover.desenhar(tela)
        btn_voltar_menu_gameover.desenhar(tela)

    pygame.display.flip()

pygame.quit()
sys.exit()