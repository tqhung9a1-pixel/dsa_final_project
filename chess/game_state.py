# from bitboard import Board, Zobrist, get_piece_idx
# from move import Move
# from move_generator import MoveGenerator, NOT_A_FILE, NOT_H_FILE
# from evaluation import PIECE_VALUES


# class GameState:
#     def __init__(self):
#         self.board = Board()
#         self.white_to_move = True
#         self.move_log = []
#         self.en_passant_square = None
#         self.en_passant_log = []
#         self.castling_rights = {
#             'wK': True,
#             'wQ': True,
#             'bK': True,
#             'bQ': True
#         }
#         self.castling_rights_log = []
#         self.fifty_move_counter = 0
#         self.fifty_move_log = []
#         self.points = {'w': 0, 'b': 0}
#         self.zobrist_hash = self.init_zobrist()
#         self.captured_piece_log = []
#         self.points_log = []

#     def load_custom_position(self, bitboards_dict, white_to_move=True):
#         """
#         Load một vị trí tùy chỉnh từ Board Editor.
#         bitboards_dict: {"wK": int, "wQ": int, ..., "bK": int, ...}
#         """
#         from bitboard import get_piece_idx, Zobrist

#         for key in self.board.bitboards:
#             self.board.bitboards[key] = bitboards_dict.get(key, 0)
#         self.board.update_occupancies()

#         self.white_to_move = white_to_move
#         self.move_log = []
#         self.en_passant_square = None
#         self.en_passant_log = []
#         self.castling_rights = {"wK": False, "wQ": False,
#                                 "bK": False, "bQ": False}
#         if self.board.bitboards["wK"] & (1 << 4):   # e1
#             if self.board.bitboards["wR"] & (1 << 7):
#                 self.castling_rights["wK"] = True
#             if self.board.bitboards["wR"] & (1 << 0):
#                 self.castling_rights["wQ"] = True
#         if self.board.bitboards["bK"] & (1 << 60):  # e8
#             if self.board.bitboards["bR"] & (1 << 63):
#                 self.castling_rights["bK"] = True
#             if self.board.bitboards["bR"] & (1 << 56):
#                 self.castling_rights["bQ"] = True

#         self.castling_rights_log = []
#         self.fifty_move_counter = 0
#         self.fifty_move_log = []
#         self.captured_piece_log = []
#         self.points_log = []
#         self.points = {"w": 0, "b": 0}
#         self.zobrist_hash = self.init_zobrist()

#     def init_zobrist(self):
#         """Tính toán hash từ đầu cho trạng thái khởi tạo"""
#         h = 0
#         for piece, bb in self.board.bitboards.items():
#             p_idx = get_piece_idx(piece)
#             temp_bb = bb
#             while temp_bb:
#                 sq = (temp_bb & -temp_bb).bit_length() - 1
#                 h ^= Zobrist.table[p_idx][sq]
#                 temp_bb &= temp_bb - 1

#         if not self.white_to_move:
#             h ^= Zobrist.side_to_move

#         castle_idx = self._get_castle_index()
#         h ^= Zobrist.castling[castle_idx]

#         if self.en_passant_square:
#             h ^= Zobrist.en_passant[self.en_passant_square % 8]
#         return h

#     def _get_castle_index(self):
#         idx = 0
#         if self.castling_rights['wK']:
#             idx |= 1
#         if self.castling_rights['wQ']:
#             idx |= 2
#         if self.castling_rights['bK']:
#             idx |= 4
#         if self.castling_rights['bQ']:
#             idx |= 8
#         return idx

#     def is_in_check(self):
#         by_white = not self.white_to_move
#         prefix = 'w' if self.white_to_move else 'b'
#         for piece_name, bitboard in self.board.bitboards.items():
#             if not piece_name.startswith(prefix):
#                 continue
#             else:
#                 if piece_name[1] == "K":
#                     for square in range(64):
#                         if bitboard & (1 << square):
#                             return MoveGenerator.is_square_attacked(square, by_white, self.board.bitboards, self.board.all_pieces)

#     def get_legal_moves(self):
#         moves = []
#         color = "White" if self.white_to_move else "Black"
#         prefix = 'w' if self.white_to_move else "b"
#         own_pieces = self.board.white_pieces if self.white_to_move else self.board.black_pieces
#         enemy_pieces = self.board.black_pieces if self.white_to_move else self.board.white_pieces

#         for piece_name, bitboard in self.board.bitboards.items():
#             if not piece_name.startswith(prefix):
#                 continue
#             for square in range(64):
#                 if not (bitboard & (1 << square)):
#                     continue
#                 piece_type = piece_name[1]
#                 raw_moves = 0
#                 if piece_type == 'P':
#                     raw_moves = MoveGenerator.get_pawn_moves(
#                         square, color, self.board.all_pieces, enemy_pieces)
#                 elif piece_type == 'N':
#                     raw_moves = MoveGenerator.get_knight_moves(square)
#                 elif piece_type == 'B':
#                     raw_moves = MoveGenerator.get_bishop_moves(
#                         square, self.board.all_pieces)
#                 elif piece_type == 'R':
#                     raw_moves = MoveGenerator.get_rook_moves(
#                         square, self.board.all_pieces)
#                 elif piece_type == 'Q':
#                     raw_moves = MoveGenerator.get_queen_moves(
#                         square, self.board.all_pieces)
#                 elif piece_type == 'K':
#                     raw_moves = MoveGenerator.get_king_moves(square)

#                 raw_moves &= ~own_pieces
#                 for target in range(64):
#                     if not (raw_moves & (1 << target)):
#                         continue

#                     is_capture = bool(enemy_pieces & (1 << target))
#                     is_promotion = (piece_type == 'P') and (
#                         (color == "White" and target >= 56) or
#                         (color == "Black" and target <= 7)
#                     )

#                     if is_promotion:
#                         if is_capture:
#                             promotion_flags = [
#                                 Move.PROMOTION_CAPTURE_QUEEN, Move.PROMOTION_CAPTURE_ROOK,
#                                 Move.PROMOTION_CAPTURE_BISHOP, Move.PROMOTION_CAPTURE_KNIGHT
#                             ]
#                         else:
#                             promotion_flags = [
#                                 Move.PROMOTION_QUEEN, Move.PROMOTION_ROOK,
#                                 Move.PROMOTION_BISHOP, Move.PROMOTION_KNIGHT
#                             ]
#                         for flag in promotion_flags:
#                             candidate = Move.encode(square, target, flag)
#                             self.make_move(candidate)
#                             self.white_to_move = not self.white_to_move
#                             in_check = self.is_in_check()
#                             self.white_to_move = not self.white_to_move
#                             self.unmake_move()
#                             if not in_check:
#                                 moves.append(candidate)
#                     else:
#                         if is_capture:
#                             flag = Move.CAPTURE
#                         elif piece_type == 'P' and abs(target - square) == 16:
#                             flag = Move.DOUBLE_PAWN_PUSH
#                         else:
#                             flag = Move.NORMAL
#                         candidate = Move.encode(square, target, flag)
#                         self.make_move(candidate)
#                         self.white_to_move = not self.white_to_move
#                         in_check = self.is_in_check()
#                         self.white_to_move = not self.white_to_move
#                         self.unmake_move()
#                         if not in_check:
#                             moves.append(candidate)

#         if self.en_passant_square is not None:
#             ep_sq = self.en_passant_square
#             ep_bit = 1 << ep_sq
#             pawn_key = 'wP' if self.white_to_move else 'bP'
#             pawn_bb = self.board.bitboards[pawn_key]

#             if self.white_to_move:
#                 attackers = ((ep_bit >> 7) & NOT_A_FILE) | (
#                     (ep_bit >> 9) & NOT_H_FILE)
#             else:
#                 attackers = ((ep_bit << 7) & NOT_H_FILE) | (
#                     (ep_bit << 9) & NOT_A_FILE)

#             attackers &= pawn_bb

#             for sq in range(64):
#                 if attackers & (1 << sq):
#                     candidate = Move.encode(sq, ep_sq, Move.EN_PASSANT)
#                     self.make_move(candidate)
#                     self.white_to_move = not self.white_to_move
#                     in_check = self.is_in_check()
#                     self.white_to_move = not self.white_to_move
#                     self.unmake_move()
#                     if not in_check:
#                         moves.append(candidate)

#         by_enemy = not self.white_to_move

#         if self.white_to_move:
#             if self.castling_rights['wK']:
#                 if not (self.board.all_pieces & ((1 << 5) | (1 << 6))):
#                     if not MoveGenerator.is_square_attacked(4, by_enemy, self.board.bitboards, self.board.all_pieces) and \
#                             not MoveGenerator.is_square_attacked(5, by_enemy, self.board.bitboards, self.board.all_pieces) and \
#                             not MoveGenerator.is_square_attacked(6, by_enemy, self.board.bitboards, self.board.all_pieces):
#                         moves.append(Move.encode(4, 6, Move.CASTLING))

#             if self.castling_rights['wQ']:
#                 if not (self.board.all_pieces & ((1 << 1) | (1 << 2) | (1 << 3))):
#                     if not MoveGenerator.is_square_attacked(4, by_enemy, self.board.bitboards, self.board.all_pieces) and \
#                             not MoveGenerator.is_square_attacked(3, by_enemy, self.board.bitboards, self.board.all_pieces) and \
#                             not MoveGenerator.is_square_attacked(2, by_enemy, self.board.bitboards, self.board.all_pieces):
#                         moves.append(Move.encode(4, 2, Move.CASTLING))
#         else:
#             if self.castling_rights['bK']:
#                 if not (self.board.all_pieces & ((1 << 61) | (1 << 62))):
#                     if not MoveGenerator.is_square_attacked(60, by_enemy, self.board.bitboards, self.board.all_pieces) and \
#                             not MoveGenerator.is_square_attacked(61, by_enemy, self.board.bitboards, self.board.all_pieces) and \
#                             not MoveGenerator.is_square_attacked(62, by_enemy, self.board.bitboards, self.board.all_pieces):
#                         moves.append(Move.encode(60, 62, Move.CASTLING))

#             if self.castling_rights['bQ']:
#                 if not (self.board.all_pieces & ((1 << 57) | (1 << 58) | (1 << 59))):
#                     if not MoveGenerator.is_square_attacked(60, by_enemy, self.board.bitboards, self.board.all_pieces) and \
#                             not MoveGenerator.is_square_attacked(59, by_enemy, self.board.bitboards, self.board.all_pieces) and \
#                             not MoveGenerator.is_square_attacked(58, by_enemy, self.board.bitboards, self.board.all_pieces):
#                         moves.append(Move.encode(60, 58, Move.CASTLING))
#         return moves

#     def make_move(self, move):
#         new_piece = None
#         start = Move.get_start(move)
#         target = Move.get_target(move)
#         flag = Move.get_flag(move)

#         promotion_flags = [
#             Move.PROMOTION_QUEEN, Move.PROMOTION_ROOK,
#             Move.PROMOTION_BISHOP, Move.PROMOTION_KNIGHT,
#             Move.PROMOTION_CAPTURE_QUEEN, Move.PROMOTION_CAPTURE_ROOK,
#             Move.PROMOTION_CAPTURE_BISHOP, Move.PROMOTION_CAPTURE_KNIGHT
#         ]

#         piece_moved = None
#         for piece_name, bitboard in self.board.bitboards.items():
#             if bitboard & (1 << start):
#                 piece_moved = piece_name
#                 break

#         piece_captured = None
#         capture_flags = [Move.CAPTURE, Move.PROMOTION_CAPTURE_QUEEN,
#                          Move.PROMOTION_CAPTURE_ROOK, Move.PROMOTION_CAPTURE_BISHOP,
#                          Move.PROMOTION_CAPTURE_KNIGHT]

#         if flag in capture_flags:
#             for piece_name, bitboard in self.board.bitboards.items():
#                 if bitboard & (1 << target):
#                     piece_captured = piece_name
#                     break
#         elif flag == Move.EN_PASSANT:
#             piece_captured = 'bP' if self.white_to_move else 'wP'

#         self.zobrist_hash ^= Zobrist.castling[self._get_castle_index()]
#         if self.en_passant_square is not None:
#             self.zobrist_hash ^= Zobrist.en_passant[self.en_passant_square % 8]

#         self.en_passant_log.append(self.en_passant_square)
#         self.en_passant_square = None

#         self.castling_rights_log.append(self.castling_rights.copy())
#         self.fifty_move_log.append(self.fifty_move_counter)
#         self.points_log.append(self.points.copy())  # LƯU ĐIỂM ĐỂ UNMAKE

#         if piece_moved == 'wK':
#             self.castling_rights['wK'] = False
#             self.castling_rights['wQ'] = False
#         elif piece_moved == 'bK':
#             self.castling_rights['bK'] = False
#             self.castling_rights['bQ'] = False
#         elif piece_moved == 'wR':
#             if start == 0:
#                 self.castling_rights['wQ'] = False
#             elif start == 7:
#                 self.castling_rights['wK'] = False
#         elif piece_moved == 'bR':
#             if start == 56:
#                 self.castling_rights['bQ'] = False
#             elif start == 63:
#                 self.castling_rights['bK'] = False

#         if piece_captured == 'wR':
#             if target == 0:
#                 self.castling_rights['wQ'] = False
#             elif target == 7:
#                 self.castling_rights['wK'] = False
#         elif piece_captured == 'bR':
#             if target == 56:
#                 self.castling_rights['bQ'] = False
#             elif target == 63:
#                 self.castling_rights['bK'] = False

#         if piece_moved[1] == 'P' or piece_captured is not None:
#             self.fifty_move_counter = 0
#         else:
#             self.fifty_move_counter += 1

#         if flag == Move.DOUBLE_PAWN_PUSH:
#             if self.white_to_move:
#                 self.en_passant_square = target - 8
#             else:
#                 self.en_passant_square = target + 8

#         self.zobrist_hash ^= Zobrist.castling[self._get_castle_index()]
#         if self.en_passant_square is not None:
#             self.zobrist_hash ^= Zobrist.en_passant[self.en_passant_square % 8]

#         if piece_captured is not None:
#             cap_sq = target
#             if flag == Move.EN_PASSANT:
#                 cap_sq = target - 8 if self.white_to_move else target + 8
#                 self.board.bitboards[piece_captured] &= ~(
#                     1 << cap_sq)  # Cập nhật Bitboard cho EP
#             else:
#                 self.board.bitboards[piece_captured] &= ~(
#                     1 << target)  # Cập nhật Bitboard thường

#             self.zobrist_hash ^= Zobrist.table[get_piece_idx(
#                 piece_captured)][cap_sq]

#             reward = PIECE_VALUES[piece_captured[1]] // 10
#             if self.white_to_move:
#                 self.points['w'] += reward
#             else:
#                 self.points['b'] += reward

#         self.board.bitboards[piece_moved] &= ~(1 << start)
#         self.zobrist_hash ^= Zobrist.table[get_piece_idx(piece_moved)][start]

#         final_piece = piece_moved
#         if flag in promotion_flags:
#             color_prefix = piece_moved[0]
#             if flag in (Move.PROMOTION_QUEEN, Move.PROMOTION_CAPTURE_QUEEN):
#                 new_piece = color_prefix + 'Q'
#             elif flag in (Move.PROMOTION_ROOK, Move.PROMOTION_CAPTURE_ROOK):
#                 new_piece = color_prefix + 'R'
#             elif flag in (Move.PROMOTION_BISHOP, Move.PROMOTION_CAPTURE_BISHOP):
#                 new_piece = color_prefix + 'B'
#             elif flag in (Move.PROMOTION_KNIGHT, Move.PROMOTION_CAPTURE_KNIGHT):
#                 new_piece = color_prefix + 'N'
#             final_piece = new_piece

#         self.board.bitboards[final_piece] |= (1 << target)
#         self.zobrist_hash ^= Zobrist.table[get_piece_idx(final_piece)][target]

#         if flag == Move.CASTLING:
#             if target == 6:
#                 self.board.bitboards['wR'] &= ~(1 << 7)
#                 self.board.bitboards['wR'] |= (1 << 5)
#                 self.zobrist_hash ^= Zobrist.table[get_piece_idx(
#                     'wR')][7] ^ Zobrist.table[get_piece_idx('wR')][5]
#             elif target == 2:
#                 self.board.bitboards['wR'] &= ~(1 << 0)
#                 self.board.bitboards['wR'] |= (1 << 3)
#                 self.zobrist_hash ^= Zobrist.table[get_piece_idx(
#                     'wR')][0] ^ Zobrist.table[get_piece_idx('wR')][3]
#             elif target == 62:
#                 self.board.bitboards['bR'] &= ~(1 << 63)
#                 self.board.bitboards['bR'] |= (1 << 61)
#                 self.zobrist_hash ^= Zobrist.table[get_piece_idx(
#                     'bR')][63] ^ Zobrist.table[get_piece_idx('bR')][61]
#             elif target == 58:
#                 self.board.bitboards['bR'] &= ~(1 << 56)
#                 self.board.bitboards['bR'] |= (1 << 59)
#                 self.zobrist_hash ^= Zobrist.table[get_piece_idx(
#                     'bR')][56] ^ Zobrist.table[get_piece_idx('bR')][59]

#         history_record = {
#             'move': move,
#             'piece_moved': piece_moved,
#             'piece_captured': piece_captured,
#             'promoted_to': new_piece if flag in promotion_flags else None
#         }
#         self.move_log.append(history_record)

#         self.zobrist_hash ^= Zobrist.side_to_move
#         self.white_to_move = not self.white_to_move
#         self.board.update_occupancies()

#     def unmake_move(self):
#         if not self.move_log:
#             return

#         record = self.move_log.pop()
#         move = record['move']
#         piece_moved = record['piece_moved']
#         piece_captured = record['piece_captured']
#         promoted_to = record['promoted_to']

#         start = Move.get_start(move)
#         target = Move.get_target(move)
#         flag = Move.get_flag(move)

#         self.zobrist_hash ^= Zobrist.castling[self._get_castle_index()]
#         if self.en_passant_square is not None:
#             self.zobrist_hash ^= Zobrist.en_passant[self.en_passant_square % 8]

#         self.en_passant_square = self.en_passant_log.pop()
#         self.castling_rights = self.castling_rights_log.pop()
#         self.fifty_move_counter = self.fifty_move_log.pop()
#         self.points = self.points_log.pop()

#         self.white_to_move = not self.white_to_move
#         self.zobrist_hash ^= Zobrist.side_to_move

#         self.zobrist_hash ^= Zobrist.castling[self._get_castle_index()]
#         if self.en_passant_square is not None:
#             self.zobrist_hash ^= Zobrist.en_passant[self.en_passant_square % 8]

#         final_piece = promoted_to if promoted_to else piece_moved

#         self.board.bitboards[final_piece] &= ~(1 << target)
#         self.zobrist_hash ^= Zobrist.table[get_piece_idx(final_piece)][target]

#         self.board.bitboards[piece_moved] |= (1 << start)
#         self.zobrist_hash ^= Zobrist.table[get_piece_idx(piece_moved)][start]

#         if piece_captured is not None:
#             cap_sq = target
#             if flag == Move.EN_PASSANT:
#                 cap_sq = target - 8 if self.white_to_move else target + 8
#             self.board.bitboards[piece_captured] |= (1 << cap_sq)
#             self.zobrist_hash ^= Zobrist.table[get_piece_idx(
#                 piece_captured)][cap_sq]

#         if flag == Move.CASTLING:
#             if target == 6:
#                 self.board.bitboards['wR'] &= ~(1 << 5)
#                 self.board.bitboards['wR'] |= (1 << 7)
#                 self.zobrist_hash ^= Zobrist.table[get_piece_idx(
#                     'wR')][5] ^ Zobrist.table[get_piece_idx('wR')][7]
#             elif target == 2:
#                 self.board.bitboards['wR'] &= ~(1 << 3)
#                 self.board.bitboards['wR'] |= (1 << 0)
#                 self.zobrist_hash ^= Zobrist.table[get_piece_idx(
#                     'wR')][3] ^ Zobrist.table[get_piece_idx('wR')][0]
#             elif target == 62:
#                 self.board.bitboards['bR'] &= ~(1 << 61)
#                 self.board.bitboards['bR'] |= (1 << 63)
#                 self.zobrist_hash ^= Zobrist.table[get_piece_idx(
#                     'bR')][61] ^ Zobrist.table[get_piece_idx('bR')][63]
#             elif target == 58:
#                 self.board.bitboards['bR'] &= ~(1 << 59)
#                 self.board.bitboards['bR'] |= (1 << 56)
#                 self.zobrist_hash ^= Zobrist.table[get_piece_idx(
#                     'bR')][59] ^ Zobrist.table[get_piece_idx('bR')][56]

#         self.board.update_occupancies()

#     def get_game_status(self):
#         if self.fifty_move_counter >= 100:
#             return "Draw-50Move"

#         legal_moves = self.get_legal_moves()

#         if len(legal_moves) == 0:
#             if self.is_in_check():
#                 if self.white_to_move:
#                     return "Checkmate-BlackWins"
#                 else:
#                     return "Checkmate-WhiteWins"
#             else:
#                 return "Stalemate"

#         return "Ongoing"

from bitboard import Board, Zobrist, get_piece_idx
from move import Move
from move_generator import MoveGenerator, NOT_A_FILE, NOT_H_FILE
from evaluation import PIECE_VALUES


class GameState:
    """Quản lý trạng thái toàn bộ của ván cờ: bàn cờ, lượt đi, lịch sử nước đi,
    quyền nhập thành, ô ăn tốt qua đường, bộ đếm 50 nước đi, hash Zobrist và điểm số."""

    def __init__(self):
        """Khởi tạo trạng thái ván cờ với vị trí ban đầu và các giá trị mặc định."""
        self.board = Board()
        self.white_to_move = True
        self.move_log = []
        self.en_passant_square = None
        self.en_passant_log = []
        self.castling_rights = {
            'wK': True,
            'wQ': True,
            'bK': True,
            'bQ': True
        }
        self.castling_rights_log = []
        self.fifty_move_counter = 0
        self.fifty_move_log = []
        self.points = {'w': 0, 'b': 0}
        self.zobrist_hash = self.init_zobrist()
        self.captured_piece_log = []
        self.points_log = []

    def load_custom_position(self, bitboards_dict, white_to_move=True):
        """
        Tải một vị trí tùy chỉnh từ Board Editor vào trạng thái hiện tại.

        Args:
            bitboards_dict (dict): Dictionary chứa bitboard cho từng loại quân,
                ví dụ: {"wK": int, "wQ": int, ..., "bK": int, ...}
            white_to_move (bool): Xác định bên nào được đi tiếp (True = Trắng).
        """
        from bitboard import get_piece_idx, Zobrist

        for key in self.board.bitboards:
            self.board.bitboards[key] = bitboards_dict.get(key, 0)
        self.board.update_occupancies()

        self.white_to_move = white_to_move
        self.move_log = []
        self.en_passant_square = None
        self.en_passant_log = []
        self.castling_rights = {"wK": False, "wQ": False,
                                "bK": False, "bQ": False}
        if self.board.bitboards["wK"] & (1 << 4):
            if self.board.bitboards["wR"] & (1 << 7):
                self.castling_rights["wK"] = True
            if self.board.bitboards["wR"] & (1 << 0):
                self.castling_rights["wQ"] = True
        if self.board.bitboards["bK"] & (1 << 60):
            if self.board.bitboards["bR"] & (1 << 63):
                self.castling_rights["bK"] = True
            if self.board.bitboards["bR"] & (1 << 56):
                self.castling_rights["bQ"] = True

        self.castling_rights_log = []
        self.fifty_move_counter = 0
        self.fifty_move_log = []
        self.captured_piece_log = []
        self.points_log = []
        self.points = {"w": 0, "b": 0}
        self.zobrist_hash = self.init_zobrist()

    def init_zobrist(self):
        """
        Tính toán giá trị hash Zobrist từ đầu cho trạng thái hiện tại.

        Returns:
            int: Giá trị hash duy nhất đại diện cho trạng thái bàn cờ,
                lượt đi, quyền nhập thành và ô ăn tốt qua đường.
        """
        h = 0
        for piece, bb in self.board.bitboards.items():
            p_idx = get_piece_idx(piece)
            temp_bb = bb
            while temp_bb:
                sq = (temp_bb & -temp_bb).bit_length() - 1
                h ^= Zobrist.table[p_idx][sq]
                temp_bb &= temp_bb - 1

        if not self.white_to_move:
            h ^= Zobrist.side_to_move

        castle_idx = self._get_castle_index()
        h ^= Zobrist.castling[castle_idx]

        if self.en_passant_square:
            h ^= Zobrist.en_passant[self.en_passant_square % 8]
        return h

    def _get_castle_index(self):
        """
        Chuyển đổi quyền nhập thành thành chỉ số 0-15 dùng cho bảng Zobrist.

        Returns:
            int: Chỉ số biểu diễn tổ hợp quyền nhập thành hiện tại.
        """
        idx = 0
        if self.castling_rights['wK']:
            idx |= 1
        if self.castling_rights['wQ']:
            idx |= 2
        if self.castling_rights['bK']:
            idx |= 4
        if self.castling_rights['bQ']:
            idx |= 8
        return idx

    def is_in_check(self):
        """
        Kiểm tra xem Vua của bên đang đến lượt có đang bị chiếu hay không.

        Returns:
            bool: True nếu Vua đang bị chiếu, False nếu không.
        """
        by_white = not self.white_to_move
        prefix = 'w' if self.white_to_move else 'b'
        for piece_name, bitboard in self.board.bitboards.items():
            if not piece_name.startswith(prefix):
                continue
            if piece_name[1] == "K":
                for square in range(64):
                    if bitboard & (1 << square):
                        return MoveGenerator.is_square_attacked(
                            square, by_white, self.board.bitboards, self.board.all_pieces)

    def get_legal_moves(self):
        """
        Sinh danh sách tất cả nước đi hợp lệ cho bên đang đến lượt,
        bao gồm: di chuyển thường, ăn quân, phong cấp, ăn tốt qua đường và nhập thành.
        Loại bỏ các nước đi khiến Vua của bên mình bị chiếu.

        Returns:
            list[int]: Danh sách các nước đi đã mã hóa (dạng integer).
        """
        moves = []
        color = "White" if self.white_to_move else "Black"
        prefix = 'w' if self.white_to_move else "b"
        own_pieces = self.board.white_pieces if self.white_to_move else self.board.black_pieces
        enemy_pieces = self.board.black_pieces if self.white_to_move else self.board.white_pieces

        for piece_name, bitboard in self.board.bitboards.items():
            if not piece_name.startswith(prefix):
                continue
            for square in range(64):
                if not (bitboard & (1 << square)):
                    continue
                piece_type = piece_name[1]
                raw_moves = 0
                if piece_type == 'P':
                    raw_moves = MoveGenerator.get_pawn_moves(
                        square, color, self.board.all_pieces, enemy_pieces)
                elif piece_type == 'N':
                    raw_moves = MoveGenerator.get_knight_moves(square)
                elif piece_type == 'B':
                    raw_moves = MoveGenerator.get_bishop_moves(
                        square, self.board.all_pieces)
                elif piece_type == 'R':
                    raw_moves = MoveGenerator.get_rook_moves(
                        square, self.board.all_pieces)
                elif piece_type == 'Q':
                    raw_moves = MoveGenerator.get_queen_moves(
                        square, self.board.all_pieces)
                elif piece_type == 'K':
                    raw_moves = MoveGenerator.get_king_moves(square)

                raw_moves &= ~own_pieces
                for target in range(64):
                    if not (raw_moves & (1 << target)):
                        continue

                    is_capture = bool(enemy_pieces & (1 << target))
                    is_promotion = (piece_type == 'P') and (
                        (color == "White" and target >= 56) or
                        (color == "Black" and target <= 7)
                    )

                    if is_promotion:
                        if is_capture:
                            promotion_flags = [
                                Move.PROMOTION_CAPTURE_QUEEN, Move.PROMOTION_CAPTURE_ROOK,
                                Move.PROMOTION_CAPTURE_BISHOP, Move.PROMOTION_CAPTURE_KNIGHT
                            ]
                        else:
                            promotion_flags = [
                                Move.PROMOTION_QUEEN, Move.PROMOTION_ROOK,
                                Move.PROMOTION_BISHOP, Move.PROMOTION_KNIGHT
                            ]
                        for flag in promotion_flags:
                            candidate = Move.encode(square, target, flag)
                            self.make_move(candidate)
                            self.white_to_move = not self.white_to_move
                            in_check = self.is_in_check()
                            self.white_to_move = not self.white_to_move
                            self.unmake_move()
                            if not in_check:
                                moves.append(candidate)
                    else:
                        if is_capture:
                            flag = Move.CAPTURE
                        elif piece_type == 'P' and abs(target - square) == 16:
                            flag = Move.DOUBLE_PAWN_PUSH
                        else:
                            flag = Move.NORMAL
                        candidate = Move.encode(square, target, flag)
                        self.make_move(candidate)
                        self.white_to_move = not self.white_to_move
                        in_check = self.is_in_check()
                        self.white_to_move = not self.white_to_move
                        self.unmake_move()
                        if not in_check:
                            moves.append(candidate)

        if self.en_passant_square is not None:
            ep_sq = self.en_passant_square
            ep_bit = 1 << ep_sq
            pawn_key = 'wP' if self.white_to_move else 'bP'
            pawn_bb = self.board.bitboards[pawn_key]

            if self.white_to_move:
                attackers = ((ep_bit >> 7) & NOT_A_FILE) | (
                    (ep_bit >> 9) & NOT_H_FILE)
            else:
                attackers = ((ep_bit << 7) & NOT_H_FILE) | (
                    (ep_bit << 9) & NOT_A_FILE)

            attackers &= pawn_bb

            for sq in range(64):
                if attackers & (1 << sq):
                    candidate = Move.encode(sq, ep_sq, Move.EN_PASSANT)
                    self.make_move(candidate)
                    self.white_to_move = not self.white_to_move
                    in_check = self.is_in_check()
                    self.white_to_move = not self.white_to_move
                    self.unmake_move()
                    if not in_check:
                        moves.append(candidate)

        by_enemy = not self.white_to_move

        if self.white_to_move:
            if self.castling_rights['wK']:
                if not (self.board.all_pieces & ((1 << 5) | (1 << 6))):
                    if not MoveGenerator.is_square_attacked(4, by_enemy, self.board.bitboards, self.board.all_pieces) and \
                            not MoveGenerator.is_square_attacked(5, by_enemy, self.board.bitboards, self.board.all_pieces) and \
                            not MoveGenerator.is_square_attacked(6, by_enemy, self.board.bitboards, self.board.all_pieces):
                        moves.append(Move.encode(4, 6, Move.CASTLING))

            if self.castling_rights['wQ']:
                if not (self.board.all_pieces & ((1 << 1) | (1 << 2) | (1 << 3))):
                    if not MoveGenerator.is_square_attacked(4, by_enemy, self.board.bitboards, self.board.all_pieces) and \
                            not MoveGenerator.is_square_attacked(3, by_enemy, self.board.bitboards, self.board.all_pieces) and \
                            not MoveGenerator.is_square_attacked(2, by_enemy, self.board.bitboards, self.board.all_pieces):
                        moves.append(Move.encode(4, 2, Move.CASTLING))
        else:
            if self.castling_rights['bK']:
                if not (self.board.all_pieces & ((1 << 61) | (1 << 62))):
                    if not MoveGenerator.is_square_attacked(60, by_enemy, self.board.bitboards, self.board.all_pieces) and \
                            not MoveGenerator.is_square_attacked(61, by_enemy, self.board.bitboards, self.board.all_pieces) and \
                            not MoveGenerator.is_square_attacked(62, by_enemy, self.board.bitboards, self.board.all_pieces):
                        moves.append(Move.encode(60, 62, Move.CASTLING))

            if self.castling_rights['bQ']:
                if not (self.board.all_pieces & ((1 << 57) | (1 << 58) | (1 << 59))):
                    if not MoveGenerator.is_square_attacked(60, by_enemy, self.board.bitboards, self.board.all_pieces) and \
                            not MoveGenerator.is_square_attacked(59, by_enemy, self.board.bitboards, self.board.all_pieces) and \
                            not MoveGenerator.is_square_attacked(58, by_enemy, self.board.bitboards, self.board.all_pieces):
                        moves.append(Move.encode(60, 58, Move.CASTLING))
        return moves

    def make_move(self, move):
        """
        Thực hiện một nước đi và cập nhật toàn bộ trạng thái ván cờ:
        - Cập nhật bitboard, hash Zobrist, quyền nhập thành, ô ăn tốt qua đường
        - Lưu lịch sử để phục vụ unmake_move
        - Cập nhật bộ đếm 50 nước đi và điểm số

        Args:
            move (int): Nước đi đã được mã hóa theo định dạng của lớp Move.
        """
        new_piece = None
        start = Move.get_start(move)
        target = Move.get_target(move)
        flag = Move.get_flag(move)

        promotion_flags = [
            Move.PROMOTION_QUEEN, Move.PROMOTION_ROOK,
            Move.PROMOTION_BISHOP, Move.PROMOTION_KNIGHT,
            Move.PROMOTION_CAPTURE_QUEEN, Move.PROMOTION_CAPTURE_ROOK,
            Move.PROMOTION_CAPTURE_BISHOP, Move.PROMOTION_CAPTURE_KNIGHT
        ]

        piece_moved = None
        for piece_name, bitboard in self.board.bitboards.items():
            if bitboard & (1 << start):
                piece_moved = piece_name
                break

        piece_captured = None
        capture_flags = [Move.CAPTURE, Move.PROMOTION_CAPTURE_QUEEN,
                         Move.PROMOTION_CAPTURE_ROOK, Move.PROMOTION_CAPTURE_BISHOP,
                         Move.PROMOTION_CAPTURE_KNIGHT]

        if flag in capture_flags:
            for piece_name, bitboard in self.board.bitboards.items():
                if bitboard & (1 << target):
                    piece_captured = piece_name
                    break
        elif flag == Move.EN_PASSANT:
            piece_captured = 'bP' if self.white_to_move else 'wP'

        self.zobrist_hash ^= Zobrist.castling[self._get_castle_index()]
        if self.en_passant_square is not None:
            self.zobrist_hash ^= Zobrist.en_passant[self.en_passant_square % 8]

        self.en_passant_log.append(self.en_passant_square)
        self.en_passant_square = None

        self.castling_rights_log.append(self.castling_rights.copy())
        self.fifty_move_log.append(self.fifty_move_counter)
        self.points_log.append(self.points.copy())

        if piece_moved == 'wK':
            self.castling_rights['wK'] = False
            self.castling_rights['wQ'] = False
        elif piece_moved == 'bK':
            self.castling_rights['bK'] = False
            self.castling_rights['bQ'] = False
        elif piece_moved == 'wR':
            if start == 0:
                self.castling_rights['wQ'] = False
            elif start == 7:
                self.castling_rights['wK'] = False
        elif piece_moved == 'bR':
            if start == 56:
                self.castling_rights['bQ'] = False
            elif start == 63:
                self.castling_rights['bK'] = False

        if piece_captured == 'wR':
            if target == 0:
                self.castling_rights['wQ'] = False
            elif target == 7:
                self.castling_rights['wK'] = False
        elif piece_captured == 'bR':
            if target == 56:
                self.castling_rights['bQ'] = False
            elif target == 63:
                self.castling_rights['bK'] = False

        if piece_moved[1] == 'P' or piece_captured is not None:
            self.fifty_move_counter = 0
        else:
            self.fifty_move_counter += 1

        if flag == Move.DOUBLE_PAWN_PUSH:
            if self.white_to_move:
                self.en_passant_square = target - 8
            else:
                self.en_passant_square = target + 8

        self.zobrist_hash ^= Zobrist.castling[self._get_castle_index()]
        if self.en_passant_square is not None:
            self.zobrist_hash ^= Zobrist.en_passant[self.en_passant_square % 8]

        if piece_captured is not None:
            cap_sq = target
            if flag == Move.EN_PASSANT:
                cap_sq = target - 8 if self.white_to_move else target + 8
                self.board.bitboards[piece_captured] &= ~(1 << cap_sq)
            else:
                self.board.bitboards[piece_captured] &= ~(1 << target)

            self.zobrist_hash ^= Zobrist.table[get_piece_idx(
                piece_captured)][cap_sq]

            reward = PIECE_VALUES[piece_captured[1]] // 10
            if self.white_to_move:
                self.points['w'] += reward
            else:
                self.points['b'] += reward

        self.board.bitboards[piece_moved] &= ~(1 << start)
        self.zobrist_hash ^= Zobrist.table[get_piece_idx(piece_moved)][start]

        final_piece = piece_moved
        if flag in promotion_flags:
            color_prefix = piece_moved[0]
            if flag in (Move.PROMOTION_QUEEN, Move.PROMOTION_CAPTURE_QUEEN):
                new_piece = color_prefix + 'Q'
            elif flag in (Move.PROMOTION_ROOK, Move.PROMOTION_CAPTURE_ROOK):
                new_piece = color_prefix + 'R'
            elif flag in (Move.PROMOTION_BISHOP, Move.PROMOTION_CAPTURE_BISHOP):
                new_piece = color_prefix + 'B'
            elif flag in (Move.PROMOTION_KNIGHT, Move.PROMOTION_CAPTURE_KNIGHT):
                new_piece = color_prefix + 'N'
            final_piece = new_piece

        self.board.bitboards[final_piece] |= (1 << target)
        self.zobrist_hash ^= Zobrist.table[get_piece_idx(final_piece)][target]

        if flag == Move.CASTLING:
            if target == 6:
                self.board.bitboards['wR'] &= ~(1 << 7)
                self.board.bitboards['wR'] |= (1 << 5)
                self.zobrist_hash ^= Zobrist.table[get_piece_idx(
                    'wR')][7] ^ Zobrist.table[get_piece_idx('wR')][5]
            elif target == 2:
                self.board.bitboards['wR'] &= ~(1 << 0)
                self.board.bitboards['wR'] |= (1 << 3)
                self.zobrist_hash ^= Zobrist.table[get_piece_idx(
                    'wR')][0] ^ Zobrist.table[get_piece_idx('wR')][3]
            elif target == 62:
                self.board.bitboards['bR'] &= ~(1 << 63)
                self.board.bitboards['bR'] |= (1 << 61)
                self.zobrist_hash ^= Zobrist.table[get_piece_idx(
                    'bR')][63] ^ Zobrist.table[get_piece_idx('bR')][61]
            elif target == 58:
                self.board.bitboards['bR'] &= ~(1 << 56)
                self.board.bitboards['bR'] |= (1 << 59)
                self.zobrist_hash ^= Zobrist.table[get_piece_idx(
                    'bR')][56] ^ Zobrist.table[get_piece_idx('bR')][59]

        history_record = {
            'move': move,
            'piece_moved': piece_moved,
            'piece_captured': piece_captured,
            'promoted_to': new_piece if flag in promotion_flags else None
        }
        self.move_log.append(history_record)

        self.zobrist_hash ^= Zobrist.side_to_move
        self.white_to_move = not self.white_to_move
        self.board.update_occupancies()

    def unmake_move(self):
        """
        Hoàn tác nước đi cuối cùng, khôi phục toàn bộ trạng thái ván cờ
        về trước khi nước đi đó được thực hiện, bao gồm: bitboard, hash Zobrist,
        quyền nhập thành, ô ăn tốt qua đường, bộ đếm 50 nước đi và điểm số.
        """
        if not self.move_log:
            return

        record = self.move_log.pop()
        move = record['move']
        piece_moved = record['piece_moved']
        piece_captured = record['piece_captured']
        promoted_to = record['promoted_to']

        start = Move.get_start(move)
        target = Move.get_target(move)
        flag = Move.get_flag(move)

        self.zobrist_hash ^= Zobrist.castling[self._get_castle_index()]
        if self.en_passant_square is not None:
            self.zobrist_hash ^= Zobrist.en_passant[self.en_passant_square % 8]

        self.en_passant_square = self.en_passant_log.pop()
        self.castling_rights = self.castling_rights_log.pop()
        self.fifty_move_counter = self.fifty_move_log.pop()
        self.points = self.points_log.pop()

        self.white_to_move = not self.white_to_move
        self.zobrist_hash ^= Zobrist.side_to_move

        self.zobrist_hash ^= Zobrist.castling[self._get_castle_index()]
        if self.en_passant_square is not None:
            self.zobrist_hash ^= Zobrist.en_passant[self.en_passant_square % 8]

        final_piece = promoted_to if promoted_to else piece_moved

        self.board.bitboards[final_piece] &= ~(1 << target)
        self.zobrist_hash ^= Zobrist.table[get_piece_idx(final_piece)][target]

        self.board.bitboards[piece_moved] |= (1 << start)
        self.zobrist_hash ^= Zobrist.table[get_piece_idx(piece_moved)][start]

        if piece_captured is not None:
            cap_sq = target
            if flag == Move.EN_PASSANT:
                cap_sq = target - 8 if self.white_to_move else target + 8
            self.board.bitboards[piece_captured] |= (1 << cap_sq)
            self.zobrist_hash ^= Zobrist.table[get_piece_idx(
                piece_captured)][cap_sq]

        if flag == Move.CASTLING:
            if target == 6:
                self.board.bitboards['wR'] &= ~(1 << 5)
                self.board.bitboards['wR'] |= (1 << 7)
                self.zobrist_hash ^= Zobrist.table[get_piece_idx(
                    'wR')][5] ^ Zobrist.table[get_piece_idx('wR')][7]
            elif target == 2:
                self.board.bitboards['wR'] &= ~(1 << 3)
                self.board.bitboards['wR'] |= (1 << 0)
                self.zobrist_hash ^= Zobrist.table[get_piece_idx(
                    'wR')][3] ^ Zobrist.table[get_piece_idx('wR')][0]
            elif target == 62:
                self.board.bitboards['bR'] &= ~(1 << 61)
                self.board.bitboards['bR'] |= (1 << 63)
                self.zobrist_hash ^= Zobrist.table[get_piece_idx(
                    'bR')][61] ^ Zobrist.table[get_piece_idx('bR')][63]
            elif target == 58:
                self.board.bitboards['bR'] &= ~(1 << 59)
                self.board.bitboards['bR'] |= (1 << 56)
                self.zobrist_hash ^= Zobrist.table[get_piece_idx(
                    'bR')][59] ^ Zobrist.table[get_piece_idx('bR')][56]

        self.board.update_occupancies()

    def get_game_status(self):
        """
        Xác định trạng thái hiện tại của ván cờ.

        Returns:
            str: Một trong các giá trị:
                - "Draw-50Move": Hòa do quy tắc 50 nước đi
                - "Checkmate-WhiteWins"/"Checkmate-BlackWins": Chiếu hết
                - "Stalemate": Hòa do hết nước đi hợp lệ (pat)
                - "Ongoing": Ván cờ vẫn đang tiếp diễn
        """
        if self.fifty_move_counter >= 100:
            return "Draw-50Move"

        legal_moves = self.get_legal_moves()

        if len(legal_moves) == 0:
            if self.is_in_check():
                if self.white_to_move:
                    return "Checkmate-BlackWins"
                else:
                    return "Checkmate-WhiteWins"
            else:
                return "Stalemate"

        return "Ongoing"
