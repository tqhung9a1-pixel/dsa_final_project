# DÙNG 16 bit ĐỂ LƯU 3 THỨ (TRẠNG THÁI NƯỚC ĐI(4bit), Ô BẮT ĐẦU(6bit), Ô MỤC TIÊU(6bit))
class Move:
    """
    Kỹ thuật Bit Packing:
    bit 0-5: start square, bit 6-11: target square, bit 12-15: flags.
    Giúp tối ưu hóa việc lưu trữ hàng triệu nước đi trong bộ nhớ.
    """
    NORMAL = 0
    CAPTURE = 1             # Ăn quân
    DOUBLE_PAWN_PUSH = 2    # Tốt tiến 2 ô
    EN_PASSANT = 3          # Bắt Tốt qua đường

    PROMOTION_QUEEN = 4
    PROMOTION_ROOK = 5      # Phong cấp
    PROMOTION_BISHOP = 6
    PROMOTION_KNIGHT = 7

    PROMOTION_CAPTURE_QUEEN = 8
    PROMOTION_CAPTURE_ROOK = 9
    PROMOTION_CAPTURE_BISHOP = 10
    PROMOTION_CAPTURE_KNIGHT = 11

    CASTLING = 12           # Nhập thành

    @staticmethod
    def encode(start_square, target_square, flag=NORMAL):
        # HÀM NÀY DÙNG ĐỂ LƯU TRẠNG THÁI NƯỚC ĐI, Ô BẮT ĐẦU VÀ Ô ĐI TỚI
        # bit 0 - 5: ô bắt đầu
        # bit 6 - 11: ô mục tiêu
        # bit 12 - 15: trạng thái
        return start_square | (target_square << 6) | (flag << 12)

    @staticmethod
    def get_start(move):
        return move & 0b111111
        # TỔNG HỢP TRẠNG THÁI ĐANG ĐƯỢC LƯU DƯỚI DÃY 16BIT VÀ
        # THỰC HIỆN PHÉP & 111111 ĐỂ CHỈ LẤY 6 BIT ĐẦU TIÊN

    @staticmethod
    def get_target(move):
        return (move >> 6) & 0b111111

    @staticmethod
    def get_flag(move):
        return (move >> 12) & 0b1111
