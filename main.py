from src.game import Game


def main():
    game = Game()

    # 示例：开始第一关，非重力模式，简单难度
    game.start_level(1, mode="non-gravity", difficulty="easy")

    game.run()


if __name__ == "__main__":
    main()