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

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

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

FORMATO_FASE_POR_FAIXA = [
    [(4, 1500), (2, 1200)],
    [(3, 1600), (3, 1600)],
    [(0, 0)],
    [(3, 1300)],
    [(0, 0)],
    [(4, 1400)],
    [(3, 1800)],
]

VELOCIDADE_FASE_POR_FAIXA = [200, 180, 160, 140, 120, 100, 80]

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

running = True
while running:
    dt_ms = clock.tick(FPS)
    dt = dt_ms / 1000.0
    agora_ms = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key in (pygame.K_LEFT, pygame.K_a):
                jog.movimentacao(-PASSO_X, 0)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                jog.movimentacao(PASSO_X, 0)
            elif event.key in (pygame.K_UP, pygame.K_w):
                jog.movimentacao(0, -PASSO_Y)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                jog.movimentacao(0, PASSO_Y)

    for ctrl in faixa_controladores:
        ctrl.update(agora_ms, carros)

    for c in list(carros):
        c.update(dt)

    verificar_colisoes_e_reset(jog, carros, faixa_controladores)

    tela.fill(FUNDO)

    for c in carros:
        tela.blit(c.surf, c.rect)
    tela.blit(jog.surf, jog.rect)

    pygame.display.flip()

pygame.quit()
sys.exit()