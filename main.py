import pygame, sys, random, json, os
pygame.init()

# Constantes e configurações
LARGURA, ALTURA = 640, 800
FPS = 60

# Configurações do jogo
TAM_JOGADOR = 40
PASSO_X = TAM_JOGADOR
PASSO_Y = 70
JOGADOR_POS_INICIAL = (LARGURA // 2, ALTURA - TAM_JOGADOR - 10)
COR_JOGADOR = (50, 200, 50)

# Configurações das faixas e carros
QTD_FAIXAS = 7
FAIXA_ALTURA = PASSO_Y
TOPO_FAIXA = 80
ESPACAMENTO_FAIXA = 0
CARRO_LARGURA = TAM_JOGADOR
CARRO_ALTURA = TAM_JOGADOR
CARRO_COR = (220, 50, 50)
ESPACAMENTO_GRUPO = 6

# Cores
BRANCO = (255,255,255)
PRETO = (0,0,0)
CINZA = (120,120,120)
AZUL_ESCURO = (10,10,50)
FUNDO = (30,160,200)

# Estados do jogo
ESTADO_MENU = "menu"
ESTADO_PREPARO = "preparo"
ESTADO_JOGANDO = "jogando"
ESTADO_INFO = "info"
ESTADO_VITORIA = "vitoria"
ESTADO_RANKING = "ranking"
ESTADO_GAMEOVER = "gameover"
ESTADO_PAUSADO = "pausado"
ESTADO_INFINITO_NOME = "inf_nome"
ESTADO_RANKING_INFINITO = "ranking_inf"

PASTA_RANKING = "ranking.json"
PASTA_RANKING_INFINITO = "ranking_infinito.json"

estado = ESTADO_MENU

# modo atual: 'campanha' ou 'infinito'
modo_jogo = None

# Inicialização do Pygame
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
info_font = pygame.font.SysFont(None, 28)
vitoria_font = pygame.font.SysFont(None, 30)
vitoria_tempo_font = pygame.font.SysFont(None, 36)
rank_font_campanha = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 64)
rank_font = pygame.font.SysFont(None, 32)

# Variáveis de tempo
inicio_tempo_ms = None
pausa_inicio_ms = None

# Botões
BOTAO_LARGURA, BOTAO_ALTURA = 240, 56
ESPACAMENTO_BOTAO = 24
centro_x = LARGURA // 2

# Variáveis auxiliares
tempo_vitoria_secs = 0.0
nome_entrada = ""

# Para modo infinito
pontuacao_infinito = 0
faixas_visitadas = set()

# Padrões de faixas por fase (mantidos)
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
        [(3,1100), (2,2000)],
        [(4,1200), (2,1200)],
        [(0,0)],
        [(4,1000), (2,1800)],
        [(3,1500), (3,1500)],
        [(2,1200), (2,1200), (2,1200), (2,1000)]
    ]
}

# Velocidades das faixas por fase
VELOCIDADES_FAIXA_POR_FASE = {
    1: [200, 180, 160, 140, 120, 100, 80],
    2: [240, 240, 220, 200, 180, 160, 160, 140, 120]
}

# Grupos de sprites
BUFFER_FAIXAS_VISIVEIS = 3
MAX_FAIXAS_MANTER = 48

# Mundo / câmera variáveis
camera_y = 0.0
mundo_top = 0.0
mundo_bottom = 0.0
comeco_centro_y = 0.0
contagem_faixas_geradas = 0
seguindo_ativo = False

# Carregar imagens e fazer resize
imagem_menu = pygame.transform.scale(pygame.image.load("telas/raposa_louca.png"), (LARGURA, ALTURA))
imagem_preparo = pygame.transform.scale(pygame.image.load("telas/apertar.png"), (LARGURA, ALTURA))
imagem_gameover = pygame.transform.scale(pygame.image.load("telas/game_over2.png"), (LARGURA, ALTURA))
imagem_gameover_infinito = pygame.transform.scale(pygame.image.load("telas/game_over_infinito.png"), (LARGURA, ALTURA))
imagem_info = pygame.transform.scale(pygame.image.load("telas/tela de fundo.png"), (LARGURA, ALTURA))
imagem_vitoria = pygame.transform.scale(pygame.image.load("telas/tela_vitoria.png"), (LARGURA, ALTURA))
imagem_ranking = pygame.transform.scale(pygame.image.load("telas/ranking.png"), (LARGURA, ALTURA))

# Imagens do jogador (raposa)
imagens_jogador = [
    pygame.transform.scale(pygame.image.load("raposa/fox01.png"), (TAM_JOGADOR, TAM_JOGADOR)),
    pygame.transform.scale(pygame.image.load("raposa/fox02.png"), (TAM_JOGADOR, TAM_JOGADOR)),
    pygame.transform.scale(pygame.image.load("raposa/fox03.png"), (TAM_JOGADOR, TAM_JOGADOR))
]

# Imagens dos carros
imagens_carros = [
    pygame.transform.scale(pygame.image.load("carro/carro1.png"), (CARRO_LARGURA, CARRO_ALTURA)),
    pygame.transform.scale(pygame.image.load("carro/carro2.png"), (CARRO_LARGURA, CARRO_ALTURA)),
    pygame.transform.scale(pygame.image.load("carro/carro3.png"), (CARRO_LARGURA, CARRO_ALTURA)),
    pygame.transform.scale(pygame.image.load("carro/carro4.png"), (CARRO_LARGURA, CARRO_ALTURA)),
    pygame.transform.scale(pygame.image.load("carro/carro5.png"), (CARRO_LARGURA, CARRO_ALTURA)),
    pygame.transform.scale(pygame.image.load("carro/carro6.png"), (CARRO_LARGURA, CARRO_ALTURA)),
    pygame.transform.scale(pygame.image.load("carro/caminhao1.png"), (CARRO_LARGURA, CARRO_ALTURA)),
    pygame.transform.scale(pygame.image.load("carro/caminhao2.png"), (CARRO_LARGURA, CARRO_ALTURA)),
    pygame.transform.scale(pygame.image.load("carro/caminhao3.png"), (CARRO_LARGURA, CARRO_ALTURA))
]

# Imagens das faixas e área segura
imagem_faixa = pygame.transform.scale(pygame.image.load("rua/rua01.png"), (LARGURA, FAIXA_ALTURA))
imagem_area_segura = pygame.transform.scale(pygame.image.load("rua/grama.png"), (LARGURA, TOPO_FAIXA))

# Classes do jogo
class Botao:
    def __init__(self, rect, texto, visivel=True):
        self.rect = pygame.Rect(rect)
        self.texto = texto
        self.visivel = visivel
    def desenhar(self, surf):
        if not self.visivel:
            return
        pygame.draw.rect(surf, CINZA, self.rect)
        txt = font.render(self.texto, True, PRETO)
        surf.blit(txt, (self.rect.centerx - txt.get_width() // 2, self.rect.centery - txt.get_height() // 2))
    def clicado(self, mouse_x, mouse_y):
        return self.rect.collidepoint(mouse_x,mouse_y)

class Jogador(pygame.sprite.Sprite):
    def __init__(self, start_pos):
        super().__init__()
        self.imagem_index = 0
        self.surf = imagens_jogador[self.imagem_index].copy()
        self.rect = self.surf.get_rect(center=start_pos)
        self.vidas = 3
        self.invencivel_ate = 0
        self.frame_counter = 0

    def update_imagem(self):
        self.frame_counter += 1
        if self.frame_counter >= 20:  # Troca de imagem a cada 20 frames
            self.imagem_index = (self.imagem_index + 1) % len(imagens_jogador)
            self.surf = imagens_jogador[self.imagem_index].copy()
            self.frame_counter = 0

    def movimentacao(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(LARGURA, self.rect.right)
        if modo_jogo == 'campanha':
            self.rect.top = max(0, self.rect.top)
            self.rect.bottom = min(ALTURA, self.rect.bottom)

    def reseta_comeco(self):
        if modo_jogo == 'campanha':
            self.rect.midbottom = (LARGURA // 2, ALTURA - 30)
        else:
            self.rect.centerx = LARGURA // 2
            self.rect.centery = comeco_centro_y

    def esta_invencivel(self):
        return pygame.time.get_ticks() < getattr(self, "invencivel_ate", 0)

    def defini_invencivel(self, duracao_ms):
        self.invencivel_ate = pygame.time.get_ticks() + duracao_ms

class Carro(pygame.sprite.Sprite):
    def __init__(self, centro_y, direcao, vel, x_inicial=None, deslocamento_spawn=0):
        super().__init__()
        self.imagem_index = random.randint(0, len(imagens_carros) - 1)
        self.surf = imagens_carros[self.imagem_index].copy()
        self.rect = self.surf.get_rect()
        self.rect.centery = centro_y
        self.direcao = direcao
        self.vel = float(vel)
        if x_inicial is not None:
            self.x = float(x_inicial)
        else:
            if direcao == 1:
                self.x = float(-self.rect.width - 10 + deslocamento_spawn)
            else:
                self.x = float(LARGURA + 10 - deslocamento_spawn)
        self.rect.x = int(self.x)

    def update(self, tempo_delta):
        self.x += self.vel * self.direcao * tempo_delta
        self.rect.x = int(self.x)
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
        self.indice_formato = 0
        self.estado = "waiting"
        self.prox_acao = pygame.time.get_ticks()
        self.spawnados_no_grupo = 0
        self.prox_spawn_interno = 0

    def atualizar(self, agora_ms, grupo_carros):
        if self.estado == "waiting":
            if agora_ms >= self.prox_acao:
                self.estado = "spawning_group"
                self.spawnados_no_grupo = 0
                self.prox_spawn_interno = agora_ms
        elif self.estado == "spawning_group":
            if not self.formato:
                self.formato = [(3, 1200)]
            conta, espera = self.formato[self.indice_formato]
            if conta == 0:
                self.indice_formato = (self.indice_formato + 1) % len(self.formato)
                self.estado = "waiting"
                self.prox_acao = agora_ms + max(50, espera)
                return

            espacamento_spawn = max(ESPACAMENTO_GRUPO, 2)
            largura_grupo_total = conta * CARRO_LARGURA + max(0, (conta - 1)) * espacamento_spawn
            espacamento_entre_grupos = 3 * TAM_JOGADOR
            vel_px_por_s = max(1.0, float(self.vel))
            min_wait_ms = int(((largura_grupo_total + espacamento_entre_grupos) / vel_px_por_s) * 1000)

            if agora_ms >= self.prox_spawn_interno:
                VARIACAO_SPAWN = 30
                variacao = random.randint(0, VARIACAO_SPAWN)
                if self.direcao == 1:
                    primeira_esquerda = - largura_grupo_total - variacao
                else:
                    primeira_esquerda = LARGURA + variacao

                for i in range(conta):
                    x = primeira_esquerda + i * (CARRO_LARGURA + espacamento_spawn)
                    c = Carro(self.centro_y, self.direcao, self.vel, x_inicial=x)
                    grupo_carros.add(c)

                self.spawnados_no_grupo = conta
                self.estado = "waiting"
                self.prox_acao = agora_ms + max(50, espera, min_wait_ms)
                self.indice_formato = (self.indice_formato + 1) % len(self.formato)

# Funções auxiliares
def criacao_inicial_grupos(grupo_carros, controladores):
    grupo_carros.empty()
    for ctrl in controladores:
        if not ctrl.formato:
            ctrl.formato = [(3,1500)]
        conta, espera = ctrl.formato[ctrl.indice_formato]
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
                novo_carro.x = novo_carro.rect.x
            else:
                direita_desejada = primeira_esquerda + total_group_largura
                novo_carro.rect.right = int(direita_desejada - i * (CARRO_LARGURA + ESPACAMENTO_GRUPO))
                novo_carro.x = novo_carro.rect.x
            grupo_carros.add(novo_carro)
        ctrl.prox_acao = pygame.time.get_ticks() + espera

def construir_controladores_por_fase(fase, qtd_faixas_override=None):
    controladores = []
    if fase == 1:
        qtd_faixas = qtd_faixas_override or 7
        padroes = PADROES_FAIXA_POR_FASE.get(1, [])
        velocidades = VELOCIDADES_FAIXA_POR_FASE.get(1, [])
    else:
        qtd_faixas = qtd_faixas_override or 9
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

def limites_fase(fase, controladores):
    if not controladores:
        return 0, 0
    topo = min(c.centro_y - FAIXA_ALTURA//2 for c in controladores)
    bottom = max(c.centro_y + FAIXA_ALTURA//2 for c in controladores)
    return topo, bottom

def garantir_topo_preenchido():
    global faixa_controladores, mundo_top, contagem_faixas_geradas
    if not faixa_controladores:
        return
    visible_lanes = int((ALTURA / FAIXA_ALTURA)) + BUFFER_FAIXAS_VISIVEIS
    while len(faixa_controladores) < visible_lanes:
        current_top = faixa_controladores[0]
        novo_indice = current_top.faixa_index - 1
        topo_y = faixa_controladores[0].centro_y
        if modo_jogo == 'infinito':
            padroes_fase2 = PADROES_FAIXA_POR_FASE.get(2, [])
            velocidades_fase2 = VELOCIDADES_FAIXA_POR_FASE.get(2, [])
            if padroes_fase2:
                padrao = padroes_fase2[contagem_faixas_geradas % len(padroes_fase2)]
            else:
                padrao = [(3,1500)]
            if velocidades_fase2:
                speed = velocidades_fase2[contagem_faixas_geradas % len(velocidades_fase2)]
            else:
                speed = 140
            direcao = 1 if random.random() < 0.5 else -1
        else:
            padrao = random.choice(PADROES_FAIXA_POR_FASE.get(1, [[(3,1500)]]))
            direcao = 1 if random.random() < 0.5 else -1
            speeds = VELOCIDADES_FAIXA_POR_FASE.get(1, [])
            speed = random.choice(speeds) if speeds else 140
        novo = FaixaController(novo_indice, topo_y - (FAIXA_ALTURA + ESPACAMENTO_FAIXA), direcao, speed, padrao)
        novo.faixa_index = novo_indice
        novo.centro_y = faixa_controladores[0].centro_y - (FAIXA_ALTURA + ESPACAMENTO_FAIXA)
        faixa_controladores.insert(0, novo)
        mundo_top = min(mundo_top, novo.centro_y - FAIXA_ALTURA//2)
        try:
            contagem, espera_depois = novo.formato[novo.indice_formato]
        except Exception:
            contagem, espera_depois = 0,0
        if contagem > 0:
            espacamento_spawn = max(ESPACAMENTO_GRUPO, 2)
            largura_grupo_total = contagem * CARRO_LARGURA + max(0, (contagem - 1)) * espacamento_spawn
            alvo_cx = random.randint(int(LARGURA*0.15), int(LARGURA*0.85))
            primeira_esquerda = alvo_cx - largura_grupo_total // 2
            for i in range(contagem):
                x_spawn = primeira_esquerda + i * (CARRO_LARGURA + espacamento_spawn)
                carros.add(Carro(novo.centro_y, novo.direcao, novo.vel, x_inicial=x_spawn))
            novo.prox_acao = pygame.time.get_ticks() + max(80, espera_depois // 3)
        contagem_faixas_geradas += 1

def criar_faixa_topo():
    global faixa_controladores, mundo_top, contagem_faixas_geradas
    if not faixa_controladores:
        return
    current_top = faixa_controladores[0]
    novo_indice = current_top.faixa_index - 1
    topo_y = current_top.centro_y
    if modo_jogo == 'infinito':
        padroes_fase2 = PADROES_FAIXA_POR_FASE.get(2, [])
        velocidades_fase2 = VELOCIDADES_FAIXA_POR_FASE.get(2, [])
        if padroes_fase2:
            padrao = padroes_fase2[contagem_faixas_geradas % len(padroes_fase2)]
        else:
            padrao = [(3,1500)]
        if velocidades_fase2:
            speed = velocidades_fase2[contagem_faixas_geradas % len(velocidades_fase2)]
        else:
            speed = 140
        direction = 1 if random.random() < 0.5 else -1
    else:
        padrao = random.choice(PADROES_FAIXA_POR_FASE.get(1, [[(3,1500)]]))
        direction = 1 if random.random() < 0.5 else -1
        speeds = VELOCIDADES_FAIXA_POR_FASE.get(1, [])
        speed = random.choice(speeds) if speeds else 140
    novo = FaixaController(novo_indice, topo_y - (FAIXA_ALTURA + ESPACAMENTO_FAIXA), direction, speed, padrao)
    novo.faixa_index = novo_indice
    novo.centro_y = faixa_controladores[0].centro_y - (FAIXA_ALTURA + ESPACAMENTO_FAIXA)
    faixa_controladores.insert(0, novo)
    mundo_top = min(mundo_top, novo.centro_y - FAIXA_ALTURA//2)
    try:
        contagem, espera_depois = novo.formato[novo.indice_formato]
    except Exception:
        contagem, espera_depois = 0,0
    if contagem > 0:
        espacamento_spawn = max(ESPACAMENTO_GRUPO, 2)
        largura_grupo_total = contagem * CARRO_LARGURA + max(0, (contagem - 1)) * espacamento_spawn
        alvo_cx = random.randint(int(LARGURA*0.15), int(LARGURA*0.85))
        primeira_esquerda = alvo_cx - largura_grupo_total // 2
        for i in range(contagem):
            x_spawn = primeira_esquerda + i * (CARRO_LARGURA + espacamento_spawn)
            carros.add(Carro(novo.centro_y, novo.direcao, novo.vel, x_inicial=x_spawn))
        novo.prox_acao = pygame.time.get_ticks() + max(80, espera_depois // 3)
    contagem_faixas_geradas += 1
    aparar_faixas()

def aparar_faixas():
    global faixa_controladores, carros, mundo_bottom
    if not faixa_controladores:
        return
    while len(faixa_controladores) > MAX_FAIXAS_MANTER:
        removed = faixa_controladores.pop()
        for spr in list(carros):
            try:
                if abs(spr.rect.centery - (removed.centro_y)) < FAIXA_ALTURA//2:
                    spr.kill()
            except Exception:
                pass
        if faixa_controladores:
            last = faixa_controladores[-1]
            mundo_bottom = last.centro_y + FAIXA_ALTURA // 2

def mover_jogador_vertical_passo(direcao):
    global comeco_centro_y, carros, faixa_controladores, contagem_faixas_geradas, pontuacao_infinito, visited_faixas
    if not faixa_controladores:
        return
    centros = [c.centro_y for c in faixa_controladores]
    altura_passo = FAIXA_ALTURA
    def indice_mais_proximo(y):
        return min(range(len(centros)), key=lambda i: abs(centros[i] - y))
    if direcao == -1:
        ultima_faixa_centro = centros[-1]
        if jog.rect.centery > ultima_faixa_centro:
            novo_y = jog.rect.centery - altura_passo
            if novo_y < ultima_faixa_centro:
                novo_y = ultima_faixa_centro
            jog.rect.centery = novo_y
        else:
            idx = indice_mais_proximo(jog.rect.centery)
            new_idx = max(0, idx - 1)
            jog.rect.centery = centros[new_idx]

        try:
            controlador_mais_proximo = min(faixa_controladores, key=lambda c: abs(c.centro_y - jog.rect.centery))
            indice_absoluto = controlador_mais_proximo.faixa_index
            if modo_jogo == 'infinito':
                if indice_absoluto not in visited_faixas:
                    visited_faixas.add(indice_absoluto)
                    pontuacao_infinito += 1
        except Exception:
            pass

        meio_tela_mundo = camera_y + ALTURA // 2
        if jog.rect.centery < meio_tela_mundo:
            criar_faixa_topo()
    else:
        ultima_faixa_centro = centros[-1]
        if jog.rect.centery >= ultima_faixa_centro:
            novo_y = jog.rect.centery + altura_passo
            if novo_y > comeco_centro_y:
                novo_y = comeco_centro_y
            jog.rect.centery = novo_y
        else:
            idx = indice_mais_proximo(jog.rect.centery)
            if idx == len(centros) - 1:
                jog.rect.centery = ultima_faixa_centro + altura_passo
            else:
                new_idx = min(len(centros)-1, idx + 1)
                jog.rect.centery = centros[new_idx]
    jog.rect.centerx = max(TAM_JOGADOR//2, min(LARGURA - TAM_JOGADOR//2, jog.rect.centerx))

def resetar_estado_fase(fase):
    global carros, faixa_controladores, mundo_top, mundo_bottom, comeco_centro_y, camera_y, lanes_generated_count, visited_faixas
    carros.empty()
    faixa_controladores = construir_controladores_por_fase(fase)
    try:
        if modo_jogo == 'campanha' and faixa_controladores:
            faixa_controladores[0].formato = [(0,0)]
    except Exception:
        pass
    mundo_top, mundo_bottom = limites_fase(fase, faixa_controladores)
    comeco_centro_y = mundo_bottom + FAIXA_ALTURA
    jog.reseta_comeco()
    camera_y = mundo_bottom - ALTURA
    criacao_inicial_grupos(carros, faixa_controladores)
    garantir_topo_preenchido()
    contagem_faixas_geradas = len(faixa_controladores)
    visited_faixas = set()
    if faixa_controladores:
        inicial_abs_index = faixa_controladores[-1].faixa_index
        visited_faixas.add(inicial_abs_index)

def resetar_estado_infinito():
    global carros, faixa_controladores, mundo_top, mundo_bottom, comeco_centro_y, camera_y, contagem_faixas_geradas, visited_faixas, pontuacao_infinito
    carros.empty()
    faixa_controladores = construir_controladores_por_fase(1, qtd_faixas_override=QTD_FAIXAS)
    mundo_top, mundo_bottom = limites_fase(1, faixa_controladores)
    comeco_centro_y = mundo_bottom + 200
    jog.reseta_comeco()
    camera_y = mundo_bottom + 100000
    garantir_topo_preenchido()
    contagem_faixas_geradas = len(faixa_controladores)
    pontuacao_infinito = 0
    visited_faixas = set()
    if faixa_controladores:
        inicial_abs_index = faixa_controladores[-1].faixa_index
        visited_faixas.add(inicial_abs_index)

def verificar_colisoes_e_reset(jogador, carros, controladores):
    colisao_detectada = pygame.sprite.spritecollideany(jogador, carros)
    if colisao_detectada:
        jogador.reseta_comeco()
        carros.empty()
        novas_controladores = construir_controladores_por_fase(fase)
        try:
            if modo_jogo == 'campanha' and novas_controladores:
                novas_controladores[0].formato = [(0,0)]
        except Exception:
            pass
        criacao_inicial_grupos(carros, novas_controladores)
        controladores[:] = novas_controladores
        return True
    return False

def carregar_ranking():
    if not os.path.exists(PASTA_RANKING):
        return []
    try:
        with open(PASTA_RANKING, "r", encoding="utf-8") as f:
            dados = json.load(f)
            if isinstance(dados, list):
                dados_ordenados = sorted(dados, key=lambda x: x.get("time", float("inf")))
                return dados_ordenados[:10]
    except Exception:
        pass
    return []

def salvar_ranking(entries):
    try:
        entradas_ordenadas = sorted(entries, key=lambda x: x.get("time", float("inf")))[:10]
        with open(PASTA_RANKING, "w", encoding="utf-8") as f:
            json.dump(entradas_ordenadas, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Erro salvando ranking:", e)

def carregar_ranking_infinito():
    if not os.path.exists(PASTA_RANKING_INFINITO):
        return []
    try:
        with open(PASTA_RANKING_INFINITO, "r", encoding="utf-8") as f:
            dados = json.load(f)
            if isinstance(dados, list):
                dados_ordenados = sorted(dados, key=lambda x: x.get("score", 0), reverse=True)
                return dados_ordenados[:10]
    except Exception:
        pass
    return []

def salvar_ranking_infinito(entries):
    try:
        entradas_ordenadas = sorted(entries, key=lambda x: x.get("score", 0), reverse=True)[:10]
        with open(PASTA_RANKING_INFINITO, "w", encoding="utf-8") as f:
            json.dump(entradas_ordenadas, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Erro salvando ranking infinito:", e)

# Inicialização do jogo
jog = Jogador(JOGADOR_POS_INICIAL)

# inicializa variáveis de mundo/câmera com controladores iniciais
carros = pygame.sprite.Group()
fase = 1
faixa_controladores = construir_controladores_por_fase(fase)
criacao_inicial_grupos(carros, faixa_controladores)

# calcula limites iniciais e posições do jogador/câmera
mundo_top, mundo_bottom = limites_fase(fase, faixa_controladores)
comeco_centro_y = mundo_bottom + FAIXA_ALTURA
jog.reseta_comeco()
camera_y = mundo_bottom - ALTURA
garantir_topo_preenchido()
contagem_faixas_geradas = len(faixa_controladores)

# marca faixa inicial visitada para infinito
visited_faixas = set()
if faixa_controladores:
    inicial_abs_index = faixa_controladores[-1].faixa_index
    visited_faixas.add(inicial_abs_index)

# Botões
botao_campanha = Botao((60, 510, BOTAO_LARGURA, BOTAO_ALTURA), "Campanha", visivel=False)
botao_infinito = Botao((LARGURA - BOTAO_LARGURA - 60, 510, BOTAO_LARGURA, BOTAO_ALTURA), "Infinito", visivel=False)
botao_info = Botao((60, 575, BOTAO_LARGURA, BOTAO_ALTURA), "Informações", visivel=False)
botao_sair = Botao((LARGURA - BOTAO_LARGURA - 60, 575, BOTAO_LARGURA, BOTAO_ALTURA), "Sair", visivel=False)
botao_reiniciar_ranking = Botao((55, ALTURA - 225, 250, 85), "Reinício rápido (R)", visivel=False)
botao_voltar_menu_ranking = Botao((LARGURA - 305, ALTURA - 225, 250, 85), "Voltar ao Menu (ESC)", visivel=False)
botao_reiniciar_gameover = Botao((centro_x - 250, 550, 500, 80), "Reinício rápido (R)", visivel=False)
botao_voltar_menu_gameover = Botao((centro_x - 250, 450, 500, 80), "Voltar ao Menu (ESC)", visivel=False)
botao_continuar = Botao((centro_x - BOTAO_LARGURA//2, 300, BOTAO_LARGURA, BOTAO_ALTURA), "Continuar (ESC)")
botao_voltar_menu_pausa = Botao((centro_x - BOTAO_LARGURA//2, 300 + BOTAO_ALTURA + 20, BOTAO_LARGURA, BOTAO_ALTURA), "Voltar ao Menu")
botao_iniciar_jogo = Botao((centro_x - 290, 300, 580, 70), "Iniciar Jogo (E)", visivel=False)
botao_voltar_menu_preparo = Botao((centro_x - 290, 405, 580, 70), "Voltar ao Menu (ESC)", visivel=False)
botao_reiniciar_ranking_inf = Botao((55, ALTURA - 225, 250, 85), "Reinício rápido (R)", visivel=False)
botao_voltar_menu_ranking_inf = Botao((LARGURA - 305, ALTURA - 225, 250, 85), "Voltar ao Menu (ESC)", visivel=False)

# Loop principal
executando = True
while executando:
    tempo_ms = clock.tick(FPS)
    tempo_delta = tempo_ms / 1000.0
    agora_ms = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            executando = False

        if event.type == pygame.KEYDOWN:
            if estado == ESTADO_RANKING:
                if event.key == pygame.K_ESCAPE:
                    estado = ESTADO_MENU
                    continue
                if event.key == pygame.K_r:
                    modo_jogo = 'campanha'
                    fase = 1
                    jog.vidas = 3
                    resetar_estado_fase(fase)
                    jog.reseta_comeco()
                    estado = ESTADO_JOGANDO
                    inicio_tempo_ms = pygame.time.get_ticks()
                    continue

            if estado == ESTADO_RANKING_INFINITO:
                if event.key == pygame.K_ESCAPE:
                    estado = ESTADO_MENU
                    continue
                if event.key == pygame.K_r:
                    modo_jogo = 'infinito'
                    pontuacao_infinito = 0
                    jog.vidas = 1
                    resetar_estado_infinito()
                    estado = ESTADO_JOGANDO
                    inicio_tempo_ms = None
                    continue

            if estado == ESTADO_GAMEOVER:
                if event.key == pygame.K_ESCAPE:
                    estado = ESTADO_MENU
                    continue
                if event.key == pygame.K_r:
                    modo_jogo = 'campanha'
                    fase = 1
                    jog.vidas = 3
                    resetar_estado_fase(fase)
                    jog.reseta_comeco()
                    estado = ESTADO_JOGANDO
                    inicio_tempo_ms = pygame.time.get_ticks()
                    continue

            if estado == ESTADO_INFINITO_NOME:
                if event.key == pygame.K_BACKSPACE:
                    nome_input = nome_input[:-1]
                elif event.key == pygame.K_RETURN:
                    entries = carregar_ranking_infinito()
                    entries.append({"name": nome_input if nome_input.strip() != "" else "Anon", "score": pontuacao_infinito})
                    salvar_ranking_infinito(entries)
                    nome_input = ""
                    estado = ESTADO_RANKING_INFINITO
                else:
                    if len(nome_input) < 16:
                        ch = event.unicode
                        if ch.isprintable():
                            nome_input += ch
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
                    if modo_jogo == 'campanha':
                        fase = 1
                        jog.vidas = 3
                        resetar_estado_fase(fase)
                        inicio_tempo_ms = pygame.time.get_ticks()
                    else:
                        pontuacao_infinito = 0
                        jog.vidas = 1
                        resetar_estado_infinito()
                        inicio_tempo_ms = None
                    pausa_inicio_ms = None
                    estado = ESTADO_JOGANDO
                    continue
                if event.key == pygame.K_m:
                    pausa_inicio_ms = None
                    inicio_tempo_ms = None
                    estado = ESTADO_MENU
                    continue

            if estado == ESTADO_PREPARO:
                if event.key == pygame.K_e:
                    if modo_jogo == 'campanha':
                        fase = 1
                        jog.vidas = 3
                        resetar_estado_fase(fase)
                        jog.reseta_comeco()
                        inicio_tempo_ms = pygame.time.get_ticks()
                    else:
                        pontuacao_infinito = 0
                        jog.vidas = 1
                        resetar_estado_infinito()
                        inicio_tempo_ms = None
                    estado = ESTADO_JOGANDO
                    continue
                if event.key == pygame.K_ESCAPE:
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
                    if modo_jogo == 'campanha':
                        jog.movimentacao(0, -PASSO_Y)
                    else:
                        mover_jogador_vertical_passo(-1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if modo_jogo == 'campanha':
                        jog.movimentacao(0, PASSO_Y)
                    else:
                        mover_jogador_vertical_passo(+1)
            elif estado == ESTADO_MENU:
                if event.key == pygame.K_ESCAPE:
                    executando = False
            elif estado == ESTADO_INFO:
                if event.key == pygame.K_ESCAPE:
                    estado = ESTADO_MENU

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x,mouse_y = event.pos
            if estado == ESTADO_MENU:
                if botao_campanha.clicado(mouse_x,mouse_y):
                    modo_jogo = 'campanha'
                    estado = ESTADO_PREPARO
                elif botao_infinito.clicado(mouse_x,mouse_y):
                    modo_jogo = 'infinito'
                    estado = ESTADO_PREPARO
                elif botao_info.clicado(mouse_x,mouse_y):
                    estado = ESTADO_INFO
                elif botao_sair.clicado(mouse_x,mouse_y):
                    executando = False
            elif estado == ESTADO_INFO:
                estado = ESTADO_MENU
            elif estado == ESTADO_RANKING:
                if botao_reiniciar_ranking.clicado(mouse_x, mouse_y):
                    modo_jogo = 'campanha'
                    fase = 1
                    jog.vidas = 3
                    resetar_estado_fase(fase)
                    jog.reseta_comeco()
                    estado = ESTADO_JOGANDO
                    inicio_tempo_ms = pygame.time.get_ticks()
                if botao_voltar_menu_ranking.clicado(mouse_x, mouse_y):
                    estado = ESTADO_MENU
            elif estado == ESTADO_RANKING_INFINITO:
                if botao_reiniciar_ranking_inf.clicado(mouse_x, mouse_y):
                    modo_jogo = 'infinito'
                    pontuacao_infinito = 0
                    jog.vidas = 1
                    resetar_estado_infinito()
                    estado = ESTADO_JOGANDO
                    inicio_tempo_ms = None
                if botao_voltar_menu_ranking_inf.clicado(mouse_x, mouse_y):
                    estado = ESTADO_MENU
            elif estado == ESTADO_GAMEOVER:
                if botao_reiniciar_gameover.clicado(mouse_x, mouse_y):
                    modo_jogo = 'campanha'
                    fase = 1
                    jog.vidas = 3
                    resetar_estado_fase(fase)
                    jog.reseta_comeco()
                    estado = ESTADO_JOGANDO
                    inicio_tempo_ms = pygame.time.get_ticks()
                if botao_voltar_menu_gameover.clicado(mouse_x, mouse_y):
                    estado = ESTADO_MENU
            elif estado == ESTADO_PAUSADO:
                if botao_continuar.clicado(mouse_x, mouse_y):
                    if pausa_inicio_ms is not None and inicio_tempo_ms is not None:
                        delta = pygame.time.get_ticks() - pausa_inicio_ms
                        inicio_tempo_ms += delta
                    pausa_inicio_ms = None
                    estado = ESTADO_JOGANDO
                if botao_voltar_menu_pausa.clicado(mouse_x, mouse_y):
                    pausa_inicio_ms = None
                    inicio_tempo_ms = None
                    estado = ESTADO_MENU
            elif estado == ESTADO_PREPARO:
                if botao_iniciar_jogo.clicado(mouse_x, mouse_y):
                    if modo_jogo == 'campanha':
                        fase = 1
                        jog.vidas = 3
                        resetar_estado_fase(fase)
                        jog.reseta_comeco()
                        inicio_tempo_ms = pygame.time.get_ticks()
                    else:
                        pontuacao_infinito = 0
                        jog.vidas = 1
                        resetar_estado_infinito()
                        inicio_tempo_ms = None
                    estado = ESTADO_JOGANDO
                if botao_voltar_menu_preparo.clicado(mouse_x, mouse_y):
                    estado = ESTADO_MENU

    if estado == ESTADO_JOGANDO:
        for ctrl in faixa_controladores:
            ctrl.atualizar(agora_ms, carros)
        for c in list(carros):
            c.update(tempo_delta)

        colisao_detectada = pygame.sprite.spritecollideany(jog, carros)
        if colisao_detectada:
            if modo_jogo == 'campanha':
                reset_colisao = verificar_colisoes_e_reset(jog, carros, faixa_controladores)
                if reset_colisao:
                    jog.vidas -= 1
                    if jog.vidas <= 0:
                        estado = ESTADO_GAMEOVER
                        inicio_tempo_ms = None
            else:
                if not jog.esta_invencivel():
                    jog.defini_invencivel(800)
                    jog.vidas -= 1
                    if jog.vidas <= 0:
                        estado = ESTADO_INFINITO_NOME
                        nome_input = ""

        if modo_jogo == 'campanha':
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
        else:
            mundo_top_calc, mundo_bottom_calc = limites_fase(fase, faixa_controladores)
            finish_y = mundo_top_calc + TOPO_FAIXA
            if jog.rect.top <= finish_y:
                pontuacao_infinito += 1
                resetar_estado_infinito()
                jog.vidas = 1

        mundo_top, mundo_bottom = limites_fase(fase, faixa_controladores)
        if not faixa_controladores:
            min_cam = mundo_top
            max_cam = mundo_bottom - ALTURA
        else:
            min_cam = mundo_top
            if modo_jogo == 'infinito':
                max_cam = mundo_bottom
            else:
                max_cam = mundo_bottom - ALTURA
        if max_cam < min_cam:
            max_cam = min_cam

        meio_tela_mundo = camera_y + ALTURA // 2

        if jog.rect.centery < meio_tela_mundo:
            seguindo_ativo = True
        if jog.rect.centery > camera_y + int(ALTURA * 0.75):
            seguindo_ativo = False

        alpha = 0.35
        if seguindo_ativo:
            desired_cam = int(jog.rect.centery - ALTURA // 2)
            camera_y = int(camera_y + (desired_cam - camera_y) * alpha)
        else:
            desired_cam = int(max_cam)
            camera_y = int(camera_y + (desired_cam - camera_y) * (alpha * 0.6))

        camera_y = max(min_cam, min(max_cam, camera_y))

        garantir_topo_preenchido()

    tela.fill(FUNDO)

    if estado == ESTADO_MENU:
        tela.blit(imagem_menu, (0, 0))
        botao_campanha.desenhar(tela)
        botao_infinito.desenhar(tela)
        botao_info.desenhar(tela)
        botao_sair.desenhar(tela)

    elif estado == ESTADO_PREPARO:
        tela.blit(imagem_preparo, (0, 0))

        botao_iniciar_jogo.desenhar(tela)
        botao_voltar_menu_preparo.desenhar(tela)

    elif estado == ESTADO_INFO:
        tela.blit(imagem_info, (0, 0))
        linhas = [
            "Como jogar:",
            "- Aperte as setas ou WASD para mover o jogador.",
            "",
            "Informações:",
            "- Modo campanha:",
            "- Você deve chegar ao topo.",
            "- Inicia o jogo com 3 vidas.",
            "- Cada colisão com um carro faz perder 1 vida.",
            "- Se perder todas as 3 vidas, aparece Game Over com o tempo.",
            "",
            "Modo infinito:",
            "- Subir o máximo que conseguir.",
            "- Você inicia o modo infinito com 1 vida.",
            "- Colete power-ups para ganhar vidas extras (máximo 5).",
            "- Cada colisão com um carro faz perder 1 vida.",
            "- Se perder suas as vidas, aparece Game Over com a pontuação.",
            "",
            "Aperte ESC para voltar ao menu."
        ]
        y = 120
        for ln in linhas:
            txt = info_font.render(ln, True, PRETO)
            tela.blit(txt, (40,y))
            y += 36

    elif estado == ESTADO_JOGANDO:
        if modo_jogo == 'campanha':
            # Desenhar área segura (grama)
            topo = pygame.Rect(0, 0, LARGURA, TOPO_FAIXA)
            tela.blit(imagem_area_segura, (0, 0))

            # Desenhar faixas com a imagem de rua
            num_faixas_para_desenhar = len(faixa_controladores) if 'faixa_controladores' in globals() else QTD_FAIXAS
            for i in range(num_faixas_para_desenhar):
                faixa_rect = pygame.Rect(0, TOPO_FAIXA + i*(FAIXA_ALTURA+ESPACAMENTO_FAIXA), LARGURA, FAIXA_ALTURA)
                # Desenha a imagem de rua com tile
                for x in range(0, LARGURA, imagem_faixa.get_width()):
                    tela.blit(imagem_faixa, (x, faixa_rect.top))

            # Atualizar imagem do jogador
            jog.update_imagem()

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
        else:
            topo = pygame.Rect(0, 0, LARGURA, TOPO_FAIXA)
            tela.blit(imagem_area_segura, (0, 0))
            # Não preenche com fill, deixa a grama à vista

            num_faixas_para_desenhar = len(faixa_controladores) if 'faixa_controladores' in globals() else QTD_FAIXAS
            for i, ctrl in enumerate(faixa_controladores):
                r_world_top = ctrl.centro_y - FAIXA_ALTURA//2
                r_tela_top = r_world_top - camera_y
                r = pygame.Rect(0, int(r_tela_top), LARGURA, FAIXA_ALTURA)
                if r.bottom < 0 or r.top > ALTURA:
                    continue
                # Desenha a imagem de rua com tile
                for x in range(0, LARGURA, imagem_faixa.get_width()):
                    tela.blit(imagem_faixa, (x, int(r_tela_top)))

            # Atualizar imagem do jogador
            jog.update_imagem()

            for c in carros:
                tela.blit(c.surf, (c.rect.x, c.rect.y - camera_y))

            tela.blit(jog.surf, (jog.rect.x, jog.rect.y - camera_y))

            texto_vidas = font.render(f"Vidas: {jog.vidas}  Pontos: {pontuacao_infinito}", True, BRANCO)
            tela.blit(texto_vidas, (10, 10))

    elif estado == ESTADO_PAUSADO:
        topo = pygame.Rect(0, 0, LARGURA, TOPO_FAIXA)
        tela.blit(imagem_area_segura, (0, 0))
        for i, ctrl in enumerate(faixa_controladores):
            r_world_top = ctrl.centro_y - FAIXA_ALTURA//2
            r_tela_top = r_world_top - camera_y
            r = pygame.Rect(0, int(r_tela_top), LARGURA, FAIXA_ALTURA)
            if r.bottom < 0 or r.top > ALTURA:
                continue
            # Desenha a imagem de rua com tile
            for x in range(0, LARGURA, imagem_faixa.get_width()):
                tela.blit(imagem_faixa, (x, int(r_tela_top)))
        for c in carros:
            tela.blit(c.surf, (c.rect.x, c.rect.y - camera_y))
        tela.blit(jog.surf, (jog.rect.x, jog.rect.y - camera_y))

        s = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        s.fill((0,0,0,140))
        tela.blit(s, (0,0))

        titulo = big_font.render("PAUSADO", True, BRANCO)
        tela.blit(titulo, ((LARGURA - titulo.get_width()) // 2, 120))

        botao_continuar.desenhar(tela)
        botao_voltar_menu_pausa.desenhar(tela)

        instr = font.render("Pressione ESC para continuar ou R para reiniciar", True, BRANCO)
        tela.blit(instr, ((LARGURA - instr.get_width()) // 2, 480))

    elif estado == ESTADO_VITORIA:
        tela.blit(imagem_vitoria, (0, 0))

        t = vitoria_tempo_font.render(f"Seu tempo: {tempo_vitoria_secs:.3f}s", True, BRANCO)
        tela.blit(t, ((LARGURA - t.get_width()) // 2, 345))

        prompt = vitoria_font.render("Digite seu nome e pressione Enter:", True, PRETO)
        tela.blit(prompt, ((LARGURA - prompt.get_width()) // 2, 405))

        box = pygame.Rect((LARGURA//2 - 200, 440, 400, 40))
        pygame.draw.rect(tela, (240,240,240), box)
        pygame.draw.rect(tela, PRETO, box, 2)
        name_surf = font.render(nome_input, True, PRETO)
        tela.blit(name_surf, (box.x + 8, box.y + 8))

    elif estado == ESTADO_RANKING:
        tela.blit(imagem_ranking, (0, 0))
        entries = carregar_ranking()

        entry_surfs = []
        for idx, e in enumerate(entries, start=1):
            line = f"{idx}. {e['name']} - {e['time']:.3f}s"
            entry_surfs.append(rank_font_campanha.render(line, True, PRETO))

        spacing = 32
        total_height = len(entry_surfs) * spacing
        desloc_y = 40
        start_y = max(20, (ALTURA - total_height) // 2 - desloc_y + 32)

        y = start_y
        for surf in entry_surfs:
            x = (LARGURA - surf.get_width()) // 2 + 40
            tela.blit(surf, (x, y))
            y += spacing

        botao_reiniciar_ranking.desenhar(tela)
        botao_voltar_menu_ranking.desenhar(tela)

    elif estado == ESTADO_INFINITO_NOME:
        tela.blit(imagem_gameover_infinito, (0, 0))

        t = vitoria_tempo_font.render(f"Sua pontuação: {pontuacao_infinito} pontos", True, BRANCO)
        tela.blit(t, ((LARGURA - t.get_width()) // 2, 340))

        prompt = vitoria_font.render("Digite seu nome e pressione Enter:", True, PRETO)
        tela.blit(prompt, ((LARGURA - prompt.get_width()) // 2, 425))

        box = pygame.Rect((LARGURA//2 - 200, 470, 400, 40))
        pygame.draw.rect(tela, (240,240,240), box)
        pygame.draw.rect(tela, PRETO, box, 2)
        name_surf = font.render(nome_input, True, PRETO)
        tela.blit(name_surf, (box.x + 8, box.y + 8))

    elif estado == ESTADO_RANKING_INFINITO:
        tela.blit(imagem_ranking, (0, 0))
        entries = carregar_ranking_infinito()

        entry_surfs = []
        for idx, e in enumerate(entries, start=1):
            line = f"{idx}. {e['name']} - {e['score']} pts"
            entry_surfs.append(rank_font_campanha.render(line, True, PRETO))

        spacing = 32
        total_height = len(entry_surfs) * spacing
        desloc_y = 40
        start_y = max(20, (ALTURA - total_height) // 2 - desloc_y + 32)

        y = start_y
        for surf in entry_surfs:
            x = (LARGURA - surf.get_width()) // 2 + 40
            tela.blit(surf, (x, y))
            y += spacing

        botao_reiniciar_ranking_inf.desenhar(tela)
        botao_voltar_menu_ranking_inf.desenhar(tela)

    elif estado == ESTADO_GAMEOVER:
        tela.blit(imagem_gameover, (0, 0))

        botao_reiniciar_gameover.desenhar(tela)
        botao_voltar_menu_gameover.desenhar(tela)

    pygame.display.flip()

pygame.quit()
sys.exit()