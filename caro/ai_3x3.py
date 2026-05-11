from core_engine import GameController, BaseAI
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class AI_3x3(BaseAI):
    def evaluate_board(self, board, game_engine):
        return 0


if __name__ == "__main__":
    ai_player = AI_3x3(symbol="O", depth=9)
    game = GameController(size=3, win_condition=3, ai_player=ai_player)
    print("CHÀO MỪNG ĐẾN VỚI CARO 3x3")
    game.play()
