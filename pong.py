import pygame
import sys
import math
import random
from abc import ABC, abstractmethod

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 60
BALL_SIZE = 7
PLAYER_SPEED = 5
AI_SPEED = 7
BALL_SPEED_MIN = 4
BALL_SPEED_MAX = 8
BOUNCE_VARIATION = 2.0

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

SOUND_HIT   = "assets/sounds/hit.mp3"
SOUND_WALL  = "assets/sounds/wall.mp3"
SOUND_GOAL  = "assets/sounds/goal.mp3"
SOUND_MUSIC = "assets/sounds/music.mp3"


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
        self.vel_x = 5 * random.choice([-1, 1])
        self.vel_y = 5 * random.choice([-1, 1])

    def _apply_variation(self) -> None:
        self.vel_y += random.uniform(-BOUNCE_VARIATION, BOUNCE_VARIATION)
        min_vy = 1.5
        if abs(self.vel_y) < min_vy:
            self.vel_y = math.copysign(min_vy, self.vel_y)
        speed = (self.vel_x ** 2 + self.vel_y ** 2) ** 0.5
        scale = max(BALL_SPEED_MIN, min(speed, BALL_SPEED_MAX)) / speed
        self.vel_x *= scale
        self.vel_y *= scale

    def bounce_x(self) -> None:
        self.vel_x *= -1
        self._apply_variation()

    def bounce_y(self) -> None:
        self.vel_y *= -1
        self._apply_variation()

    def move(self) -> None:
        self.x += self.vel_x
        self.y += self.vel_y
        if self.y <= 0:
            self.y = 0
            self.bounce_y()
        elif self.y >= SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT - 1
            self.bounce_y()

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


class AudioManager:
    def __init__(self) -> None:
        pygame.mixer.init()
        self._hit  = self._load(SOUND_HIT)
        self._wall = self._load(SOUND_WALL)
        self._goal = self._load(SOUND_GOAL)
        self._load_music(SOUND_MUSIC)

    def _load(self, path: str):
        try:
            return pygame.mixer.Sound(path)
        except (FileNotFoundError, pygame.error):
            return None

    def _load_music(self, path: str) -> None:
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(loops=-1)
        except (FileNotFoundError, pygame.error):
            pass

    def play_hit(self)  -> None: self._hit  and self._hit.play()
    def play_wall(self) -> None: self._wall and self._wall.play()
    def play_goal(self) -> None: self._goal and self._goal.play()


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
        self.audio = AudioManager()
        self.renderer = Renderer()
        self.clock = pygame.time.Clock()
        self.score1 = 0
        self.score2 = 0

    def _handle_collisions(self) -> None:
        if self.ball.rect().colliderect(self.p1.rect()) or \
           self.ball.rect().colliderect(self.p2.rect()):
            self.ball.bounce_x()
            self.audio.play_hit()

        prev_y = self.ball.y - self.ball.vel_y
        if (prev_y > 0 and self.ball.y <= 0) or \
           (prev_y < SCREEN_HEIGHT and self.ball.y >= SCREEN_HEIGHT):
            self.audio.play_wall()

    def _handle_score(self) -> None:
        if self.ball.x <= 0:
            self.score2 += 1
            self.audio.play_goal()
            self.ball.reset()
        elif self.ball.x >= SCREEN_WIDTH:
            self.score1 += 1
            self.audio.play_goal()
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