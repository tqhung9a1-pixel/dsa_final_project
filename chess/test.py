# """
# TEST LOGIC CỜ VUA
# So sánh game của bạn với python-chess (chuẩn FIDE)
# Chạy: python test_logic.py
# """
# from move import Move
# from game_state import GameState
# import chess
# import random
# import sys
# import os

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# # ==========================================
# # CHUYỂN ĐỔI NƯỚC ĐI
# # ==========================================


# def my_move_to_uci(move):
#     """Chuyển nước đi của game mình sang chuỗi UCI (vd: e2e4)"""
#     start = Move.get_start(move)
#     target = Move.get_target(move)
#     flag = Move.get_flag(move)

#     sf = chr(ord('a') + start % 8) + str(start // 8 + 1)
#     tf = chr(ord('a') + target % 8) + str(target // 8 + 1)

#     promo = {
#         Move.PROMOTION_QUEEN:          'q',
#         Move.PROMOTION_ROOK:           'r',
#         Move.PROMOTION_BISHOP:         'b',
#         Move.PROMOTION_KNIGHT:         'n',
#         Move.PROMOTION_CAPTURE_QUEEN:  'q',
#         Move.PROMOTION_CAPTURE_ROOK:   'r',
#         Move.PROMOTION_CAPTURE_BISHOP: 'b',
#         Move.PROMOTION_CAPTURE_KNIGHT: 'n',
#     }
#     return sf + tf + promo.get(flag, '')


# def get_my_uci_set(gs):
#     """Lấy tập hợp UCI moves từ game của mình"""
#     return set(my_move_to_uci(m) for m in gs.get_legal_moves())


# def get_chess_uci_set(board):
#     """Lấy tập hợp UCI moves từ python-chess"""
#     return set(m.uci() for m in board.legal_moves)


# # ==========================================
# # TEST 1: VỊ TRÍ KHỞI ĐẦU
# # ==========================================
# def test_start_position():
#     print("\n" + "="*50)
#     print("TEST 1: VỊ TRÍ KHỞI ĐẦU")
#     print("="*50)

#     gs = GameState()
#     board = chess.Board()

#     my_mvs = get_my_uci_set(gs)
#     chess_mvs = get_chess_uci_set(board)

#     missing = chess_mvs - my_mvs   # python-chess có nhưng mình thiếu
#     extra = my_mvs - chess_mvs   # mình có nhưng python-chess không có

#     if not missing and not extra:
#         print(f"✅ PASS — {len(my_mvs)} nước đi khớp hoàn toàn!")
#     else:
#         print(f"❌ FAIL — Mình: {len(my_mvs)}, python-chess: {len(chess_mvs)}")
#         if missing:
#             print(f"   Thiếu nước: {sorted(missing)}")
#         if extra:
#             print(f"   Thừa nước:  {sorted(extra)}")
#     return not missing and not extra


# # ==========================================
# # TEST 2: RANDOM GAME (nhiều nước đi)
# # ==========================================
# def test_random_game(num_moves=40, seed=42):
#     print("\n" + "="*50)
#     print(f"TEST 2: RANDOM GAME ({num_moves} nước)")
#     print("="*50)

#     random.seed(seed)
#     gs = GameState()
#     board = chess.Board()
#     move_history = []

#     for i in range(num_moves):
#         my_mvs = get_my_uci_set(gs)
#         chess_mvs = get_chess_uci_set(board)

#         missing = chess_mvs - my_mvs
#         extra = my_mvs - chess_mvs

#         if missing or extra:
#             print(f"❌ FAIL ở nước {i+1}")
#             print(f"   Lịch sử: {' '.join(move_history)}")
#             print(f"   FEN: {board.fen()}")
#             print(f"   Mình: {len(my_mvs)}, python-chess: {len(chess_mvs)}")
#             if missing:
#                 print(f"   Thiếu: {sorted(missing)}")
#             if extra:
#                 print(f"   Thừa:  {sorted(extra)}")
#             return False

#         # Chọn nước đi ngẫu nhiên từ python-chess (chuẩn)
#         chess_move = random.choice(list(board.legal_moves))
#         uci = chess_move.uci()
#         move_history.append(uci)

#         # Tìm nước tương ứng trong game mình
#         my_match = [m for m in gs.get_legal_moves()
#                     if my_move_to_uci(m) == uci]

#         if not my_match:
#             print(f"❌ FAIL — Không tìm thấy nước '{uci}' trong game mình!")
#             print(f"   Lịch sử: {' '.join(move_history)}")
#             return False

#         gs.make_move(my_match[0])
#         board.push(chess_move)

#         # Kiểm tra game over
#         if board.is_game_over():
#             print(f"✅ Game kết thúc ở nước {i+1}: {board.result()}")
#             break

#     print(f"✅ PASS — {len(move_history)} nước đi, không phát hiện lỗi!")
#     return True


# # ==========================================
# # TEST 3: CÁC VỊ TRÍ ĐẶC BIỆT (FEN)
# # ==========================================
# SPECIAL_POSITIONS = {
#     "En Passant trắng": "rnbqkbnr/ppp1p1pp/8/3pPp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 3",
#     "En Passant đen":   "rnbqkbnr/pppp1ppp/8/8/3Pp3/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 2",
#     "Nhập thành trắng": "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1",
#     "Nhập thành đen":   "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R b KQkq - 0 1",
#     "Chiếu hết":        "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3",
#     "Stalemate":        "k7/8/1Q6/8/8/8/8/7K b - - 0 1",
#     "Phong cấp":        "8/P7/8/8/8/8/8/4K1k1 w - - 0 1",
# }


# def fen_to_gamestate(fen):
#     """Tạo GameState từ FEN string"""
#     import chess as ch
#     board = ch.Board(fen)
#     gs = GameState()

#     # Reset tất cả bitboard
#     for key in gs.board.bitboards:
#         gs.board.bitboards[key] = 0

#     # Map từ python-chess sang tên bitboard
#     piece_map = {
#         (ch.PAWN,   ch.WHITE): 'wP', (ch.KNIGHT, ch.WHITE): 'wN',
#         (ch.BISHOP, ch.WHITE): 'wB', (ch.ROOK,   ch.WHITE): 'wR',
#         (ch.QUEEN,  ch.WHITE): 'wQ', (ch.KING,   ch.WHITE): 'wK',
#         (ch.PAWN,   ch.BLACK): 'bP', (ch.KNIGHT, ch.BLACK): 'bN',
#         (ch.BISHOP, ch.BLACK): 'bB', (ch.ROOK,   ch.BLACK): 'bR',
#         (ch.QUEEN,  ch.BLACK): 'bQ', (ch.KING,   ch.BLACK): 'bK',
#     }

#     for sq in range(64):
#         piece = board.piece_at(sq)
#         if piece:
#             key = piece_map[(piece.piece_type, piece.color)]
#             gs.board.bitboards[key] |= (1 << sq)

#     gs.white_to_move = board.turn == ch.WHITE

#     # En passant
#     if board.ep_square is not None:
#         gs.en_passant_square = board.ep_square

#     # Castling rights
#     gs.castling_rights['wK'] = bool(board.castling_rights & ch.BB_H1)
#     gs.castling_rights['wQ'] = bool(board.castling_rights & ch.BB_A1)
#     gs.castling_rights['bK'] = bool(board.castling_rights & ch.BB_H8)
#     gs.castling_rights['bQ'] = bool(board.castling_rights & ch.BB_A8)

#     gs.board.update_occupancies()
#     return gs


# def test_special_positions():
#     print("\n" + "="*50)
#     print("TEST 3: VỊ TRÍ ĐẶC BIỆT")
#     print("="*50)

#     all_pass = True
#     for name, fen in SPECIAL_POSITIONS.items():
#         try:
#             gs = fen_to_gamestate(fen)
#             board = chess.Board(fen)

#             my_mvs = get_my_uci_set(gs)
#             chess_mvs = get_chess_uci_set(board)

#             missing = chess_mvs - my_mvs
#             extra = my_mvs - chess_mvs

#             if not missing and not extra:
#                 print(f"  ✅ {name} — {len(my_mvs)} nước khớp")
#             else:
#                 print(f"  ❌ {name}")
#                 print(
#                     f"     Mình: {len(my_mvs)}, python-chess: {len(chess_mvs)}")
#                 if missing:
#                     print(f"     Thiếu: {sorted(missing)}")
#                 if extra:
#                     print(f"     Thừa:  {sorted(extra)}")
#                 all_pass = False
#         except Exception as ex:
#             print(f"  ⚠️  {name} — Lỗi: {ex}")
#             all_pass = False

#     return all_pass


# # ==========================================
# # TEST 4: NHIỀU RANDOM GAME
# # ==========================================
# def test_multiple_games(num_games=10, moves_per_game=30):
#     print("\n" + "="*50)
#     print(f"TEST 4: {num_games} RANDOM GAMES ({moves_per_game} nước/game)")
#     print("="*50)

#     passed = 0
#     for i in range(num_games):
#         result = test_random_game_silent(moves_per_game, seed=i*17+3)
#         if result:
#             passed += 1
#             print(f"  ✅ Game {i+1:2d} — PASS")
#         else:
#             print(f"  ❌ Game {i+1:2d} — FAIL")

#     print(f"\nKết quả: {passed}/{num_games} games pass")
#     return passed == num_games


# def test_random_game_silent(num_moves, seed):
#     random.seed(seed)
#     gs = GameState()
#     board = chess.Board()

#     for i in range(num_moves):
#         my_mvs = get_my_uci_set(gs)
#         chess_mvs = get_chess_uci_set(board)

#         if my_mvs != chess_mvs:
#             return False

#         if board.is_game_over():
#             break

#         chess_move = random.choice(list(board.legal_moves))
#         uci = chess_move.uci()
#         my_match = [m for m in gs.get_legal_moves()
#                     if my_move_to_uci(m) == uci]

#         if not my_match:
#             return False

#         gs.make_move(my_match[0])
#         board.push(chess_move)

#     return True


# # ==========================================
# # CHẠY TẤT CẢ TEST
# # ==========================================
# if __name__ == '__main__':
#     print("🔍 BẮT ĐẦU KIỂM TRA LOGIC CỜ VUA")
#     print("Dùng python-chess làm chuẩn so sánh\n")

#     results = []
#     results.append(("Vị trí khởi đầu",   test_start_position()))
#     results.append(("Vị trí đặc biệt",   test_special_positions()))
#     results.append(("Random game 40 nước", test_random_game(40)))
#     results.append(("10 random games",    test_multiple_games(10, 30)))

#     print("\n" + "="*50)
#     print("KẾT QUẢ TỔNG HỢP")
#     print("="*50)
#     for name, ok in results:
#         print(f"  {'✅' if ok else '❌'} {name}")

#     total = sum(1 for _, ok in results if ok)
#     print(f"\n{total}/{len(results)} test suites pass")
#     if total == len(results):
#         print("🎉 Logic game hoàn toàn chuẩn!")
#     else:
#         print("⚠️  Còn bug cần sửa!")

"""
TEST LOGIC CỜ VUA
So sánh game của bạn với python-chess (chuẩn FIDE)

Mục đích:
    Kiểm tra tính đúng đắn của engine cờ vua tự xây dựng bằng cách
    so sánh tập nước đi hợp lệ với thư viện python-chess đã được kiểm chứng.

Cách chạy:
    python test_logic.py

Kết quả:
    - ✅ PASS: Logic nước đi khớp hoàn toàn với chuẩn FIDE
    - ❌ FAIL: Phát hiện sai lệch, cần kiểm tra lại implementation
"""
from move import Move
from game_state import GameState
import chess
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ==========================================
# CHUYỂN ĐỔI NƯỚC ĐI
# ==========================================


def my_move_to_uci(move):
    """
    Chuyển đổi nước đi từ định dạng nội bộ sang chuỗi UCI chuẩn.

    Ví dụ: e2e4, e7e8q (phong cấp Hậu), g1f3

    Args:
        move (int): Mã nước đi dạng bitfield của game

    Returns:
        str: Chuỗi UCI (Universal Chess Interface), vd: "e2e4", "e7e8q"
    """
    start = Move.get_start(move)
    target = Move.get_target(move)
    flag = Move.get_flag(move)

    sf = chr(ord('a') + start % 8) + str(start // 8 + 1)
    tf = chr(ord('a') + target % 8) + str(target // 8 + 1)

    promo = {
        Move.PROMOTION_QUEEN:          'q',
        Move.PROMOTION_ROOK:           'r',
        Move.PROMOTION_BISHOP:         'b',
        Move.PROMOTION_KNIGHT:         'n',
        Move.PROMOTION_CAPTURE_QUEEN:  'q',
        Move.PROMOTION_CAPTURE_ROOK:   'r',
        Move.PROMOTION_CAPTURE_BISHOP: 'b',
        Move.PROMOTION_CAPTURE_KNIGHT: 'n',
    }
    return sf + tf + promo.get(flag, '')


def get_my_uci_set(gs):
    """
    Lấy tập hợp tất cả nước đi hợp lệ từ GameState của game mình, định dạng UCI.

    Args:
        gs (GameState): Đối tượng trạng thái game hiện tại

    Returns:
        set[str]: Tập hợp các chuỗi UCI biểu diễn nước đi hợp lệ
    """
    return set(my_move_to_uci(m) for m in gs.get_legal_moves())


def get_chess_uci_set(board):
    """
    Lấy tập hợp tất cả nước đi hợp lệ từ python-chess, định dạng UCI.

    Args:
        board (chess.Board): Đối tượng bàn cờ từ thư viện python-chess

    Returns:
        set[str]: Tập hợp các chuỗi UCI biểu diễn nước đi hợp lệ
    """
    return set(m.uci() for m in board.legal_moves)


# ==========================================
# TEST 1: VỊ TRÍ KHỞI ĐẦU
# ==========================================
def test_start_position():
    """
    Kiểm tra nước đi hợp lệ ở vị trí khởi đầu tiêu chuẩn.

    So sánh tập nước đi từ GameState của game mình với python-chess
    khi cả hai cùng ở bàn cờ bắt đầu (FEN mặc định).

    Returns:
        bool: True nếu khớp hoàn toàn, False nếu có sai lệch
    """
    print("\n" + "="*50)
    print("TEST 1: VỊ TRÍ KHỞI ĐẦU")
    print("="*50)

    gs = GameState()
    board = chess.Board()

    my_mvs = get_my_uci_set(gs)
    chess_mvs = get_chess_uci_set(board)

    missing = chess_mvs - my_mvs   # python-chess có nhưng mình thiếu
    extra = my_mvs - chess_mvs   # mình có nhưng python-chess không có

    if not missing and not extra:
        print(f"✅ PASS — {len(my_mvs)} nước đi khớp hoàn toàn!")
    else:
        print(f"❌ FAIL — Mình: {len(my_mvs)}, python-chess: {len(chess_mvs)}")
        if missing:
            print(f"   Thiếu nước: {sorted(missing)}")
        if extra:
            print(f"   Thừa nước:  {sorted(extra)}")
    return not missing and not extra


# ==========================================
# TEST 2: RANDOM GAME (nhiều nước đi)
# ==========================================
def test_random_game(num_moves=40, seed=42):
    """
    Kiểm tra logic qua một ván cờ ngẫu nhiên với nhiều nước đi liên tiếp.

    Tạo một chuỗi nước đi ngẫu nhiên, sau mỗi nước so sánh tập nước đi
    hợp lệ giữa game mình và python-chess để phát hiện sai lệch.

    Args:
        num_moves (int): Số nước đi tối đa để test (mặc định: 40)
        seed (int): Seed cho random để kết quả tái lập được

    Returns:
        bool: True nếu tất cả nước đi khớp, False nếu phát hiện lỗi
    """
    print("\n" + "="*50)
    print(f"TEST 2: RANDOM GAME ({num_moves} nước)")
    print("="*50)

    random.seed(seed)
    gs = GameState()
    board = chess.Board()
    move_history = []

    for i in range(num_moves):
        my_mvs = get_my_uci_set(gs)
        chess_mvs = get_chess_uci_set(board)

        missing = chess_mvs - my_mvs
        extra = my_mvs - chess_mvs

        if missing or extra:
            print(f"❌ FAIL ở nước {i+1}")
            print(f"   Lịch sử: {' '.join(move_history)}")
            print(f"   FEN: {board.fen()}")
            print(f"   Mình: {len(my_mvs)}, python-chess: {len(chess_mvs)}")
            if missing:
                print(f"   Thiếu: {sorted(missing)}")
            if extra:
                print(f"   Thừa:  {sorted(extra)}")
            return False

        # Chọn nước đi ngẫu nhiên từ python-chess (chuẩn)
        chess_move = random.choice(list(board.legal_moves))
        uci = chess_move.uci()
        move_history.append(uci)

        # Tìm nước tương ứng trong game mình
        my_match = [m for m in gs.get_legal_moves()
                    if my_move_to_uci(m) == uci]

        if not my_match:
            print(f"❌ FAIL — Không tìm thấy nước '{uci}' trong game mình!")
            print(f"   Lịch sử: {' '.join(move_history)}")
            return False

        gs.make_move(my_match[0])
        board.push(chess_move)

        # Kiểm tra game over
        if board.is_game_over():
            print(f"✅ Game kết thúc ở nước {i+1}: {board.result()}")
            break

    print(f"✅ PASS — {len(move_history)} nước đi, không phát hiện lỗi!")
    return True


# ==========================================
# TEST 3: CÁC VỊ TRÍ ĐẶC BIỆT (FEN)
# ==========================================
SPECIAL_POSITIONS = {
    "En Passant trắng": "rnbqkbnr/ppp1p1pp/8/3pPp2/8/8/PPPP1PPP/RNBQKBNR w KQkq f6 0 3",
    "En Passant đen":   "rnbqkbnr/pppp1ppp/8/8/3Pp3/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 2",
    "Nhập thành trắng": "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1",
    "Nhập thành đen":   "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R b KQkq - 0 1",
    "Chiếu hết":        "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3",
    "Stalemate":        "k7/8/1Q6/8/8/8/8/7K b - - 0 1",
    "Phong cấp":        "8/P7/8/8/8/8/8/4K1k1 w - - 0 1",
}


def fen_to_gamestate(fen):
    """
    Tạo đối tượng GameState từ chuỗi FEN.

    Chuyển đổi vị trí bàn cờ mô tả bằng FEN sang định dạng bitboard
    nội bộ của game, bao gồm: vị trí quân, lượt đi, en passant, castling rights.

    Args:
        fen (str): Chuỗi FEN mô tả vị trí bàn cờ

    Returns:
        GameState: Đối tượng trạng thái game đã được khởi tạo từ FEN
    """
    import chess as ch
    board = ch.Board(fen)
    gs = GameState()

    # Reset tất cả bitboard
    for key in gs.board.bitboards:
        gs.board.bitboards[key] = 0

    # Map từ python-chess sang tên bitboard
    piece_map = {
        (ch.PAWN,   ch.WHITE): 'wP', (ch.KNIGHT, ch.WHITE): 'wN',
        (ch.BISHOP, ch.WHITE): 'wB', (ch.ROOK,   ch.WHITE): 'wR',
        (ch.QUEEN,  ch.WHITE): 'wQ', (ch.KING,   ch.WHITE): 'wK',
        (ch.PAWN,   ch.BLACK): 'bP', (ch.KNIGHT, ch.BLACK): 'bN',
        (ch.BISHOP, ch.BLACK): 'bB', (ch.ROOK,   ch.BLACK): 'bR',
        (ch.QUEEN,  ch.BLACK): 'bQ', (ch.KING,   ch.BLACK): 'bK',
    }

    for sq in range(64):
        piece = board.piece_at(sq)
        if piece:
            key = piece_map[(piece.piece_type, piece.color)]
            gs.board.bitboards[key] |= (1 << sq)

    gs.white_to_move = board.turn == ch.WHITE

    # En passant
    if board.ep_square is not None:
        gs.en_passant_square = board.ep_square

    # Castling rights
    gs.castling_rights['wK'] = bool(board.castling_rights & ch.BB_H1)
    gs.castling_rights['wQ'] = bool(board.castling_rights & ch.BB_A1)
    gs.castling_rights['bK'] = bool(board.castling_rights & ch.BB_H8)
    gs.castling_rights['bQ'] = bool(board.castling_rights & ch.BB_A8)

    gs.board.update_occupancies()
    return gs


def test_special_positions():
    """
    Kiểm tra logic với các vị trí cờ đặc biệt: en passant, nhập thành, chiếu hết, stalemate, phong cấp.

    Duyệt qua danh sách FEN đặc biệt, tạo GameState tương ứng và so sánh
    tập nước đi hợp lệ với python-chess.

    Returns:
        bool: True nếu tất cả vị trí đặc biệt pass, False nếu có vị trí fail
    """
    print("\n" + "="*50)
    print("TEST 3: VỊ TRÍ ĐẶC BIỆT")
    print("="*50)

    all_pass = True
    for name, fen in SPECIAL_POSITIONS.items():
        try:
            gs = fen_to_gamestate(fen)
            board = chess.Board(fen)

            my_mvs = get_my_uci_set(gs)
            chess_mvs = get_chess_uci_set(board)

            missing = chess_mvs - my_mvs
            extra = my_mvs - chess_mvs

            if not missing and not extra:
                print(f"  ✅ {name} — {len(my_mvs)} nước khớp")
            else:
                print(f"  ❌ {name}")
                print(
                    f"     Mình: {len(my_mvs)}, python-chess: {len(chess_mvs)}")
                if missing:
                    print(f"     Thiếu: {sorted(missing)}")
                if extra:
                    print(f"     Thừa:  {sorted(extra)}")
                all_pass = False
        except Exception as ex:
            print(f"  ⚠️  {name} — Lỗi: {ex}")
            all_pass = False

    return all_pass


# ==========================================
# TEST 4: NHIỀU RANDOM GAME
# ==========================================
def test_multiple_games(num_games=10, moves_per_game=30):
    """
    Chạy kiểm tra trên nhiều ván cờ ngẫu nhiên để tăng độ tin cậy.

    Thực hiện test_random_game nhiều lần với seed khác nhau,
    thống kê số ván pass/fail để đánh giá độ ổn định của logic.

    Args:
        num_games (int): Số ván game để test (mặc định: 10)
        moves_per_game (int): Số nước đi tối đa mỗi ván (mặc định: 30)

    Returns:
        bool: True nếu tất cả games pass, False nếu có game fail
    """
    print("\n" + "="*50)
    print(f"TEST 4: {num_games} RANDOM GAMES ({moves_per_game} nước/game)")
    print("="*50)

    passed = 0
    for i in range(num_games):
        result = test_random_game_silent(moves_per_game, seed=i*17+3)
        if result:
            passed += 1
            print(f"  ✅ Game {i+1:2d} — PASS")
        else:
            print(f"  ❌ Game {i+1:2d} — FAIL")

    print(f"\nKết quả: {passed}/{num_games} games pass")
    return passed == num_games


def test_random_game_silent(num_moves, seed):
    """
    Phiên bản silent của test_random_game, không in log, dùng cho batch testing.

    Args:
        num_moves (int): Số nước đi tối đa để test
        seed (int): Seed cho random

    Returns:
        bool: True nếu tất cả nước đi khớp, False nếu có sai lệch
    """
    random.seed(seed)
    gs = GameState()
    board = chess.Board()

    for i in range(num_moves):
        my_mvs = get_my_uci_set(gs)
        chess_mvs = get_chess_uci_set(board)

        if my_mvs != chess_mvs:
            return False

        if board.is_game_over():
            break

        chess_move = random.choice(list(board.legal_moves))
        uci = chess_move.uci()
        my_match = [m for m in gs.get_legal_moves()
                    if my_move_to_uci(m) == uci]

        if not my_match:
            return False

        gs.make_move(my_match[0])
        board.push(chess_move)

    return True


# ==========================================
# CHẠY TẤT CẢ TEST
# ==========================================
if __name__ == '__main__':
    print("🔍 BẮT ĐẦU KIỂM TRA LOGIC CỜ VUA")
    print("Dùng python-chess làm chuẩn so sánh\n")

    results = []
    results.append(("Vị trí khởi đầu",   test_start_position()))
    results.append(("Vị trí đặc biệt",   test_special_positions()))
    results.append(("Random game 40 nước", test_random_game(40)))
    results.append(("10 random games",    test_multiple_games(10, 30)))

    print("\n" + "="*50)
    print("KẾT QUẢ TỔNG HỢP")
    print("="*50)
    for name, ok in results:
        print(f"  {'✅' if ok else '❌'} {name}")

    total = sum(1 for _, ok in results if ok)
    print(f"\n{total}/{len(results)} test suites pass")
    if total == len(results):
        print("🎉 Logic game hoàn toàn chuẩn!")
    else:
        print("⚠️  Còn bug cần sửa!")
