from threading import Thread, Lock, Condition
from collections import deque, defaultdict
import time
import random

class Playground:
    def __init__(self, max_players):
        self.max_players = max_players
        self.current_team = None
        self.player_count = 0
        self.lock = Lock()
        self.cv = Condition(self.lock)
        self.waiting_players = defaultdict(int)
        self.waiting_teams = deque()
        self.players_to_release = 0

    def player_arrive(self, team_id, player_id):
        with self.cv:
            self.waiting_players[team_id] += 1
            if team_id not in self.waiting_teams:
                self.waiting_teams.append(team_id)
            while (
                not ((self.current_team is None and team_id == self.waiting_teams[0]) or
                not (team_id != self.current_team or
                self.players_to_release == 0))
            ):
                self.cv.wait()
            print(f'Player {player_id} Team {team_id} released. Queue: {self.waiting_teams}, Count: {self.player_count}')
            if self.current_team is None:
                next_team = self.waiting_teams[0]
                self.current_team = next_team
                self.players_to_release = min(self.waiting_players[next_team],
                                              self.max_players)

            self.waiting_players[self.current_team] -= 1
            self.players_to_release -= 1
            self.player_count += 1

            if self.players_to_release == 0 and self.waiting_players[self.current_team] == 0:
                self.waiting_teams.popleft()
    
    def player_leave(self, team_id, player_id):
        with self.cv:
            self.player_count -= 1
            print(f"Player {player_id} from Team {team_id} LEFT. Count: {self.player_count}")
            if self.player_count == 0:
                self.current_team = None
                print(f"Team {team_id} COMPLETED TURN. Queue: {self.waiting_teams}")
                self.cv.notify_all()

# # Simulation
def player_task(playground, team_id, player_id):
    time.sleep(random.uniform(1, 3))
    playground.player_arrive(team_id, player_id)
    time.sleep(random.uniform(0.5, 2))  # simulate playing
    playground.player_leave(team_id, player_id)


def main():
    playground = Playground(10)
    teams = [1, 2, 3]
    player_threads = []

    for i in range(100):
        t = Thread(target=player_task, args=[playground, random.choice(teams), i])
        player_threads.append(t)
        t.start()
    
    for t in player_threads:
        t.join()


if __name__ == "__main__":
    main()