from RubiksBot import RubiksBot
from RubiksSolver import RubiksSolver
import kociemba

"""
Instructions: 

    -For inputting cube state:
    Upon calling main() you will be promted to enter the current state of the unsolved cube.
    On a hard surface, place the Rubiks cube with the side with the green middle square facing you
    and the side with the middle white square facing up. As you are prompted for each side, read the
    side from top left to bottom right and enter the first letter of each square color consecutively,
    without spaces in between. For the top and bottom sides, from the initial starting orientation
    that was specified above, rotate the cube 90degrees to the bottom and -90degrees to the top 
    respectively. From each of these positions, you can once again read the side state from top
    left to bottom right, line by line and input as a string.

    -For placing cube into bot:
    When you are facing the bot, place the cube with the side with the green middle square facing you
    and the side with the white middle square facing above.
"""



def main():
    """Main driver function for Rubiks cube solver program."""

    bot = RubiksBot()
    solver = RubiksSolver(None)

    # 1. Set start cube state
    state = {}
    letter_to_color_conv = {'g': 'Green', 'b': 'Blue', 'o': 'Orange', 'r': 'Red', 'w': 'White', 'y': 'Yellow'}
    for side in ['FACE', 'BACK', 'LEFT', 'RIGHT', 'TOP', 'BOTTOM']:
        side_input = input(f"Please enter state for {side}: ")    # Input will be a string of length 9, each letter representing first letter of color
        side_input = [i for i in side_input]  # Convert string to a list

        # Replace each letter in list with its respective color
        for i in range(len(side_input)):
            side_input[i] = letter_to_color_conv[side_input[i]]
        
        # Store side input to dict
        state[side] = side_input
    
    solver.cube_state = state   # Set state

    # 2. Get cube solution
    kociemba_input = solver.encode_before_kociemba()        # Prepare input for kociemba using current cube state
    kociemba_output = kociemba.solve(kociemba_input)        # Access the solution string
    decoded_solution = solver.decode_after_kociemba(kociemba_output)  # Decode the solution into a list of moves. Ex: [[side, direction], [...], ...]


    # 3. Execute moves through bot
    for side, direction in decoded_solution:
        
        bot.load_side(side)   # Load side to rotate
        
        # Update cube state in script
        solver.current_side_being_moved = side
        solver.current_direction_of_rotation = direction
        solver.make_move() # Make virtual move (Also updates cube state)
         
        bot.turn_cube(direction)    # Rotate cube
        
    print("Cube solved: ", solver.is_solved())


if __name__ =='__main__':
    main()
