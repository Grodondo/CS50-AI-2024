import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.crossword.variables:
            for word in self.crossword.words:
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        revised = False
        overlap = self.crossword.overlaps[x, y]

        if overlap is None:
            return False
        
        words_to_delete = []

        # We look through all of the words inside the domains of the variables[x,y]
        for word_in_dom_x in self.domains[x]:
            word_is_consistent = False
            for word_in_dom_y in self.domains[y]:
                # We check if the overlapping characters in both words are the same
                if word_in_dom_x[overlap[0]] == word_in_dom_y[overlap[1]]:
                    word_is_consistent = True
                    break
            if word_is_consistent is False:
                words_to_delete.append(word_in_dom_x)
                revised = True
                            

                    
                    
        # We remove all of the words that did not match from the domain of X
        for word in words_to_delete:
            self.domains[x].remove(word)

        return revised
    

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        queue = []
        queue = arcs if arcs is not None else [
            (x, y) for x in self.crossword.variables for y in self.crossword.variables if x != y and self.crossword.overlaps[x, y] is not None
        ] 
        while queue:
            (x, y) = queue.pop(0)
            if self.revise(x, y):
                if (len(self.domains[x]) == 0):
                    return False
                for neighbor_x in self.crossword.neighbors(x):
                    if neighbor_x is not y:
                        queue.append(neighbor_x, x)
                #TODO for each Z in X.neighbors - {Y}:
                    #Enqueue(queue, (Z,X))
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        for variable in self.crossword.variables:
            if variable not in assignment or assignment[variable] is None:
                return False 
        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        words_in_assignment = list(assignment.values())
        if len(words_in_assignment) != len(set(words_in_assignment)):
            return False

        for var, word in assignment.items():
            if var.lenght != len(word):
                return False

        for var in assignment.keys():
            for neighbor in self.crossword.neighbors(var):
                    overlap = self.crossword.overlaps[neighbor, var]
                    if overlap is None:
                        return False
                    
                    """
                    # We look through all of the words inside the domains of the variables[x,y]
                    for word_in_dom_n in self.domains[neighbor]:
                        for word_in_dom_v in self.domains[var]:
                            # We check if the overlapping characters in both words are the same
                            if word_in_dom_n[overlap[0]] != word_in_dom_v[overlap[1]]:
                    """

        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        ordered_words = list(self.domains[var])
        # TODO


        return ordered_words

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_vars = [var for var in self.crossword.variables if var not in assignment]

        selected_vars = []
        max_n_words = float('inf')

        # We look for the variable with the minimum number of remaining values in its domain
        for var in unassigned_vars:
            n_words = len(self.domains[var])
            
            if n_words == max_n_words:
                selected_vars.append(var)
            elif n_words < max_n_words:
                max_n_words = n_words
                selected_vars.clear()
                selected_vars.append(var)

        # If there is a tie, we select the variable with the highest degree
        selected_var = None
        if len(selected_vars) > 1:
            max_degree = -1
            for var in selected_vars:
                degree = len(self.crossword.neighbors(var))
                if max_degree < degree:
                    max_degree = degree
                    selected_var = var
        else:
            selected_var = selected_vars[0]

        return selected_var

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for word in self.order_domain_values(var, assignment):
            assignment[var] = word
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            assignment[var] = None


        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
