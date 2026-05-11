from core_engine import GameController, BaseAI
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

weights = [
    [3, 1, 1, 3],
    [1, 5, 5, 1],
    [1, 5, 5, 1],
    [3, 1, 1, 3]
]


class AI_4x4(BaseAI):
    def evaluate_board(self, board, game_engine):
        score = 0
        for r in range(4):
            for c in range(4):
                if board.grid[r][c] == self.symbol:
                    score += weights[r][c]
                elif board.grid[r][c] == self.opponent:
                    score -= weights[r][c]
        return score


if __name__ == "__main__":
    ai_player = AI_4x4(symbol="O", depth=5)
    game = GameController(size=4, win_condition=4, ai_player=ai_player)
    print("CHÀO MỪNG ĐẾN VỚI CARO 4X4")
    game.play()
