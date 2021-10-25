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

#include "kuhn_poker.h"
#include "real_net.h"

#include <sstream>

namespace kuhn_poker {
std::string Game::action_to_string(Action action) const {
    if (action == 0) {
      return "fold";
    } else if (action == 1){
      return "check";
    } else if (action == 2){
      return "call";
    } else if (action == 3){{
      return "raise";
    }
  }
}

std::string Game::state_to_string(const PartialPublicState& state) const {
  std::ostringstream ss;
  const std::string last_action = state.last_action == kInitialAction
                                   ? "start"
                                   : action_to_string(state.last_action);
  ss << "(pid=" << state.player_id << ",last=" << last_action << ")";
  return ss.str();
}

}  // namespace kuhn_poker