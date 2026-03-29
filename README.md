# Pong SOLID

Jogo Pong em Python + Pygame em arquivo único, estruturado com os princípios SOLID.

## Como executar

```bash
pip install pygame
python pong.py
```

**Controles:** `↑` / `↓` para mover a raquete. Feche a janela para sair.

---

## Configurações

Todas as constantes ficam no topo do arquivo e podem ser ajustadas sem tocar na lógica:

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

---

## Classes

### `PlayerController` (ABC)
Interface que todos os controladores devem implementar.

```python
def update(self, paddle: Paddle, ball: Ball) -> None
```

### `HumanController`
Lê `K_UP` e `K_DOWN` a cada frame e move a raquete via `PLAYER_SPEED`.

### `AIController`
Compara o centro da raquete com o `Y` da bola e move em direção a ela via `AI_SPEED`.

### `Ball`
Gerencia posição e velocidade da bola.

| Método | Descrição |
|---|---|
| `reset()` | Reposiciona no centro com velocidade padrão |
| `move()` | Avança a posição e reflete nas paredes horizontais |
| `rect()` | Retorna `pygame.Rect` para detecção de colisão |

### `Paddle`
Representa uma raquete com movimento limitado aos bordos da tela.

| Método | Descrição |
|---|---|
| `move(dy)` | Move `dy` pixels no eixo Y com clamp |
| `rect()` | Retorna `pygame.Rect` para detecção de colisão |

### `Renderer`
Responsável exclusivamente pela camada visual.

| Método | Descrição |
|---|---|
| `__init__()` | Inicializa Pygame e cria a janela |
| `draw(ball, p1, p2, s1, s2)` | Desenha fundo, raquetes, bola e placar |

### `Game`
Coordena o loop principal, recebendo controladores via injeção de dependência.

| Método | Descrição |
|---|---|
| `_handle_collisions()` | Inverte `vel_x` ao colidir com uma raquete |
| `_handle_score()` | Atualiza placar e reseta a bola quando ela sai da tela |
| `_update()` | Executa um ciclo: move bola, atualiza controladores, colisões e placar |
| `run()` | Loop principal a 60 FPS |

---

## Princípios SOLID

| Princípio | Aplicação |
|---|---|
| **S** — Single Responsibility | Cada classe tem uma única responsabilidade: `Ball` gerencia a bola, `Renderer` cuida da tela, `Game` coordena o jogo |
| **O** — Open/Closed | Novos controladores podem ser adicionados sem alterar `Game` ou qualquer outra classe |
| **L** — Liskov Substitution | `HumanController` e `AIController` são intercambiáveis onde se espera um `PlayerController` |
| **I** — Interface Segregation | `PlayerController` expõe apenas `update(paddle, ball)` |
| **D** — Dependency Inversion | `Game` depende da abstração `PlayerController`, não das implementações concretas |

---

## Extensibilidade

Para adicionar um novo controlador, herde de `PlayerController` e implemente `update()`:

```python
class NetworkController(PlayerController):
    def update(self, paddle: Paddle, ball: Ball) -> None:
        paddle.move(self._receive_input())
```

Passe-o ao instanciar o jogo:

```python
Game(HumanController(), NetworkController()).run()
```
