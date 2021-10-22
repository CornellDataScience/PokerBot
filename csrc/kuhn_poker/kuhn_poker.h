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

namespace kuhn_poker
{

  using Action = int;

  // Public state of the game without tracking the history of the game.
  struct PartialPublicState
  {
    // Previous call.
    //0: fold, 1: check, 2: call, 3: bet
    Action last_action;
    // Player to make move next.
    int player_id;
    double relative_pot;
    int starting_player;

    bool operator==(const PartialPublicState &state) const
    {
      return last_action == state.last_action && player_id == state.player_id && relative_pot == state.relative_pot && starting_player == state.starting_player;
    }
  };

  class Game
  {
  public:
    const int deck_size;
    const std::pair<int, int> community_pot;
    const std::pair<int, int> stack;

    Game(int deck_size)
        : deck_size(deck_size),
          num_actions_(4),
          num_hands_(deck_size),
          community_pot_(community_pot),
          stack_(stack) {}

    // Number of dice for all the players.
    int deck_size() const { return deck_size_; }
    // Maximum number of distinct actions in every node.
    Action num_actions() const { return num_actions_; }
    // Number of distrinct game states at the beginning of the game. In other
    // words, number of different realization of the chance nodes.
    int num_hands() const { return num_hands_; }
    // Community pot(ante)
    std::pair<int, int> community_pot() const { return community_pot_; }
    //stack
    std::pair<int, int> stack() const { return stack_; }
    // Upper bound for how deep game tree could be.
    int max_depth() const { return 3; }

    PartialPublicState get_initial_state() const
    {
      PartialPublicState state;
      state.last_action = kInitialAction;
      state.player_id = 0;
      state.starting_player = 0;
      return state;
    }

    // Get range of possible actions in the state as [min_action, max_action).
    // 0 = fold
    // 1 = call
    // 2 = check
    // 3 = bet
    std::pair<int, int> get_action_list(
        const PartialPublicState &state) const
    {
      return state.last_action == kInitialAction || (state.starting_player == 1 - state.player_id && state.last_action == 1)
                 ? std::pair<int, int>(2, 3)
                 : std::pair<int, int>(0, 1);
    }

    bool is_terminal(const PartialPublicState &state) const
    {
      return state.last_action <= 1 || (state.last_action == 2 && state.player_id == 1 - state.starting_player);
    }

    PartialPublicState act(const PartialPublicState &state, Action action) const
    {
      const auto action_list = get_action_list(state);
      assert(action == action_list.first || action == action_list.second);
      PartialPublicState new_state;
      new_state.last_action = action;
      new_state.player_id = 1 - state.player_id;
      return new_state;
    }

    std::string action_to_string(Action action) const;
    std::string state_to_string(const PartialPublicState &state) const;

  private:
    static constexpr int kInitialAction = -1;
    const Action num_actions_;
    const int num_hands_;
  };

} // namespace kuhn_poker
