import pygame
import sys
from abc import ABC, abstractmethod

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 60
BALL_SIZE = 7
PLAYER_SPEED = 5
AI_SPEED = 7

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class PlayerController(ABC):
    @abstractmethod
    def update(self, paddle: "Paddle", ball: "Ball") -> None:
        pass


class HumanController(PlayerController):
    def update(self, paddle: "Paddle", ball: "Ball") -> None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            paddle.move(-PLAYER_SPEED)
        if keys[pygame.K_DOWN]:
            paddle.move(PLAYER_SPEED)


class AIController(PlayerController):
    def update(self, paddle: "Paddle", ball: "Ball") -> None:
        center = paddle.y + PADDLE_HEIGHT // 2
        if center < ball.y:
            paddle.move(AI_SPEED)
        elif center > ball.y:
            paddle.move(-AI_SPEED)


class Ball:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.vel_x = 5
        self.vel_y = 5

    def move(self) -> None:
        self.x += self.vel_x
        self.y += self.vel_y
        if self.y <= 0 or self.y >= SCREEN_HEIGHT:
            self.vel_y *= -1

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, BALL_SIZE, BALL_SIZE)


class Paddle:
    def __init__(self, x: int) -> None:
        self.x = x
        self.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2

    def move(self, dy: int) -> None:
        self.y = max(0, min(self.y + dy, SCREEN_HEIGHT - PADDLE_HEIGHT))

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT)


class Renderer:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong SOLID")
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, ball: Ball, p1: Paddle, p2: Paddle, score1: int, score2: int) -> None:
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, WHITE, p1.rect())
        pygame.draw.rect(self.screen, WHITE, p2.rect())
        pygame.draw.circle(self.screen, WHITE, (ball.x, ball.y), BALL_SIZE)
        score = self.font.render(f"{score1} - {score2}", True, WHITE)
        self.screen.blit(score, score.get_rect(center=(SCREEN_WIDTH // 2, 30)))
        pygame.display.flip()


class Game:
    def __init__(self, controller1: PlayerController, controller2: PlayerController) -> None:
        self.ball = Ball()
        self.p1 = Paddle(15)
        self.p2 = Paddle(SCREEN_WIDTH - 25)
        self.controller1 = controller1
        self.controller2 = controller2
        self.renderer = Renderer()
        self.clock = pygame.time.Clock()
        self.score1 = 0
        self.score2 = 0

    def _handle_collisions(self) -> None:
        if self.ball.rect().colliderect(self.p1.rect()) or \
           self.ball.rect().colliderect(self.p2.rect()):
            self.ball.vel_x *= -1

    def _handle_score(self) -> None:
        if self.ball.x <= 0:
            self.score2 += 1
            self.ball.reset()
        elif self.ball.x >= SCREEN_WIDTH:
            self.score1 += 1
            self.ball.reset()

    def _update(self) -> None:
        self.ball.move()
        self.controller1.update(self.p1, self.ball)
        self.controller2.update(self.p2, self.ball)
        self._handle_collisions()
        self._handle_score()

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self._update()
            self.renderer.draw(self.ball, self.p1, self.p2, self.score1, self.score2)
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game(HumanController(), AIController()).run()
