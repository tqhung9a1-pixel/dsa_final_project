# """CHARO — Main Menu  (subprocess launcher)"""
# import pygame
# import sys
# import math
# import os
# import subprocess

# pygame.init()
# W, H = 1280, 720
# screen = pygame.display.set_mode((W, H))
# pygame.display.set_caption("CHARO")
# clock = pygame.time.Clock()
# BASE = os.path.dirname(os.path.abspath(__file__))

# # ── Colours ──────────────────────────────────────────────
# BG = (2,   0,   8)
# CYAN = (0,  220, 200)
# PINK = (210,  0, 175)
# WHITE = (255, 255, 255)
# GRAY = (130, 130, 150)
# DIM = (55,  55,  70)

# # ── Fonts ─────────────────────────────────────────────────


# def mf(sz, bold=True):
#     for n in ["Consolas", "Courier New", "Lucida Console"]:
#         try:
#             f = pygame.font.SysFont(n, sz, bold=bold)
#             if f:
#                 return f
#         except:
#             pass
#     return pygame.font.Font(None, sz)


# F_LOGO = mf(88)
# F_TITLE = mf(28)
# F_BTN = mf(20)
# F_SUB = mf(15, bold=False)
# F_HINT = mf(13, bold=False)

# # ── Draw helpers ──────────────────────────────────────────


# def ctxt(surf, text, font, cx, cy, col, glow=False):
#     if glow:
#         h = font.render(text, True, col)
#         h.set_alpha(45)
#         for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
#             surf.blit(h, (cx-h.get_width()//2+dx, cy-h.get_height()//2+dy))
#     s = font.render(text, True, col)
#     surf.blit(s, (cx-s.get_width()//2, cy-s.get_height()//2))


# STARS = [(int((i*337+j*179) % W), int((i*179+j*337) % H), (i*7+j*13) % 60)
#          for i in range(6) for j in range(8)]


# def ctxt_split(surf, text, font, cx, cy, glow=False):
#     for col, clip_rect in [
#         (CYAN, pygame.Rect(0,     0, W//2,   surf.get_height())),
#         (PINK, pygame.Rect(W//2,  0, W//2,   surf.get_height())),
#     ]:
#         if glow:
#             gh = font.render(text, True, col)
#             gh.set_alpha(45)
#             gx = cx - gh.get_width()//2
#             gy = cy - gh.get_height()//2
#             for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
#                 surf.set_clip(clip_rect)
#                 surf.blit(gh, (gx+dx, gy+dy))
#         s = font.render(text, True, col)
#         surf.set_clip(clip_rect)
#         surf.blit(s, (cx - s.get_width()//2, cy - s.get_height()//2))
#     surf.set_clip(None)


# def draw_bg(t):
#     screen.fill(BG)
#     for cx, col in [(W//4, CYAN), (3*W//4, PINK)]:
#         tmp = pygame.Surface((W//2, H), pygame.SRCALPHA)
#         p = int(14+5*math.sin(t*0.7))
#         for i in range(6, 0, -1):
#             pygame.draw.circle(tmp, (*col, p*i//6), (W//4, H//2), (W//3)*i//5)
#         screen.blit(tmp, (0 if cx == W//4 else W//2, 0))
#     for sx, sy, ph in STARS:
#         a = int(55+35*math.sin(t*0.7+ph))
#         s = pygame.Surface((2, 2), pygame.SRCALPHA)
#         s.fill((*WHITE, a))
#         screen.blit(s, (sx, sy))
#     # Divider
#     pulse = int(160+60*math.sin(t*1.5))
#     tmp = pygame.Surface((W, H), pygame.SRCALPHA)
#     pygame.draw.line(tmp, (*PINK, pulse//4), (W//2, 0), (W//2, H), 10)
#     pygame.draw.line(tmp, (*PINK, pulse//2), (W//2, 0), (W//2, H), 3)
#     screen.blit(tmp, (0, 0))
#     pygame.draw.line(screen, WHITE, (W//2, 0), (W//2, H), 1)


# def draw_caro_mini(cx, cy, sz, t, color=CYAN):
#     s = sz//3
#     ox = cx-sz//2
#     oy = cy-sz//2
#     tmp = pygame.Surface((sz, sz), pygame.SRCALPHA)
#     p = int(130*(0.75+0.25*math.sin(t*1.8)))
#     m = s//4
#     for i in range(1, 3):
#         pygame.draw.line(tmp, (*color, p), (i*s, 0), (i*s, sz), 1)
#         pygame.draw.line(tmp, (*color, p), (0, i*s), (sz, i*s), 1)
#     pygame.draw.line(tmp, (*color, p), (m, m), (s-m, s-m), 2)
#     pygame.draw.line(tmp, (*color, p), (s-m, m), (m, s-m), 2)
#     pygame.draw.circle(tmp, (*color, p), (s+s//2, s+s//2), s//2-m, 2)
#     bx, by = 2*s, 2*s
#     pygame.draw.line(tmp, (*color, p), (bx+m, by+m), (bx+s-m, by+s-m), 2)
#     pygame.draw.line(tmp, (*color, p), (bx+s-m, by+m), (bx+m, by+s-m), 2)
#     screen.blit(tmp, (ox, oy))


# def draw_chess_mini(cx, cy, sz, t, color=PINK):
#     s = sz//4
#     ox = cx-sz//2
#     oy = cy-sz//2
#     tmp = pygame.Surface((sz+2, sz+2), pygame.SRCALPHA)
#     p = int(130*(0.75+0.25*math.sin(t*1.8+1)))
#     for r in range(4):
#         for c in range(4):
#             if (r+c) % 2 == 0:
#                 pygame.draw.rect(tmp, (*color, 50), (c*s, r*s, s, s))
#     pygame.draw.rect(tmp, (*color, p), (0, 0, sz, sz), 1)
#     kx, ky = sz//2, sz//2
#     pts = [(kx-14, ky+10), (kx-14, ky-2), (kx-6, ky-10),
#            (kx, ky-2), (kx+6, ky-10), (kx+14, ky-2), (kx+14, ky+10)]
#     pygame.draw.polygon(tmp, (*color, p), pts, 2)
#     screen.blit(tmp, (ox, oy))

# # ── Button ────────────────────────────────────────────────


# class Btn:
#     def __init__(self, rect, label, col=CYAN, sub="", font=None):
#         self.rect = pygame.Rect(rect)
#         self.label = label
#         self.sub = sub
#         self.col = col
#         self.font = font or F_BTN
#         self.hov = False

#     def update(self, pos): self.hov = self.rect.collidepoint(pos)
#     def clicked(self, pos): return self.rect.collidepoint(pos)

#     def draw(self, t):
#         col = tuple(min(255, int(c*1.15))
#                     for c in self.col) if self.hov else self.col
#         tmp = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
#         tmp.fill((*col, 55 if self.hov else 22))
#         screen.blit(tmp, self.rect.topleft)
#         pygame.draw.rect(screen, col, self.rect, 2, border_radius=6)
#         if self.hov:
#             g = self.rect.inflate(6, 6)
#             t2 = pygame.Surface((g.w, g.h), pygame.SRCALPHA)
#             pygame.draw.rect(t2, (*col, 40), (0, 0, g.w, g.h),
#                              2, border_radius=8)
#             screen.blit(t2, g.topleft)
#         cy = self.rect.centery-(10 if self.sub else 0)
#         ctxt(screen, self.label, self.font, self.rect.centerx, cy, col)
#         if self.sub:
#             s = F_HINT.render(self.sub, True, GRAY)
#             screen.blit(s, (self.rect.centerx-s.get_width() //
#                         2, self.rect.centery+13))


# class SplitBtn(Btn):
#     """Nút nằm vắt qua đường kẻ giữa — trái CYAN, phải PINK."""

#     def __init__(self, rect, label, sub="", font=None):
#         super().__init__(rect, label, col=CYAN, sub=sub, font=font)
#         self.col2 = PINK

#     def draw(self, t):
#         split = W // 2
#         r = self.rect
#         # Vẽ nền 2 nửa
#         for col, clip in [
#             (CYAN, pygame.Rect(r.x,     r.y, split - r.x,        r.h)),
#             (PINK, pygame.Rect(split,   r.y, r.right - split,     r.h)),
#         ]:
#             tmp = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
#             tmp.fill((*col, 55 if self.hov else 22))
#             screen.set_clip(clip)
#             screen.blit(tmp, r.topleft)

#         screen.set_clip(None)

#         # Viền 2 nửa
#         for col, clip in [
#             (CYAN, pygame.Rect(r.x,   r.y, split - r.x,    r.h)),
#             (PINK, pygame.Rect(split, r.y, r.right - split, r.h)),
#         ]:
#             screen.set_clip(clip)
#             pygame.draw.rect(screen, col, r, 2, border_radius=6)

#         screen.set_clip(None)

#         # Hover glow
#         if self.hov:
#             for col, clip in [
#                 (CYAN, pygame.Rect(r.x,   r.y-3, split-r.x+3,   r.h+6)),
#                 (PINK, pygame.Rect(split-3, r.y-3, r.right-split+6, r.h+6)),
#             ]:
#                 g = r.inflate(6, 6)
#                 t2 = pygame.Surface((g.w, g.h), pygame.SRCALPHA)
#                 pygame.draw.rect(
#                     t2, (*col, 40), (0, 0, g.w, g.h), 2, border_radius=8)
#                 screen.set_clip(clip)
#                 screen.blit(t2, g.topleft)
#             screen.set_clip(None)

#         # Text + sub (không clip, để text hiện đầy đủ ở giữa)
#         cy_txt = r.centery - (10 if self.sub else 0)
#         ctxt_split(screen, self.label, self.font or F_BTN, r.centerx, cy_txt)
#         if self.sub:
#             s = F_HINT.render(self.sub, True, GRAY)
#             screen.blit(s, (r.centerx - s.get_width()//2, r.centery + 13))


# # ── States ────────────────────────────────────────────────
# S_MAIN = "main"
# S_CARO = "caro"
# S_CDIFF = "cdiff"
# S_XDIFF = "xdiff"
# S_CTYPE = "ctype"
# S_XTYPE = "xtype"
# state = S_MAIN
# sel_mode = None

# DEPTHS = {"3x3": [2, 5, 9], "4x4": [1, 2, 4],
#           "5x5": [1, 3, 5], "chess": [1, 2, 3]}


# def _main_btns():
#     cy = H//2+130
#     bw, bh = 240, 62
#     return [Btn((W//4-bw//2, cy, bw, bh), "PLAY CARO",  CYAN, "Tic-tac-toe strategy"),
#             Btn((3*W//4-bw//2, cy, bw, bh), "PLAY CHESS", PINK, "Traditional chess")]


# def _caro_btns():
#     bw, bh = 270, 190
#     gap = 55
#     total = 3*bw + 2*gap
#     sx = (W - total) // 2
#     cy = H // 2
#     return [
#         Btn((sx,            cy-bh//2, bw, bh),
#             "3 x 3", CYAN, "Classic",  mf(40)),
#         SplitBtn((sx+bw+gap,     cy-bh//2, bw, bh),
#                  "4 x 4", "Medium",   mf(40)),
#         Btn((sx+2*(bw+gap), cy-bh//2, bw, bh),
#             "5 x 5", PINK, "10x10",   mf(40)),
#     ]


# def _diff_btns(left_col):
#     lbls = [("Easy", "Beginner"), ("Medium", "Balanced"), ("Hard", "Expert")]
#     bw, bh = 230, 84
#     gap = 50
#     total = 3*bw + 2*gap
#     sx = (W - total) // 2
#     cy = H // 2 + 60
#     return [
#         Btn((sx,            cy-bh//2, bw, bh),
#             lbls[0][0], CYAN, lbls[0][1]),  # Easy luôn CYAN
#         SplitBtn((sx+bw+gap,     cy-bh//2, bw, bh),
#                  lbls[1][0], lbls[1][1]),   # Medium split
#         Btn((sx+2*(bw+gap), cy-bh//2, bw, bh),
#             lbls[2][0], PINK, lbls[2][1]),  # Hard luôn PINK
#     ]


# def _ctype_btns():
#     bw, bh, gap = 260, 80, 60
#     sx = W//2 - bw - gap//2
#     cy = H//2 + 40
#     return [
#         Btn((sx,        cy-bh//2, bw, bh), "VS MÁY",       CYAN, "Player vs AI"),
#         Btn((sx+bw+gap, cy-bh//2, bw, bh),
#             "2 NGƯỜI CHƠI", PINK, "Player vs Player"),
#     ]


# def _xtype_btns():
#     bw, bh, gap = 260, 80, 60
#     sx = W//2 - bw - gap//2
#     cy = H//2 + 40
#     return [
#         Btn((sx,        cy-bh//2, bw, bh), "VS MÁY",       CYAN, "Player vs AI"),
#         Btn((sx+bw+gap, cy-bh//2, bw, bh),
#             "2 NGƯỜI CHƠI", PINK, "Player vs Player"),
#     ]


# def _back(): return Btn((28, 28, 110, 40), "< BACK", GRAY, font=F_SUB)


# def draw_diff_screen(btns, back, t, title, col, prev_fn=None):
#     draw_bg(t)
#     ctxt_split(screen, title, F_TITLE, W//2, 72, glow=True)
#     if prev_fn:
#         prev_fn(W//2, H//2-100, 120, t)
#     for b in btns:
#         b.draw(t)
#     back.draw(t)

# # ── Launch ────────────────────────────────────────────────


# def launch_caro(mode, depth, pvp=False):
#     script = os.path.join(BASE, "caro", "caro_gui.py")
#     args = [sys.executable, script, mode, str(depth)]
#     if pvp:
#         args.append("pvp")
#     subprocess.Popen(args)


# def launch_chess(depth, pvp=False):
#     script = os.path.join(BASE, "chess", "gui.py")
#     args = [sys.executable, script, str(depth)]
#     if pvp:
#         args.append("pvp")
#     subprocess.Popen(args)

# # ── Main ──────────────────────────────────────────────────


# def main():
#     global state, sel_mode
#     main_btns = _main_btns()
#     caro_btns = _caro_btns()
#     cdiff_btns = _diff_btns(PINK)
#     xdiff_btns = _diff_btns(CYAN)
#     ctype_btns = _ctype_btns()
#     xtype_btns = _xtype_btns()
#     back_btn = _back()
#     t = 0.0
#     while True:
#         dt = clock.tick(60)/1000.0
#         t += dt
#         mx, my = pygame.mouse.get_pos()

#         active = {S_MAIN: main_btns, S_CARO: caro_btns+[back_btn],
#                   S_CDIFF: cdiff_btns+[back_btn], S_XDIFF: xdiff_btns+[back_btn],
#                   S_CTYPE: ctype_btns+[back_btn], S_XTYPE: xtype_btns+[back_btn]}.get(state, [])
#         for b in active:
#             b.update((mx, my))

#         for ev in pygame.event.get():
#             if ev.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#             if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
#                 if state == S_MAIN:
#                     pygame.quit()
#                     sys.exit()
#                 else:
#                     state = S_MAIN
#             if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
#                 if state == S_MAIN:
#                     if main_btns[0].clicked((mx, my)):
#                         state = S_CARO
#                     elif main_btns[1].clicked((mx, my)):
#                         state = S_XTYPE
#                 elif state == S_CARO:
#                     if back_btn.clicked((mx, my)):
#                         state = S_MAIN
#                     else:
#                         for i, b in enumerate(caro_btns):
#                             if b.clicked((mx, my)):
#                                 sel_mode = ["3x3", "4x4", "5x5"][i]
#                                 cdiff_btns = _diff_btns(CYAN)
#                                 state = S_CTYPE
#                                 break
#                 elif state == S_CTYPE:
#                     if back_btn.clicked((mx, my)):
#                         state = S_CARO
#                     elif ctype_btns[0].clicked((mx, my)):
#                         cdiff_btns = _diff_btns(CYAN)
#                         state = S_CDIFF
#                     elif ctype_btns[1].clicked((mx, my)):
#                         launch_caro(sel_mode, 0, pvp=True)
#                 elif state == S_XTYPE:
#                     if back_btn.clicked((mx, my)):
#                         state = S_MAIN
#                     elif xtype_btns[0].clicked((mx, my)):
#                         xdiff_btns = _diff_btns(PINK)
#                         state = S_XDIFF
#                     elif xtype_btns[1].clicked((mx, my)):
#                         launch_chess(0, pvp=True)
#                 elif state == S_CDIFF:
#                     if back_btn.clicked((mx, my)):
#                         state = S_CARO
#                     else:
#                         for i, b in enumerate(cdiff_btns):
#                             if b.clicked((mx, my)):
#                                 launch_caro(sel_mode, DEPTHS[sel_mode][i])
#                                 break
#                 elif state == S_XDIFF:
#                     if back_btn.clicked((mx, my)):
#                         state = S_MAIN
#                     else:
#                         for i, b in enumerate(xdiff_btns):
#                             if b.clicked((mx, my)):
#                                 launch_chess(DEPTHS["chess"][i])
#                                 break

#         # Draw
#         if state == S_MAIN:
#             draw_bg(t)
#             ctxt(screen, "WELCOME TO", F_SUB, W//2, H//2-85, GRAY)
#             ctxt(screen, "CHARO", F_LOGO, W//2, H//2-18, WHITE, glow=True)
#             ctxt(screen, "CARO", F_TITLE, W//4,   H//2-115, CYAN, glow=True)
#             ctxt(screen, "CHESS", F_TITLE, 3*W//4, H//2-115, PINK, glow=True)
#             draw_caro_mini(W//4,   H//2-18, 150, t)
#             draw_chess_mini(3*W//4, H//2-18, 150, t)
#             for b in main_btns:
#                 b.draw(t)
#             h = F_HINT.render("ESC to quit", True, DIM)
#             screen.blit(h, (W//2-h.get_width()//2, H-26))
#         elif state == S_CARO:
#             draw_bg(t)
#             ctxt_split(screen, "SELECT CARO MODE",
#                        F_TITLE, W//2, 72, glow=True)
#             for i, b in enumerate(caro_btns):
#                 draw_caro_mini(b.rect.centerx, b.rect.centery-28, 110, t+i*0.7)
#             for b in caro_btns:
#                 b.draw(t)
#             back_btn.draw(t)
#         elif state == S_CDIFF:
#             lbl = {"3x3": "3x3", "4x4": "4x4", "5x5": "5x5"}[sel_mode]
#             draw_diff_screen(cdiff_btns, back_btn, t,
#                              f"DIFFICULTY — CARO {lbl}", CYAN, draw_caro_mini)
#         elif state == S_XDIFF:
#             draw_diff_screen(xdiff_btns, back_btn, t,
#                              "DIFFICULTY — CHESS", PINK, draw_chess_mini)
#         elif state == S_CTYPE:
#             draw_bg(t)
#             lbl = sel_mode.upper() if sel_mode else ""
#             ctxt_split(screen, f"CARO {lbl} — CHỌN CHẾ ĐỘ",
#                        F_TITLE, W//2, 72, glow=True)
#             draw_caro_mini(ctype_btns[0].rect.centerx,
#                            ctype_btns[0].rect.top - 55, 90, t, color=CYAN)
#             draw_caro_mini(ctype_btns[1].rect.centerx,
#                            ctype_btns[1].rect.top - 55, 90, t + 1.0, color=PINK)
#             for b in ctype_btns:
#                 b.draw(t)
#             back_btn.draw(t)
#         elif state == S_XTYPE:
#             draw_bg(t)
#             ctxt_split(screen, "CHESS — CHỌN CHẾ ĐỘ",
#                        F_TITLE, W//2, 72, glow=True)
#             draw_chess_mini(xtype_btns[0].rect.centerx,
#                             xtype_btns[0].rect.top - 55, 90, t, color=CYAN)
#             draw_chess_mini(xtype_btns[1].rect.centerx,
#                             xtype_btns[1].rect.top - 55, 90, t + 1.0, color=PINK)
#             pulse = int(120 + 60 * math.sin(t * 2.0))
#             for b in xtype_btns:
#                 b.draw(t)
#             back_btn.draw(t)
#         pygame.display.flip()


# if __name__ == "__main__":
#     main()

"""CHARO — Main Menu (subprocess launcher)"""
import pygame
import sys
import math
import os
import subprocess

pygame.init()
W, H = 1280, 720
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("CHARO")
clock = pygame.time.Clock()
BASE = os.path.dirname(os.path.abspath(__file__))

BG = (2, 0, 8)
CYAN = (0, 220, 200)
PINK = (210, 0, 175)
WHITE = (255, 255, 255)
GRAY = (130, 130, 150)
DIM = (55, 55, 70)


def mf(sz, bold=True):
    """
    Tạo đối tượng font pygame với kích thước và độ đậm cho trước.
    Thử lần lượt các font hệ thống phổ biến, nếu không có thì dùng font mặc định.

    Args:
        sz (int): Kích thước font.
        bold (bool): Có in đậm font hay không.

    Returns:
        pygame.font.Font: Đối tượng font đã được tạo.
    """
    for n in ["Consolas", "Courier New", "Lucida Console"]:
        try:
            f = pygame.font.SysFont(n, sz, bold=bold)
            if f:
                return f
        except:
            pass
    return pygame.font.Font(None, sz)


F_LOGO = mf(88)
F_TITLE = mf(28)
F_BTN = mf(20)
F_SUB = mf(15, bold=False)
F_HINT = mf(13, bold=False)

STARS = [(int((i*337+j*179) % W), int((i*179+j*337) % H), (i*7+j*13) % 60)
         for i in range(6) for j in range(8)]


def ctxt(surf, text, font, cx, cy, col, glow=False):
    """
    Vẽ văn bản căn giữa với tùy chọn hiệu ứng glow (phát sáng).

    Args:
        surf (pygame.Surface): Bề mặt để vẽ.
        text (str): Nội dung văn bản.
        font (pygame.font.Font): Font chữ sử dụng.
        cx (int): Tọa độ X trung tâm.
        cy (int): Tọa độ Y trung tâm.
        col (tuple): Màu sắc (R, G, B).
        glow (bool): Có vẽ hiệu ứng glow xung quanh text hay không.
    """
    if glow:
        h = font.render(text, True, col)
        h.set_alpha(45)
        for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
            surf.blit(h, (cx-h.get_width()//2+dx, cy-h.get_height()//2+dy))
    s = font.render(text, True, col)
    surf.blit(s, (cx-s.get_width()//2, cy-s.get_height()//2))


def ctxt_split(surf, text, font, cx, cy, glow=False):
    """
    Vẽ văn bản căn giữa với hiệu ứng chia đôi màu: nửa trái CYAN, nửa phải PINK.

    Args:
        surf (pygame.Surface): Bề mặt để vẽ.
        text (str): Nội dung văn bản.
        font (pygame.font.Font): Font chữ sử dụng.
        cx (int): Tọa độ X trung tâm.
        cy (int): Tọa độ Y trung tâm.
        glow (bool): Có vẽ hiệu ứng glow xung quanh text hay không.
    """
    for col, clip_rect in [
        (CYAN, pygame.Rect(0, 0, W//2, surf.get_height())),
        (PINK, pygame.Rect(W//2, 0, W//2, surf.get_height())),
    ]:
        if glow:
            gh = font.render(text, True, col)
            gh.set_alpha(45)
            gx = cx - gh.get_width()//2
            gy = cy - gh.get_height()//2
            for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3)]:
                surf.set_clip(clip_rect)
                surf.blit(gh, (gx+dx, gy+dy))
        s = font.render(text, True, col)
        surf.set_clip(clip_rect)
        surf.blit(s, (cx - s.get_width()//2, cy - s.get_height()//2))
    surf.set_clip(None)


def draw_bg(t):
    """
    Vẽ nền chính của ứng dụng với hiệu ứng hoạt hình:
    - Gradient tròn phát sáng hai bên (CYAN/PINK)
    - Các ngôi sao nhấp nháy ngẫu nhiên
    - Đường kẻ chia đôi màn hình có hiệu ứng pulse

    Args:
        t (float): Thời gian chạy dùng để tính toán animation.
    """
    screen.fill(BG)
    for cx, col in [(W//4, CYAN), (3*W//4, PINK)]:
        tmp = pygame.Surface((W//2, H), pygame.SRCALPHA)
        p = int(14+5*math.sin(t*0.7))
        for i in range(6, 0, -1):
            pygame.draw.circle(tmp, (*col, p*i//6), (W//4, H//2), (W//3)*i//5)
        screen.blit(tmp, (0 if cx == W//4 else W//2, 0))
    for sx, sy, ph in STARS:
        a = int(55+35*math.sin(t*0.7+ph))
        s = pygame.Surface((2, 2), pygame.SRCALPHA)
        s.fill((*WHITE, a))
        screen.blit(s, (sx, sy))
    pulse = int(160+60*math.sin(t*1.5))
    tmp = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.line(tmp, (*PINK, pulse//4), (W//2, 0), (W//2, H), 10)
    pygame.draw.line(tmp, (*PINK, pulse//2), (W//2, 0), (W//2, H), 3)
    screen.blit(tmp, (0, 0))
    pygame.draw.line(screen, WHITE, (W//2, 0), (W//2, H), 1)


def draw_caro_mini(cx, cy, sz, t, color=CYAN):
    """
    Vẽ icon mini biểu tượng trò chơi Caro với hiệu ứng hoạt hình.

    Args:
        cx (int): Tọa độ X trung tâm của icon.
        cy (int): Tọa độ Y trung tâm của icon.
        sz (int): Kích thước tổng của icon.
        t (float): Thời gian chạy dùng để tính animation.
        color (tuple): Màu chủ đạo của icon (mặc định là CYAN).
    """
    s = sz//3
    ox = cx-sz//2
    oy = cy-sz//2
    tmp = pygame.Surface((sz, sz), pygame.SRCALPHA)
    p = int(130*(0.75+0.25*math.sin(t*1.8)))
    m = s//4
    for i in range(1, 3):
        pygame.draw.line(tmp, (*color, p), (i*s, 0), (i*s, sz), 1)
        pygame.draw.line(tmp, (*color, p), (0, i*s), (sz, i*s), 1)
    pygame.draw.line(tmp, (*color, p), (m, m), (s-m, s-m), 2)
    pygame.draw.line(tmp, (*color, p), (s-m, m), (m, s-m), 2)
    pygame.draw.circle(tmp, (*color, p), (s+s//2, s+s//2), s//2-m, 2)
    bx, by = 2*s, 2*s
    pygame.draw.line(tmp, (*color, p), (bx+m, by+m), (bx+s-m, by+s-m), 2)
    pygame.draw.line(tmp, (*color, p), (bx+s-m, by+m), (bx+m, by+s-m), 2)
    screen.blit(tmp, (ox, oy))


def draw_chess_mini(cx, cy, sz, t, color=PINK):
    """
    Vẽ icon mini biểu tượng trò chơi Cờ vua với hiệu ứng hoạt hình.

    Args:
        cx (int): Tọa độ X trung tâm của icon.
        cy (int): Tọa độ Y trung tâm của icon.
        sz (int): Kích thước tổng của icon.
        t (float): Thời gian chạy dùng để tính animation.
        color (tuple): Màu chủ đạo của icon (mặc định là PINK).
    """
    s = sz//4
    ox = cx-sz//2
    oy = cy-sz//2
    tmp = pygame.Surface((sz+2, sz+2), pygame.SRCALPHA)
    p = int(130*(0.75+0.25*math.sin(t*1.8+1)))
    for r in range(4):
        for c in range(4):
            if (r+c) % 2 == 0:
                pygame.draw.rect(tmp, (*color, 50), (c*s, r*s, s, s))
    pygame.draw.rect(tmp, (*color, p), (0, 0, sz, sz), 1)
    kx, ky = sz//2, sz//2
    pts = [(kx-14, ky+10), (kx-14, ky-2), (kx-6, ky-10),
           (kx, ky-2), (kx+6, ky-10), (kx+14, ky-2), (kx+14, ky+10)]
    pygame.draw.polygon(tmp, (*color, p), pts, 2)
    screen.blit(tmp, (ox, oy))


class Btn:
    """
    Lớp đại diện cho một nút bấm trong giao diện.
    Hỗ trợ trạng thái hover, vẽ nền, viền, text và subtext.
    """

    def __init__(self, rect, label, col=CYAN, sub="", font=None):
        """
        Khởi tạo nút bấm.

        Args:
            rect (tuple): Vị trí và kích thước (x, y, width, height).
            label (str): Văn bản chính hiển thị trên nút.
            col (tuple): Màu chủ đạo của nút.
            sub (str): Văn bản phụ hiển thị bên dưới label.
            font (pygame.font.Font, optional): Font chữ cho label.
        """
        self.rect = pygame.Rect(rect)
        self.label = label
        self.sub = sub
        self.col = col
        self.font = font or F_BTN
        self.hov = False

    def update(self, pos):
        """
        Cập nhật trạng thái hover dựa trên vị trí con trỏ chuột.

        Args:
            pos (tuple): Tọa độ (x, y) của con trỏ chuột.
        """
        self.hov = self.rect.collidepoint(pos)

    def clicked(self, pos):
        """
        Kiểm tra xem vị trí chuột có nằm trong vùng nút để xử lý click.

        Args:
            pos (tuple): Tọa độ (x, y) của con trỏ chuột.

        Returns:
            bool: True nếu chuột click trong vùng nút.
        """
        return self.rect.collidepoint(pos)

    def draw(self, t):
        """
        Vẽ nút lên màn hình với hiệu ứng hover và glow.

        Args:
            t (float): Thời gian chạy (dùng cho animation nếu cần mở rộng).
        """
        col = tuple(min(255, int(c*1.15))
                    for c in self.col) if self.hov else self.col
        tmp = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        tmp.fill((*col, 55 if self.hov else 22))
        screen.blit(tmp, self.rect.topleft)
        pygame.draw.rect(screen, col, self.rect, 2, border_radius=6)
        if self.hov:
            g = self.rect.inflate(6, 6)
            t2 = pygame.Surface((g.w, g.h), pygame.SRCALPHA)
            pygame.draw.rect(t2, (*col, 40), (0, 0, g.w, g.h),
                             2, border_radius=8)
            screen.blit(t2, g.topleft)
        cy = self.rect.centery-(10 if self.sub else 0)
        ctxt(screen, self.label, self.font, self.rect.centerx, cy, col)
        if self.sub:
            s = F_HINT.render(self.sub, True, GRAY)
            screen.blit(s, (self.rect.centerx-s.get_width() //
                        2, self.rect.centery+13))


class SplitBtn(Btn):
    """
    Nút đặc biệt nằm vắt qua đường kẻ giữa màn hình:
    - Nửa trái dùng màu CYAN, nửa phải dùng màu PINK.
    - Kế thừa từ lớp Btn, ghi đè phương thức draw để xử lý chia đôi màu.
    """

    def __init__(self, rect, label, sub="", font=None):
        """
        Khởi tạo nút chia đôi màu.

        Args:
            rect (tuple): Vị trí và kích thước (x, y, width, height).
            label (str): Văn bản chính hiển thị trên nút.
            sub (str): Văn bản phụ hiển thị bên dưới label.
            font (pygame.font.Font, optional): Font chữ cho label.
        """
        super().__init__(rect, label, col=CYAN, sub=sub, font=font)
        self.col2 = PINK

    def draw(self, t):
        """
        Vẽ nút với nền và viền chia đôi màu CYAN/PINK, hỗ trợ hover glow.

        Args:
            t (float): Thời gian chạy (dùng cho animation nếu cần mở rộng).
        """
        split = W // 2
        r = self.rect
        for col, clip in [
            (CYAN, pygame.Rect(r.x, r.y, split - r.x, r.h)),
            (PINK, pygame.Rect(split, r.y, r.right - split, r.h)),
        ]:
            tmp = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            tmp.fill((*col, 55 if self.hov else 22))
            screen.set_clip(clip)
            screen.blit(tmp, r.topleft)

        screen.set_clip(None)

        for col, clip in [
            (CYAN, pygame.Rect(r.x, r.y, split - r.x, r.h)),
            (PINK, pygame.Rect(split, r.y, r.right - split, r.h)),
        ]:
            screen.set_clip(clip)
            pygame.draw.rect(screen, col, r, 2, border_radius=6)

        screen.set_clip(None)

        if self.hov:
            for col, clip in [
                (CYAN, pygame.Rect(r.x, r.y-3, split-r.x+3, r.h+6)),
                (PINK, pygame.Rect(split-3, r.y-3, r.right-split+6, r.h+6)),
            ]:
                g = r.inflate(6, 6)
                t2 = pygame.Surface((g.w, g.h), pygame.SRCALPHA)
                pygame.draw.rect(
                    t2, (*col, 40), (0, 0, g.w, g.h), 2, border_radius=8)
                screen.set_clip(clip)
                screen.blit(t2, g.topleft)
            screen.set_clip(None)

        cy_txt = r.centery - (10 if self.sub else 0)
        ctxt_split(screen, self.label, self.font or F_BTN, r.centerx, cy_txt)
        if self.sub:
            s = F_HINT.render(self.sub, True, GRAY)
            screen.blit(s, (r.centerx - s.get_width()//2, r.centery + 13))


S_MAIN = "main"
S_CARO = "caro"
S_CDIFF = "cdiff"
S_XDIFF = "xdiff"
S_CTYPE = "ctype"
S_XTYPE = "xtype"
state = S_MAIN
sel_mode = None

DEPTHS = {"3x3": [2, 5, 9], "4x4": [1, 2, 4],
          "5x5": [1, 3, 5], "chess": [1, 2, 3]}


def _main_btns():
    """
    Tạo danh sách các nút chính của màn hình menu: PLAY CARO và PLAY CHESS.

    Returns:
        list[Btn]: Danh sách các đối tượng Btn đã được khởi tạo.
    """
    cy = H//2+130
    bw, bh = 240, 62
    return [Btn((W//4-bw//2, cy, bw, bh), "PLAY CARO", CYAN, "Tic-tac-toe strategy"),
            Btn((3*W//4-bw//2, cy, bw, bh), "PLAY CHESS", PINK, "Traditional chess")]


def _caro_btns():
    """
    Tạo danh sách các nút chọn chế độ chơi Caro: 3x3, 4x4, 5x5.

    Returns:
        list[Btn|SplitBtn]: Danh sách các nút chọn kích thước bàn cờ.
    """
    bw, bh = 270, 190
    gap = 55
    total = 3*bw + 2*gap
    sx = (W - total) // 2
    cy = H // 2
    return [
        Btn((sx, cy-bh//2, bw, bh), "3 x 3", CYAN, "Classic", mf(40)),
        SplitBtn((sx+bw+gap, cy-bh//2, bw, bh), "4 x 4", "Medium", mf(40)),
        Btn((sx+2*(bw+gap), cy-bh//2, bw, bh), "5 x 5", PINK, "10x10", mf(40)),
    ]


def _diff_btns(left_col):
    """
    Tạo danh sách các nút chọn độ khó: Easy, Medium, Hard.

    Args:
        left_col (tuple): Màu cho nút Easy (CYAN hoặc PINK tùy ngữ cảnh).

    Returns:
        list[Btn|SplitBtn]: Danh sách các nút chọn độ khó.
    """
    lbls = [("Easy", "Beginner"), ("Medium", "Balanced"), ("Hard", "Expert")]
    bw, bh = 230, 84
    gap = 50
    total = 3*bw + 2*gap
    sx = (W - total) // 2
    cy = H // 2 + 60
    return [
        Btn((sx, cy-bh//2, bw, bh), lbls[0][0], CYAN, lbls[0][1]),
        SplitBtn((sx+bw+gap, cy-bh//2, bw, bh), lbls[1][0], lbls[1][1]),
        Btn((sx+2*(bw+gap), cy-bh//2, bw, bh), lbls[2][0], PINK, lbls[2][1]),
    ]


def _ctype_btns():
    """
    Tạo danh sách các nút chọn chế độ chơi cho Caro: VS MÁY hoặc 2 NGƯỜI CHƠI.

    Returns:
        list[Btn]: Danh sách các nút chọn chế độ chơi.
    """
    bw, bh, gap = 260, 80, 60
    sx = W//2 - bw - gap//2
    cy = H//2 + 40
    return [
        Btn((sx, cy-bh//2, bw, bh), "VS MÁY", CYAN, "Player vs AI"),
        Btn((sx+bw+gap, cy-bh//2, bw, bh),
            "2 NGƯỜI CHƠI", PINK, "Player vs Player"),
    ]


def _xtype_btns():
    """
    Tạo danh sách các nút chọn chế độ chơi cho Chess: VS MÁY hoặc 2 NGƯỜI CHƠI.

    Returns:
        list[Btn]: Danh sách các nút chọn chế độ chơi.
    """
    bw, bh, gap = 260, 80, 60
    sx = W//2 - bw - gap//2
    cy = H//2 + 40
    return [
        Btn((sx, cy-bh//2, bw, bh), "VS MÁY", CYAN, "Player vs AI"),
        Btn((sx+bw+gap, cy-bh//2, bw, bh),
            "2 NGƯỜI CHƠI", PINK, "Player vs Player"),
    ]


def _back():
    """
    Tạo nút BACK để quay lại màn hình trước.

    Returns:
        Btn: Đối tượng nút back đã được khởi tạo.
    """
    return Btn((28, 28, 110, 40), "< BACK", GRAY, font=F_SUB)


def draw_diff_screen(btns, back, t, title, col, prev_fn=None):
    """
    Vẽ màn hình chọn độ khó với nền động, tiêu đề, icon minh họa và các nút.

    Args:
        btns (list[Btn]): Danh sách các nút độ khó cần vẽ.
        back (Btn): Nút back để quay lại.
        t (float): Thời gian chạy cho animation.
        title (str): Tiêu đề màn hình.
        col (tuple): Màu chủ đạo để vẽ icon minh họa.
        prev_fn (callable, optional): Hàm vẽ icon mini (draw_caro_mini hoặc draw_chess_mini).
    """
    draw_bg(t)
    ctxt_split(screen, title, F_TITLE, W//2, 72, glow=True)
    if prev_fn:
        prev_fn(W//2, H//2-100, 120, t)
    for b in btns:
        b.draw(t)
    back.draw(t)


def launch_caro(mode, depth, pvp=False):
    """
    Khởi chạy trò chơi Caro dưới dạng subprocess độc lập.

    Args:
        mode (str): Chế độ bàn cờ ("3x3", "4x4", "5x5").
        depth (int): Độ sâu tìm kiếm của AI.
        pvp (bool, optional): Có phải chế độ 2 người chơi hay không.
    """
    script = os.path.join(BASE, "caro", "caro_gui.py")
    args = [sys.executable, script, mode, str(depth)]
    if pvp:
        args.append("pvp")
    subprocess.Popen(args)


def launch_chess(depth, pvp=False):
    """
    Khởi chạy trò chơi Chess dưới dạng subprocess độc lập.

    Args:
        depth (int): Độ sâu tìm kiếm của AI.
        pvp (bool, optional): Có phải chế độ 2 người chơi hay không.
    """
    script = os.path.join(BASE, "chess", "gui.py")
    args = [sys.executable, script, str(depth)]
    if pvp:
        args.append("pvp")
    subprocess.Popen(args)


def main():
    """
    Hàm chính điều khiển vòng lặp game và quản lý trạng thái các màn hình:
    - S_MAIN: Menu chính chọn Caro/Chess
    - S_CARO: Chọn kích thước bàn cờ Caro
    - S_CTYPE/S_XTYPE: Chọn chế độ chơi (PvP/PvAI)
    - S_CDIFF/S_XDIFF: Chọn độ khó cho AI

    Xử lý sự kiện chuột, bàn phím và vẽ giao diện tương ứng với từng trạng thái.
    """
    global state, sel_mode
    main_btns = _main_btns()
    caro_btns = _caro_btns()
    cdiff_btns = _diff_btns(PINK)
    xdiff_btns = _diff_btns(CYAN)
    ctype_btns = _ctype_btns()
    xtype_btns = _xtype_btns()
    back_btn = _back()
    t = 0.0
    while True:
        dt = clock.tick(60)/1000.0
        t += dt
        mx, my = pygame.mouse.get_pos()

        active = {S_MAIN: main_btns, S_CARO: caro_btns+[back_btn],
                  S_CDIFF: cdiff_btns+[back_btn], S_XDIFF: xdiff_btns+[back_btn],
                  S_CTYPE: ctype_btns+[back_btn], S_XTYPE: xtype_btns+[back_btn]}.get(state, [])
        for b in active:
            b.update((mx, my))

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                if state == S_MAIN:
                    pygame.quit()
                    sys.exit()
                else:
                    state = S_MAIN
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if state == S_MAIN:
                    if main_btns[0].clicked((mx, my)):
                        state = S_CARO
                    elif main_btns[1].clicked((mx, my)):
                        state = S_XTYPE
                elif state == S_CARO:
                    if back_btn.clicked((mx, my)):
                        state = S_MAIN
                    else:
                        for i, b in enumerate(caro_btns):
                            if b.clicked((mx, my)):
                                sel_mode = ["3x3", "4x4", "5x5"][i]
                                cdiff_btns = _diff_btns(CYAN)
                                state = S_CTYPE
                                break
                elif state == S_CTYPE:
                    if back_btn.clicked((mx, my)):
                        state = S_CARO
                    elif ctype_btns[0].clicked((mx, my)):
                        cdiff_btns = _diff_btns(CYAN)
                        state = S_CDIFF
                    elif ctype_btns[1].clicked((mx, my)):
                        launch_caro(sel_mode, 0, pvp=True)
                elif state == S_XTYPE:
                    if back_btn.clicked((mx, my)):
                        state = S_MAIN
                    elif xtype_btns[0].clicked((mx, my)):
                        xdiff_btns = _diff_btns(PINK)
                        state = S_XDIFF
                    elif xtype_btns[1].clicked((mx, my)):
                        launch_chess(0, pvp=True)
                elif state == S_CDIFF:
                    if back_btn.clicked((mx, my)):
                        state = S_CARO
                    else:
                        for i, b in enumerate(cdiff_btns):
                            if b.clicked((mx, my)):
                                launch_caro(sel_mode, DEPTHS[sel_mode][i])
                                break
                elif state == S_XDIFF:
                    if back_btn.clicked((mx, my)):
                        state = S_MAIN
                    else:
                        for i, b in enumerate(xdiff_btns):
                            if b.clicked((mx, my)):
                                launch_chess(DEPTHS["chess"][i])
                                break

        if state == S_MAIN:
            draw_bg(t)
            ctxt(screen, "WELCOME TO", F_SUB, W//2, H//2-85, GRAY)
            ctxt(screen, "CHARO", F_LOGO, W//2, H//2-18, WHITE, glow=True)
            ctxt(screen, "CARO", F_TITLE, W//4, H//2-115, CYAN, glow=True)
            ctxt(screen, "CHESS", F_TITLE, 3*W//4, H//2-115, PINK, glow=True)
            draw_caro_mini(W//4, H//2-18, 150, t)
            draw_chess_mini(3*W//4, H//2-18, 150, t)
            for b in main_btns:
                b.draw(t)
            h = F_HINT.render("ESC to quit", True, DIM)
            screen.blit(h, (W//2-h.get_width()//2, H-26))
        elif state == S_CARO:
            draw_bg(t)
            ctxt_split(screen, "SELECT CARO MODE",
                       F_TITLE, W//2, 72, glow=True)
            for i, b in enumerate(caro_btns):
                draw_caro_mini(b.rect.centerx, b.rect.centery-28, 110, t+i*0.7)
            for b in caro_btns:
                b.draw(t)
            back_btn.draw(t)
        elif state == S_CDIFF:
            lbl = {"3x3": "3x3", "4x4": "4x4", "5x5": "5x5"}[sel_mode]
            draw_diff_screen(cdiff_btns, back_btn, t,
                             f"DIFFICULTY — CARO {lbl}", CYAN, draw_caro_mini)
        elif state == S_XDIFF:
            draw_diff_screen(xdiff_btns, back_btn, t,
                             "DIFFICULTY — CHESS", PINK, draw_chess_mini)
        elif state == S_CTYPE:
            draw_bg(t)
            lbl = sel_mode.upper() if sel_mode else ""
            ctxt_split(screen, f"CARO {lbl} — CHỌN CHẾ ĐỘ",
                       F_TITLE, W//2, 72, glow=True)
            draw_caro_mini(
                ctype_btns[0].rect.centerx, ctype_btns[0].rect.top - 55, 90, t, color=CYAN)
            draw_caro_mini(
                ctype_btns[1].rect.centerx, ctype_btns[1].rect.top - 55, 90, t + 1.0, color=PINK)
            for b in ctype_btns:
                b.draw(t)
            back_btn.draw(t)
        elif state == S_XTYPE:
            draw_bg(t)
            ctxt_split(screen, "CHESS — CHỌN CHẾ ĐỘ",
                       F_TITLE, W//2, 72, glow=True)
            draw_chess_mini(
                xtype_btns[0].rect.centerx, xtype_btns[0].rect.top - 55, 90, t, color=CYAN)
            draw_chess_mini(
                xtype_btns[1].rect.centerx, xtype_btns[1].rect.top - 55, 90, t + 1.0, color=PINK)
            pulse = int(120 + 60 * math.sin(t * 2.0))
            for b in xtype_btns:
                b.draw(t)
            back_btn.draw(t)
        pygame.display.flip()


if __name__ == "__main__":
    main()
