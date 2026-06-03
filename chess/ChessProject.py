import tkinter as tk
from tkinter import messagebox
import chess
import chess.engine


class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Chess vs Stockfish")

        self.board = chess.Board()
        self.selected_square = None
        self.square_size = 72

        self.engine = chess.engine.SimpleEngine.popen_uci(
            "engine/stockfish/stockfish-windows-x86-64-avx2.exe"
        )

        self.light_color = "#F0D9B5"
        self.dark_color = "#B58863"
        self.select_color = "#F6F669"
        self.move_color = "#A9D18E"

        self.piece_symbols = {
            "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
            "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚"
        }

        self.status_label = tk.Label(
            root,
            text="White to move",
            font=("Arial", 14, "bold"),
            pady=10
        )
        self.status_label.pack()

        board_pixel = self.square_size * 8
        self.canvas = tk.Canvas(
            root,
            width=board_pixel,
            height=board_pixel,
            highlightthickness=0
        )
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.on_click)

        self.draw_board()
        self.update_status()

    def draw_board(self):
        self.canvas.delete("all")

        legal_targets = set()

        if self.selected_square is not None:
            for move in self.board.legal_moves:
                if move.from_square == self.selected_square:
                    legal_targets.add(move.to_square)

        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size

                square = chess.square(col, 7 - row)

                color = self.light_color if (row + col) % 2 == 0 else self.dark_color

                if square == self.selected_square:
                    color = self.select_color
                elif square in legal_targets:
                    color = self.move_color

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline="black"
                )

                piece = self.board.piece_at(square)

                if piece:
                    symbol = self.piece_symbols[piece.symbol()]
                    self.canvas.create_text(
                        (x1 + x2) // 2,
                        (y1 + y2) // 2,
                        text=symbol,
                        font=("Arial", 34)
                    )

    def on_click(self, event):
        if self.board.turn == chess.BLACK:
            return

        if self.board.is_game_over():
            return

        col = event.x // self.square_size
        row = event.y // self.square_size

        if not (0 <= col < 8 and 0 <= row < 8):
            return

        clicked_square = chess.square(col, 7 - row)
        clicked_piece = self.board.piece_at(clicked_square)

        if self.selected_square is None:
            if clicked_piece and clicked_piece.color == chess.WHITE:
                self.selected_square = clicked_square
                self.draw_board()
            return

        if clicked_square == self.selected_square:
            self.selected_square = None
            self.draw_board()
            return

        if clicked_piece and clicked_piece.color == chess.WHITE:
            self.selected_square = clicked_square
            self.draw_board()
            return

        move = chess.Move(self.selected_square, clicked_square)

        if move in self.board.legal_moves:
            self.player_move(move)
            return

        if self.is_pawn_promotion(self.selected_square, clicked_square):
            promotion_move = chess.Move(
                self.selected_square,
                clicked_square,
                promotion=chess.QUEEN
            )

            if promotion_move in self.board.legal_moves:
                self.player_move(promotion_move)
                return

        self.selected_square = None
        self.draw_board()

    def player_move(self, move):
        self.board.push(move)

        self.selected_square = None
        self.draw_board()
        self.update_status()
        self.check_game_over()

        if not self.board.is_game_over():
            self.root.after(300, self.ai_move)

    def ai_move(self):
        if self.board.is_game_over():
            return

        result = self.engine.play(
            self.board,
            chess.engine.Limit(time=0.5)
        )

        self.board.push(result.move)

        self.draw_board()
        self.update_status()
        self.check_game_over()

    def is_pawn_promotion(self, from_sq, to_sq):
        piece = self.board.piece_at(from_sq)

        if not piece or piece.piece_type != chess.PAWN:
            return False

        rank = chess.square_rank(to_sq)
        return rank == 0 or rank == 7

    def update_status(self):
        turn_text = "White to move" if self.board.turn == chess.WHITE else "Stockfish thinking..."

        if self.board.is_check():
            turn_text += "  |  Check!"

        self.status_label.config(text=turn_text)

    def check_game_over(self):
        if self.board.is_checkmate():
            winner = "Stockfish" if self.board.turn == chess.WHITE else "White"
            messagebox.showinfo("Game Over", f"Checkmate! {winner} wins.")

        elif self.board.is_stalemate():
            messagebox.showinfo("Game Over", "Stalemate!")

        elif self.board.is_insufficient_material():
            messagebox.showinfo("Game Over", "Draw by insufficient material!")

        elif self.board.is_seventyfive_moves():
            messagebox.showinfo("Game Over", "Draw by seventy-five move rule!")

        elif self.board.is_fivefold_repetition():
            messagebox.showinfo("Game Over", "Draw by fivefold repetition!")

    def on_close(self):
        self.engine.quit()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ChessGUI(root)

    root.protocol("WM_DELETE_WINDOW", app.on_close)

    root.mainloop()


if __name__ == "__main__":
    main()