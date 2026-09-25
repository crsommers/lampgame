import asyncio
import pygame

## pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

## predraw setup
screen.fill("purple")
pygame.display.flip()

## Mouse class
class Mouse:
    pos: tuple[int, int] = (400, 300)

    @staticmethod
    def update() -> None:
        """Updates the mouse state. Call this once per frame."""
        Mouse.pos = pygame.mouse.get_pos()

    @staticmethod
    def move_to(x: int, y: int) -> None:
        """Moves the mouse to the specified position."""
        pygame.mouse.set_pos((x, y))
        Mouse.pos = (x, y)

    @staticmethod
    def button(button: int) -> bool:
        """Returns True if the specified mouse button is pressed."""
        return pygame.mouse.get_pressed()[button]

    @staticmethod
    def draw() -> None:
        """Draws the mouse cursor on the specified surface."""
        pygame.draw.circle(screen, "white", Mouse.pos, 5)



## definitely not overcomplicated keypress handler
def on_keypress(key: int) -> None:
    print(f'[{pygame.key.name(key)}] was pressed')

## good 'ol ~~async~~ main()
async def main():
    while True:
        ## poll for events
        Mouse.update()

        ## event iterater
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN: on_keypress(event.key)

        ## Per-Frame Updates
        screen.fill((150, 0, 150))

        ## Per-Frame Renders
        Mouse.draw()

        ## update the full display every frame for ease of use
        pygame.display.flip()
        await asyncio.sleep(0)

asyncio.run(main())