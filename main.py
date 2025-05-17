from game import PinballGame

if __name__ == "__main__":
    import game_context
    game_context.game = PinballGame()
    game_context.game.run()
