# Pong SOLID

Jogo Pong em Python + Pygame, arquivo único, arquitetura SOLID.

## Como executar

```bash
pip install pygame
python pong.py
```

**Controles:** `↑` / `↓` para mover a raquete. Feche a janela para sair.

---

## Estrutura de arquivos

```
PongRefatorado/
├── pong.py
└── assets/
    └── sounds/
        ├── hit.mp3
        ├── wall.mp3
        ├── goal.mp3
        └── music.mp3
```

---

## Constantes

| Constante | Valor | Descrição |
|---|---|---|
| `SCREEN_WIDTH` | 800 | Largura da janela (px) |
| `SCREEN_HEIGHT` | 600 | Altura da janela (px) |
| `FPS` | 60 | Quadros por segundo |
| `PADDLE_WIDTH` | 10 | Largura da raquete (px) |
| `PADDLE_HEIGHT` | 60 | Altura da raquete (px) |
| `BALL_SIZE` | 7 | Raio da bola (px) |
| `PLAYER_SPEED` | 5 | Velocidade da raquete do jogador (px/frame) |
| `AI_SPEED` | 7 | Velocidade da raquete da IA (px/frame) |
| `BALL_SPEED_MIN` | 4 | Velocidade mínima da bola após variação |
| `BALL_SPEED_MAX` | 8 | Velocidade máxima da bola após variação |
| `BOUNCE_VARIATION` | 2.0 | Intensidade da variação aleatória de ângulo no rebote |
| `POWERUP_INTERVAL` | 5000 | Intervalo em ms para ativar a fragmentação |
| `FRAGMENT_COUNT` | 3 | Quantidade de bolas falsas geradas na fragmentação |

---

## Classes

### `PlayerController` (ABC)

Interface abstrata que todos os controladores devem implementar.

```python
def update(self, paddle: Paddle, ball: Ball) -> None
```

---

### `HumanController`

Lê o estado do teclado a cada frame e move a raquete com `PLAYER_SPEED`.

| Tecla | Ação |
|---|---|
| `↑` | Move a raquete para cima |
| `↓` | Move a raquete para baixo |

---

### `AIController`

Move a raquete automaticamente alinhando seu centro ao `Y` da bola verdadeira com `AI_SPEED`.

---

### `Ball`

Representa qualquer bola em jogo, verdadeira ou fragmento.

| Atributo | Tipo | Descrição |
|---|---|---|
| `x, y` | `float` | Posição atual na tela |
| `vel_x, vel_y` | `float` | Velocidade nos eixos X e Y |
| `color` | `tuple` | Cor RGB da bola |
| `real` | `bool` | `True` se é a bola que pontua, `False` se é distração |

| Método | Descrição |
|---|---|
| `spawn_center()` | Factory: cria a bola principal no centro com direção aleatória |
| `_apply_variation()` | Aplica delta aleatório no ângulo e normaliza a velocidade entre `BALL_SPEED_MIN` e `BALL_SPEED_MAX` |
| `bounce_x()` | Inverte `vel_x` e aplica variação |
| `bounce_y()` | Inverte `vel_y` e aplica variação |
| `move()` | Avança posição e rebate nas paredes, reposicionando a bola no limite antes de rebater |
| `rect()` | Retorna `pygame.Rect` para detecção de colisão |
| `spawn_fragments()` | Gera `FRAGMENT_COUNT` bolas falsas coloridas na mesma posição, na mesma direção horizontal |

---

### `Paddle`

Raquete com movimento restrito aos limites verticais da tela.

| Método | Descrição |
|---|---|
| `move(dy)` | Move `dy` pixels no eixo Y com clamp entre `0` e `SCREEN_HEIGHT - PADDLE_HEIGHT` |
| `rect()` | Retorna `pygame.Rect` para detecção de colisão |

---

### `AudioManager`

Gerencia todos os sons do jogo. Falha silenciosamente se algum arquivo não for encontrado.

| Método | Arquivo | Quando é chamado |
|---|---|---|
| `play_hit()` | `hit.mp3` | Colisão da bola com a raquete |
| `play_wall()` | `wall.mp3` | Colisão da bola com o topo ou fundo |
| `play_goal()` | `goal.mp3` | Ponto marcado |
| — | `music.mp3` | Trilha em loop contínuo durante o jogo |

---

### `Renderer`

Responsável exclusivamente pela camada visual do jogo (SRP).

| Método | Descrição |
|---|---|
| `__init__()` | Inicializa Pygame, cria a janela e carrega a fonte |
| `draw(balls, p1, p2, s1, s2)` | Desenha fundo, raquetes, todas as bolas com suas cores e o placar |

---

### `Game`

Coordena o loop principal. Controladores são injetados via construtor (DIP).

| Método | Descrição |
|---|---|
| `_reset_balls()` | Substitui todas as bolas por uma nova bola principal no centro |
| `_real_ball()` | Retorna a bola com `real=True` |
| `_handle_collisions()` | Detecta colisões com raquetes e paredes, aplica rebote e dispara fragmentação quando o power-up está ativo |
| `_handle_score()` | Pontua quando a bola real sai da tela, descarta falsas que saem e reseta se necessário |
| `_handle_powerup_timer()` | Ativa `_powerup_ready` após `POWERUP_INTERVAL` ms |
| `_update()` | Executa um ciclo: timer, movimento, controllers, colisões e placar |
| `run()` | Loop principal a 60 FPS com captura de eventos |

---

## Princípios SOLID

| Princípio | Aplicação |
|---|---|
| **S** — Single Responsibility | `AudioManager` cuida só do áudio, `Renderer` só da tela, `Ball` só da sua física |
| **O** — Open/Closed | Novos controladores ou comportamentos podem ser adicionados sem alterar `Game` |
| **L** — Liskov Substitution | `HumanController` e `AIController` são intercambiáveis onde se espera `PlayerController` |
| **I** — Interface Segregation | `PlayerController` expõe apenas `update(paddle, ball)` |
| **D** — Dependency Inversion | `Game` depende da abstração `PlayerController`, não das implementações concretas |