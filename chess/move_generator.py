NOT_A_FILE = 0xFEFEFEFEFEFEFEFE
NOT_H_FILE = 0x7F7F7F7F7F7F7F7F
NOT_AB_FILE = 0xFCFCFCFCFCFCFCFC
NOT_GH_FILE = 0x3F3F3F3F3F3F3F3F


class MoveGenerator:
    # QUÂN MÃ
    @staticmethod
    def get_knight_moves(square):
        bit = 1 << square
        moves = 0

        # DỌC 2, NGANG 1
        moves |= (bit << 15) & NOT_H_FILE
        moves |= (bit << 17) & NOT_A_FILE
        moves |= (bit >> 15) & NOT_A_FILE
        moves |= (bit >> 17) & NOT_H_FILE

        # NGANG 2, DỌC 1
        moves |= (bit << 6) & NOT_GH_FILE
        moves |= (bit << 10) & NOT_AB_FILE
        moves |= (bit >> 6) & NOT_AB_FILE
        moves |= (bit >> 10) & NOT_GH_FILE

        return moves

    # QUÂN VUA
    @staticmethod
    def get_king_moves(square):
        bit = 1 << square
        moves = 0

        # ĐI NGANG
        moves |= (bit << 1) & NOT_A_FILE
        moves |= (bit >> 1) & NOT_H_FILE

        # ĐI DỌC
        moves |= (bit << 8)
        moves |= (bit >> 8)

        # ĐI CHÉO
        moves |= (bit << 7) & NOT_H_FILE
        moves |= (bit << 9) & NOT_A_FILE
        moves |= (bit >> 7) & NOT_A_FILE
        moves |= (bit >> 9) & NOT_H_FILE
        return moves

    # XE + TƯỢNG + HẬU
    @staticmethod
    def get_slider_moves(square, blockers, is_bishop):
        moves = 0
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)
                      ] if is_bishop else [(1, 0), (-1, 0), (0, 1), (0, -1)]

        start_r = square // 8
        start_c = square % 8

        for dr, dc in directions:
            r, c = start_r + dr, start_c + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target_square = r*8 + c
                bit = 1 << target_square
                moves |= bit
                if blockers & bit:
                    break
                r += dr
                c += dc
        return moves

    @staticmethod
    def get_rook_moves(square, blockers):
        return MoveGenerator.get_slider_moves(square, blockers, is_bishop=False)

    @staticmethod
    def get_bishop_moves(square, blockers):
        return MoveGenerator.get_slider_moves(square, blockers, is_bishop=True)

    @staticmethod
    def get_queen_moves(square, blockers):
        return MoveGenerator.get_rook_moves(square, blockers) | MoveGenerator.get_bishop_moves(square, blockers)

    # TỐT
    @staticmethod
    def get_pawn_moves(square, color, blockers, enemies):
        bit = 1 << square
        moves = 0
        attacks = 0

        if color == "White":
            single_push = (bit << 8) & ~blockers
            moves |= single_push

            # BƯỚC ĐI BAN ĐẦU(ĐI 2 Ô)
            if single_push > 0 and (square // 8 == 1):
                double_push = (single_push << 8) & ~blockers
                moves |= double_push

            # ĂN CHÉO
            attacks |= (bit << 7) & NOT_H_FILE & enemies
            attacks |= (bit << 9) & NOT_A_FILE & enemies
        else:
            single_push = (bit >> 8) & ~blockers
            moves |= single_push

            # BƯỚC ĐI BAN ĐẦU(ĐI 2 Ô)
            if single_push > 0 and (square // 8 == 6):
                double_push = (single_push >> 8) & ~blockers
                moves |= double_push

            # ĂN CHÉO
            attacks |= (bit >> 7) & NOT_A_FILE & enemies
            attacks |= (bit >> 9) & NOT_H_FILE & enemies

        return moves | attacks

    @staticmethod
    def is_square_attacked(square, by_white, bitboards, all_pieces):
        if by_white:
            # KIỂM TRA XEM CÓ QUÂN NÀO ĐANG ĐE DỌA VUA CỦA MÌNH KHÔNG BẰNG CÁCH ĐẶT QUÂN TƯƠNG ỨNG
            # VÀO Ô ĐÓ XONG RỒI KIỂM TRA XEM QUÂN ĐÓ CÓ ĂN ĐƯỢC QUÂN ĐỊCH NÀO KHÔNG.
            if MoveGenerator.get_knight_moves(square) & bitboards['wN']:
                return True
            if MoveGenerator.get_rook_moves(square, all_pieces) & (bitboards['wR'] | bitboards['wQ']):
                return True
            if MoveGenerator.get_bishop_moves(square, all_pieces) & (bitboards['wB'] | bitboards['wQ']):
                return True
            bit = 1 << square
            pawn_attacks = ((bit >> 7) & NOT_A_FILE) | (
                (bit >> 9) & NOT_H_FILE)
            if pawn_attacks & bitboards['wP']:
                return True
            if MoveGenerator.get_king_moves(square) & bitboards['wK']:
                return True
        else:
            if MoveGenerator.get_knight_moves(square) & bitboards['bN']:
                return True
            if MoveGenerator.get_rook_moves(square, all_pieces) & (bitboards['bR'] | bitboards['bQ']):
                return True
            if MoveGenerator.get_bishop_moves(square, all_pieces) & (bitboards['bB'] | bitboards['bQ']):
                return True
            bit = 1 << square
            pawn_attacks = ((bit << 7) & NOT_H_FILE) | (
                (bit << 9) & NOT_A_FILE)
            if pawn_attacks & bitboards['bP']:
                return True
            if MoveGenerator.get_king_moves(square) & bitboards['bK']:
                return True

        return False
