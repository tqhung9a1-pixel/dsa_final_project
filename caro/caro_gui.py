"""
CHARO — Caro Game GUI
Usage: python caro_gui.py <mode> <depth>
  mode  : 3x3 | 4x4 | 5x5
  depth : integer
"""
from core_engine import Board, GameEngine, BaseAI
import pygame
import sys
import os
import math
import threading

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)


def load_ai(mode, depth):
    """Khởi tạo và trả về đối tượng AI phù hợp với kích thước bàn cờ và độ sâu tìm kiếm."""
    if mode == "3x3":
        from ai_3x3 import AI_3x3
        return AI_3x3(symbol="O", depth=depth)
    elif mode == "4x4":
        from ai_4x4 import AI_4x4
        return AI_4x4(symbol="O", depth=depth)
    else:
        from ai_5x5 import AI_5x5
        return AI_5x5(symbol="O", depth=depth)


mode = sys.argv[1] if len(sys.argv) > 1 else "3x3"
depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
is_pvp = len(sys.argv) > 3 and sys.argv[3] == "pvp"

SIZE_MAP = {"3x3": 3, "4x4": 4, "5x5": 10}
WIN_MAP = {"3x3": 3, "4x4": 4, "5x5": 5}
BOARD_N = SIZE_MAP[mode]
WIN_COND = WIN_MAP[mode]

pygame.init()
SQ = max(44, min(76, 580 // BOARD_N))
PAD = 50
PNL_W = 220
SCR_W = SQ * BOARD_N + PAD * 2 + PNL_W
SCR_H = max(480, SQ * BOARD_N + PAD * 2)
screen = pygame.display.set_mode((SCR_W, SCR_H))
pygame.display.set_caption(f"CHARO  |  Caro {mode.upper()}")
clock = pygame.time.Clock()
FPS = 60

BG = (4,   2,  12)
GRID = (0,  180, 165)
X_COL = (0,  220, 200)
O_COL = (210,  0, 180)
WIN_C = (255, 210,  50)
PNL_BG = (8,   4,  20)
WHITE = (255, 255, 255)
GRAY = (130, 130, 150)
DIM = (55,  55,  70)


def mf(size, bold=True):
    """Tạo font chữ với kích thước cho trước, có fallback sang font mặc định nếu cần."""
    for n in ["Consolas", "Courier New", "Lucida Console"]:
        try:
            f = pygame.font.SysFont(n, size, bold=bold)
            if f:
                return f
        except:
            pass
    return pygame.font.Font(None, size)


F_TITLE = mf(20, bold=True)
F_INFO = mf(17, bold=False)
F_SMALL = mf(14, bold=False)
F_BIG = mf(36, bold=True)


def txt(surf, text, font, cx, cy, color):
    """Vẽ văn bản căn giữa tại vị trí (cx, cy) trên bề mặt surf."""
    s = font.render(text, True, color)
    surf.blit(s, (cx - s.get_width()//2, cy - s.get_height()//2))


def txt_l(surf, text, font, x, y, color):
    """Vẽ văn bản căn trái tại vị trí (x, y) trên bề mặt surf."""
    surf.blit(font.render(text, True, color), (x, y))


def soft_glow_line(surf, p1, p2, color, thick=2):
    """Vẽ đoạn thẳng với hiệu ứng phát sáng mềm (nhiều lớp alpha)."""
    tmp = pygame.Surface((SCR_W, SCR_H), pygame.SRCALPHA)
    pygame.draw.line(tmp, (*color, 35), p1, p2, thick + 6)
    pygame.draw.line(tmp, (*color, 90), p1, p2, thick + 2)
    surf.blit(tmp, (0, 0))
    pygame.draw.line(surf, color, p1, p2, thick)


def soft_glow_circle(surf, cx, cy, r, color, thick=3):
    """Vẽ hình tròn với hiệu ứng phát sáng mềm (nhiều lớp alpha)."""
    tmp = pygame.Surface((SCR_W, SCR_H), pygame.SRCALPHA)
    pygame.draw.circle(tmp, (*color, 35), (cx, cy), r + 4, thick + 4)
    pygame.draw.circle(tmp, (*color, 90), (cx, cy), r + 1, thick + 2)
    surf.blit(tmp, (0, 0))
    pygame.draw.circle(surf, color, (cx, cy), r, thick)


def cell_px(r, c):
    """Chuyển đổi tọa độ ô lưới (hàng, cột) sang tọa độ pixel trung tâm ô đó."""
    return PAD + c*SQ + SQ//2, PAD + r*SQ + SQ//2


def px_cell(mx, my):
    """Chuyển đổi tọa độ pixel từ chuột sang tọa độ ô lưới (hàng, cột), trả None nếu ngoài bàn."""
    c = (mx - PAD) // SQ
    r = (my - PAD) // SQ
    if 0 <= r < BOARD_N and 0 <= c < BOARD_N:
        return r, c
    return None, None


board = Board(BOARD_N)
engine = GameEngine(board, WIN_COND)
ai = load_ai(mode, depth)
ai.symbol = "O"

cur_player = "X"
game_over = False
winner = None
ai_thinking = False
ai_result = [None]
win_cells = []
t_anim = 0.0


def find_win_cells(player):
    """Tìm và trả về danh sách các ô tạo thành chuỗi thắng của người chơi."""
    g, n, w = board.grid, board.size, WIN_COND
    for r in range(n):
        for c in range(n):
            for dr, dc in [(0, 1), (1, 0), (1, 1), (1, -1)]:
                cells = []
                for k in range(w):
                    nr, nc = r+k*dr, c+k*dc
                    if 0 <= nr < n and 0 <= nc < n and g[nr][nc] == player:
                        cells.append((nr, nc))
                    else:
                        break
                if len(cells) == w:
                    return cells
    return []


def restart():
    """Đặt lại toàn bộ trạng thái trò chơi về ban đầu."""
    global board, engine, ai, cur_player, game_over, winner
    global ai_thinking, ai_result, win_cells
    board = Board(BOARD_N)
    engine = GameEngine(board, WIN_COND)
    ai = load_ai(mode, depth)
    ai.symbol = "O"
    cur_player = "X"
    game_over = False
    winner = None
    ai_thinking = False
    ai_result = [None]
    win_cells = []


STARS = [(int((i*317+j*193) % SCR_W), int((i*193+j*317) % SCR_H), (i*11+j*7) % 50)
         for i in range(5) for j in range(6)]


def draw_bg(t):
    """Vẽ nền với hiệu ứng sao nhấp nháy theo thời gian."""
    screen.fill(BG)
    for sx, sy, ph in STARS:
        a = int(50 + 30 * math.sin(t*0.6 + ph))
        s = pygame.Surface((2, 2), pygame.SRCALPHA)
        s.fill((*WHITE, a))
        screen.blit(s, (sx, sy))


def draw_grid():
    """Vẽ lưới bàn cờ với viền bo góc và hiệu ứng nền mờ."""
    board_w = SQ * BOARD_N
    board_h = SQ * BOARD_N
    tmp = pygame.Surface((board_w+2, board_h+2), pygame.SRCALPHA)
    pygame.draw.rect(tmp, (*GRID, 40), (0, 0, board_w +
                                        2, board_h+2), border_radius=4)
    screen.blit(tmp, (PAD-1, PAD-1))

    for i in range(BOARD_N + 1):
        x = PAD + i*SQ
        y = PAD + i*SQ
        pygame.draw.line(screen, (*GRID, 160), (x, PAD), (x, PAD + board_h), 1)
        pygame.draw.line(screen, (*GRID, 160), (PAD, y), (PAD + board_w, y), 1)
    pygame.draw.rect(screen, GRID, (PAD, PAD, board_w,
                                    board_h), 2, border_radius=4)


def draw_pieces():
    """Vẽ các quân cờ X và O đã đặt trên bàn với hiệu ứng glow."""
    for r in range(BOARD_N):
        for c in range(BOARD_N):
            p = board.grid[r][c]
            if p == " ":
                continue
            cx, cy = cell_px(r, c)
            m = max(7, SQ//2 - 9)
            tk = max(2, SQ//14)
            if p == "X":
                soft_glow_line(screen, (cx-m, cy-m), (cx+m, cy+m), X_COL, tk)
                soft_glow_line(screen, (cx+m, cy-m), (cx-m, cy+m), X_COL, tk)
            else:
                soft_glow_circle(screen, cx, cy, m, O_COL, tk)


def draw_highlights(hint_move):
    """Vẽ highlight cho nước đi cuối và ô gợi ý (nếu có)."""
    if hasattr(board, 'move_history') and len(board.move_history) > 0:
        lr, lc, piece = board.move_history[-1]
        pygame.draw.rect(screen, (255, 255, 0),
                         (PAD + lc*SQ, PAD + lr*SQ, SQ, SQ), 3)

    if hint_move:
        hr, hc = hint_move
        pygame.draw.rect(screen, (0, 255, 0),
                         (PAD + hc*SQ, PAD + hr*SQ, SQ, SQ), 4)


def draw_win_cells(t):
    """Vẽ hiệu ứng pulse trên các ô thắng cuộc."""
    pulse = int(55 + 30 * math.sin(t * 3.5))
    for r, c in win_cells:
        s = pygame.Surface((SQ, SQ), pygame.SRCALPHA)
        s.fill((*WIN_C, pulse))
        screen.blit(s, (PAD + c*SQ, PAD + r*SQ))
        pygame.draw.rect(screen, (*WIN_C, 180),
                         (PAD+c*SQ, PAD+r*SQ, SQ, SQ), 2)


def draw_hover(hr, hc):
    """Vẽ hiệu ứng hover khi di chuột lên ô trống hợp lệ."""
    if hr is None or board.grid[hr][hc] != " " or game_over:
        return
    s = pygame.Surface((SQ, SQ), pygame.SRCALPHA)
    s.fill((*X_COL, 22))
    screen.blit(s, (PAD + hc*SQ, PAD + hr*SQ))
    pygame.draw.rect(screen, (*X_COL, 80), (PAD+hc*SQ, PAD+hr*SQ, SQ, SQ), 1)


def draw_panel():
    """Vẽ panel bên phải hiển thị thông tin trò chơi và hướng dẫn phím."""
    px = PAD + SQ*BOARD_N + 12
    pw = PNL_W - 12
    pcx = px + pw//2

    tmp = pygame.Surface((PNL_W, SCR_H), pygame.SRCALPHA)
    tmp.fill((*PNL_BG, 230))
    screen.blit(tmp, (PAD + SQ*BOARD_N, 0))
    pygame.draw.line(screen, (*GRID, 60), (PAD + SQ*BOARD_N, 0),
                     (PAD + SQ*BOARD_N, SCR_H), 1)

    y = 28
    txt(screen, "CHARO", F_TITLE, pcx, y, WHITE)
    y += 30
    pygame.draw.line(screen, (*GRID, 60), (px, y), (px+pw, y))
    y += 12

    txt_l(screen, f"Mode :  {mode.upper()}", F_INFO, px, y, GRAY)
    y += 24
    txt_l(screen, f"Depth:  {depth}",        F_INFO, px, y, GRAY)
    y += 24
    pygame.draw.line(screen, (*GRID, 40), (px, y), (px+pw, y))
    y += 16

    if not game_over:
        if ai_thinking:
            txt(screen, "AI thinking...", F_SMALL, pcx, y+10, O_COL)
        else:
            if is_pvp:
                who = f"Player {cur_player} Turn"
            else:
                who = "Your turn  (X)" if cur_player == "X" else "AI turn    (O)"
            col = X_COL if cur_player == "X" else O_COL
            txt(screen, who, F_SMALL, pcx, y+10, col)
        y += 36
    else:
        if winner == "X":
            msg = "X WINS!" if is_pvp else "YOU WIN!"
            txt(screen, msg, F_BIG, pcx, y+18, WIN_C)
        elif winner == "O":
            msg = "O WINS!" if is_pvp else "AI WINS!"
            txt(screen, msg, F_BIG, pcx, y+18, O_COL)
        else:
            txt(screen, "DRAW", F_BIG, pcx, y+18, GRAY)
        y += 50

    y = SCR_H - 90
    pygame.draw.line(screen, (*GRID, 40), (px, y), (px+pw, y))
    y += 10
    txt_l(screen, "S    Gợi ý nước đi", F_SMALL,
          px, y, (0, 255, 0))
    y += 22
    txt_l(screen, "Z    Undo", F_SMALL, px, y, WIN_C)
    y += 22
    txt_l(screen, "R    Restart", F_SMALL, px, y, DIM)
    y += 22
    txt_l(screen, "ESC  Exit",   F_SMALL, px, y, DIM)


def ai_thread():
    """Hàm chạy trong thread riêng để tính nước đi AI, tránh block GUI."""
    global ai_thinking
    ai_result[0] = ai.get_best_move(board, engine)
    ai_thinking = False


def main():
    """Vòng lặp chính của game: xử lý sự kiện, cập nhật logic, và vẽ màn hình."""
    global cur_player, game_over, winner, ai_thinking, t_anim, win_cells
    hr = hc = None
    hint_move = None

    while True:
        dt = clock.tick(FPS) / 1000.0
        t_anim += dt
        mx, my = pygame.mouse.get_pos()
        hr, hc = px_cell(mx, my)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if ev.key == pygame.K_r:
                    restart()
                    hint_move = None

                if ev.key == pygame.K_z:
                    if not ai_thinking and hasattr(board, 'move_history') and len(board.move_history) >= 2:
                        board.undo_last_move()
                        board.undo_last_move()
                        hint_move = None

                        game_over = False
                        winner = None
                        win_cells = []
                        cur_player = "X"

                if ev.key == pygame.K_s:
                    if not game_over and not ai_thinking and cur_player == "X":
                        old_sym = ai.symbol
                        ai.symbol = "X"
                        ai.opponent = "O"
                        best_move = ai.get_best_move(board, engine)
                        if best_move:
                            hint_move = best_move
                        ai.symbol = old_sym
                        ai.opponent = "X"

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if not game_over and not ai_thinking:
                    r, c = px_cell(mx, my)
                    if r is not None and board.is_valid_move(r, c):
                        board.place_piece(r, c, cur_player, is_real=True)
                        hint_move = None
                        if engine.check_winner(cur_player):
                            win_cells = find_win_cells(cur_player)
                            game_over = True
                            winner = cur_player
                        elif board.is_full():
                            game_over = True
                            winner = None
                        else:
                            if not is_pvp:
                                cur_player = "O"
                                ai_thinking = True
                                ai_result[0] = None
                                threading.Thread(target=ai_thread,
                                                 daemon=True).start()
                            else:
                                cur_player = "O" if cur_player == "X" else "X"

        if not ai_thinking and cur_player == "O" and ai_result[0] is not None:
            r, c = ai_result[0]
            ai_result[0] = None
            if board.is_valid_move(r, c):
                board.place_piece(r, c, "O", is_real=True)
                hint_move = None
                if engine.check_winner("O"):
                    win_cells = find_win_cells("O")
                    game_over = True
                    winner = "O"
                elif board.is_full():
                    game_over = True
                    winner = None
                else:
                    cur_player = "X"

        # Render
        draw_bg(t_anim)
        draw_grid()
        draw_highlights(hint_move)
        if win_cells:
            draw_win_cells(t_anim)
        draw_pieces()
        if not game_over:
            draw_hover(hr, hc)
        draw_panel()
        pygame.display.flip()


if __name__ == "__main__":
    main()
