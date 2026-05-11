from evaluation import evaluate, PIECE_VALUES
from move import Move
import random
import time

# Điểm số
MAX_SCORE = 1000000
MIN_SCORE = -1000000

# Transposition Table flags
TT_EXACT = 0
TT_LOWERBOUND = 1
TT_UPPERBOUND = 2

transposition_table = {}

QS_MAX_DEPTH = 4


def get_piece_value(gs, sq):
    """Hàm phụ trợ lấy giá trị quân cờ tại một ô bitboard"""
    for name, bb in gs.board.bitboards.items():
        if bb & (1 << sq):
            return PIECE_VALUES[name[1]]
    return 0


def score_move(move, gs):
    """
    Chấm điểm độ ưu tiên của một nước đi để sắp xếp (Move Ordering).
    Nước nào điểm cao sẽ được AI ưu tiên mang ra tính trước.
    """
    score = 0
    flag = Move.get_flag(move)
    start_sq = Move.get_start(move)
    target_sq = Move.get_target(move)

    if flag in (Move.PROMOTION_QUEEN, Move.PROMOTION_CAPTURE_QUEEN):
        score += 900

    if flag in (Move.CAPTURE, Move.EN_PASSANT, Move.PROMOTION_CAPTURE_QUEEN,
                Move.PROMOTION_CAPTURE_ROOK, Move.PROMOTION_CAPTURE_BISHOP, Move.PROMOTION_CAPTURE_KNIGHT):

        victim_val = get_piece_value(gs, target_sq)
        if flag == Move.EN_PASSANT:
            victim_val = 100

        attacker_val = get_piece_value(gs, start_sq)

        score += (victim_val * 10) - attacker_val

    if flag == Move.CASTLING:
        score += 50

    return score


def quiescence_search(gs, alpha, beta, maximizing_player, qs_depth=0):
    """
    Tìm kiếm tĩnh với giới hạn độ sâu QS_MAX_DEPTH.
    Ngăn stack overflow khi có nhiều nước ăn quân liên tiếp (vd: full queen position).
    """
    stand_pat = evaluate(gs)

    if qs_depth >= QS_MAX_DEPTH:
        return stand_pat

    if maximizing_player:
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat
    else:
        if stand_pat <= alpha:
            return alpha
        if beta > stand_pat:
            beta = stand_pat

    legal_moves = gs.get_legal_moves()

    if gs.is_in_check():
        capture_moves = legal_moves
    else:
        capture_moves = [m for m in legal_moves if Move.get_flag(m) in
                         (Move.CAPTURE, Move.EN_PASSANT, Move.PROMOTION_CAPTURE_QUEEN,
                          Move.PROMOTION_CAPTURE_ROOK, Move.PROMOTION_CAPTURE_BISHOP,
                          Move.PROMOTION_CAPTURE_KNIGHT)]

    if not capture_moves:
        return stand_pat

    capture_moves.sort(key=lambda m: score_move(m, gs), reverse=True)

    if maximizing_player:
        for move in capture_moves:
            gs.make_move(move)
            score = quiescence_search(gs, alpha, beta, False, qs_depth + 1)
            gs.unmake_move()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha
    else:
        for move in capture_moves:
            gs.make_move(move)
            score = quiescence_search(gs, alpha, beta, True, qs_depth + 1)
            gs.unmake_move()
            if score <= alpha:
                return alpha
            if score < beta:
                beta = score
        return beta


def search(gs, depth, alpha, beta, maximizing_player):
    """
    Hàm đệ quy Alpha-Beta chính tích hợp Transposition Table.
    """
    hash_key = gs.zobrist_hash
    if hash_key in transposition_table:
        entry = transposition_table[hash_key]
        if entry['depth'] >= depth:
            if entry['flag'] == TT_EXACT:
                return entry['score']
            elif entry['flag'] == TT_LOWERBOUND:
                alpha = max(alpha, entry['score'])
            elif entry['flag'] == TT_UPPERBOUND:
                beta = min(beta, entry['score'])

            if alpha >= beta:
                return entry['score']

    orig_alpha = alpha
    orig_beta = beta

    if depth == 0:
        return quiescence_search(gs, alpha, beta, maximizing_player)

    legal_moves = gs.get_legal_moves()
    if not legal_moves:
        if gs.is_in_check():
            return (MIN_SCORE + depth) if maximizing_player else (MAX_SCORE - depth)
        return 0  # Stalemate

    legal_moves.sort(key=lambda m: score_move(m, gs), reverse=True)

    best_score = MIN_SCORE if maximizing_player else MAX_SCORE

    for move in legal_moves:
        gs.make_move(move)
        score = search(gs, depth - 1, alpha, beta, not maximizing_player)
        gs.unmake_move()

        if maximizing_player:
            if score > best_score:
                best_score = score
            alpha = max(alpha, score)
        else:
            if score < best_score:
                best_score = score
            beta = min(beta, score)

        if alpha >= beta:
            break  # Cắt tỉa

    tt_flag = TT_EXACT
    if best_score <= orig_alpha:
        tt_flag = TT_UPPERBOUND
    elif best_score >= orig_beta:
        tt_flag = TT_LOWERBOUND

    transposition_table[hash_key] = {
        'score': best_score,
        'depth': depth,
        'flag': tt_flag
    }

    return best_score


def get_best_move(gs, depth=3):
    """
    Hàm entry point để GUI gọi lấy nước đi tốt nhất.
    """
    global transposition_table

    TIME_LIMITS = {1: 1.5, 2: 3.0, 3: 5.0, 4: 8.0}
    deadline = time.time() + TIME_LIMITS.get(depth, 5.0)

    if len(transposition_table) > 1000000:
        transposition_table.clear()

    legal_moves = gs.get_legal_moves()
    if not legal_moves:
        return None

    random.shuffle(legal_moves)
    legal_moves.sort(key=lambda m: score_move(m, gs), reverse=True)

    best_move = legal_moves[0]
    alpha = MIN_SCORE
    beta = MAX_SCORE
    maximizing = gs.white_to_move
    current_best_score = MIN_SCORE if maximizing else MAX_SCORE

    print(f"AI đang tính toán ở độ sâu {depth}...")

    for move in legal_moves:
        if time.time() > deadline:
            print(f"  [time limit hit, returning best so far]")
            break

        gs.make_move(move)
        score = search(gs, depth - 1, alpha, beta, not maximizing)
        gs.unmake_move()

        if maximizing:
            if score > current_best_score:
                current_best_score = score
                best_move = move
            alpha = max(alpha, score)
        else:
            if score < current_best_score:
                current_best_score = score
                best_move = move
            beta = min(beta, score)

    return best_move
