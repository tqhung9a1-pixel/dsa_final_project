"""
CHARO — Board Editor
Flow: đặt quân → chọn độ khó → trả về result cho gui.py

Trả về dict:
  {"bitboards": {...}, "white_to_move": bool, "depth": int}
hoặc None nếu cancel.

Gọi từ gui.py:
  from board_editor import BoardEditor
  result = BoardEditor(screen, pieces).run()
"""
import pygame
import math

SQ = 70
BOARD_PX = SQ * 8
PNL_W = 300
W = BOARD_PX + PNL_W
H = BOARD_PX + 40

BG = (2,   0,   8)
SQ_DARK = (15,  8,  30)
SQ_LIGHT = (22, 14,  42)
GRID_C = (40,  28,  70)
CYAN = (0,  220, 200)
PINK = (210,  0, 175)
WHITE = (255, 255, 255)
GRAY = (130, 130, 150)
DIM = (55,  55,  70)
RED = (220,  60,  60)
GREEN_C = (60,  200, 100)
PNL_BG = (6,   3,  16)

ALL_PIECES = ["wK", "wQ", "wR", "wB", "wN", "wP",
              "bK", "bQ", "bR", "bB", "bN", "bP"]


def _mf(sz, bold=True):
    for n in ["Consolas", "Courier New", "Lucida Console"]:
        try:
            f = pygame.font.SysFont(n, sz, bold=bold)
            if f:
                return f
        except:
            pass
    return pygame.font.Font(None, sz)


def sq_xy(sq): return (sq % 8)*SQ, (7-sq//8)*SQ


def xy_sq(x, y):
    f, r = x//SQ, 7-y//SQ
    return r*8+f if (0 <= f < 8 and 0 <= r < 8) else None


# ── Placement rules ───────────────────────────────────────
MAX_PIECES = 16


def _in_zone(sq, piece_name):
    """Trắng chỉ đặt rank 1-2 (sq//8 ≤ 1), Đen rank 7-8 (sq//8 ≥ 6)."""
    rank = sq // 8
    return rank <= 1 if piece_name.startswith("w") else rank >= 6


def ctxt(surf, text, font, cx, cy, col):
    s = font.render(text, True, col)
    surf.blit(s, (cx-s.get_width()//2, cy-s.get_height()//2))


def ltxt(surf, text, font, x, y, col):
    surf.blit(font.render(text, True, col), (x, y))


def neon_box(surf, rect, col, bw=2, r=4):
    t = pygame.Surface((rect.w+8, rect.h+8), pygame.SRCALPHA)
    pygame.draw.rect(t, (*col, 28), (0, 0, rect.w+8, rect.h+8),
                     bw+3, border_radius=r+3)
    surf.blit(t, (rect.x-4, rect.y-4))
    pygame.draw.rect(surf, col, rect, bw, border_radius=r)


def neon_ln(surf, p1, p2, col, size=(W, H)):
    t = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.line(t, (*col, 30), p1, p2, 5)
    surf.blit(t, (0, 0))
    pygame.draw.line(surf, col, p1, p2, 1)


def fill_box(surf, rect, col, a=25):
    t = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    t.fill((*col, a))
    surf.blit(t, rect.topleft)


STARS = [(int((i*337+j*179) % W), int((i*179+j*337) % H), (i*7+j*13) % 60)
         for i in range(5) for j in range(7)]


def draw_stars(surf, t):
    for sx, sy, ph in STARS:
        a = int(50+28*math.sin(t*0.7+ph))
        s = pygame.Surface((2, 2), pygame.SRCALPHA)
        s.fill((*WHITE, a))
        surf.blit(s, (sx, sy))


# ══════════════════════════════════════════════════════════
class BoardEditor:

    def __init__(self, screen, pieces):
        self.screen = screen
        # self.pieces = pieces_dict
        self.pieces = {k: pygame.transform.smoothscale(
            v, (SQ, SQ)) for k, v in pieces.items()}
        self.F_T = _mf(20)
        self.F_M = _mf(17)
        self.F_S = _mf(14, bold=False)
        self.F_XS = _mf(12, bold=False)

    # ── Internal state ────────────────────────────────────
    def _init(self, from_start=True):
        self.bbs = {n: 0 for n in ALL_PIECES}
        if from_start:
            from bitboard import Board
            for k, v in Board().bitboards.items():
                self.bbs[k] = v
        self.sel_piece = "wQ"
        self.white_first = True
        self.err = ""

    def _piece_at(self, sq):
        for n, bb in self.bbs.items():
            if bb & (1 << sq):
                return n
        return None

    def _count(self, color):
        """Tổng số quân của 'w' hoặc 'b'."""
        total = 0
        for name, bb in self.bbs.items():
            if name.startswith(color):
                total += bin(bb).count("1")
        return total

    def _validate(self):
        wk = bin(self.bbs["wK"]).count("1")
        bk = bin(self.bbs["bK"]).count("1")
        if wk == 0:
            return "White has no king!"
        if bk == 0:
            return "Black has no king!"
        return ""

    # ── Board click ─────────────────────────────
    def _click(self, sq, right=False):
        existing = self._piece_at(sq)
        if right:
            if existing:
                self.bbs[existing] &= ~(1 << sq)
            self.err = ""
            return

        is_white = self.sel_piece.startswith("w")
        piece_type = self.sel_piece[1]
        side_prefix = "w" if is_white else "b"
        side_list = ["wK", "wQ", "wR", "wB", "wN", "wP"] if is_white else [
            "bK", "bQ", "bR", "bB", "bN", "bP"]

        # Tính toán hàng (row) hiện tại. sq chạy từ 0 -> 63
        r = sq // 8

        # Nếu click vào đúng quân đang chọn -> Xóa quân đó (Toggle)
        if existing == self.sel_piece:
            self.bbs[existing] &= ~(1 << sq)
            self.err = ""
            return

        # =========================================================
        # 1. RÀNG BUỘC ZONE (VÙNG ĐẶT QUÂN)
        # Lưu ý: Nếu hệ tọa độ của bạn bị ngược (Trắng ở dưới, Đen ở trên)
        # thì bạn hãy đảo ngược điều kiện (is_white check r < 6, else check r > 1) nhé!
        # =========================================================
        if is_white:
            # White zone: 2 dòng đầu (hàng 0 và hàng 1)
            if r > 1:
                self.err = "Quân Xanh (White) chỉ được\nđặt ở 2 dòng đầu tiên!"
                return
        else:
            # Black zone: 2 dòng cuối (hàng 6 và hàng 7)
            if r < 6:
                self.err = "Quân Hồng (Black) chỉ được\nđặt ở 2 dòng cuối cùng!"
                return

        # =========================================================
        # 2. RÀNG BUỘC SỐ LƯỢNG (Tối đa 16 quân, 1 Vua)
        # =========================================================
        total_side_count = sum(bin(self.bbs[p]).count("1") for p in side_list)

        if piece_type == "K":
            # Xóa Vua cũ nếu đặt Vua mới
            self.bbs[self.sel_piece] = 0
        else:
            # Kiểm tra giới hạn 16 quân
            is_replacing_same_side = existing and existing.startswith(
                side_prefix)
            if not is_replacing_same_side:
                if total_side_count >= 16:
                    side_name = "Xanh (Cyan)" if is_white else "Hồng (Pink)"
                    self.err = f"Phe {side_name} đã đạt giới hạn 16 quân!"
                    return

        # 3. Thực hiện đặt quân
        if existing:
            self.bbs[existing] &= ~(1 << sq)

        self.bbs[self.sel_piece] |= 1 << sq
        self.err = ""  # Xóa lỗi nếu đặt thành công

    # ══════════════════════════════════════════════════════
    # SCREEN 1 — EDIT BOARD
    # ══════════════════════════════════════════════════════
    def _draw_edit(self, t, mx, my):
        self.screen.fill(BG)
        draw_stars(self.screen, t)

        # Board squares
        for sq in range(64):
            f, r = sq % 8, sq//8
            x, y = sq_xy(sq)
            pygame.draw.rect(self.screen,
                             SQ_LIGHT if (f+r) % 2 == 0 else SQ_DARK, (x, y, SQ, SQ))
            pygame.draw.rect(self.screen, GRID_C, (x, y, SQ, SQ), 1)

        # Zone highlights: cyan tint rank 1-2, pink tint rank 7-8
        zone_surf = pygame.Surface((BOARD_PX, BOARD_PX), pygame.SRCALPHA)
        for sq in range(64):
            rank = sq // 8
            x, y = sq_xy(sq)
            if rank <= 1:     # white zone
                pygame.draw.rect(zone_surf, (*CYAN, 18), (x, y, SQ, SQ))
            elif rank >= 6:   # black zone
                pygame.draw.rect(zone_surf, (*PINK, 18), (x, y, SQ, SQ))
            else:             # forbidden — dim overlay
                pygame.draw.rect(zone_surf, (0, 0, 0, 55), (x, y, SQ, SQ))
        self.screen.blit(zone_surf, (0, 0))

        # Zone border labels
        for rank, col, label in [(0, "", ""), (1, CYAN, "WHITE ZONE"),
                                 (6, PINK, "BLACK ZONE"), (7, "", "")]:
            if label:
                s = self.F_XS.render(label, True, col)
                y_lbl = (7 - rank) * SQ + 2
                self.screen.blit(s, (BOARD_PX - s.get_width() - 4, y_lbl))

        # Hover + ghost preview (only in valid zone for current piece)
        if mx < BOARD_PX:
            sq = xy_sq(mx, my)
            if sq is not None:
                x, y = sq_xy(sq)
                in_valid = _in_zone(sq, self.sel_piece)
                hover_col = CYAN if in_valid else (100, 40, 40)
                ov = pygame.Surface((SQ, SQ), pygame.SRCALPHA)
                ov.fill((*hover_col, 30 if in_valid else 20))
                self.screen.blit(ov, (x, y))
                pygame.draw.rect(
                    self.screen, (*hover_col, 100), (x, y, SQ, SQ), 1)
                if in_valid and self.sel_piece in self.pieces:
                    g = self.pieces[self.sel_piece].copy()
                    g.set_alpha(95)
                    self.screen.blit(g, (x, y))

        # Pieces on board
        for name, bb in self.bbs.items():
            tmp = bb
            while tmp:
                sq = (tmp & -tmp).bit_length()-1
                tmp &= tmp-1
                if name in self.pieces:
                    self.screen.blit(self.pieces[name], sq_xy(sq))

        # Board border
        pygame.draw.rect(self.screen, CYAN, (0, 0, BOARD_PX, BOARD_PX), 2)
        for f in range(8):
            s = self.F_XS.render(chr(ord('a')+f), True, GRAY)
            self.screen.blit(s, (f*SQ+SQ-s.get_width()-3,
                             BOARD_PX-s.get_height()-2))
        for r in range(8):
            s = self.F_XS.render(str(r+1), True, GRAY)
            self.screen.blit(s, (2, (7-r)*SQ+2))

        # ── Panel ─────────────────────────────────────────
        PX = BOARD_PX+12
        PW = PNL_W-18
        PCX = BOARD_PX+PNL_W//2
        bg = pygame.Surface((PNL_W, H), pygame.SRCALPHA)
        bg.fill((*PNL_BG, 240))
        self.screen.blit(bg, (BOARD_PX, 0))
        neon_ln(self.screen, (BOARD_PX, 0), (BOARD_PX, H), CYAN)

        y = 16
        ctxt(self.screen, "BOARD EDITOR", self.F_T, PCX, y, WHITE)
        y += 28
        neon_ln(self.screen, (PX, y), (PX+PW, y), CYAN)
        y += 10

        # Piece selector: 6 per row, 2 rows
        ltxt(self.screen, "Select piece:", self.F_S, PX, y, GRAY)
        y += 18
        CW = PW//6
        CH = 44
        self._pcells = {}
        for idx, name in enumerate(ALL_PIECES):
            ci, ri = idx % 6, idx//6
            rect = pygame.Rect(PX+ci*CW, y+ri*(CH+3), CW-2, CH)
            self._pcells[name] = rect
            pc = CYAN if name.startswith("w") else PINK
            sel = name == self.sel_piece
            fill_box(self.screen, rect, pc, 55 if sel else 15)
            pygame.draw.rect(self.screen, pc, rect,
                             2 if sel else 1, border_radius=3)
            if name in self.pieces:
                img = pygame.transform.smoothscale(self.pieces[name], (34, 34))
                self.screen.blit(
                    img, (rect.x+rect.w//2-17, rect.y+rect.h//2-17))
        y += 2*(CH+3)+10

        neon_ln(self.screen, (PX, y), (PX+PW, y), PINK)
        y += 10

        # Turn selector
        ltxt(self.screen, "First move:", self.F_S, PX, y, GRAY)
        y += 18
        hw = PW//2-4
        self._turn_w = pygame.Rect(PX, y, hw, 30)
        self._turn_b = pygame.Rect(PX+hw+8, y, hw, 30)
        for r, col, active in [(self._turn_w, CYAN, self.white_first),
                               (self._turn_b, PINK, not self.white_first)]:
            fill_box(self.screen, r, col, 55 if active else 15)
            pygame.draw.rect(self.screen, col, r, 2, border_radius=4)
        ctxt(self.screen, "White", self.F_S,
             self._turn_w.centerx, self._turn_w.centery, CYAN)
        ctxt(self.screen, "Black", self.F_S,
             self._turn_b.centerx, self._turn_b.centery, PINK)
        y += 40

        neon_ln(self.screen, (PX, y), (PX+PW, y), PINK)
        y += 10

        # King + piece count status
        wk = bin(self.bbs["wK"]).count("1")
        bk = bin(self.bbs["bK"]).count("1")
        wc = self._count("w")
        bc = self._count("b")
        for label, cnt, total, ok in [
            ("White King:", wk, 1, wk == 1),
            ("White pieces:", wc, 16, True),
            ("Black King:", bk, 1, bk == 1),
            ("Black pieces:", bc, 16, True),
        ]:
            if "piece" in label:
                col = RED if cnt > MAX_PIECES else (
                    GREEN_C if cnt > 0 else GRAY)
            else:
                col = GREEN_C if ok else RED
            ltxt(self.screen, f"{label}  {cnt} / {total}",
                 self.F_S, PX, y, col)
            y += 20
        if self.err:
            lines = self.err.split('\n')

            for line in lines:
                ltxt(self.screen, line, self.F_S, PX, y, RED)
                y += 20
        y += 4

        # Buttons
        y = H-118
        neon_ln(self.screen, (PX, y), (PX+PW, y), PINK)
        y += 10
        hw2 = PW//2-4
        self._btn_clear = pygame.Rect(PX, y, hw2, 32)
        self._btn_reset = pygame.Rect(PX+hw2+8, y, hw2, 32)
        for r, lbl in [(self._btn_clear, "Clear"), (self._btn_reset, "Reset")]:
            fill_box(self.screen, r, GRAY, 20)
            pygame.draw.rect(self.screen, GRAY, r, 1, border_radius=4)
            ctxt(self.screen, lbl, self.F_S, r.centerx, r.centery, GRAY)
        y += 42

        ready = self._validate() == ""
        ok_col = GREEN_C if ready else DIM
        self._btn_ok = pygame.Rect(PX, y, PW, 36)
        fill_box(self.screen, self._btn_ok, ok_col, 40 if ready else 10)
        pygame.draw.rect(self.screen, ok_col, self._btn_ok, 2, border_radius=5)
        ctxt(self.screen, "NEXT  →  Choose Difficulty",
             self.F_S, self._btn_ok.centerx, self._btn_ok.centery, ok_col)
        y += 44

        self._btn_cancel = pygame.Rect(PX, y, PW, 26)
        fill_box(self.screen, self._btn_cancel, GRAY, 10)
        pygame.draw.rect(self.screen, GRAY, self._btn_cancel,
                         1, border_radius=4)
        ctxt(self.screen, "Cancel", self.F_XS,
             self._btn_cancel.centerx, self._btn_cancel.centery, DIM)

    def _run_edit(self):
        clock = pygame.time.Clock()
        while True:
            t = pygame.time.get_ticks()/1000
            mx, my = pygame.mouse.get_pos()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return "quit"
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    return None

                if ev.type == pygame.MOUSEBUTTONDOWN:
                    pos = ev.pos

                    # Board
                    if pos[0] < BOARD_PX:
                        sq = xy_sq(*pos)
                        if sq is not None:
                            self._click(sq, right=(ev.button == 3))
                        continue

                    if ev.button != 1:
                        continue

                    # Piece selector
                    for name, r in self._pcells.items():
                        if r.collidepoint(pos):
                            self.sel_piece = name
                            break

                    # Turn
                    if hasattr(self, "_turn_w") and self._turn_w.collidepoint(pos):
                        self.white_first = True
                    if hasattr(self, "_turn_b") and self._turn_b.collidepoint(pos):
                        self.white_first = False

                    # Clear / Reset
                    if hasattr(self, "_btn_clear") and self._btn_clear.collidepoint(pos):
                        self._init(from_start=False)
                    if hasattr(self, "_btn_reset") and self._btn_reset.collidepoint(pos):
                        self._init(from_start=True)

                    # Cancel
                    if hasattr(self, "_btn_cancel") and self._btn_cancel.collidepoint(pos):
                        return None

                    # Next
                    if hasattr(self, "_btn_ok") and self._btn_ok.collidepoint(pos):
                        err = self._validate()
                        if err:
                            self.err = err
                        else:
                            self.err = ""
                            return "diff"

            self._draw_edit(t, mx, my)
            pygame.display.flip()
            clock.tick(60)

    # ══════════════════════════════════════════════════════
    # SCREEN 2 — CHOOSE DIFFICULTY
    # ══════════════════════════════════════════════════════
    def _run_diff(self):
        clock = pygame.time.Clock()
        DIFFS = [("Easy",   "Beginner", 1),
                 ("Medium", "Balanced", 2),
                 ("Hard",   "Expert",   3)]
        bw, bh, gap = 230, 90, 50
        total = 3*bw+2*gap
        sx = (W-total)//2
        cy = H//2+50
        btns = [(pygame.Rect(sx+i*(bw+gap), cy-bh//2, bw, bh), lbl, sub, d)
                for i, (lbl, sub, d) in enumerate(DIFFS)]
        back = pygame.Rect(28, 28, 110, 38)

        while True:
            t = pygame.time.get_ticks()/1000
            mx, my = pygame.mouse.get_pos()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    return "quit", None
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    return "back", None
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if back.collidepoint(ev.pos):
                        return "back", None
                    for rect, lbl, sub, d in btns:
                        if rect.collidepoint(ev.pos):
                            return "ok", d

            # Draw
            self.screen.fill(BG)
            draw_stars(self.screen, t)
            pulse = int(150+50*math.sin(t*1.5))
            tmp = pygame.Surface((W, H), pygame.SRCALPHA)
            pygame.draw.line(tmp, (*PINK, pulse//3), (W//2, 0), (W//2, H), 8)
            pygame.draw.line(tmp, (*PINK, pulse),   (W//2, 0), (W//2, H), 1)
            self.screen.blit(tmp, (0, 0))

            ctxt(self.screen, "CHOOSE DIFFICULTY", self.F_T, W//2, 70, PINK)
            ctxt(self.screen, "Custom Position",   self.F_S, W//2, 98, GRAY)

            for rect, lbl, sub, d in btns:
                hov = rect.collidepoint(mx, my)
                fill_box(self.screen, rect, PINK, 55 if hov else 20)
                neon_box(self.screen, rect, PINK, bw=2 if hov else 1, r=6)
                ctxt(self.screen, lbl, self.F_M,
                     rect.centerx, rect.centery-12, PINK)
                ctxt(self.screen, sub, self.F_S,
                     rect.centerx, rect.centery+14, GRAY)

            hov_b = back.collidepoint(mx, my)
            fill_box(self.screen, back, GRAY, 35 if hov_b else 12)
            pygame.draw.rect(self.screen, GRAY, back, 1, border_radius=4)
            ctxt(self.screen, "< Back", self.F_S,
                 back.centerx, back.centery, GRAY)

            pygame.display.flip()
            clock.tick(60)

    # ══════════════════════════════════════════════════════
    # MAIN ENTRY
    # ══════════════════════════════════════════════════════
    def run(self):
        self._init(from_start=True)

        while True:
            action = self._run_edit()
            if action is None or action == "quit":
                return None

            # action == "diff"
            while True:
                outcome, depth = self._run_diff()
                if outcome == "quit":
                    return None
                if outcome == "back":
                    break          # back to edit screen
                if outcome == "ok":
                    return {
                        "bitboards":     {k: v for k, v in self.bbs.items()},
                        "white_to_move": self.white_first,
                        "depth":         depth,
                    }
