# """
# CHARO — Chess GUI  (Neon style)
# Usage: python gui.py [depth]
# """
# import pygame
# import sys
# import os
# import math

# from game_state import GameState
# from move import Move
# from ai_engine import get_best_move

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(BASE_DIR)

# # ── Window ────────────────────────────────────────────────
# SQ = 80
# BOARD_PX = SQ * 8
# PNL_W = 230
# W = BOARD_PX + PNL_W
# H = BOARD_PX
# FPS = 60

# # ── Neon palette ──────────────────────────────────────────
# BG_OUT = (2,   0,   8)
# SQ_DARK = (15,  8,  30)
# SQ_LIGHT = (22,  14, 42)
# CYAN = (0,  220, 200)
# PINK = (210,  0, 175)
# GOLD = (255, 210,  50)
# WHITE = (255, 255, 255)
# GRAY = (130, 130, 150)
# DIM = (55,  55,  70)
# PNL_BG = (6,   3,  16)

# HL_SEL = (0,  220, 200,  55)
# HL_MOVE = (0,  220, 200,  80)
# HL_CAP = (210,  0, 175,  90)
# HL_LAST = (255, 210,  50,  45)

# GRID_COL = (40,  28,  70)

# # ── Fonts ─────────────────────────────────────────────────


# def mf(size, bold=True):
#     for n in ["Consolas", "Courier New", "Lucida Console"]:
#         try:
#             f = pygame.font.SysFont(n, size, bold=bold)
#             if f:
#                 return f
#         except:
#             pass
#     return pygame.font.Font(None, size)

# # ── Helpers ───────────────────────────────────────────────


# def sq_to_xy(sq):
#     f, r = sq % 8, sq // 8
#     return f * SQ, (7 - r) * SQ


# def xy_to_sq(x, y):
#     f, r = x // SQ, 7 - y // SQ
#     if 0 <= f < 8 and 0 <= r < 8:
#         return r * 8 + f
#     return None


# def draw_txt(surf, text, font, cx, cy, color):
#     s = font.render(text, True, color)
#     surf.blit(s, (cx - s.get_width()//2, cy - s.get_height()//2))


# def draw_txt_l(surf, text, font, x, y, color):
#     surf.blit(font.render(text, True, color), (x, y))


# def neon_line(surf, p1, p2, color, w=1):
#     tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
#     pygame.draw.line(tmp, (*color, 40), p1, p2, w + 4)
#     surf.blit(tmp, (0, 0))
#     pygame.draw.line(surf, color, p1, p2, w)


# def t_anim():
#     return pygame.time.get_ticks() / 1000.0


# # ── Stars (static) ────────────────────────────────────────
# STARS = [(int((i*337+j*179) % W), int((i*179+j*337) % H), (i*7+j*13) % 60)
#          for i in range(5) for j in range(7)]

# # ══════════════════════════════════════════════════════════


# class ChessGUI:
#     MODES = ["PVP", "PVE", "EVE"]
#     AI_DEPTH = {"Easy": 1, "Medium": 2, "Hard": 3, "Expert": 4}

#     def __init__(self):
#         pygame.init()
#         pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
#         self.screen = pygame.display.set_mode((W, H))
#         pygame.display.set_caption("CHARO  |  Chess")

#         self.mode_idx = 1
#         self.diff = "Medium"
#         self._reset_state()

#         self.pieces = self._load_pieces()
#         self.sounds = self._load_sounds()
#         self.f_sm = mf(15, bold=False)
#         self.f_md = mf(18, bold=True)
#         self.f_big = mf(32, bold=True)
#         self.f_coord = mf(12, bold=False)
#         self.f_title = mf(22, bold=True)

#     @property
#     def mode(self): return self.MODES[self.mode_idx]

#     def _reset_state(self):
#         self.gs = GameState()
#         self.legal = self.gs.get_legal_moves()
#         self.sel = None
#         self.sel_mv = []
#         self.last_move = None
#         self.over = False
#         self.status = "Ongoing"
#         self.dragging = False
#         self.drag_sq = None
#         self.drag_img = None
#         self.drag_pos = (0, 0)
#         self._ai_thinking = False
#         self.hint_move = None
#         self._hint_result = [None]

#     # ── Asset loading ──────────────────────────────────────
#     def _load_pieces(self):
#         pieces = {}
#         d = os.path.join(BASE_DIR, "assets", "pieces_2d")
#         names = ["wP", "wN", "wB", "wR", "wQ", "wK",
#                  "bP", "bN", "bB", "bR", "bQ", "bK"]
#         for n in names:
#             p = os.path.join(d, n + ".png")
#             if os.path.exists(p):
#                 img = pygame.image.load(p).convert_alpha()
#                 pieces[n] = pygame.transform.smoothscale(img, (SQ, SQ))
#         return pieces

#     def _load_sounds(self):
#         sounds = {}
#         d = os.path.join(BASE_DIR, "assets", "sounds")
#         for name in ["select", "move", "capture", "check", "game_over"]:
#             p = os.path.join(d, name + ".wav")
#             if os.path.exists(p):
#                 try:
#                     sounds[name] = pygame.mixer.Sound(p)
#                 except:
#                     pass
#         return sounds

#     def _play(self, name):
#         if name in self.sounds:
#             self.sounds[name].play()

#     def _piece_at(self, sq):
#         for n, bb in self.gs.board.bitboards.items():
#             if bb & (1 << sq):
#                 return n
#         return None

#     # ── Drawing ────────────────────────────────────────────
#     def _draw_bg(self):
#         self.screen.fill(BG_OUT)
#         t = t_anim()
#         for sx, sy, ph in STARS:
#             a = int(50 + 28 * math.sin(t * 0.7 + ph))
#             s = pygame.Surface((2, 2), pygame.SRCALPHA)
#             s.fill((*WHITE, a))
#             self.screen.blit(s, (sx, sy))

#     def _draw_board(self):
#         t = t_anim()
#         for sq in range(64):
#             f, r = sq % 8, sq // 8
#             x, y = sq_to_xy(sq)
#             base = SQ_LIGHT if (f + r) % 2 == 0 else SQ_DARK
#             pygame.draw.rect(self.screen, base, (x, y, SQ, SQ))
#             # subtle grid line
#             pygame.draw.rect(self.screen, GRID_COL, (x, y, SQ, SQ), 1)

#         # Board outer border (animated glow)
#         pulse = int(120 + 40 * math.sin(t * 1.2))
#         tmp = pygame.Surface((BOARD_PX + 8, BOARD_PX + 8), pygame.SRCALPHA)
#         pygame.draw.rect(tmp, (*PINK, pulse // 3),
#                          (0, 0, BOARD_PX+8, BOARD_PX+8), 3, border_radius=4)
#         self.screen.blit(tmp, (-4, -4))
#         pygame.draw.rect(self.screen, PINK, (0, 0, BOARD_PX, BOARD_PX), 2)

#         # Coordinates
#         for f in range(8):
#             col = CYAN if f % 2 == 0 else (*CYAN[:2], CYAN[2]//2 + 80)
#             s = self.f_coord.render(chr(ord("a") + f), True, GRAY)
#             self.screen.blit(s, (f*SQ + SQ - s.get_width() -
#                              3, BOARD_PX - s.get_height() - 2))
#         for r in range(8):
#             s = self.f_coord.render(str(r + 1), True, GRAY)
#             self.screen.blit(s, (2, (7 - r)*SQ + 2))

#     def _draw_highlights(self):
#         surf = pygame.Surface((BOARD_PX, BOARD_PX), pygame.SRCALPHA)
#         t = t_anim()

#         # Last move
#         if self.last_move:
#             for sq in self.last_move:
#                 x, y = sq_to_xy(sq)
#                 pygame.draw.rect(surf, HL_LAST, (x, y, SQ, SQ))

#         # Selected square
#         if self.sel is not None:
#             x, y = sq_to_xy(self.sel)
#             pygame.draw.rect(surf, HL_SEL, (x, y, SQ, SQ))
#             # Animated border
#             pulse = int(160 + 60 * math.sin(t * 3))
#             pygame.draw.rect(surf, (*CYAN, pulse), (x, y, SQ, SQ), 2)

#         # Legal moves
#         for m in self.sel_mv:
#             tg = Move.get_target(m)
#             cap = bool(self.gs.board.all_pieces & (1 << tg))
#             cx, cy = sq_to_xy(tg)
#             cx += SQ // 2
#             cy += SQ // 2
#             if cap:
#                 pygame.draw.circle(surf, HL_CAP, (cx, cy), SQ//2 - 3, 5)
#             else:
#                 pygame.draw.circle(surf, HL_MOVE, (cx, cy), SQ // 5)

#         # King in check
#         if self.gs.is_in_check():
#             key = "wK" if self.gs.white_to_move else "bK"
#             bb = self.gs.board.bitboards.get(key, 0)
#             pulse = int(140 + 80 * math.sin(t * 4))
#             for sq in range(64):
#                 if bb & (1 << sq):
#                     x, y = sq_to_xy(sq)
#                     for i in range(SQ//2, 0, -4):
#                         a = int(pulse * (1 - i / (SQ//2)))
#                         pygame.draw.circle(surf, (220, 0, 0, a),
#                                            (x + SQ//2, y + SQ//2), i)

#         if self.hint_move:
#             for sq, color in [(self.hint_move[0], (255, 255, 0, 60)),
#                               (self.hint_move[1], (0, 255, 120, 80))]:
#                 x, y = sq_to_xy(sq)
#                 pygame.draw.rect(surf, color, (x, y, SQ, SQ))
#                 pygame.draw.rect(surf, (*color[:3], 180), (x, y, SQ, SQ), 3)
#         self.screen.blit(surf, (0, 0))

#     def _draw_pieces(self):
#         for sq in range(64):
#             if self.dragging and sq == self.drag_sq:
#                 continue
#             name = self._piece_at(sq)
#             if name and name in self.pieces:
#                 x, y = sq_to_xy(sq)
#                 self.screen.blit(self.pieces[name], (x, y))
#         if self.dragging and self.drag_img:
#             mx, my = self.drag_pos
#             r = self.drag_img.get_rect(center=(mx, my))
#             self.screen.blit(self.drag_img, r)

#     def _draw_panel(self):
#         px = BOARD_PX + 14
#         pw = PNL_W - 18
#         pcx = BOARD_PX + PNL_W // 2
#         t = t_anim()

#         # Panel bg
#         tmp = pygame.Surface((PNL_W, H), pygame.SRCALPHA)
#         tmp.fill((*PNL_BG, 240))
#         self.screen.blit(tmp, (BOARD_PX, 0))
#         neon_line(self.screen, (BOARD_PX, 0), (BOARD_PX, H), PINK, w=1)

#         y = 24
#         # Title
#         draw_txt(self.screen, "CHARO", self.f_title, pcx, y, WHITE)
#         y += 28

#         # Divider
#         neon_line(self.screen, (px, y), (px+pw, y), PINK, w=1)
#         y += 14

#         # Turn indicator
#         if not self.over:
#             turn = "WHITE" if self.gs.white_to_move else "BLACK"
#             col = CYAN if self.gs.white_to_move else PINK
#             draw_txt(self.screen, f"Turn: {turn}", self.f_md, pcx, y+10, col)
#         y += 32

#         # Mode / diff
#         draw_txt_l(self.screen, f"Mode :  {self.mode}", self.f_sm, px, y, GRAY)
#         y += 22
#         draw_txt_l(
#             self.screen, f"AI   :  {self.diff}",  self.f_sm, px, y, GRAY)
#         y += 22

#         neon_line(self.screen, (px, y), (px+pw, y), PINK, w=1)
#         y += 14

#         # Moves / last
#         draw_txt_l(
#             self.screen, f"Moves: {len(self.gs.move_log)}", self.f_sm, px, y, GRAY)
#         y += 22
#         if self.last_move:
#             sf = chr(ord("a") + self.last_move[0] %
#                      8) + str(self.last_move[0]//8+1)
#             tf = chr(ord("a") + self.last_move[1] %
#                      8) + str(self.last_move[1]//8+1)
#             draw_txt_l(
#                 self.screen, f"Last:  {sf}-{tf}", self.f_sm, px, y, GRAY)
#         y += 22

#         neon_line(self.screen, (px, y), (px+pw, y), PINK, w=1)
#         y += 14

#         # AI thinking
#         if self._ai_thinking:
#             pulse = int(180 + 60 * math.sin(t * 4))
#             col = (*PINK, pulse)
#             draw_txt(self.screen, "AI thinking...", self.f_sm, pcx, y+10, PINK)
#             y += 30
#         elif self.over:
#             msgs = {
#                 "Checkmate-BlackWins": ("BLACK WINS!", PINK),
#                 "Checkmate-WhiteWins": ("WHITE WINS!", CYAN),
#                 "Stalemate":           ("STALEMATE",   GOLD),
#                 "Draw-50Move":         ("DRAW",         GRAY),
#             }
#             msg, col = msgs.get(self.status, ("GAME OVER", GRAY))
#             draw_txt(self.screen, msg, self.f_big, pcx, y+20, col)
#             y += 50

#         # Controls at bottom
#         y = H - 110
#         neon_line(self.screen, (px, y), (px+pw, y), PINK, w=1)
#         y += 12
#         controls = [("R", "Restart"), ("Z", "Undo"), ("S", "Hint"),
#                     ("E", "Editor"), ("ESC", "Quit")]
#         for key, desc in controls:
#             k = self.f_sm.render(f"[{key}]", True, GOLD)
#             d = self.f_sm.render(desc, True, DIM)
#             self.screen.blit(k, (px, y))
#             self.screen.blit(d, (px + 48, y))
#             y += 20

#     def _render(self):
#         self._draw_bg()
#         self._draw_board()
#         self._draw_highlights()
#         self._draw_pieces()
#         self._draw_panel()
#         pygame.display.flip()

#     # ── Input ──────────────────────────────────────────────
#     def _handle_down(self, mx, my):
#         if self.over or my >= BOARD_PX or mx >= BOARD_PX:
#             return
#         if self.mode == "EVE":
#             return
#         is_ai_turn = (self.mode == "PVE" and not self.gs.white_to_move) or (
#             self.mode == "EVE")
#         if is_ai_turn:
#             return
#         sq = xy_to_sq(mx, my)
#         if sq is None:
#             return
#         pfx = "w" if self.gs.white_to_move else "b"
#         p = self._piece_at(sq)

#         if self.sel is not None:
#             matching = [m for m in self.sel_mv if Move.get_target(m) == sq]
#             if matching:
#                 self._exec(matching)
#                 return
#             if p and p.startswith(pfx):
#                 self._start_sel(sq, p)
#                 return
#             self.sel = None
#             self.sel_mv = []
#             return

#         if p and p.startswith(pfx):
#             self._start_sel(sq, p)

#     def _start_sel(self, sq, piece):
#         self.sel = sq
#         self.sel_mv = [m for m in self.legal if Move.get_start(m) == sq]
#         self.dragging = True
#         self.drag_sq = sq
#         self.drag_img = self.pieces.get(piece)
#         self.drag_pos = pygame.mouse.get_pos()
#         self._play("select")

#     def _handle_up(self, mx, my):
#         if not self.dragging:
#             return
#         self.dragging = False
#         if my >= BOARD_PX or mx >= BOARD_PX:
#             self.drag_sq = None
#             return
#         sq = xy_to_sq(mx, my)
#         if sq is not None and sq != self.drag_sq:
#             matching = [m for m in self.sel_mv if Move.get_target(m) == sq]
#             if matching:
#                 self._exec(matching)
#         self.drag_sq = None

#     def _exec(self, matching):
#         move = matching[0]
#         for m in matching:
#             if Move.get_flag(m) in (Move.PROMOTION_QUEEN, Move.PROMOTION_CAPTURE_QUEEN):
#                 move = m
#                 break
#         flag = Move.get_flag(move)
#         is_cap = flag in (Move.CAPTURE, Move.EN_PASSANT,
#                           Move.PROMOTION_CAPTURE_QUEEN, Move.PROMOTION_CAPTURE_ROOK,
#                           Move.PROMOTION_CAPTURE_BISHOP, Move.PROMOTION_CAPTURE_KNIGHT)
#         self.hint_move = None
#         self.last_move = (Move.get_start(move), Move.get_target(move))
#         self.gs.make_move(move)
#         self.legal = self.gs.get_legal_moves()
#         self.sel = None
#         self.sel_mv = []
#         self.status = self.gs.get_game_status()
#         if self.status != "Ongoing":
#             self._play("game_over")
#             self.over = True
#         elif self.gs.is_in_check():
#             self._play("check")
#         elif is_cap:
#             self._play("capture")
#         else:
#             self._play("move")

#     def _do_ai(self):
#         self._ai_thinking = True
#         self._render()
#         depth = self.AI_DEPTH.get(self.diff, 2)
#         best = get_best_move(self.gs, depth=depth)
#         if best:
#             flag = Move.get_flag(best)
#             is_cap = flag in (Move.CAPTURE, Move.EN_PASSANT,
#                               Move.PROMOTION_CAPTURE_QUEEN, Move.PROMOTION_CAPTURE_ROOK,
#                               Move.PROMOTION_CAPTURE_BISHOP, Move.PROMOTION_CAPTURE_KNIGHT)
#             self.last_move = (Move.get_start(best), Move.get_target(best))
#             self.gs.make_move(best)
#             self.legal = self.gs.get_legal_moves()
#             self.status = self.gs.get_game_status()
#             if self.status != "Ongoing":
#                 self._play("game_over")
#                 self.over = True
#             elif self.gs.is_in_check():
#                 self._play("check")
#             elif is_cap:
#                 self._play("capture")
#             else:
#                 self._play("move")
#         self._ai_thinking = False

#     def _hint_thread(self):
#         import threading
#         import copy
#         gs_copy = copy.deepcopy(self.gs)
#         depth = self.AI_DEPTH.get(self.diff, 2)

#         def _run():
#             move = get_best_move(gs_copy, depth=depth)
#             self._hint_result[0] = move if move else False

#         threading.Thread(target=_run, daemon=True).start()

#     def restart(self):
#         self._reset_state()

#     # ── Main loop ──────────────────────────────────────────
#     def run(self):
#         clock = pygame.time.Clock()
#         DIFFS = list(self.AI_DEPTH.keys())

#         while True:
#             is_ai = (self.mode == "PVE" and not self.gs.white_to_move) or (
#                 self.mode == "EVE")

#             for ev in pygame.event.get():
#                 if ev.type == pygame.QUIT:
#                     pygame.quit()
#                     sys.exit()
#                 if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
#                     self._handle_down(*ev.pos)
#                 if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
#                     self._handle_up(*ev.pos)
#                 if ev.type == pygame.MOUSEMOTION and self.dragging:
#                     self.drag_pos = ev.pos
#                 if ev.type == pygame.KEYDOWN:
#                     if ev.key == pygame.K_ESCAPE:
#                         pygame.quit()
#                         sys.exit()
#                     if ev.key == pygame.K_r:
#                         self.restart()
#                     if ev.key == pygame.K_s:
#                         if not self.over and not self._ai_thinking and self._hint_result[0] is None:
#                             if self.mode == "PVP" or (self.mode == "PVE" and self.gs.white_to_move):
#                                 self._hint_result[0] = None
#                                 self._hint_thread()
#                     if ev.key == pygame.K_e and not self._ai_thinking:
#                         from board_editor import BoardEditor
#                         editor = BoardEditor(self.screen, self.pieces)
#                         res = editor.run()
#                         if res:
#                             self.gs.board.bitboards = res["bitboards"].copy()
#                             self.gs.white_to_move = res["white_to_move"]

#                             w_pieces = sum(self.gs.board.bitboards[p] for p in [
#                                            "wK", "wQ", "wR", "wB", "wN", "wP"])
#                             b_pieces = sum(self.gs.board.bitboards[p] for p in [
#                                            "bK", "bQ", "bR", "bB", "bN", "bP"])
#                             self.gs.board.white_pieces = w_pieces
#                             self.gs.board.black_pieces = b_pieces
#                             self.gs.board.all_pieces = w_pieces | b_pieces

#                             self.gs.move_log = []
#                             self.legal = self.gs.get_legal_moves()
#                             self.sel = None
#                             self.sel_mv = []
#                             self.status = self.gs.get_game_status()
#                             self.over = (self.status != "Ongoing")
#                             self.last_move = None

#                             if "depth" in res:
#                                 diff_map_rev = {
#                                     1: "Easy", 2: "Medium", 3: "Hard", 4: "Expert"}
#                                 self.diff = diff_map_rev.get(
#                                     res["depth"], self.diff)
#                     if ev.key == pygame.K_d:
#                         idx = DIFFS.index(self.diff)
#                         self.diff = DIFFS[(idx + 1) % len(DIFFS)]
#                     if ev.key == pygame.K_z and not self.over and not is_ai:
#                         self.gs.unmake_move()
#                         if self.mode == "PVE":
#                             self.gs.unmake_move()
#                         self.legal = self.gs.get_legal_moves()
#                         self.sel = None
#                         self.sel_mv = []
#                         self.over = False
#                         self.status = "Ongoing"
#                         self.last_move = None
#             if self._hint_result[0] is not None and self._hint_result[0] is not False:
#                 move = self._hint_result[0]
#                 self._hint_result[0] = None
#                 self.hint_move = (Move.get_start(move), Move.get_target(move))
#             self._render()
#             clock.tick(FPS)

#             if is_ai and not self._ai_thinking:
#                 pygame.time.delay(120)
#                 self._do_ai()
#                 if self.mode == "EVE":
#                     pygame.time.delay(250)


# if __name__ == "__main__":
#     depth_arg = int(sys.argv[1]) if len(
#         sys.argv) > 1 and sys.argv[1].isdigit() else 2

#     mode_arg = sys.argv[2].lower() if len(sys.argv) > 2 else None

#     diff_map = {1: "Easy", 2: "Medium", 3: "Hard", 4: "Expert"}
#     mode_map = {"pvp": 0, "pve": 1, "eve": 2}  # Ánh xạ mode string → index

#     gui = ChessGUI()
#     gui.diff = diff_map.get(depth_arg, "Medium")

#     if mode_arg in mode_map:
#         gui.mode_idx = mode_map[mode_arg]

#     gui.run()

"""
CHARO — Chess GUI  (Neon style)
Usage: python gui.py [depth] [mode]

Giao diện cờ vua phong cách neon với hỗ trợ chế độ PVP/PVE/EVE,
tích hợp AI, kéo-thả quân cờ, và hiệu ứng visual cho nước đi/chiếu tướng.

Tham số:
    depth (int, tùy chọn): Độ sâu tìm kiếm của AI (1-4). Mặc định: 2
    mode (str, tùy chọn): Chế độ chơi: "pvp", "pve", hoặc "eve". Mặc định: "pve"
"""
import pygame
import sys
import os
import math

from game_state import GameState
from move import Move
from ai_engine import get_best_move

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# ── Window ────────────────────────────────────────────────
SQ = 80
BOARD_PX = SQ * 8
PNL_W = 230
W = BOARD_PX + PNL_W
H = BOARD_PX
FPS = 60

# ── Neon palette ──────────────────────────────────────────
BG_OUT = (2,   0,   8)
SQ_DARK = (15,  8,  30)
SQ_LIGHT = (22,  14, 42)
CYAN = (0,  220, 200)
PINK = (210,  0, 175)
GOLD = (255, 210,  50)
WHITE = (255, 255, 255)
GRAY = (130, 130, 150)
DIM = (55,  55,  70)
PNL_BG = (6,   3,  16)

HL_SEL = (0,  220, 200,  55)
HL_MOVE = (0,  220, 200,  80)
HL_CAP = (210,  0, 175,  90)
HL_LAST = (255, 210,  50,  45)

GRID_COL = (40,  28,  70)

# ── Fonts ─────────────────────────────────────────────────


def mf(size, bold=True):
    """
    Tạo font chữ với cơ chế fallback.

    Thử lần lượt: Consolas → Courier New → Lucida Console → font mặc định.

    Args:
        size (int): Cỡ font theo pixel
        bold (bool): Có dùng đậm hay không

    Returns:
        pygame.font.Font: Đối tượng font đã load
    """
    for n in ["Consolas", "Courier New", "Lucida Console"]:
        try:
            f = pygame.font.SysFont(n, size, bold=bold)
            if f:
                return f
        except:
            pass
    return pygame.font.Font(None, size)

# ── Helpers ───────────────────────────────────────────────


def sq_to_xy(sq):
    """
    Chuyển đổi chỉ số ô cờ (0-63) sang tọa độ pixel trên màn hình.

    Args:
        sq (int): Chỉ số ô (0=a1, 63=h8)

    Returns:
        tuple: (x, y) tọa độ pixel
    """
    f, r = sq % 8, sq // 8
    return f * SQ, (7 - r) * SQ


def xy_to_sq(x, y):
    """
    Chuyển đổi tọa độ pixel sang chỉ số ô cờ.

    Args:
        x (int): Tọa độ X pixel
        y (int): Tọa độ Y pixel

    Returns:
        int or None: Chỉ số ô (0-63), hoặc None nếu ngoài bàn cờ
    """
    f, r = x // SQ, 7 - y // SQ
    if 0 <= f < 8 and 0 <= r < 8:
        return r * 8 + f
    return None


def draw_txt(surf, text, font, cx, cy, color):
    """
    Vẽ văn bản căn giữa tại vị trí cho trước.

    Args:
        surf (pygame.Surface): Bề mặt đích để vẽ
        text (str): Nội dung văn bản
        font (pygame.font.Font): Font chữ sử dụng
        cx (int): Tọa độ X tâm
        cy (int): Tọa độ Y tâm
        color (tuple): Màu RGB của text
    """
    s = font.render(text, True, color)
    surf.blit(s, (cx - s.get_width()//2, cy - s.get_height()//2))


def draw_txt_l(surf, text, font, x, y, color):
    """
    Vẽ văn bản căn trái tại vị trí cho trước.

    Args:
        surf (pygame.Surface): Bề mặt đích để vẽ
        text (str): Nội dung văn bản
        font (pygame.font.Font): Font chữ sử dụng
        x (int): Tọa độ X góc trái
        y (int): Tọa độ Y góc trên
        color (tuple): Màu RGB của text
    """
    surf.blit(font.render(text, True, color), (x, y))


def neon_line(surf, p1, p2, color, w=1):
    """
    Vẽ đường thẳng với hiệu ứng neon (viền mờ + lõi sáng).

    Args:
        surf (pygame.Surface): Bề mặt đích
        p1 (tuple): Điểm bắt đầu (x, y)
        p2 (tuple): Điểm kết thúc (x, y)
        color (tuple): Màu RGB của đường
        w (int): Độ dày đường chính (mặc định: 1)
    """
    tmp = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.line(tmp, (*color, 40), p1, p2, w + 4)
    surf.blit(tmp, (0, 0))
    pygame.draw.line(surf, color, p1, p2, w)


def t_anim():
    """
    Lấy thời gian hiện tại tính bằng giây (dùng cho animation).

    Returns:
        float: Thời gian tính bằng giây kể từ khi pygame khởi động
    """
    return pygame.time.get_ticks() / 1000.0


# ── Stars (static) ────────────────────────────────────────
STARS = [(int((i*337+j*179) % W), int((i*179+j*337) % H), (i*7+j*13) % 60)
         for i in range(5) for j in range(7)]

# ══════════════════════════════════════════════════════════


class ChessGUI:
    """
    Lớp quản lý giao diện chính của trò chơi cờ vua CHARO.

    Xử lý: vẽ bàn cờ, nhận input người dùng, điều khiển AI,
    quản lý trạng thái game và hiển thị panel thông tin.
    """

    MODES = ["PVP", "PVE", "EVE"]
    AI_DEPTH = {"Easy": 1, "Medium": 2, "Hard": 3, "Expert": 4}

    def __init__(self):
        """
        Khởi tạo ChessGUI: setup pygame, load assets, khởi tạo trạng thái game.
        """
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("CHARO  |  Chess")

        self.mode_idx = 1
        self.diff = "Medium"
        self._reset_state()

        self.pieces = self._load_pieces()
        self.sounds = self._load_sounds()
        self.f_sm = mf(15, bold=False)
        self.f_md = mf(18, bold=True)
        self.f_big = mf(32, bold=True)
        self.f_coord = mf(12, bold=False)
        self.f_title = mf(22, bold=True)

    @property
    def mode(self):
        """
        Trả về tên chế độ chơi hiện tại dưới dạng string.

        Returns:
            str: "PVP", "PVE", hoặc "EVE"
        """
        return self.MODES[self.mode_idx]

    def _reset_state(self):
        """
        Đặt lại toàn bộ trạng thái game về mặc định (ván mới).
        """
        self.gs = GameState()
        self.legal = self.gs.get_legal_moves()
        self.sel = None
        self.sel_mv = []
        self.last_move = None
        self.over = False
        self.status = "Ongoing"
        self.dragging = False
        self.drag_sq = None
        self.drag_img = None
        self.drag_pos = (0, 0)
        self._ai_thinking = False
        self.hint_move = None
        self._hint_result = [None]

    # ── Asset loading ──────────────────────────────────────
    def _load_pieces(self):
        """
        Load hình ảnh các quân cờ từ thư mục assets.

        Returns:
            dict: Ánh xạ tên quân (vd: "wP") → pygame.Surface đã resize
        """
        pieces = {}
        d = os.path.join(BASE_DIR, "assets", "pieces_2d")
        names = ["wP", "wN", "wB", "wR", "wQ", "wK",
                 "bP", "bN", "bB", "bR", "bQ", "bK"]
        for n in names:
            p = os.path.join(d, n + ".png")
            if os.path.exists(p):
                img = pygame.image.load(p).convert_alpha()
                pieces[n] = pygame.transform.smoothscale(img, (SQ, SQ))
        return pieces

    def _load_sounds(self):
        """
        Load file âm thanh hiệu ứng từ thư mục assets.

        Returns:
            dict: Ánh xạ tên sound → pygame.mixer.Sound object
        """
        sounds = {}
        d = os.path.join(BASE_DIR, "assets", "sounds")
        for name in ["select", "move", "capture", "check", "game_over"]:
            p = os.path.join(d, name + ".wav")
            if os.path.exists(p):
                try:
                    sounds[name] = pygame.mixer.Sound(p)
                except:
                    pass
        return sounds

    def _play(self, name):
        """
        Phát âm thanh hiệu ứng nếu file tồn tại.

        Args:
            name (str): Tên sound cần phát (vd: "select", "capture")
        """
        if name in self.sounds:
            self.sounds[name].play()

    def _piece_at(self, sq):
        """
        Kiểm tra xem ô cờ có quân nào không.

        Args:
            sq (int): Chỉ số ô cờ (0-63)

        Returns:
            str or None: Tên quân (vd: "wK", "bP") hoặc None nếu ô trống
        """
        for n, bb in self.gs.board.bitboards.items():
            if bb & (1 << sq):
                return n
        return None

    # ── Drawing ────────────────────────────────────────────
    def _draw_bg(self):
        """Vẽ nền tối với hiệu ứng sao nhấp nháy."""
        self.screen.fill(BG_OUT)
        t = t_anim()
        for sx, sy, ph in STARS:
            a = int(50 + 28 * math.sin(t * 0.7 + ph))
            s = pygame.Surface((2, 2), pygame.SRCALPHA)
            s.fill((*WHITE, a))
            self.screen.blit(s, (sx, sy))

    def _draw_board(self):
        """Vẽ bàn cờ 8x8 với ô sáng/tối, viền neon và tọa độ a-h, 1-8."""
        t = t_anim()
        for sq in range(64):
            f, r = sq % 8, sq // 8
            x, y = sq_to_xy(sq)
            base = SQ_LIGHT if (f + r) % 2 == 0 else SQ_DARK
            pygame.draw.rect(self.screen, base, (x, y, SQ, SQ))
            # subtle grid line
            pygame.draw.rect(self.screen, GRID_COL, (x, y, SQ, SQ), 1)

        # Board outer border (animated glow)
        pulse = int(120 + 40 * math.sin(t * 1.2))
        tmp = pygame.Surface((BOARD_PX + 8, BOARD_PX + 8), pygame.SRCALPHA)
        pygame.draw.rect(tmp, (*PINK, pulse // 3),
                         (0, 0, BOARD_PX+8, BOARD_PX+8), 3, border_radius=4)
        self.screen.blit(tmp, (-4, -4))
        pygame.draw.rect(self.screen, PINK, (0, 0, BOARD_PX, BOARD_PX), 2)

        # Coordinates
        for f in range(8):
            col = CYAN if f % 2 == 0 else (*CYAN[:2], CYAN[2]//2 + 80)
            s = self.f_coord.render(chr(ord("a") + f), True, GRAY)
            self.screen.blit(s, (f*SQ + SQ - s.get_width() -
                             3, BOARD_PX - s.get_height() - 2))
        for r in range(8):
            s = self.f_coord.render(str(r + 1), True, GRAY)
            self.screen.blit(s, (2, (7 - r)*SQ + 2))

    def _draw_highlights(self):
        """
        Vẽ các hiệu ứng highlight: ô chọn, nước đi hợp lệ,
        nước đi cuối, quân Vua bị chiếu, và hint move.
        """
        surf = pygame.Surface((BOARD_PX, BOARD_PX), pygame.SRCALPHA)
        t = t_anim()

        # Last move
        if self.last_move:
            for sq in self.last_move:
                x, y = sq_to_xy(sq)
                pygame.draw.rect(surf, HL_LAST, (x, y, SQ, SQ))

        # Selected square
        if self.sel is not None:
            x, y = sq_to_xy(self.sel)
            pygame.draw.rect(surf, HL_SEL, (x, y, SQ, SQ))
            # Animated border
            pulse = int(160 + 60 * math.sin(t * 3))
            pygame.draw.rect(surf, (*CYAN, pulse), (x, y, SQ, SQ), 2)

        # Legal moves
        for m in self.sel_mv:
            tg = Move.get_target(m)
            cap = bool(self.gs.board.all_pieces & (1 << tg))
            cx, cy = sq_to_xy(tg)
            cx += SQ // 2
            cy += SQ // 2
            if cap:
                pygame.draw.circle(surf, HL_CAP, (cx, cy), SQ//2 - 3, 5)
            else:
                pygame.draw.circle(surf, HL_MOVE, (cx, cy), SQ // 5)

        # King in check
        if self.gs.is_in_check():
            key = "wK" if self.gs.white_to_move else "bK"
            bb = self.gs.board.bitboards.get(key, 0)
            pulse = int(140 + 80 * math.sin(t * 4))
            for sq in range(64):
                if bb & (1 << sq):
                    x, y = sq_to_xy(sq)
                    for i in range(SQ//2, 0, -4):
                        a = int(pulse * (1 - i / (SQ//2)))
                        pygame.draw.circle(surf, (220, 0, 0, a),
                                           (x + SQ//2, y + SQ//2), i)

        if self.hint_move:
            for sq, color in [(self.hint_move[0], (255, 255, 0, 60)),
                              (self.hint_move[1], (0, 255, 120, 80))]:
                x, y = sq_to_xy(sq)
                pygame.draw.rect(surf, color, (x, y, SQ, SQ))
                pygame.draw.rect(surf, (*color[:3], 180), (x, y, SQ, SQ), 3)
        self.screen.blit(surf, (0, 0))

    def _draw_pieces(self):
        """Vẽ tất cả quân cờ lên bàn, xử lý riêng quân đang được kéo (drag)."""
        for sq in range(64):
            if self.dragging and sq == self.drag_sq:
                continue
            name = self._piece_at(sq)
            if name and name in self.pieces:
                x, y = sq_to_xy(sq)
                self.screen.blit(self.pieces[name], (x, y))
        if self.dragging and self.drag_img:
            mx, my = self.drag_pos
            r = self.drag_img.get_rect(center=(mx, my))
            self.screen.blit(self.drag_img, r)

    def _draw_panel(self):
        """Vẽ panel thông tin bên phải: tiêu đề, lượt đi, chế độ, điều khiển."""
        px = BOARD_PX + 14
        pw = PNL_W - 18
        pcx = BOARD_PX + PNL_W // 2
        t = t_anim()

        # Panel bg
        tmp = pygame.Surface((PNL_W, H), pygame.SRCALPHA)
        tmp.fill((*PNL_BG, 240))
        self.screen.blit(tmp, (BOARD_PX, 0))
        neon_line(self.screen, (BOARD_PX, 0), (BOARD_PX, H), PINK, w=1)

        y = 24
        # Title
        draw_txt(self.screen, "CHARO", self.f_title, pcx, y, WHITE)
        y += 28

        # Divider
        neon_line(self.screen, (px, y), (px+pw, y), PINK, w=1)
        y += 14

        # Turn indicator
        if not self.over:
            turn = "WHITE" if self.gs.white_to_move else "BLACK"
            col = CYAN if self.gs.white_to_move else PINK
            draw_txt(self.screen, f"Turn: {turn}", self.f_md, pcx, y+10, col)
        y += 32

        # Mode / diff
        draw_txt_l(self.screen, f"Mode :  {self.mode}", self.f_sm, px, y, GRAY)
        y += 22
        draw_txt_l(
            self.screen, f"AI   :  {self.diff}",  self.f_sm, px, y, GRAY)
        y += 22

        neon_line(self.screen, (px, y), (px+pw, y), PINK, w=1)
        y += 14

        # Moves / last
        draw_txt_l(
            self.screen, f"Moves: {len(self.gs.move_log)}", self.f_sm, px, y, GRAY)
        y += 22
        if self.last_move:
            sf = chr(ord("a") + self.last_move[0] %
                     8) + str(self.last_move[0]//8+1)
            tf = chr(ord("a") + self.last_move[1] %
                     8) + str(self.last_move[1]//8+1)
            draw_txt_l(
                self.screen, f"Last:  {sf}-{tf}", self.f_sm, px, y, GRAY)
        y += 22

        neon_line(self.screen, (px, y), (px+pw, y), PINK, w=1)
        y += 14

        # AI thinking
        if self._ai_thinking:
            pulse = int(180 + 60 * math.sin(t * 4))
            col = (*PINK, pulse)
            draw_txt(self.screen, "AI thinking...", self.f_sm, pcx, y+10, PINK)
            y += 30
        elif self.over:
            msgs = {
                "Checkmate-BlackWins": ("BLACK WINS!", PINK),
                "Checkmate-WhiteWins": ("WHITE WINS!", CYAN),
                "Stalemate":           ("STALEMATE",   GOLD),
                "Draw-50Move":         ("DRAW",         GRAY),
            }
            msg, col = msgs.get(self.status, ("GAME OVER", GRAY))
            draw_txt(self.screen, msg, self.f_big, pcx, y+20, col)
            y += 50

        # Controls at bottom
        y = H - 110
        neon_line(self.screen, (px, y), (px+pw, y), PINK, w=1)
        y += 12
        controls = [("R", "Restart"), ("Z", "Undo"), ("S", "Hint"),
                    ("E", "Editor"), ("ESC", "Quit")]
        for key, desc in controls:
            k = self.f_sm.render(f"[{key}]", True, GOLD)
            d = self.f_sm.render(desc, True, DIM)
            self.screen.blit(k, (px, y))
            self.screen.blit(d, (px + 48, y))
            y += 20

    def _render(self):
        """Vẽ toàn bộ khung hình: nền, bàn cờ, highlight, quân cờ, panel."""
        self._draw_bg()
        self._draw_board()
        self._draw_highlights()
        self._draw_pieces()
        self._draw_panel()
        pygame.display.flip()

    # ── Input ──────────────────────────────────────────────
    def _handle_down(self, mx, my):
        """
        Xử lý sự kiện nhấn chuột: chọn quân, bắt đầu kéo, hoặc thực hiện nước đi.

        Args:
            mx (int): Tọa độ X của chuột
            my (int): Tọa độ Y của chuột
        """
        if self.over or my >= BOARD_PX or mx >= BOARD_PX:
            return
        if self.mode == "EVE":
            return
        is_ai_turn = (self.mode == "PVE" and not self.gs.white_to_move) or (
            self.mode == "EVE")
        if is_ai_turn:
            return
        sq = xy_to_sq(mx, my)
        if sq is None:
            return
        pfx = "w" if self.gs.white_to_move else "b"
        p = self._piece_at(sq)

        if self.sel is not None:
            matching = [m for m in self.sel_mv if Move.get_target(m) == sq]
            if matching:
                self._exec(matching)
                return
            if p and p.startswith(pfx):
                self._start_sel(sq, p)
                return
            self.sel = None
            self.sel_mv = []
            return

        if p and p.startswith(pfx):
            self._start_sel(sq, p)

    def _start_sel(self, sq, piece):
        """
        Bắt đầu trạng thái chọn/kéo một quân cờ.

        Args:
            sq (int): Ô cờ được chọn
            piece (str): Tên quân cờ (vd: "wN")
        """
        self.sel = sq
        self.sel_mv = [m for m in self.legal if Move.get_start(m) == sq]
        self.dragging = True
        self.drag_sq = sq
        self.drag_img = self.pieces.get(piece)
        self.drag_pos = pygame.mouse.get_pos()
        self._play("select")

    def _handle_up(self, mx, my):
        """
        Xử lý sự kiện thả chuột: hoàn tất nước đi hoặc hủy kéo.

        Args:
            mx (int): Tọa độ X của chuột
            my (int): Tọa độ Y của chuột
        """
        if not self.dragging:
            return
        self.dragging = False
        if my >= BOARD_PX or mx >= BOARD_PX:
            self.drag_sq = None
            return
        sq = xy_to_sq(mx, my)
        if sq is not None and sq != self.drag_sq:
            matching = [m for m in self.sel_mv if Move.get_target(m) == sq]
            if matching:
                self._exec(matching)
        self.drag_sq = None

    def _exec(self, matching):
        """
        Thực thi nước đi được chọn: cập nhật trạng thái game, phát sound, reset selection.

        Args:
            matching (list): Danh sách nước đi hợp lệ tới ô đích (chọn nước promotion nếu có)
        """
        move = matching[0]
        for m in matching:
            if Move.get_flag(m) in (Move.PROMOTION_QUEEN, Move.PROMOTION_CAPTURE_QUEEN):
                move = m
                break
        flag = Move.get_flag(move)
        is_cap = flag in (Move.CAPTURE, Move.EN_PASSANT,
                          Move.PROMOTION_CAPTURE_QUEEN, Move.PROMOTION_CAPTURE_ROOK,
                          Move.PROMOTION_CAPTURE_BISHOP, Move.PROMOTION_CAPTURE_KNIGHT)
        self.hint_move = None
        self.last_move = (Move.get_start(move), Move.get_target(move))
        self.gs.make_move(move)
        self.legal = self.gs.get_legal_moves()
        self.sel = None
        self.sel_mv = []
        self.status = self.gs.get_game_status()
        if self.status != "Ongoing":
            self._play("game_over")
            self.over = True
        elif self.gs.is_in_check():
            self._play("check")
        elif is_cap:
            self._play("capture")
        else:
            self._play("move")

    def _do_ai(self):
        """Gọi AI để tính nước đi tốt nhất và thực thi nước đó."""
        self._ai_thinking = True
        self._render()
        depth = self.AI_DEPTH.get(self.diff, 2)
        best = get_best_move(self.gs, depth=depth)
        if best:
            flag = Move.get_flag(best)
            is_cap = flag in (Move.CAPTURE, Move.EN_PASSANT,
                              Move.PROMOTION_CAPTURE_QUEEN, Move.PROMOTION_CAPTURE_ROOK,
                              Move.PROMOTION_CAPTURE_BISHOP, Move.PROMOTION_CAPTURE_KNIGHT)
            self.last_move = (Move.get_start(best), Move.get_target(best))
            self.gs.make_move(best)
            self.legal = self.gs.get_legal_moves()
            self.status = self.gs.get_game_status()
            if self.status != "Ongoing":
                self._play("game_over")
                self.over = True
            elif self.gs.is_in_check():
                self._play("check")
            elif is_cap:
                self._play("capture")
            else:
                self._play("move")
        self._ai_thinking = False

    def _hint_thread(self):
        """Khởi chạy thread riêng để tính hint move, tránh làm đơ giao diện."""
        import threading
        import copy
        gs_copy = copy.deepcopy(self.gs)
        depth = self.AI_DEPTH.get(self.diff, 2)

        def _run():
            move = get_best_move(gs_copy, depth=depth)
            self._hint_result[0] = move if move else False

        threading.Thread(target=_run, daemon=True).start()

    def restart(self):
        """Đặt lại game về trạng thái ban đầu (ván mới)."""
        self._reset_state()

    # ── Main loop ──────────────────────────────────────────
    def run(self):
        """
        Vòng lặp chính của game: xử lý event, cập nhật logic, vẽ màn hình.
        Chạy đến khi người dùng thoát.
        """
        clock = pygame.time.Clock()
        DIFFS = list(self.AI_DEPTH.keys())

        while True:
            is_ai = (self.mode == "PVE" and not self.gs.white_to_move) or (
                self.mode == "EVE")

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    self._handle_down(*ev.pos)
                if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                    self._handle_up(*ev.pos)
                if ev.type == pygame.MOUSEMOTION and self.dragging:
                    self.drag_pos = ev.pos
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if ev.key == pygame.K_r:
                        self.restart()
                    if ev.key == pygame.K_s:
                        if not self.over and not self._ai_thinking and self._hint_result[0] is None:
                            if self.mode == "PVP" or (self.mode == "PVE" and self.gs.white_to_move):
                                self._hint_result[0] = None
                                self._hint_thread()
                    if ev.key == pygame.K_e and not self._ai_thinking:
                        from board_editor import BoardEditor
                        editor = BoardEditor(self.screen, self.pieces)
                        res = editor.run()
                        if res:
                            self.gs.board.bitboards = res["bitboards"].copy()
                            self.gs.white_to_move = res["white_to_move"]

                            w_pieces = sum(self.gs.board.bitboards[p] for p in [
                                           "wK", "wQ", "wR", "wB", "wN", "wP"])
                            b_pieces = sum(self.gs.board.bitboards[p] for p in [
                                           "bK", "bQ", "bR", "bB", "bN", "bP"])
                            self.gs.board.white_pieces = w_pieces
                            self.gs.board.black_pieces = b_pieces
                            self.gs.board.all_pieces = w_pieces | b_pieces

                            self.gs.move_log = []
                            self.legal = self.gs.get_legal_moves()
                            self.sel = None
                            self.sel_mv = []
                            self.status = self.gs.get_game_status()
                            self.over = (self.status != "Ongoing")
                            self.last_move = None

                            if "depth" in res:
                                diff_map_rev = {
                                    1: "Easy", 2: "Medium", 3: "Hard", 4: "Expert"}
                                self.diff = diff_map_rev.get(
                                    res["depth"], self.diff)
                    if ev.key == pygame.K_d:
                        idx = DIFFS.index(self.diff)
                        self.diff = DIFFS[(idx + 1) % len(DIFFS)]
                    if ev.key == pygame.K_z and not self.over and not is_ai:
                        self.gs.unmake_move()
                        if self.mode == "PVE":
                            self.gs.unmake_move()
                        self.legal = self.gs.get_legal_moves()
                        self.sel = None
                        self.sel_mv = []
                        self.over = False
                        self.status = "Ongoing"
                        self.last_move = None
            if self._hint_result[0] is not None and self._hint_result[0] is not False:
                move = self._hint_result[0]
                self._hint_result[0] = None
                self.hint_move = (Move.get_start(move), Move.get_target(move))
            self._render()
            clock.tick(FPS)

            if is_ai and not self._ai_thinking:
                pygame.time.delay(120)
                self._do_ai()
                if self.mode == "EVE":
                    pygame.time.delay(250)


if __name__ == "__main__":
    depth_arg = int(sys.argv[1]) if len(
        sys.argv) > 1 and sys.argv[1].isdigit() else 2

    mode_arg = sys.argv[2].lower() if len(sys.argv) > 2 else None

    diff_map = {1: "Easy", 2: "Medium", 3: "Hard", 4: "Expert"}
    mode_map = {"pvp": 0, "pve": 1, "eve": 2}

    gui = ChessGUI()
    gui.diff = diff_map.get(depth_arg, "Medium")

    if mode_arg in mode_map:
        gui.mode_idx = mode_map[mode_arg]

    gui.run()
