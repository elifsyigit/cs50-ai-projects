import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"
    
    def known_mines(self):
        """
        Returns a set of all cells in self.cells known to be mines.
        If the number of remaining cells equals the count, all must be mines.
        """
        if len(self.cells) == self.count:
            return self.cells.copy()  # Return a copy to avoid modifying the original
        return set()
 
    def known_safes(self):
    
        if self.count == 0:
            return self.cells.copy()
        return set()



    def mark_mine(self, cell):
    
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1  # Since one of the mines is confirmed



    def mark_safe(self, cell):
        """
        Removes a cell from the sentence if it is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)



class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def get_neighbors(self, cell):
        """Returns a set of valid neighbor cells within the board."""
        row, col = cell
        neighbors = set()
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if 0 <= r < self.height and 0 <= c < self.width:
                    neighbors.add((r, c))
        return neighbors - self.moves_made  # Exclude known moves

    def add_knowledge(self, cell, count):
        """
        Updates AI knowledge after revealing a cell.
        """
        # Step 1 & 2: Record the move and mark it as safe
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Step 3: Add a new sentence to the knowledge base
        neighbors = self.get_neighbors(cell)
        if neighbors:
            self.knowledge.append(Sentence(neighbors, count))

        # Step 4 & 5: Process the knowledge base iteratively
        while True:
            prev_mines = self.mines.copy()
            prev_safes = self.safes.copy()
            prev_knowledge = self.knowledge.copy()

            # Identify and mark obvious mines and safe cells
            for sentence in self.knowledge[:]:  # Copy to avoid modifying during iteration
                if sentence.count == 0:
                    for safe in sentence.cells.copy():
                        self.mark_safe(safe)
                    self.knowledge.remove(sentence)
                elif len(sentence.cells) == sentence.count:
                    for mine in sentence.cells.copy():
                        self.mark_mine(mine)
                    self.knowledge.remove(sentence)

            # Infer new sentences using subset relationships
            new_sentences = []
            for s1 in self.knowledge:
                for s2 in self.knowledge:
                    if s1 != s2 and s1.cells.issubset(s2.cells):
                        remaining_cells = s2.cells - s1.cells
                        remaining_count = s2.count - s1.count
                        if remaining_cells and remaining_count >= 0:
                            new_sentence = Sentence(remaining_cells, remaining_count)
                            if new_sentence not in self.knowledge:
                                new_sentences.append(new_sentence)

            self.knowledge.extend(new_sentences)

            # Remove empty sentences
            self.knowledge = [s for s in self.knowledge if s.cells]

            # Stop if no new information is found
            if self.mines == prev_mines and self.safes == prev_safes and self.knowledge == prev_knowledge:
                break
                
    def make_safe_move(self):
    
        """
        Returns a safe cell to choose on the Minesweeper board.
        """
        # Find the first safe cell that has not already been chosen
        for safe in self.safes:
            if safe not in self.moves_made:
                return safe
        return None  # Return None if no safe moves are available

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_cells = {(r, c) for r in range(self.height) for c in range(self.width)}

        # Get available cells that are not mines or already chosen
        available_moves = all_cells - self.moves_made - self.mines

        if available_moves:
            return random.choice(list(available_moves))  # Choose a random available cell
        return None  # Return None if no moves are available
