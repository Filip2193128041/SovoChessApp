from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Game, Move, PlayerProfile

import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__)))
from game import Game as ChessGame, ChessBot

OPENINGS = {
    'e2e4': 'King\'s Pawn Opening',
    'e2e4 e7e5': 'Open Game',
    'e2e4 c7c5': 'Sicilian Defense',
    'e2e4 e7e6': 'French Defense',
    'e2e4 c7c6': 'Caro-Kann Defense',
    'e2e4 d7d5': 'Scandinavian Defense',
    'e2e4 g8f6': 'Alekhine\'s Defense',
    'e2e4 d7d6': 'Pirc Defense',
    'e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 a7a6': 'Sicilian Najdorf',
    'e2e4 c7c5 g1f3 d7d6 d2d4 c5d4 f3d4 g8f6 b1c3 g7g6': 'Sicilian Dragon',
    'e2e4 c7c5 g1f3 e7e6 d2d4 c5d4 f3d4 a7a6': 'Sicilian Kan',
    'e2e4 c7c5 b1c3': 'Closed Sicilian',
    'e2e4 c7c5 c2c3': 'Alapin Variation',
    'e2e4 e7e6 d2d4 d7d5 b1c3 g8f6': 'French Classical',
    'e2e4 e7e6 d2d4 d7d5 e4e5': 'French Advance',
    'e2e4 e7e6 d2d4 d7d5 b1d2': 'French Tarrasch',
    'e2e4 c7c6 d2d4 d7d5 e4e5': 'Caro-Kann Advance',
    'e2e4 c7c6 d2d4 d7d5 e4d5 c6d5': 'Caro-Kann Exchange',
    'e2e4 d7d5 e4d5 d8d5': 'Scandinavian Center Counter',
    'd2d4': 'Queen\'s Pawn Opening',
    'd2d4 d7d5': 'Closed Game',
    'd2d4 g8f6 c2c4 g7g6': 'King\'s Indian Defense',
    'd2d4 g8f6 c2c4 e7e6': 'Nimzo-Indian Defense',
    'd2d4 d7d5 c2c4': 'Queen\'s Gambit',
    'd2d4 d7d5 c2c4 e7e6': 'Queen\'s Gambit Declined',
    'd2d4 d7d5 c2c4 d5c4': 'Queen\'s Gambit Accepted',
    'd2d4 d7d5 c2c4 c7c6': 'Slav Defense',
    'd2d4 g8f6 c2c4 e7e6 g1f3 b7b6': 'Queen\'s Indian Defense',
    'd2d4 g8f6 c2c4 c7c5': 'Benoni Defense',
    'c2c4': 'English Opening',
    'c2c4 e7e5': 'English Reversed Sicilian',
    'c2c4 c7c5': 'Symmetrical English',
    'g1f3': 'Réti Opening',
    'f2f4': 'Bird\'s Opening',
    'b2b3': 'Larsen\'s Opening',
    'b2b4': 'Polish Opening',
    'e2e4 e7e5 g1f3 b8c6 f1b5': 'Ruy Lopez',
    'e2e4 e7e5 g1f3 b8c6 f1c4': 'Italian Game',
    'e2e4 e7e5 g1f3 b8c6 f1c4 f8c5': 'Giuoco Piano',
    'e2e4 e7e5 g1f3 b8c6 f1c4 g8f6': 'Two Knights Defense',
    'e2e4 e7e5 f2f4': 'King\'s Gambit',
    'e2e4 e7e5 g1f3 b8c6 d2d4': 'Scotch Game',
    'e2e4 e7e5 b1c3': 'Vienna Game',
    'd2d4 g8f6 g1f3 e7e6 c1f4': 'London System',
    'd2d4 g8f6 g1f3 e7e6 c1g5': 'Torre Attack',
    'd2d4 d7d5 g1f3 g8f6 e2e3': 'Colle System',
    'd2d4 g8f6 c2c4 e7e6 g1f3 d7d5 g2g3': 'Catalan Opening',
    'e2e4 e7e5 f1c4 b8c6 d1h5 g8f6 h5f7': 'Scholar\'s Mate',
    'f2f3 e7e5 g2g4 d8h4': 'Fool\'s Mate',
}

def identify_opening(move_list):
    moves_str = ' '.join([m.from_square + m.to_square for m in move_list])
    best_match = 'Unknown Opening'
    best_length = 0
    for moves, name in OPENINGS.items():
        if moves_str.startswith(moves) and len(moves) > best_length:
            best_match = name
            best_length = len(moves)
    return best_match

def calculate_elo(winner_rating, loser_rating, k=32):
    expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))
    new_winner_rating = round(winner_rating + k * (1 - expected_winner))
    new_loser_rating = round(loser_rating + k * (0 - expected_loser))
    return new_winner_rating, new_loser_rating

def handle_checkmate(chess_game, game_obj):
    loser = game_obj.white_player if chess_game.current_turn == 'w' else game_obj.black_player
    winner = game_obj.black_player if chess_game.current_turn == 'w' else game_obj.white_player

    if winner != loser:
        new_winner_rating, new_loser_rating = calculate_elo(
            winner.current_rating,
            loser.current_rating
        )
        winner.current_rating = new_winner_rating
        winner.save()
        loser.current_rating = new_loser_rating
        loser.save()
    else:
        new_winner_rating = winner.current_rating

    all_moves = Move.objects.filter(game=game_obj).order_by('move_number')
    opening = identify_opening(all_moves)
    game_obj.winner = winner
    game_obj.opening_name = opening
    game_obj.save()

    # update player profiles
    try:
        winner_profile = PlayerProfile.objects.get(user=winner)
        winner_profile.update_stats(won=True, opening=opening)
    except PlayerProfile.DoesNotExist:
        PlayerProfile.objects.create(user=winner, total_games=1, total_wins=1, favourite_opening=opening)

    try:
        loser_profile = PlayerProfile.objects.get(user=loser)
        loser_profile.update_stats(won=False, opening=opening)
    except PlayerProfile.DoesNotExist:
        PlayerProfile.objects.create(user=loser, total_games=1, total_losses=1)

    return winner, opening, new_winner_rating

def handle_stalemate(game_obj):
    all_moves = Move.objects.filter(game=game_obj).order_by('move_number')
    opening = identify_opening(all_moves)
    game_obj.opening_name = opening
    game_obj.save()
    return opening

def pos_to_square(pos):
    row, col = pos
    return chr(col + ord('a')) + str(8 - row)

# only one home view with leaderboard
def home(request):
    top_players = User.objects.order_by('-current_rating')[:10]
    return render(request, 'home.html', {'top_players': top_players})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Wrong username or password!')
    return render(request, 'login.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken!')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            # create a profile for the new user
            PlayerProfile.objects.create(user=user)
            login(request, user)
            return redirect('home')
    return render(request, 'register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def game_view(request, game_id):
    game = Game.objects.get(id=game_id)
    return render(request, 'game.html', {'game': game})

@login_required
def start_game(request):
    game = Game.objects.create(
        white_player=request.user,
        black_player=request.user
    )
    return redirect('game', game_id=game.id)

@csrf_exempt
def make_move(request, game_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        from_square = data['from']
        to_square = data['to']

        def square_to_pos(square):
            col = ord(square[0]) - ord('a')
            row = 8 - int(square[1])
            return (row, col)

        from_pos = square_to_pos(from_square)
        to_pos = square_to_pos(to_square)

        game_obj = Game.objects.get(id=game_id)
        chess_game = ChessGame()

        past_moves = Move.objects.filter(game=game_obj).order_by('move_number')
        for move in past_moves:
            chess_game.make_move(
                square_to_pos(move.from_square),
                square_to_pos(move.to_square)
            )

        valid = chess_game.make_move(from_pos, to_pos)

        if valid:
            Move.objects.create(
                game=game_obj,
                move_number=past_moves.count() + 1,
                from_square=from_square,
                to_square=to_square
            )

            # check checkmate after player move
            if chess_game.is_checkmate():
                winner, opening, new_rating = handle_checkmate(chess_game, game_obj)
                return JsonResponse({
                    'valid': True,
                    'checkmate': True,
                    'stalemate': False,
                    'winner': winner.username,
                    'opening': opening,
                    'new_rating': new_rating
                })

            # check stalemate after player move
            if chess_game.is_stalemate():
                opening = handle_stalemate(game_obj)
                return JsonResponse({
                    'valid': True,
                    'checkmate': False,
                    'stalemate': True,
                    'opening': opening
                })

            # bot makes a move for black
            bot = ChessBot(color='b')
            bot_move = bot.get_random_move(chess_game)

            if bot_move:
                bot_from_pos, bot_to_pos = bot_move
                chess_game.make_move(bot_from_pos, bot_to_pos)

                bot_from_square = pos_to_square(bot_from_pos)
                bot_to_square = pos_to_square(bot_to_pos)

                Move.objects.create(
                    game=game_obj,
                    move_number=past_moves.count() + 2,
                    from_square=bot_from_square,
                    to_square=bot_to_square
                )

                # check checkmate after bot move
                if chess_game.is_checkmate():
                    winner, opening, new_rating = handle_checkmate(chess_game, game_obj)
                    return JsonResponse({
                        'valid': True,
                        'checkmate': True,
                        'stalemate': False,
                        'winner': winner.username,
                        'opening': opening,
                        'new_rating': new_rating
                    })

                # check stalemate after bot move
                if chess_game.is_stalemate():
                    opening = handle_stalemate(game_obj)
                    return JsonResponse({
                        'valid': True,
                        'checkmate': False,
                        'stalemate': True,
                        'opening': opening
                    })

            return JsonResponse({'valid': True, 'checkmate': False, 'stalemate': False})
        else:
            return JsonResponse({'valid': False})

    return JsonResponse({'error': 'Invalid request'})


def get_position(request, game_id):
    game_obj = Game.objects.get(id=game_id)
    past_moves = Move.objects.filter(game=game_obj).order_by('move_number')

    chess_game = ChessGame()

    def square_to_pos(square):
        col = ord(square[0]) - ord('a')
        row = 8 - int(square[1])
        return (row, col)

    for move in past_moves:
        chess_game.make_move(
            square_to_pos(move.from_square),
            square_to_pos(move.to_square)
        )

    fen = board_to_fen(chess_game.board)
    return JsonResponse({'fen': fen})


def board_to_fen(board):
    fen = ''
    for row in range(8):
        empty = 0
        for col in range(8):
            piece = board.get_piece(row, col)
            if piece is None:
                empty += 1
            else:
                if empty > 0:
                    fen += str(empty)
                    empty = 0
                symbols = {
                    'Pawn': ('P', 'p'), 'Rook': ('R', 'r'),
                    'Knight': ('N', 'n'), 'Bishop': ('B', 'b'),
                    'Queen': ('Q', 'q'), 'King': ('K', 'k')
                }
                piece_type = type(piece).__name__
                white_sym, black_sym = symbols[piece_type]
                fen += white_sym if piece.color == 'w' else black_sym
        if empty > 0:
            fen += str(empty)
        if row < 7:
            fen += '/'
    return fen

def post_game(request, game_id):
    game = Game.objects.get(id=game_id)
    user_won = game.winner == request.user
    return render(request, 'post_game.html', {
        'game': game,
        'user_won': user_won,
    })