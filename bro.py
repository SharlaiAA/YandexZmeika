import pygame
from random import choice

# Константы
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE    # 32
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE  # 24

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (255, 0, 0)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SPEED = 20

# Направления
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Все возможные ячейки поля
ALL_CELLS = {
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
}


class GameObject:
    """Базовый класс игровых объектов."""

    def __init__(self):
        """Инициализирует позицию в центре экрана."""
        self.position = (
            (SCREEN_WIDTH // 2) // GRID_SIZE * GRID_SIZE,
            (SCREEN_HEIGHT // 2) // GRID_SIZE * GRID_SIZE,
        )
        self.body_color = None

    def draw(self, surface):
        """Абстрактный метод отрисовки. Переопределяется в наследниках."""
        pass

    def draw_cell(self, surface, position, color):
        """Заливает одну ячейку указанным цветом."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, color, rect)


class Apple(GameObject):
    """Яблоко — объект, который змейка ест."""

    def __init__(self):
        """Создаёт яблоко в случайной позиции."""
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def randomize_position(self, occupied=()):
        """Устанавливает случайную свободную позицию для яблока."""
        free_cells = ALL_CELLS - set(occupied)
        if free_cells:
            self.position = choice(tuple(free_cells))
        else:
            self.position = None  # поле заполнено — победа

    def draw(self, surface):
        """Отрисовывает яблоко."""
        if self.position:
            self.draw_cell(surface, self.position, self.body_color)


class Snake(GameObject):
    """Змейка — управляемый игроком объект."""

    def __init__(self):
        """Инициализирует змейку из одной головы в центре."""
        super().__init__()
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last = None

    def update_direction(self):
        """Применяет отложенное направление."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self, apple):
        """Перемещает змейку. Если съела яблоко — растёт."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )

        self.positions.insert(0, new_head)

        # Если новая голова на яблоке — длина увеличивается,
        # и хвост НЕ удаляется
        if apple.position and new_head == apple.position:
            self.length += 1
            apple.randomize_position(self.positions)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self, surface):
        """Отрисовывает все сегменты змейки и затирает хвост."""
        for position in self.positions:
            self.draw_cell(surface, position, self.body_color)
        if self.last:
            self.draw_cell(surface, self.last, BOARD_BACKGROUND_COLOR)

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None


def handle_keys(snake):
    """Обрабатывает нажатия клавиш для смены направления."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake.direction != DOWN:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN and snake.direction != UP:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                snake.next_direction = RIGHT


def main():
    """Основной игровой цикл."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Изгиб Питона')
    clock = pygame.time.Clock()

    snake = Snake()
    apple = Apple()
    apple.randomize_position(snake.positions)

    running = True
    while running:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()

        # move() сам обрабатывает поедание яблока и рост
        snake.move(apple)

        # Проверка самоукуса
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        apple.draw(screen)
        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()