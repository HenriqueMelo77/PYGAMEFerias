# Raposa Louca

Pygame desenvolvido por Gabriel Michinhote, Henrique Melo e João Pita.

Inspirado no clássico "Crossy Road", seguindo com o mesmo objetivo, atravessar as ruas sem ser pego pelos carros. É um jogo 2D, estilo Arcade, possuindo dois modos, campanha, com fases para serem passadas o mais rápido possível, e infinito, com sistema de pontos para estrada avançada.

Vídeo com a gameplay:
https://youtube.com/shorts/abC1gGGweOg?feature=share

Para criação desse jogo, tomamos como inspiração, além da mecânica do próprio jogo e alguns estilos, esse vídeo no YouTube: https://youtu.be/lTfaa0rNLvk?si=2vq5muH62htDG2Vh, e utilizamos de IAs generativas para algumas instruções, como importação de sons e imagens, qualificação de movimentações e em alguns desenvolvimentos.

Visando o melhor funcionamento e jogabilidade, é recomendado ter os seguintes arquivos no repositório:
    -transito durante o jogo.wav
    -carro batendo na raposa.wav
    -click.wav
    -clique do botao.wav
    -gameover.wav
    -musica de fundo da tela inicial.wav
    -pulo da raposa.wav
    -vitoria.wav
    -grama.png, rua01.png (mapa)
    -fox01.png, fox02.png, fox03.png (raposa/jogador)
    -carro1.png, carro2.png, carro3.png, carro4.png, carro5.png, carro6.png (carros/inimigos)
    -caminhao1.png, caminhao2.png, caminhao3.png (caminhoes/inimigos)

MODO DE EXECUÇÃO

 -Clone ou baixe o repositório
 -Instale: pip install pygame
 -Execute o script principal (main.py)

CONTROLES

 -Seta esquerda / A: mover para a esquerda
 -Seta direita / D: mover para a direita
 -Seta para cima / W / SPACE: pular (apenas quando estiver no chão)
 -ESC: volta ao menu / pausa durante gameplay
 -R (na tela de ranking ou game over): voltar / reiniciar dependendo do estado

COMO JOGAR

Ao abrir o jogo, irão aparecer as opções "Campanha", "Infinito", "Informações" e "Sair", ao clicar em Campanha, aparecerá outra tela para iniciar a partida, cujo objetivo será avançar as fases o mais rápido possível e colocar seu nome no ranking, registrando seu tempo; já no modo Infinito, seu objetivo é avançar o máximo de estradas sem morrer, também, ao final da partida, registrando sua pontuação no ranking, competindo contra outros jogadores.

ESTRUTURA

main.py -- loop principal, tela inicial, regras, inputs, HUD, telas de jogo (Campanha e Infinito), rankings.
assets/ -- imagens, sprites, sons, músicas, fontes. ----> assets: https://www.myinstants.com/pt , as imagens são autorais.

PROBLEMAS E SOLUÇÕES

Tela preta ou erro na imagem -- verifique o caminho das imagens e sprites, se batem com o código principal.
Fontes -- caso as fontes não estejam disponíveis, copie as TTF para o diretório.
Erro de som -- verifique o caminho dos arquivos .wav.

CRÉDITOS

Criado com Python e pygame.
Professor Filipe Resina.