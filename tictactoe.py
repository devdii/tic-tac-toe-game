import json
import sys
import random
from pathlib import Path

def initialize_game():
    return {
        'board': [' '] * 9,
        'current_player': 'X',
        'game_over': False,
        'winner': None
    }

def load_game():
    try:
        with open('tictactoe.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return initialize_game()

def save_game(state):
    with open('tictactoe.json', 'w') as f:
        json.dump(state, f)
    generate_svg(state)

def generate_svg(state):
    svg = '''<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">
        <rect width="300" height="300" fill="white" stroke="black" stroke-width="2"/>
        <!-- Vertical lines -->
        <line x1="100" y1="0" x2="100" y2="300" stroke="black" stroke-width="2"/>
        <line x1="200" y1="0" x2="200" y2="300" stroke="black" stroke-width="2"/>
        <!-- Horizontal lines -->
        <line x1="0" y1="100" x2="300" y2="100" stroke="black" stroke-width="2"/>
        <line x1="0" y1="200" x2="300" y2="200" stroke="black" stroke-width="2"/>
    '''
    
    # Add X's and O's
    for i in range(9):
        x = (i % 3) * 100 + 50
        y = (i // 3) * 100 + 50
        if state['board'][i] == 'X':
            svg += f'''
            <line x1="{x-30}" y1="{y-30}" x2="{x+30}" y2="{y+30}" stroke="red" stroke-width="4"/>
            <line x1="{x+30}" y1="{y-30}" x2="{x-30}" y2="{y+30}" stroke="red" stroke-width="4"/>
            '''
        elif state['board'][i] == 'O':
            svg += f'''
            <circle cx="{x}" cy="{y}" r="30" stroke="blue" stroke-width="4" fill="none"/>
            '''
    
    # Add game status
    if state['game_over']:
        status = "Game Over - " + (f"Winner: {state['winner']}" if state['winner'] else "It's a tie!")
        svg += f'''
        <text x="150" y="280" font-family="Arial" font-size="14" text-anchor="middle">{status}</text>
        '''
    else:
        svg += f'''
        <text x="150" y="280" font-family="Arial" font-size="14" text-anchor="middle">Current Player: {state['current_player']}</text>
        '''
    
    svg += '</svg>'
    
    with open('tic_tac_toe.svg', 'w') as f:
        f.write(svg)

def check_winner(board):
    # Check rows
    for i in range(0, 9, 3):
        if board[i] == board[i+1] == board[i+2] != ' ':
            return board[i]
    
    # Check columns
    for i in range(3):
        if board[i] == board[i+3] == board[i+6] != ' ':
            return board[i]
    
    # Check diagonals
    if board[0] == board[4] == board[8] != ' ':
        return board[0]
    if board[2] == board[4] == board[6] != ' ':
        return board[2]
    
    return None

def is_board_full(board):
    return ' ' not in board

def computer_move(state):
    available_moves = [i for i, cell in enumerate(state['board']) if cell == ' ']
    if available_moves:
        return random.choice(available_moves)
    return None

def process_move(position):
    state = load_game()
    
    if state['game_over']:
        return
    
    position = int(position)
    
    # Human move
    if state['board'][position] == ' ':
        state['board'][position] = state['current_player']
        
        # Check for winner after human move
        winner = check_winner(state['board'])
        if winner:
            state['game_over'] = True
            state['winner'] = winner
        elif is_board_full(state['board']):
            state['game_over'] = True
        else:
            # Switch player to O (computer)
            state['current_player'] = 'O'
            save_game(state)
            
            # Computer move
            if not state['game_over']:
                computer_pos = computer_move(state)
                if computer_pos is not None:
                    state['board'][computer_pos] = 'O'
                    
                    # Check for winner after computer move
                    winner = check_winner(state['board'])
                    if winner:
                        state['game_over'] = True
                        state['winner'] = winner
                    elif is_board_full(state['board']):
                        state['game_over'] = True
                
                # Switch back to X (human)
                state['current_player'] = 'X'
    
    save_game(state)

def reset_game():
    initial_state = initialize_game()
    save_game(initial_state)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'move':
            process_move(sys.argv[2])
        elif sys.argv[1] == 'reset':
            reset_game()