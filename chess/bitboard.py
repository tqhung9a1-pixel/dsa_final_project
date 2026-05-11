# import random


# class Board:
#     def __init__(self):
#         # CHỈ DÙNG 1 DICTIONARY DUY NHẤT ĐỂ LƯU TOÀN BỘ 12 BITBOARD
#         self.bitboards = {
#             'wP': 0b11111111 << 8,
#             'wN': (1 << 1) | (1 << 6),
#             'wB': (1 << 2) | (1 << 5),
#             'wR': (1 << 0) | (1 << 7),
#             'wQ': (1 << 3),
#             'wK': (1 << 4),
#             'bP': 0b11111111 << 48,
#             'bN': (1 << 57) | (1 << 62),
#             'bB': (1 << 58) | (1 << 61),
#             'bR': (1 << 56) | (1 << 63),
#             'bQ': (1 << 59),
#             'bK': (1 << 60)
#         }

#         self.white_pieces = 0
#         self.black_pieces = 0
#         self.all_pieces = 0
#         self.update_occupancies()

#     def update_occupancies(self):
#         self.white_pieces = 0
#         self.black_pieces = 0

#         # Gom quân Trắng (Bắt đầu bằng chữ 'w')
#         for piece, bb in self.bitboards.items():
#             if piece.startswith('w'):
#                 self.white_pieces |= bb
#             elif piece.startswith('b'):
#                 self.black_pieces |= bb

#         self.all_pieces = self.white_pieces | self.black_pieces

#     def get_piece_at_square(self, square):
#         """Trả về tên quân cờ (vd: 'wP', 'bQ') tại ô square, nếu trống trả về None"""
#         bit_mask = 1 << square
#         for piece, bb in self.bitboards.items():
#             if bb & bit_mask:
#                 return piece
#         return None

#     def print_board(self):
#         print("\n  +-----------------+")
#         for rank in range(7, -1, -1):
#             row_str = f"{rank + 1} | "
#             for file in range(8):
#                 square = rank * 8 + file
#                 bit_mask = 1 << square

#                 # Quét xem ô này thuộc bitboard nào
#                 piece_char = ". "
#                 for piece, bb in self.bitboards.items():
#                     if bb & bit_mask:
#                         # Lấy chữ cái thứ 2 (ví dụ 'wP' -> 'P')
#                         # Nếu là quân đen, viết thường ('bP' -> 'p')
#                         char = piece[1]
#                         if piece.startswith('b'):
#                             char = char.lower()
#                         piece_char = char + " "
#                         break  # Tìm thấy quân rồi thì ngừng quét

#                 row_str += piece_char
#             print(row_str + "|")
#         print("  +-----------------+")
#         print("    a b c d e f g h\n")


# class Zobrist:
#     # Bảng 2D: [loại_quân][ô_cờ]
#     # piece_map: 'wP':0, 'wN':1 ... 'bK':11
#     table = [[random.getrandbits(64) for _ in range(64)] for _ in range(12)]
#     side_to_move = random.getrandbits(64)
#     # 4 bit quyền nhập thành -> 16 trạng thái
#     castling = [random.getrandbits(64) for _ in range(16)]
#     en_passant = [random.getrandbits(64) for _ in range(8)]  # 8 cột


# def get_piece_idx(piece_name):
#     mapping = {'wP': 0, 'wN': 1, 'wB': 2, 'wR': 3, 'wQ': 4, 'wK': 5,
#                'bP': 6, 'bN': 7, 'bB': 8, 'bR': 9, 'bQ': 10, 'bK': 11}
#     return mapping[piece_name]


# if __name__ == "__main__":
#     board = Board()
#     print("BÀN CỜ KHỞI ĐIỂM (Trắng chữ HOA, Đen chữ thường):")
#     board.print_board()

import random


class Board:
    """Quản lý biểu diễn bàn cờ bằng 12 bitboard (6 loại quân × 2 màu)."""

    def __init__(self):
        """Khởi tạo bàn cờ với vị trí ban đầu của ván cờ tiêu chuẩn."""
        self.bitboards = {
            'wP': 0b11111111 << 8,
            'wN': (1 << 1) | (1 << 6),
            'wB': (1 << 2) | (1 << 5),
            'wR': (1 << 0) | (1 << 7),
            'wQ': (1 << 3),
            'wK': (1 << 4),
            'bP': 0b11111111 << 48,
            'bN': (1 << 57) | (1 << 62),
            'bB': (1 << 58) | (1 << 61),
            'bR': (1 << 56) | (1 << 63),
            'bQ': (1 << 59),
            'bK': (1 << 60)
        }

        self.white_pieces = 0
        self.black_pieces = 0
        self.all_pieces = 0
        self.update_occupancies()

    def update_occupancies(self):
        """
        Cập nhật các bitmask tổng hợp: white_pieces, black_pieces và all_pieces
        từ 12 bitboard riêng lẻ của từng loại quân.
        """
        self.white_pieces = 0
        self.black_pieces = 0

        for piece, bb in self.bitboards.items():
            if piece.startswith('w'):
                self.white_pieces |= bb
            elif piece.startswith('b'):
                self.black_pieces |= bb

        self.all_pieces = self.white_pieces | self.black_pieces

    def get_piece_at_square(self, square):
        """
        Trả về tên quân cờ tại ô vuông được chỉ định.

        Args:
            square (int): Chỉ số ô vuông (0-63, a1=0, h8=63).

        Returns:
            str | None: Tên quân (vd: 'wP', 'bQ') nếu có quân tại ô đó,
                hoặc None nếu ô trống.
        """
        bit_mask = 1 << square
        for piece, bb in self.bitboards.items():
            if bb & bit_mask:
                return piece
        return None

    def print_board(self):
        """In bàn cờ ra console dưới dạng ASCII (Trắng: chữ HOA, Đen: chữ thường)."""
        print("\n  +-----------------+")
        for rank in range(7, -1, -1):
            row_str = f"{rank + 1} | "
            for file in range(8):
                square = rank * 8 + file
                bit_mask = 1 << square

                piece_char = ". "
                for piece, bb in self.bitboards.items():
                    if bb & bit_mask:
                        char = piece[1]
                        if piece.startswith('b'):
                            char = char.lower()
                        piece_char = char + " "
                        break

                row_str += piece_char
            print(row_str + "|")
        print("  +-----------------+")
        print("    a b c d e f g h\n")


class Zobrist:
    """
    Bảng hash Zobrist để tạo giá trị hash duy nhất cho mỗi trạng thái bàn cờ.
    Sử dụng cho transposition table và phát hiện lặp vị trí.
    """
    # Bảng 2D: [chỉ_số_quân][ô_cờ] -> giá trị hash 64-bit ngẫu nhiên
    table = [[random.getrandbits(64) for _ in range(64)] for _ in range(12)]
    # Hash cho thông tin bên nào đến lượt
    side_to_move = random.getrandbits(64)
    # Hash cho 16 tổ hợp quyền nhập thành có thể có (4 bit)
    castling = [random.getrandbits(64) for _ in range(16)]
    # Hash cho 8 cột có thể xảy ra ăn tốt qua đường
    en_passant = [random.getrandbits(64) for _ in range(8)]


def get_piece_idx(piece_name):
    """
    Ánh xạ tên quân cờ thành chỉ số 0-11 để tra bảng Zobrist.

    Args:
        piece_name (str): Tên quân theo định dạng 'wP', 'bQ', ...

    Returns:
        int: Chỉ số tương ứng (0-5: Trắng, 6-11: Đen).
    """
    mapping = {
        'wP': 0, 'wN': 1, 'wB': 2, 'wR': 3, 'wQ': 4, 'wK': 5,
        'bP': 6, 'bN': 7, 'bB': 8, 'bR': 9, 'bQ': 10, 'bK': 11
    }
    return mapping[piece_name]


if __name__ == "__main__":
    board = Board()
    print("BÀN CỜ KHỞI ĐIỂM (Trắng chữ HOA, Đen chữ thường):")
    board.print_board()
