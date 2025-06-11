from src.game import Game


def main():
    game = Game()

    game.start_level(4, mode="non-gravity", difficulty="hard")

    game.run()


if __name__ == "__main__":
    main()