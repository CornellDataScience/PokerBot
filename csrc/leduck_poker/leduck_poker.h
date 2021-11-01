// Copyright (c) Facebook, Inc. and its affiliates.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once

#include <assert.h>

#include <limits>
#include <memory>
#include <string>
#include <vector>

namespace leduck_poker
{

  using Action = int;

  // Public state of the game without tracking the history of the game.
  struct PartialPublicState
  {
    // Previous call.
    //-1: raise, 0: fold, 1: check, 2: call, 3: bet, MIN_INT: kInitialAction
    Action last_action;
    // Player to make move next.
    int player_id;
    double relative_pot;
    int starting_player;
    bool river;
    std::pair<int, int> community_pot;
    std::pair<int, int> stack;

    bool operator==(const PartialPublicState &state) const
    {
      return last_action == state.last_action && player_id == state.player_id && relative_pot == state.relative_pot && starting_player == state.starting_player && river == state.river;
    }
  };

  class Game
  {
  public:
    const int deck_size;
    std::pair<int, int> starting_community_pot;
    std::pair<int, int> starting_stack;
    //const int starting_player;

    Game(int deck_size, std::pair<int, int> community_pot, std::pair<int, int> stack)
        : deck_size(deck_size),
          num_actions_(4),
          num_hands_(deck_size),
          starting_community_pot(community_pot),
          starting_stack(stack)
    {
    }

    // Number of dice for all the players.
    int get_deck_size() const { return deck_size; }
    // Maximum number of distinct actions in every node.
    Action num_actions() const { return num_actions_; }
    // Number of distrinct game states at the beginning of the game. In other
    // words, number of different realization of the chance nodes.
    int num_hands() const { return num_hands_; }
    // Community pot(ante)
    // std::pair<int, int> get_community_pot() { return community_pot; }
    // //stack
    // std::pair<int, int> get_stack() { return stack; }
    // Upper bound for how deep game tree could be.
    int max_depth() const { return 8; }

    PartialPublicState get_initial_state() const
    {
      PartialPublicState state;
      state.last_action = kInitialAction;
      state.player_id = 0;
      state.starting_player = 0;
      state.community_pot = starting_community_pot;
      state.stack = starting_stack;
      state.river = false;
      return state;
    }

    // Get range of possible actions in the state as [min_action, max_action).

    // -1 = raise
    // 0 = fold
    // 1 = call
    // 2 = check
    // 3 = bet
    //If bet then we can fold call raise
    //If call then we're at river restart or end of game
    //If check then we use heuristic with starting players
    //If raise then fold or call

    std::pair<int, int> get_action_list(
        const PartialPublicState &state) const
    {
      if (!is_terminal(state))
      {
        if (state.last_action == kInitialAction || state.last_action == 1){//If call then we're at river restart or end of game
          return std::pair<int, int>(2, 4);
        }else if (state.last_action == 3){//If bet then we can fold call raise
          return std::pair<int, int>(-1, 2);
        }else if (state.last_action == 2){//If check then we use heuristic with starting players
          return std::pair<int, int>(2, 4);
        }else{//If raise then fold or call
          return std::pair<int, int>(0, 2);
        }
      }
      else
      {
        return std::pair<int, int>(2, 2);
      }
    }

    bool is_terminal(const PartialPublicState &state) const
    {
      return ((state.last_action == 0) || (state.river && state.last_action == 1) }} (state.river && state.last_action == 2 && state.starting_player == 1 - state.player_id);
    }

    PartialPublicState act(const PartialPublicState &state, Action action) const
    {
      const auto action_list = get_action_list(state);
      assert(action == action_list.first || action == (action_list.second - 1));
      PartialPublicState new_state;
      new_state.last_action = action;
      new_state.community_pot = state.community_pot;
      new_state.stack = state.stack;

      //betting and state
      if (action == 1 || action == 3)
      {
        if (state.player_id == 0)
        {
          new_state.community_pot.first += 1;
          new_state.stack.first -= 1;
        }
        else
        {
          new_state.community_pot.second += 1;
          new_state.stack.second -= 1;
        }
      }
      new_state.player_id = 1 - state.player_id;
      return new_state;
    }

    std::string action_to_string(Action action) const;
    std::string state_to_string(const PartialPublicState &state) const;

  private:
    static constexpr int kInitialAction = INT_MIN;
    const Action num_actions_;
    const int num_hands_;
  };

} // namespace kuhn_poker