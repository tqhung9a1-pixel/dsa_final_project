"""
CARO — Game Logic Module
Logic cốt lõi cho game Caro: bàn cờ, engine kiểm tra thắng, AI minimax, và controller.

Các class chính:
    - Board: Quản lý trạng thái bàn cờ và các thao tác cơ bản
    - GameEngine: Kiểm tra điều kiện thắng/thua/hòa
    - BaseAI: AI sử dụng thuật toán Minimax với Alpha-Beta pruning
    - GameController: Điều khiển luồng game và tương tác người dùng
"""


class Board:
    """
    Lớp quản lý bàn cờ Caro.

    Lưu trữ trạng thái các ô, lịch sử nước đi, và cung cấp các thao tác
    cơ bản: đặt quân, hủy nước đi, kiểm tra ô trống, in bàn cờ.
    """

    def __init__(self, size):
        """
        Khởi tạo bàn cờ Caro với kích thước cho trước.

        Args:
            size (int): Kích thước bàn cờ (size x size), ví dụ: 3, 4, 5
        """
        self.size = size
        self.grid = [[" " for _ in range(size)] for _ in range(size)]
        self.move_history = []

    def print_board(self):
        """
        In bàn cờ ra console với định dạng lưới dễ đọc.

        Ví dụ output (3x3):
          X | O |  
         -----------
           | X | O  
         -----------
           |   | X  
        """
        print("\n")
        for row in range(self.size):
            print(" | ".join(self.grid[row]))
            if row < self.size - 1:
                print("-" * (self.size * 4 - 1))
        print("\n")

    def is_full(self):
        """
        Kiểm tra xem bàn cờ đã đầy chưa (không còn ô trống).

        Returns:
            bool: True nếu tất cả ô đều đã có quân, False nếu còn ô trống
        """
        return all(cell != " " for row in self.grid for cell in row)

    def is_valid_move(self, r, c):
        """
        Kiểm tra xem một nước đi có hợp lệ không.

        Args:
            r (int): Chỉ số hàng (0-based)
            c (int): Chỉ số cột (0-based)

        Returns:
            bool: True nếu ô nằm trong bàn cờ và còn trống
        """
        return 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == " "

    def place_piece(self, r, c, piece, is_real=True):
        """
        Đặt một quân cờ lên bàn cờ tại vị trí cho trước.

        Args:
            r (int): Chỉ số hàng
            c (int): Chỉ số cột
            piece (str): Ký hiệu quân cờ ("X" hoặc "O")
            is_real (bool): Nếu True, lưu nước đi vào lịch sử (mặc định: True)
        """
        self.grid[r][c] = piece
        if is_real:
            self.move_history.append((r, c, piece))

    def undo_last_move(self):
        """
        Hủy nước đi cuối cùng và khôi phục trạng thái bàn cờ.

        Returns:
            bool: True nếu hủy thành công, False nếu không có nước đi để hủy
        """
        if len(self.move_history) > 0:
            r, c, piece = self.move_history.pop()
            self.grid[r][c] = " "
            return True
        return False

    def get_last_move(self):
        """
        Lấy thông tin nước đi cuối cùng đã thực hiện.

        Returns:
            tuple or None: (row, col, piece) của nước đi cuối, hoặc None nếu chưa có nước nào
        """
        if len(self.move_history) > 0:
            return self.move_history[-1]
        return None

    def remove_piece(self, r, c):
        """
        Xóa quân cờ tại vị trí cho trước (dùng cho AI simulation).

        Args:
            r (int): Chỉ số hàng
            c (int): Chỉ số cột
        """
        self.grid[r][c] = " "


class GameEngine:
    """
    Engine xử lý logic game: kiểm tra điều kiện thắng/thua.

    Hỗ trợ điều kiện thắng tùy chỉnh (win_condition): cần nối bao nhiêu quân
    liên tiếp theo hàng ngang/dọc/chéo để thắng.
    """

    def __init__(self, board, win_condition):
        """
        Khởi tạo GameEngine với bàn cờ và điều kiện thắng.

        Args:
            board (Board): Đối tượng bàn cờ để kiểm tra
            win_condition (int): Số quân liên tiếp cần có để thắng (vd: 3 cho 3x3)
        """
        self.board = board
        self.win_condition = win_condition

    def check_winner(self, player):
        """
        Kiểm tra xem người chơi đã thắng chưa.

        Duyệt toàn bộ bàn cờ theo 4 hướng: ngang, dọc, chéo xuôi, chéo ngược
        để tìm chuỗi liên tiếp đạt điều kiện thắng.

        Args:
            player (str): Ký hiệu người chơi cần kiểm tra ("X" hoặc "O")

        Returns:
            bool: True nếu player đã thắng, False nếu chưa
        """
        size = self.board.size
        grid = self.board.grid
        win_req = self.win_condition

        # Kiểm tra hàng ngang và cột dọc
        for i in range(size):
            for j in range(size - win_req + 1):
                if all(grid[i][j + k] == player for k in range(win_req)):
                    return True
                if all(grid[j+k][i] == player for k in range(win_req)):
                    return True

        # Kiểm tra 2 đường chéo
        for i in range(size - win_req + 1):
            for j in range(size - win_req + 1):
                if all(grid[i+k][j+k] == player for k in range(win_req)):
                    return True
                if all(grid[i+k][j + win_req - 1 - k] == player for k in range(win_req)):
                    return True
        return False


class BaseAI:
    """
    AI cơ bản sử dụng thuật toán Minimax với Alpha-Beta pruning.

    Tìm nước đi tối ưu bằng cách mô phỏng các nước đi tương lai,
    đánh giá trạng thái bàn cờ và chọn phương án có lợi nhất.
    """

    def __init__(self, symbol="O", depth=4):
        """
        Khởi tạo AI với ký hiệu quân và độ sâu tìm kiếm.

        Args:
            symbol (str): Ký hiệu quân của AI ("X" hoặc "O")
            depth (int): Độ sâu tìm kiếm của Minimax (càng cao càng mạnh nhưng chậm)
        """
        self.symbol = symbol
        self.depth = depth
        self.opponent = "X" if symbol == "O" else "O"

    def get_possible_moves(self, board):
        """
        Lấy danh sách tất cả các ô trống có thể đặt quân.

        Args:
            board (Board): Bàn cờ hiện tại

        Returns:
            list[tuple]: Danh sách các tọa độ (row, col) hợp lệ
        """
        moves = []
        for r in range(board.size):
            for c in range(board.size):
                if board.grid[r][c] == " ":
                    moves.append((r, c))
        return moves

    def evaluate_board(self, board, game_engine):
        """
        Hàm đánh giá heuristic cho trạng thái bàn cờ.

        Lưu ý: Hiện tại trả về 0 (chưa implement heuristic nâng cao).
        Có thể mở rộng để đánh giá: số chuỗi gần thắng, kiểm soát trung tâm, v.v.

        Args:
            board (Board): Bàn cờ cần đánh giá
            game_engine (GameEngine): Engine để hỗ trợ kiểm tra logic

        Returns:
            int: Điểm đánh giá (cao = tốt cho AI, thấp = tốt cho đối thủ)
        """
        return 0

    def minimax(self, board, game_engine, depth, alpha, beta, is_maximizing):
        """
        Thuật toán Minimax với Alpha-Beta pruning để tìm nước đi tối ưu.

        Đệ quy mô phỏng các nước đi tương lai:
        - Nếu AI thắng: trả điểm dương lớn
        - Nếu đối thủ thắng: trả điểm âm lớn
        - Nếu hết độ sâu/bàn cờ đầy: dùng hàm heuristic đánh giá
        - Alpha-Beta pruning cắt nhánh không cần thiết để tăng tốc

        Args:
            board (Board): Bàn cờ hiện tại
            game_engine (GameEngine): Engine kiểm tra thắng
            depth (int): Độ sâu còn lại của cây tìm kiếm
            alpha (float): Giá trị alpha cho pruning
            beta (float): Giá trị beta cho pruning
            is_maximizing (bool): True nếu lượt AI (tìm max), False nếu lượt đối thủ (tìm min)

        Returns:
            int: Điểm đánh giá của trạng thái hiện tại
        """
        # Kiểm tra điều kiện kết thúc
        if game_engine.check_winner(self.symbol):
            return 100000 + depth  # Ưu tiên thắng sớm
        if game_engine.check_winner(self.opponent):
            return -100000 - depth  # Ưu tiên tránh thua muộn
        if board.is_full() or depth == 0:
            return self.evaluate_board(board, game_engine)

        moves = self.get_possible_moves(board)

        if is_maximizing:
            # Lượt AI: tìm nước đi có điểm cao nhất
            best_score = -float('inf')
            for r, c in moves:
                board.place_piece(r, c, self.symbol, is_real=False)
                score = self.minimax(board, game_engine,
                                     depth - 1, alpha, beta, False)
                board.remove_piece(r, c)
                best_score = max(score, best_score)
                alpha = max(alpha, score)
                if beta <= alpha:  # Alpha-Beta pruning
                    break
            return best_score
        else:
            # Lượt đối thủ: tìm nước đi có điểm thấp nhất (tệ nhất cho AI)
            best_score = float('inf')
            for r, c in moves:
                board.place_piece(r, c, self.opponent, is_real=False)
                score = self.minimax(board, game_engine,
                                     depth - 1, alpha, beta, True)
                board.remove_piece(r, c)
                best_score = min(score, best_score)
                beta = min(beta, score)
                if beta <= alpha:  # Alpha-Beta pruning
                    break
            return best_score

    def get_best_move(self, board, game_engine):
        """
        Tìm nước đi tốt nhất cho AI tại trạng thái hiện tại.

        Duyệt tất cả nước đi hợp lệ, dùng minimax để đánh giá từng nước,
        và chọn nước có điểm số cao nhất.

        Args:
            board (Board): Bàn cờ hiện tại
            game_engine (GameEngine): Engine kiểm tra thắng

        Returns:
            tuple or None: Tọa độ (row, col) của nước đi tốt nhất, hoặc None nếu không có nước nào
        """
        best_score = -float('inf')
        best_move = None
        alpha = -float('inf')
        beta = float('inf')

        moves = self.get_possible_moves(board)
        if not moves:
            return None

        for r, c in moves:
            board.place_piece(r, c, self.symbol, is_real=False)
            score = self.minimax(board, game_engine,
                                 self.depth, alpha, beta, False)
            board.remove_piece(r, c)

            if score > best_score:
                best_score = score
                best_move = (r, c)

        return best_move


class GameController:
    """
    Controller điều khiển luồng game chính: lượt chơi, input người dùng, AI, kết thúc game.

    Kết nối các thành phần: Board, GameEngine, BaseAI thành một game hoàn chỉnh.
    """

    def __init__(self, size, win_condition, ai_player):
        """
        Khởi tạo GameController với cấu hình game.

        Args:
            size (int): Kích thước bàn cờ
            win_condition (int): Số quân liên tiếp cần để thắng
            ai_player (BaseAI): Đối tượng AI sẽ điều khiển quân đối thủ
        """
        self.board = Board(size)
        self.engine = GameEngine(self.board, win_condition)
        self.ai = ai_player
        self.human_symbol = "X"

    def play(self):
        """
        Vòng lặp chính của game: hiển thị bàn cờ, nhận input, xử lý lượt, kiểm tra kết thúc.

        Luồng:
        1. In bàn cờ
        2. Nếu lượt người: nhận input từ console, validate, đặt quân
        3. Nếu lượt AI: gọi get_best_move(), đặt quân
        4. Kiểm tra thắng/thua/hòa
        5. Đổi lượt, lặp lại
        """
        current_player = "X"
        while True:
            self.board.print_board()

            if current_player == self.human_symbol:
                # Lượt người chơi
                print(f"Lượt của bạn ({self.human_symbol})!")
                try:
                    row = int(
                        input(f"Nhập hàng (0 đến {self.board.size - 1}): "))
                    col = int(
                        input(f"Nhập cột (0 đến {self.board.size - 1}): "))
                    if not self.board.is_valid_move(row, col):
                        print("Ô này không trống hoặc không hợp lệ, hãy nhập lại!")
                        continue
                    self.board.place_piece(
                        row, col, self.human_symbol, is_real=True)
                except ValueError:
                    print("Vui lòng nhập số nguyên!")
                    continue
                except Exception as e:
                    print(f"Có lỗi xảy ra: {e}")
                    continue
            else:
                # Lượt AI
                print(f"AI ({self.ai.symbol}) đang suy nghĩ...")
                move = self.ai.get_best_move(self.board, self.engine)
                if move:
                    self.board.place_piece(
                        move[0], move[1], self.ai.symbol, is_real=True)

            # Kiểm tra kết thúc game
            if self.engine.check_winner(current_player):
                self.board.print_board()
                if current_player == self.human_symbol:
                    print("Chúc mừng! Bạn đã CHIẾN THẮNG!")
                else:
                    print("Rất tiếc, AI đã thắng!")
                break

            if self.board.is_full():
                self.board.print_board()
                print("Trận đấu HÒA!")
                break

            # Đổi lượt
            current_player = "O" if current_player == "X" else "X"
