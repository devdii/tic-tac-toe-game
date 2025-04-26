import json
import sys
import random
from pathlib import Path
import math

def initialize_game():
    return {
        'board': [' '] * 9,
        'current_player': 'X',
        'game_over': False,
        'winner': None,
        'difficulty': 'hard',  # Options: 'easy', 'medium', 'hard'
        'moves_history': [],
        'winning_line': None
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
    # Pre-calculate positions for better performance
    positions = [(i % 3 * 100 + 50, i // 3 * 100 + 50) for i in range(9)]
    
    # Base SVG template with gradient background
    svg = [
        '<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">',
        '<defs>',
        '  <linearGradient id="boardGradient" x1="0%" y1="0%" x2="100%" y2="100%">',
        '    <stop offset="0%" style="stop-color:#f3f4f6;stop-opacity:1" />',
        '    <stop offset="100%" style="stop-color:#e5e7eb;stop-opacity:1" />',
        '  </linearGradient>',
        '</defs>',
        '<rect width="300" height="300" fill="url(#boardGradient)" stroke="#374151" stroke-width="2"/>',
        '<line x1="100" y1="0" x2="100" y2="300" stroke="#374151" stroke-width="2"/>',
        '<line x1="200" y1="0" x2="200" y2="300" stroke="#374151" stroke-width="2"/>',
        '<line x1="0" y1="100" x2="300" y2="100" stroke="#374151" stroke-width="2"/>',
        '<line x1="0" y1="200" x2="300" y2="200" stroke="#374151" stroke-width="2"/>'
    ]
    
    # Add hover effect hints for empty cells
    for i, (x, y) in enumerate(positions):
        if state['board'][i] == ' ' and not state['game_over']:
            svg.append(f'<rect x="{x-45}" y="{y-45}" width="90" height="90" fill="transparent" stroke="none" opacity="0.3"/>')
    
    # Add X's and O's with animations
    for i, (x, y) in enumerate(positions):
        if state['board'][i] == 'X':
            svg.extend([
                f'<line x1="{x-30}" y1="{y-30}" x2="{x+30}" y2="{y+30}" stroke="#dc2626" stroke-width="4" stroke-linecap="round">',
                f'  <animate attributeName="stroke-dasharray" from="0,200" to="200,0" dur="0.4s" fill="freeze"/>',
                f'</line>',
                f'<line x1="{x+30}" y1="{y-30}" x2="{x-30}" y2="{y+30}" stroke="#dc2626" stroke-width="4" stroke-linecap="round">',
                f'  <animate attributeName="stroke-dasharray" from="0,200" to="200,0" dur="0.4s" fill="freeze"/>',
                f'</line>'
            ])
        elif state['board'][i] == 'O':
            svg.extend([
                f'<circle cx="{x}" cy="{y}" r="30" stroke="#2563eb" stroke-width="4" fill="none">',
                f'  <animate attributeName="stroke-dasharray" from="0,200" to="200,0" dur="0.4s" fill="freeze"/>',
                f'</circle>'
            ])
    
    # Draw winning line if game is won
    if state['winning_line']:
        start, end = state['winning_line']
        start_x, start_y = positions[start]
        end_x, end_y = positions[end]
        svg.extend([
            f'<line x1="{start_x}" y1="{start_y}" x2="{end_x}" y2="{end_y}" ',
            f'stroke="#059669" stroke-width="4" stroke-linecap="round">',
            f'  <animate attributeName="stroke-dasharray" from="0,400" to="400,0" dur="0.6s" fill="freeze"/>',
            f'</line>'
        ])
    
    # Add game status with enhanced styling
    if state['game_over']:
        status_color = '#059669' if state['winner'] else '#6b7280'
        status = "Game Over - " + ("Winner: " + state['winner'] if state['winner'] else "It's a tie!")
    else:
        status_color = '#dc2626' if state['current_player'] == 'X' else '#2563eb'
        status = f"Current Player: {state['current_player']}"
    
    # Add difficulty indicator
    difficulty_colors = {'easy': '#059669', 'medium': '#eab308', 'hard': '#dc2626'}
    svg.extend([
        f'<text x="150" y="280" font-family="Arial" font-size="14" text-anchor="middle" fill="{status_color}">{status}</text>',
        f'<text x="150" y="30" font-family="Arial" font-size="12" text-anchor="middle" fill="{difficulty_colors[state["difficulty"]]}">Difficulty: {state["difficulty"].title()}</text>'
    ])
    
    svg.append('</svg>')
    
    # Single write operation
    with open('tic_tac_toe.svg', 'w') as f:
        f.write('\n'.join(svg))

def get_winning_line(board):
    # Check rows
    for i in range(0, 9, 3):
        if board[i] == board[i+1] == board[i+2] != ' ':
            return (i, i+2)
    
    # Check columns
    for i in range(3):
        if board[i] == board[i+3] == board[i+6] != ' ':
            return (i, i+6)
    
    # Check diagonals
    if board[0] == board[4] == board[8] != ' ':
        return (0, 8)
    if board[2] == board[4] == board[6] != ' ':
        return (2, 6)
    
    return None

def check_winner(board):
    winning_line = get_winning_line(board)
    return board[winning_line[0]] if winning_line else None

def is_board_full(board):
    return ' ' not in board

def evaluate_board(board, depth):
    winner = check_winner(board)
    if winner == 'O':
        return 10 - depth
    elif winner == 'X':
        return depth - 10
    return 0

def get_empty_cells(board):
    return [i for i, cell in enumerate(board) if cell == ' ']

def minimax(board, depth, is_maximizing, alpha, beta):
    winner = check_winner(board)
    if winner or is_board_full(board) or depth == 0:
        return evaluate_board(board, depth)
    
    empty_cells = get_empty_cells(board)
    if is_maximizing:
        max_eval = -math.inf
        for pos in empty_cells:
            board[pos] = 'O'
            eval = minimax(board, depth - 1, False, alpha, beta)
            board[pos] = ' '
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for pos in empty_cells:
            board[pos] = 'X'
            eval = minimax(board, depth - 1, True, alpha, beta)
            board[pos] = ' '
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def get_best_move(state):
    board = state['board'].copy()
    difficulty = state['difficulty']
    empty_cells = get_empty_cells(board)
    
    if not empty_cells:
        return None
    
    # Easy mode: Random moves
    if difficulty == 'easy':
        return random.choice(empty_cells)
    
    # Medium mode: 70% smart moves, 30% random
    if difficulty == 'medium' and random.random() < 0.3:
        return random.choice(empty_cells)
    
    # Hard mode: Always best move
    best_score = -math.inf
    best_move = empty_cells[0]
    
    # Adjust depth based on difficulty
    max_depth = 6 if difficulty == 'hard' else 3
    
    for pos in empty_cells:
        board[pos] = 'O'
        score = minimax(board, max_depth, False, -math.inf, math.inf)
        board[pos] = ' '
        if score > best_score:
            best_score = score
            best_move = pos
    
    return best_move

def process_move(position):
    state = load_game()
    
    if state['game_over']:
        return
    
    position = int(position)
    
    # Human move
    if state['board'][position] == ' ':
        # Process human move
        state['board'][position] = 'X'
        state['moves_history'].append(position)
        
        # Check for winning line and update state
        winning_line = get_winning_line(state['board'])
        if winning_line:
            state['game_over'] = True
            state['winner'] = 'X'
            state['winning_line'] = winning_line
            state['current_player'] = 'X'
            save_game(state)
            return
        elif is_board_full(state['board']):
            state['game_over'] = True
            save_game(state)
            return
        
        # Computer move
        computer_pos = get_best_move(state)
        if computer_pos is not None:
            state['board'][computer_pos] = 'O'
            state['moves_history'].append(computer_pos)
            
            # Check game end conditions
            winning_line = get_winning_line(state['board'])
            if winning_line:
                state['game_over'] = True
                state['winner'] = 'O'
                state['winning_line'] = winning_line
            elif is_board_full(state['board']):
                state['game_over'] = True
        
        # Always keep X as current player for consistency
        state['current_player'] = 'X'
        
        # Single save operation at the end
        save_game(state)

def reset_game():
    initial_state = initialize_game()
    save_game(initial_state)

def set_difficulty(difficulty):
    if difficulty not in ['easy', 'medium', 'hard']:
        return
    state = load_game()
    state['difficulty'] = difficulty
    save_game(state)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'move':
            process_move(sys.argv[2])
        elif sys.argv[1] == 'reset':
            reset_game()
        elif sys.argv[1] == 'difficulty':
            set_difficulty(sys.argv[2])