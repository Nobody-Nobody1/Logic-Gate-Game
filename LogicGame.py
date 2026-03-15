import tkinter as tk
import random

# Game settings
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 400
BALL_SIZE = 20
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 10
BALL_SPEED = 3

class CatchTheBallGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Catch the Ball Game")

        # Create canvas
        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="black")
        self.canvas.pack()

        # Create paddle
        self.paddle = self.canvas.create_rectangle(
            (WINDOW_WIDTH - PADDLE_WIDTH) / 2, WINDOW_HEIGHT - 30,
            (WINDOW_WIDTH + PADDLE_WIDTH) / 2, WINDOW_HEIGHT - 30 + PADDLE_HEIGHT,
            fill="white"
        )

        # Create ball
        self.ball = self.canvas.create_oval(
            random.randint(0, WINDOW_WIDTH - BALL_SIZE), 0,
            random.randint(0, WINDOW_WIDTH - BALL_SIZE) + BALL_SIZE, BALL_SIZE,
            fill="red"
        )

        # Game variables
        self.ball_dx = BALL_SPEED
        self.ball_dy = BALL_SPEED
        self.score = 0
        self.game_over = False

        # Score display
        self.score_text = self.canvas.create_text(50, 20, text="Score: 0", fill="white", font=("Arial", 14))

        # Bind controls
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)

        # Start game loop
        self.update_game()

    def move_left(self, event):
        if not self.game_over:
            self.canvas.move(self.paddle, -20, 0)

    def move_right(self, event):
        if not self.game_over:
            self.canvas.move(self.paddle, 20, 0)

    def update_game(self):
        if not self.game_over:
            # Move ball
            self.canvas.move(self.ball, self.ball_dx, self.ball_dy)
            ball_coords = self.canvas.coords(self.ball)
            paddle_coords = self.canvas.coords(self.paddle)

            # Bounce off walls
            if ball_coords[0] <= 0 or ball_coords[2] >= WINDOW_WIDTH:
                self.ball_dx = -self.ball_dx
            if ball_coords[1] <= 0:
                self.ball_dy = -self.ball_dy

            # Check collision with paddle
            if (paddle_coords[0] < ball_coords[2] and
                paddle_coords[2] > ball_coords[0] and
                paddle_coords[1] < ball_coords[3] and
                paddle_coords[3] > ball_coords[1]):
                self.ball_dy = -self.ball_dy
                self.score += 1
                self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

            # Check if ball hits bottom
            if ball_coords[3] >= WINDOW_HEIGHT:
                self.game_over = True
                self.canvas.create_text(WINDOW_WIDTH/2, WINDOW_HEIGHT/2,
                                        text="GAME OVER", fill="yellow", font=("Arial", 24))

            # Continue loop
            self.root.after(20, self.update_game)

# Run the game
if __name__ == "__main__":
    root = tk.Tk()
    game = CatchTheBallGame(root)
    root.mainloop()