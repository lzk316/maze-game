from src.game import Game


def main():
    game = Game()

    game.start_level(1, mode="non-gravity", difficulty="easy")

    game.run()


if __name__ == "__main__":
    main()