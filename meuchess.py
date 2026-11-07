import os
import chess
import chess.pgn
from stockfish import Stockfish
import glob
import pygame
import sys

# CONFIGURAÇÕES INICIAIS DO SISTEMA
# O nome abaixo deve ser exatamente igual ao arquivo de 100MB que você colou na Área de Trabalho:
CAMINHO_STOCKFISH = "C:/Users/Administrator/Desktop/stockfish/stockfish-windows-x86-64-universal.exe"


pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
arquivos_pgn = glob.glob(os.path.join(pasta_downloads, "*.pgn"))

if arquivos_pgn:
    ARQUIVO_PGN = max(arquivos_pgn, key=os.path.getctime)
    print(f"📂 Arquivo PGN carregado: {os.path.basename(ARQUIVO_PGN)}")
else:
    ARQUIVO_PGN = "seus_jogos.pgn"

try:
    stockfish = Stockfish(path=CAMINHO_STOCKFISH)
    stockfish.set_depth(15)
    print("🤖 Stockfish conectado com sucesso!")
except Exception as e:
    print(f"⚠️ Stockfish desativado. Erro: {e}")
    stockfish = None


# CONFIGURAÇÕES DO PYGAME
LARGURA, ALTURA = 600, 600
TAMANHO_CASA = 512 // 8
COR_CLARA = (240, 217, 181)
COR_ESCURA = (181, 136, 99)
COR_SELECIONADA = (130, 151, 105)

UNICODE_PECAS = {
    'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
    'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟'
}

def inicializar_tela():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption("Treinador de Xadrez Blitz")
    return tela
def desenhar_tabuleiro(tela, board, inverter=False, casa_selecionada=None, status_txt="", lance_sugerido="", lance_historico=""):
    tela.fill((40, 44, 52)) # Fundo escuro elegante
    fonte_pecas = pygame.font.SysFont("Segoe UI Symbol", 45)
    fonte_texto = pygame.font.SysFont("Arial", 16)
    
    # Centraliza o tabuleiro de 512x512 na tela de 600x600
    offset_x = (LARGURA - 512) // 2
    offset_y = 20
    
    for linha in range(8):
        for coluna in range(8):
            l_render = 7 - linha if not inverter else linha
            c_render = coluna if not inverter else 7 - coluna
            quadrado = chess.square(c_render, l_render)
            
            if casa_selecionada == quadrado:
                cor = COR_SELECIONADA
            else:
                cor = COR_CLARA if (l_render + c_render) % 2 == 0 else COR_ESCURA
                
            pygame.draw.rect(tela, cor, pygame.Rect(offset_x + coluna * TAMANHO_CASA, offset_y + linha * TAMANHO_CASA, TAMANHO_CASA, TAMANHO_CASA))
            
            peca = board.piece_at(quadrado)
            if peca:
                simbolo = UNICODE_PECAS[peca.symbol()]
                cor_texto = (0, 0, 0) if peca.color == chess.BLACK else (240, 240, 240)
                texto = fonte_pecas.render(simbolo, True, cor_texto)
                area_texto = texto.get_rect(center=(offset_x + coluna * TAMANHO_CASA + TAMANHO_CASA//2, offset_y + linha * TAMANHO_CASA + TAMANHO_CASA//2))
                tela.blit(texto, area_texto)
                
    # Desenha os textos de ajuda embaixo do tabuleiro
    txt_linha1 = fonte_texto.render(status_txt, True, (255, 255, 255))
    txt_linha2 = fonte_texto.render("ESPAÇO: Dica da Engine | ESC: Voltar ao Menu", True, (180, 180, 180))
    tela.blit(txt_linha1, (offset_x, 545))
    tela.blit(txt_linha2, (offset_x, 570))

    # <<< COLE ESTE BLOCO EXATAMENTE AQUI (ANTES DO FLIP)
    # Adicione as hashtags no começo destas linhas para desligá-las:
    if lance_sugerido:
        # print(f"🎯 [DEBUG] Lance recebido! Desenhando seta para: {lance_sugerido}")
        desenhar_seta(tela, lance_sugerido, inverter)
    else:
        # print("⚪ [DEBUG] Nenhum lance sugerido ativo no momento.")
        pass
        # Seta Azul (Histórica) - Cor: (59, 130, 246)
    if lance_historico:
        desenhar_seta(tela, lance_historico, inverter, cor=(59, 130, 246))

    # Seta Vermelha (Stockfish) - Cor: (239, 68, 68)
    if lance_sugerido:
        desenhar_seta(tela, lance_sugerido, inverter, cor=(239, 68, 68))
        
    pygame.display.flip()

    pygame.display.flip()


def desenhar_seta(tela, lance_str, inverter=False, cor=(239, 68, 68)):
    """Desenha uma seta semi-transparente que permite ver as peças por baixo"""
    if not lance_str or len(lance_str) < 4:
        return
        
    casa_origem = lance_str[:2]
    casa_destino = lance_str[2:4]
    
    try:
        sq_origem = chess.parse_square(casa_origem)
        sq_destino = chess.parse_square(casa_destino)
    except ValueError:
        return

    col_o, lin_o = chess.square_file(sq_origem), chess.square_rank(sq_origem)
    col_d, lin_d = chess.square_file(sq_destino), chess.square_rank(sq_destino)
    
    lin_o, lin_d = 7 - lin_o, 7 - lin_d
    
    if inverter:
        col_o, lin_o = 7 - col_o, 7 - lin_o
        col_d, lin_d = 7 - col_d, 7 - lin_d
        
    offset_x = (600 - 512) // 2
    offset_y = 20
    
    start_x = offset_x + col_o * TAMANHO_CASA + TAMANHO_CASA // 2
    start_y = offset_y + lin_o * TAMANHO_CASA + TAMANHO_CASA // 2
    end_x = offset_x + col_d * TAMANHO_CASA + TAMANHO_CASA // 2
    end_y = offset_y + lin_d * TAMANHO_CASA + TAMANHO_CASA // 2
    
    # 🌟 CRIA UMA CAMADA TRANSPARENTE DO TAMANHO DA TELA
    camada_seta = pygame.Surface((600, 600), pygame.SRCALPHA)
    
    # Define a cor com Alpha (R, G, B, Opacidade de 0 a 255)
    # Usamos 110 para ficar suave e legível
    cor_transparente = (cor[0], cor[1], cor[2], 110)
    
    # Desenha a linha principal e a ponta na camada transparente
    pygame.draw.line(camada_seta, cor_transparente, (start_x, start_y), (end_x, end_y), 6)
    pygame.draw.circle(camada_seta, cor_transparente, (end_x, end_y), 9)
    
    # Funde a camada transparente por cima do tabuleiro original
    tela.blit(camada_seta, (0, 0))

def obter_quadrado_do_clique(pos_mouse, inverter=False):
    offset_x = (LARGURA - 512) // 2
    offset_y = 20
    x, y = pos_mouse[0] - offset_x, pos_mouse[1] - offset_y
    
    if 0 <= x < 512 and 0 <= y < 512:
        coluna = x // TAMANHO_CASA
        linha = y // TAMANHO_CASA
        c_xadrez = coluna if not inverter else 7 - coluna
        l_xadrez = 7 - linha if not inverter else linha
        return chess.square(c_xadrez, l_xadrez)
    return None

def analisar_com_engine(board):
    if not stockfish: return "Engine indisponível."
    stockfish.set_fen_position(board.fen())
    avaliacao = stockfish.get_evaluation()
    melhor = stockfish.get_best_move()
    
    # Se for avaliação normal (centipões), formata com sinal e duas casas decimais
    if avaliacao["type"] == "cp":
        val = avaliacao["value"] / 100.0
        return f"🤖 Engine: {val:+.2f} | Melhor: {melhor}"
    else:
        # Se for mate (texto), imprime o texto direto sem tentar aplicar o formatador ':+.2f'
        val = f"Mate em {avaliacao['value']}"
        return f"🤖 Engine: {val} | Melhor: {melhor}"

def mostrar_menu_visual(tela, partidas):
    fonte = pygame.font.SysFont("Arial", 18)
    fonte_tit = pygame.font.SysFont("Arial", 22, bold=True)
    relogio = pygame.time.Clock()
    
    while True:
        tela.fill((30, 32, 38))
        
        tit = fonte_tit.render("Escolha uma partida para treinar:", True, (255, 255, 255))
        tela.blit(tit, (30, 20))
        
        botoes = []
        for idx, p in enumerate(partidas[:12]):
            txt = f"[{idx}] {p.headers.get('White', 'Brancas')[:12]} vs {p.headers.get('Black', 'Negras')[:12]} ({p.headers.get('Date', '')})"
            btn_rect = pygame.Rect(30, 60 + idx * 42, 540, 35)
            
            cor_btn = (50, 55, 65) if btn_rect.collidepoint(pygame.mouse.get_pos()) else (40, 44, 52)
            pygame.draw.rect(tela, cor_btn, btn_rect, border_radius=5)
            
            txt_render = fonte.render(txt, True, (220, 220, 220))
            tela.blit(txt_render, (45, 66 + idx * 42))
            botoes.append((btn_rect, idx))
            
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                for rect, idx in botoes:
                    if rect.collidepoint(evento.pos):
                        return idx
        relogio.tick(30)

def escolher_lado_visual(tela):
    fonte = pygame.font.SysFont("Arial", 24, bold=True)
    relogio = pygame.time.Clock()
    
    btn_w = pygame.Rect(80, 250, 200, 80)
    btn_b = pygame.Rect(320, 250, 200, 80)
    
    while True:
        tela.fill((30, 32, 38))
        tit = fonte.render("Com qual cor você jogou?", True, (255, 255, 255))
        tela.blit(tit, (160, 150))
        
        cor_w = (230, 230, 230) if btn_w.collidepoint(pygame.mouse.get_pos()) else (190, 190, 190)
        pygame.draw.rect(tela, cor_w, btn_w, border_radius=8)
        txt_w = fonte.render("Brancas (W)", True, (0, 0, 0))
        tela.blit(txt_w, (110, 273))
        
        cor_b = (70, 75, 85) if btn_b.collidepoint(pygame.mouse.get_pos()) else (50, 54, 64)
        pygame.draw.rect(tela, cor_b, btn_b, border_radius=8)
        txt_b = fonte.render("Pretas (B)", True, (255, 255, 255))
        tela.blit(txt_b, (365, 273))
        
        pygame.display.flip()
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if btn_w.collidepoint(evento.pos): return 'W'
                if btn_b.collidepoint(evento.pos): return 'B'
        relogio.tick(30)

def treinar_partida(partida, tela):
    board = chess.Board()
    nosso_lado = escolher_lado_visual(tela)
    inverter = (nosso_lado == 'B')
    
    lances_reais = list(partida.mainline_moves())
    indice_lance = 0
    casa_selecionada = None
    lance_seta = ""      # Seta Vermelha (Stockfish)
    lance_real_seta = "" # Seta Azul (Histórico)
    status_txt = "Partida iniciada. Sua vez de jogar!" if nosso_lado == 'W' else "Oponente pensando..."
    relogio = pygame.time.Clock()

    while True:
        vez_das_brancas = board.turn
        eh_nosso_lance = (nosso_lado == 'W' and vez_das_brancas) or (nosso_lado == 'B' and not vez_das_brancas)
        
        desenhar_tabuleiro(tela, board, inverter, casa_selecionada, status_txt, lance_seta, lance_real_seta)
        
        if indice_lance >= len(lances_reais):
            status_txt = "🏁 Fim da partida histórica!"
            desenhar_tabuleiro(tela, board, inverter, casa_selecionada, status_txt, lance_seta, lance_real_seta)
            pygame.time.wait(3000)
            return

        # TURNO DO JOGADOR
        if eh_nosso_lance:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        status_txt = "🔍 Calculando lances..."
                        desenhar_tabuleiro(tela, board, inverter, casa_selecionada, status_txt, lance_seta, lance_real_seta)
                        
                        # Ativa a Seta Azul com o lance histórico real
                        if indice_lance < len(lances_reais):
                            lance_real_seta = lances_reais[indice_lance].uci()
                        
                        # Ativa a Seta Vermelha com o Stockfish
                        if stockfish:
                            stockfish.set_fen_position(board.fen())
                            lance_seta = stockfish.get_best_move()
                            status_txt = analisar_com_engine(board)
                        else:
                            status_txt = "Engine indisponível."
                        
                        desenhar_tabuleiro(tela, board, inverter, casa_selecionada, status_txt, lance_seta, lance_real_seta)
                        
                    elif evento.key == pygame.K_ESCAPE:
                        return
                        
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    quadrado_clicado = obter_quadrado_do_clique(evento.pos, inverter)
                    
                    if quadrado_clicado is not None:
                        if casa_selecionada is None:
                            peca = board.piece_at(quadrado_clicado)
                            if peca and peca.color == board.turn:
                                casa_selecionada = quadrado_clicado
                        else:
                            movimento = chess.Move(casa_selecionada, quadrado_clicado)
                            
                            # Promoção automática de peão
                            if board.piece_at(casa_selecionada) and board.piece_at(casa_selecionada).piece_type == chess.PAWN:
                                if chess.square_rank(quadrado_clicado) in[0, 7]:
                                    movimento.promotion = chess.QUEEN
                            
                            if movimento in board.legal_moves:
                                lance_correto = lances_reais[indice_lance] if indice_lance < len(lances_reais) else None
                                
                                # Verifica se o lance histórico ainda é legal antes de converter para texto
                                if lance_correto and lance_correto in board.legal_moves:
                                    texto_lance_real = board.san(lance_correto)
                                    if movimento == lance_correto:
                                        status_txt = "✅ Correto! Você repetiu o lance real."
                                    else:
                                        status_txt = f"⚠️ Desviou! Jogou {board.san(movimento)} (Na real foi {texto_lance_real})"
                                else:
                                    status_txt = f"🎮 Linha Nova! Você jogou {board.san(movimento)}"
                                
                                board.push(movimento)
                                indice_lance += 1
                                casa_selecionada = None
                                lance_seta = ""      # Limpa as setas após jogar
                                lance_real_seta = ""
                                desenhar_tabuleiro(tela, board, inverter, casa_selecionada, status_txt, lance_seta, lance_real_seta)
                                pygame.time.wait(600)
                            else:
                                casa_selecionada = None
        
        # TURNO DO OPONENTE HISTÓRICO / ENGINE
        else:
            pygame.time.wait(800)
            lance_oponente = None
            
            if indice_lance < len(lances_reais):
                lance_historico = lances_reais[indice_lance]
                if lance_historico in board.legal_moves:
                    lance_oponente = lance_historico
                    status_txt = f"👤 Oponente jogou (Histórico): {board.san(lance_oponente)}"
            
            if lance_oponente is None:
                if stockfish:
                    stockfish.set_fen_position(board.fen())
                    melhor_da_engine = stockfish.get_best_move()
                    if melhor_da_engine:
                        lance_oponente = chess.Move.from_uci(melhor_da_engine)
                        status_txt = f"🤖 Oponente jogou (Stockfish): {board.san(lance_oponente)}"
                
                if lance_oponente is None:
                    lance_oponente = next(iter(board.legal_moves))
                    status_txt = f"👤 Oponente jogou: {board.san(lance_oponente)}"

            board.push(lance_oponente)
            lance_real_seta = lance_oponente.uci() # Desenha a Seta Azul mostrando a jogada dele
            indice_lance += 1
            casa_selecionada = None
            lance_seta = "" # Apaga a seta vermelha de dica
            desenhar_tabuleiro(tela, board, inverter, casa_selecionada, status_txt, lance_seta, lance_real_seta)

        relogio.tick(30)


def main():
    try:
        pgn = open(ARQUIVO_PGN, encoding="utf-8")
    except FileNotFoundError:
        print("❌ Erro: Nenhum arquivo .pgn encontrado.")
        return

    partidas = []
    while True:
        partida = chess.pgn.read_game(pgn)
        if partida is None: break
        partidas.append(partida)

    if not partidas: return
    
    tela = inicializar_tela()
    
    while True:
        idx_escolhido = mostrar_menu_visual(tela, partidas)
        treinar_partida(partidas[idx_escolhido], tela)

if __name__ == "__main__":
    main()
