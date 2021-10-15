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
#include <math.h>

#include <gtest/gtest.h>

#include "kuhn_poker.h"

using namespace liars_dice;

class GameTest : public ::testing::Test {
 protected:
  const std::pair<int, int> community_pot = std::pair<int, int>(1, 1);
  const std::pair<int, int> stack = std::pair<int, int>(10, 10);
  const int deck_size = 3;
  const Game game;
  const PartialPublicState root;

  GameTest() : game(deck_size), root(game.get_initial_state()) {}
};

TEST_F(GameTest, TestRoot) {
  ASSERT_EQ(root.player_id, 0);
  {
    auto range = game.get_action_list(root);
    ASSERT_EQ(range.first, 1);
    ASSERT_EQ(range.second, 3);
  }
  {
    auto range = game.get_action_list(game.act(root, 1));
    ASSERT_EQ(range.first, 1);
    ASSERT_EQ(range.second, 3);
  }
  {
    auto state = game.act(root, 3);
    auto range = game.action_list(state);
    ASSERT_EQ(range.first, 0);
    ASSERT_EQ(range.second, 2);
  }
  {
    auto state = game.act(root, 1);
    state = game.act(state, 3);
    auto range = game.get_action_list(state);
    ASSERT_EQ(range.first, 0);
    ASSERT_EQ(range.second, 2);
  }
}

/*TEST_F(GameTest, TestPlayerSequencw) {
  auto state = root;
  for (int i = 0; i < 4 * 6 + 1; ++i) {
    state = game.act(state, i);
    ASSERT_EQ(state.player_id, (i + 1) % 2);
  }
}*/
