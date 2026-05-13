from core_engine import GameController, BaseAI
import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class ZobristHash:
    """Quản lý bảng băm Zobrist để mã hóa trạng thái bàn cờ nhanh chóng."""

    def __init__(self, size):
        """Khởi tạo bảng random 64-bit cho từng ô và trạng thái quân cờ."""
        self.size = size
        self.table = [[[random.getrandbits(64) for _ in range(3)]
                       for _ in range(size)]
                      for _ in range(size)]
        self.current_hash = 0

    def init_hash(self, board):
        """Tính giá trị hash ban đầu dựa trên trạng thái bàn cờ."""
        h = 0
        for r in range(self.size):
            for c in range(self.size):
                piece = board.grid[r][c]
                p_idx = 0 if piece == " " else (1 if piece == "X" else 2)
                h ^= self.table[r][c][p_idx]
        self.current_hash = h
        return h

    def update(self, r, c, old_piece, new_piece):
        """Cập nhật hash khi có nước đi mới bằng phép XOR."""
        old_idx = 0 if old_piece == " " else (1 if old_piece == "X" else 2)
        new_idx = 0 if new_piece == " " else (1 if new_piece == "X" else 2)
        self.current_hash ^= self.table[r][c][old_idx]
        self.current_hash ^= self.table[r][c][new_idx]
        return self.current_hash


def calculate_point(window, player):
    """
    Đánh giá điểm cho một chuỗi 5 ô liên tiếp.
    Trả về điểm dương nếu có lợi cho player, âm nếu đối thủ có lợi.
    """
    score = 0
    oop = "X" if player == "O" else "O"
    counts = window.count(player)
    empt = window.count(" ")
    oop_counts = window.count(oop)

    if counts > 0 and oop_counts > 0:
        return 0

    if counts == 5:
        score += 100000
    elif counts == 4 and empt == 1:
        score += 10000
    elif counts == 3 and empt == 2:
        score += 5000
    elif counts == 2 and empt == 3:
        score += 50

    if oop_counts == 4 and empt == 1:
        score -= 50000
    elif oop_counts == 3 and empt == 2:
        score -= 20000
    return score


class AI_5x5(BaseAI):
    """AI chơi Caro sử dụng Minimax, Alpha-Beta pruning và Zobrist Hashing."""

    def __init__(self, symbol="O", depth=5):
        """Khởi tạo AI với ký hiệu quân cờ, độ sâu tìm kiếm và bộ nhớ cache."""
        super().__init__(symbol, depth)
        self.zobrist = ZobristHash(10)
        self.memo = {}

    def evaluate_cell(self, board, r, c, player):
        """Đánh giá tiềm năng của một ô cờ cụ thể dựa trên các hướng xung quanh."""
        score = 0
        size = board.size
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            for offset in range(-4, 1):
                window = []
                valid_window = True
                for i in range(5):
                    nr = r + dr * (offset + i)
                    nc = c + dc * (offset + i)
                    if 0 <= nr < size and 0 <= nc < size:
                        window.append(board.grid[nr][nc])
                    else:
                        valid_window = False
                        break
                if valid_window:
                    score += calculate_point(window, player)
        return score

    def get_possible_moves(self, board):
        """
        Sinh danh sách nước đi khả thi, ưu tiên vùng có quân cờ lân cận.
        Giới hạn số lượng nước đi trả về để tối ưu hiệu năng tìm kiếm.
        """
        moves = set()
        size = board.size
        has_piece = False

        for r in range(size):
            for c in range(size):
                if board.grid[r][c] != " ":
                    has_piece = True
                    for i in range(max(0, r - 2), min(size, r + 3)):
                        for j in range(max(0, c - 2), min(size, c + 3)):
                            if board.grid[i][j] == " ":
                                moves.add((i, j))

        if not has_piece:
            return [(size // 2, size // 2)]

        move_scores = []
        WIN_THRESHOLD = 50000   # ← chỉ trigger open-4 trở lên
        BLOCK_THRESHOLD = 30000  # ← chặn khi đối thủ có open-4

        for r, c in moves:
            board.grid[r][c] = self.symbol
            my_score = self.evaluate_cell(board, r, c, self.symbol)
            board.grid[r][c] = self.opponent
            opp_score = self.evaluate_cell(board, r, c, self.opponent)
            board.grid[r][c] = " "

            if my_score >= WIN_THRESHOLD:
                return [(r, c)]  # Thắng ngay, đi liền

            combined = my_score + opp_score * 1.2  # ← trọng số phòng thủ cao hơn tí
            move_scores.append((combined, opp_score, (r, c)))

        # Sort: ưu tiên chặn nếu điểm đối thủ cao
        move_scores.sort(key=lambda x: x[0], reverse=True)

        # Đảm bảo nước chặn critical không bị bỏ sót
        critical_blocks = [(s, o, m)
                           for s, o, m in move_scores if o >= BLOCK_THRESHOLD]
        if critical_blocks:
            best_block = max(critical_blocks, key=lambda x: x[1])
            top = [m[2] for m in move_scores[:5]]
            if best_block[2] not in top:
                top[-1] = best_block[2]
            return top

        limit = 8 if self.depth <= 3 else 5
        return [m[2] for m in move_scores[:limit]]

    def evaluate_board(self, board, game_engine):
        """
        Đánh giá toàn bộ bàn cờ bằng cách quét các mẫu trong vùng chiến sự.
        Chỉ tính toán trong bounding box mở rộng để giảm thao tác thừa.
        """
        score = 0
        size = board.size

        min_r, max_r = size, 0
        min_c, max_c = size, 0
        has_piece = False

        for r in range(size):
            for c in range(size):
                if board.grid[r][c] != " ":
                    min_r = min(min_r, r)
                    max_r = max(max_r, r)
                    min_c = min(min_c, c)
                    max_c = max(max_c, c)
                    has_piece = True

        if not has_piece:
            return 0

        min_r = max(0, min_r - 4)
        max_r = min(size - 1, max_r + 4)
        min_c = max(0, min_c - 4)
        max_c = min(size - 1, max_c + 4)

        directions = [
            # horizontal
            lambda r, c, i: (r, c + i),
            # vertical
            lambda r, c, i: (r + i, c),
            # diagonal
            lambda r, c, i: (r + i, c + i),
            # anti-diagonal
            lambda r, c, i: (r + i, c - i),
        ]

        ranges = [
            (range(min_r, max_r + 1), range(min_c, max_c - 3)),
            (range(min_r, max_r - 3), range(min_c, max_c + 1)),
            (range(min_r, max_r - 3), range(min_c, max_c - 3)),
            (range(min_r, max_r - 3), range(min_c + 4, max_c + 1)),
        ]

        for (rows, cols), get_pos in zip(ranges, directions):
            for r in rows:
                for c in cols:
                    line = [board.grid[get_pos(r, c, i)[0]][get_pos(r, c, i)[
                        1]] for i in range(5)]
                    # ← Trừ điểm đối thủ
                    score += self.score_pattern(line,
                                                self.symbol, self.opponent, " ")
                    score -= self.score_pattern(line,
                                                self.opponent, self.symbol, " ")

        return score

    def score_pattern(self, line, p, opp, e):
        """
        Tính điểm cho một mẫu 5 ô dựa trên các cấu hình chiến thuật.
        Ưu tiên điểm cao cho thế thắng, điểm âm cho thế bị đe dọa.
        """
        s = opp + "".join(line) + opp
        pts = 0

        pts += s.count(p*5) * 100000000
        pts += s.count(e + p*4) * 5000000
        pts += s.count(p*4 + e) * 5000000

        pts += s.count(opp + p*4 + e) * 100000
        pts += s.count(e + p*4 + opp) * 100000
        pts += s.count(e + p*3 + e) * 50000

        pts += s.count(e + p + e + p*2 + e) * 40000
        pts += s.count(e + p*2 + e + p + e) * 40000

        pts += s.count(opp + p*3 + e + e) * 1000
        pts += s.count(e + e + p*3 + opp) * 1000
        pts += s.count(e + p*2 + e) * 500

        return pts

    def find_forced_moves(self, board, game_engine):
        """
        Tìm nước đi bắt buộc: thắng ngay hoặc chặn đối thủ thắng.
        Trả về tọa độ nếu tìm thấy, ngược lại trả None.
        """
        size = board.size

        for r in range(size):
            for c in range(size):
                if board.grid[r][c] == " ":
                    board.place_piece(r, c, self.symbol, is_real=False)
                    if game_engine.check_winner(self.symbol):
                        board.remove_piece(r, c)
                        return (r, c)
                    board.remove_piece(r, c)

        for r in range(size):
            for c in range(size):
                if board.grid[r][c] == " ":
                    board.place_piece(r, c, self.opponent, is_real=False)
                    if game_engine.check_winner(self.opponent):
                        board.remove_piece(r, c)
                        return (r, c)
                    board.remove_piece(r, c)

        return None

    def get_best_move(self, board, game_engine):
        """Tìm nước đi tốt nhất bằng Minimax với Alpha-Beta pruning và Memoization."""
        forced_move = self.find_forced_moves(board, game_engine)
        if forced_move:
            return forced_move

        best_score = -float('inf')
        best_move = None
        alpha = -float('inf')
        beta = float('inf')

        self.zobrist.init_hash(board)
        moves = self.get_possible_moves(board)
        if not moves:
            return None

        for r, c in moves:
            board.place_piece(r, c, self.symbol, is_real=False)
            next_hash = self.zobrist.update(r, c, " ", self.symbol)

            score = self.minimax_memo(
                board, game_engine, self.depth, alpha, beta, False, next_hash)

            board.remove_piece(r, c)
            self.zobrist.update(r, c, self.symbol, " ")

            if score > best_score:
                best_score = score
                best_move = (r, c)

        return best_move

    def minimax_memo(self, board, game_engine, depth, alpha, beta, is_maximizing, current_hash):
        """
        Hàm Minimax đệ quy có nhớ, sử dụng Alpha-Beta pruning.
        Trả về điểm đánh giá cho trạng thái hiện tại của bàn cờ.
        """
        if current_hash in self.memo:
            memo_depth, memo_score = self.memo[current_hash]
            if memo_depth >= depth:
                return memo_score

        if game_engine.check_winner(self.symbol):
            return 100000 + depth
        if game_engine.check_winner(self.opponent):
            return -100000 - depth
        if board.is_full() or depth == 0:
            return self.evaluate_board(board, game_engine)

        moves = self.get_possible_moves(board)

        if is_maximizing:
            best_score = -float('inf')
            for r, c in moves:
                board.place_piece(r, c, self.symbol, is_real=False)
                new_hash = self.zobrist.update(r, c, " ", self.symbol)

                score = self.minimax_memo(
                    board, game_engine, depth - 1, alpha, beta, False, new_hash)

                board.remove_piece(r, c)
                self.zobrist.update(r, c, self.symbol, " ")

                best_score = max(score, best_score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
        else:
            best_score = float('inf')
            for r, c in moves:
                board.place_piece(r, c, self.opponent, is_real=False)
                new_hash = self.zobrist.update(r, c, " ", self.opponent)

                score = self.minimax_memo(
                    board, game_engine, depth - 1, alpha, beta, True, new_hash)

                board.remove_piece(r, c)
                self.zobrist.update(r, c, self.opponent, " ")

                best_score = min(score, best_score)
                beta = min(beta, score)
                if beta <= alpha:
                    break

        self.memo[current_hash] = (depth, best_score)
        return best_score


if __name__ == "__main__":
    ai_player = AI_5x5(symbol="O", depth=5)
    game = GameController(size=10, win_condition=5, ai_player=ai_player)
    print("CHÀO MỪNG ĐẾN VỚI CARO 5X5")
    game.play()
