import pygame
import sys
import random

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

estado = ESTADO_MENU

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
big_font = pygame.font.SysFont(None, 56)

FORMATO_FASE_POR_FAIXA = [
    [(4, 1500), (2, 1200)],     # Faixa 0
    [(3, 1600), (3, 1600)],     # Faixa 1
    [(0, 0)],                   # Faixa 2
    [(3, 1300)],                # Faixa 3
    [(0, 0)],                   # Faixa 4
    [(4, 1400)],                # Faixa 5
    [(3, 1800)],                # Faixa 6
]

VELOCIDADE_FASE_POR_FAIXA = [200, 180, 160, 140, 120, 100, 80]

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


def controle_criacao_faixa():
    controladores = []
    for i in range(QTD_FAIXAS):
        topo_y = TOPO_FAIXA + i * (FAIXA_ALTURA + ESPACAMENTO_FAIXA)
        direcao = 1 if (i % 2 == 0) else -1
        if random.random() < 0.5:
            direcao *= -1
        base_vel = VELOCIDADE_FASE_POR_FAIXA[i] if i < len(VELOCIDADE_FASE_POR_FAIXA) else 120 + i * 20
        formato = FORMATO_FASE_POR_FAIXA[i] if i < len(FORMATO_FASE_POR_FAIXA) else [(3, 1500)]
        ctrl = FaixaController(i, topo_y, direcao, base_vel, formato)
        ctrl.prox_acao = pygame.time.get_ticks() + random.randint(0, 1500)
        controladores.append(ctrl)
    return controladores

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

def verificar_colisoes_e_reset(jogador, carros, controladores):
    colisao = pygame.sprite.spritecollideany(jogador, carros)
    if colisao:
        jogador.reseta_comeco()
        carros.empty()
        novas_controladores = controle_criacao_faixa()
        criacao_inicial_grupos(carros, novas_controladores)
        controladores[:] = novas_controladores
        return True
    return False

jog = Jogador(JOGADOR_POS_INICIAL)
jog.reseta_comeco()

carros = pygame.sprite.Group()
faixa_controladores = controle_criacao_faixa()
criacao_inicial_grupos(carros, faixa_controladores)

BTN_W, BTN_H = 220, 56
BTN_SPACING = 24
center_x = LARGURA // 2

btn_jogar = Botao((center_x - BTN_W//2, 320+ (BTN_H + 28)/20, BTN_W, BTN_H), "Jogar")
btn_info = Botao((center_x - BTN_W//2, 320 + BTN_H + 28, BTN_W, BTN_H), "Informações")
btn_sair = Botao((center_x - BTN_W//2, 320 + (BTN_H + 28)*2, BTN_W, BTN_H), "Sair")

running = True
while running:
    dt_ms = clock.tick(FPS)
    dt = dt_ms / 1000.0
    agora_ms = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if estado == ESTADO_JOGANDO:
                if event.key == pygame.K_ESCAPE:
                    estado = ESTADO_MENU
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
                    carros.empty()
                    faixa_controladores = controle_criacao_faixa()
                    criacao_inicial_grupos(carros, faixa_controladores)
                    jog.reseta_comeco()
                    estado = ESTADO_JOGANDO
                elif btn_info.clicado(mx,my):
                    estado = ESTADO_INFO
                elif btn_sair.clicado(mx,my):
                    running = False
            elif estado == ESTADO_INFO:
                estado = ESTADO_MENU

    if estado == ESTADO_JOGANDO:
        for ctrl in faixa_controladores:
            ctrl.update(agora_ms, carros)
        for c in list(carros):
            c.update(dt)
        verificar_colisoes_e_reset(jog, carros, faixa_controladores)

    tela.fill(FUNDO)

    if estado == ESTADO_MENU:
        titulo = big_font.render("CROSSY CLONE", True, BRANCO)
        tela.blit(titulo, ((LARGURA - titulo.get_width()) // 2, 120))
        btn_jogar.desenhar(tela)
        btn_info.desenhar(tela)
        btn_sair.desenhar(tela)

    elif estado == ESTADO_INFO:
        lines = [
            "Como jogar:",
            "- Use as setas ou WASD para mover por passos (um passo por tecla).",
            "- Objetivo: evitar os carros e atravessar as faixas.",
            "- Clique para voltar ao Menu."
        ]
        y = 120
        for ln in lines:
            txt = font.render(ln, True, BRANCO)
            tela.blit(txt, (40,y))
            y += 36

    elif estado == ESTADO_JOGANDO:
        top_zone = pygame.Rect(0, 0, LARGURA, TOPO_FAIXA)
        

        for c in carros:
            tela.blit(c.surf, c.rect)
        tela.blit(jog.surf, jog.rect)

    pygame.display.flip()

pygame.quit()
sys.exit()