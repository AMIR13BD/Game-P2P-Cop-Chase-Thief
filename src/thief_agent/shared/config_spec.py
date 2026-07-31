"""Appendix F specification tables: required fields, fixed values, minimums, defaults."""

REQUIRED = {
    "board_and_agents": [
        "grid_size",
        "num_agents",
        "thief_start",
        "cop_start",
        "axis_origin_corner",
        "axis_start_index",
    ],
    "world": ["map_area", "hint_max_words"],
    "movement_and_barriers": ["move_set", "max_barriers", "max_moves", "survival_threshold"],
    "scoring": [
        "capture_cop",
        "capture_thief",
        "survival_cop",
        "survival_thief",
        "tie_score",
        "technical_loss",
    ],
    "pheromones": ["pheromone_center_intensity", "pheromone_decay", "pheromone_grid_size"],
    "network_and_league": [
        "response_timeout_sec",
        "watchdog_timeout_sec",
        "num_games",
        "diversity_reward",
        "min_games_to_pass",
        "token_budget_per_series",
        "max_games_per_team",
    ],
    "rate_limiter_gatekeeper": [
        "requests_per_minute",
        "concurrent_requests",
        "retry_backoff_sec",
        "max_retries",
        "queue_depth",
    ],
}
FIXED = {
    "num_agents": 2,
    "pheromone_center_intensity": 0.9,
    "pheromone_decay": 0.10,
    "pheromone_grid_size": 5,
    "capture_cop": 20,
    "capture_thief": 5,
    "survival_cop": 5,
    "survival_thief": 10,
    "tie_score": 2,
    "technical_loss": 0,
}
MINIMUMS = {
    "grid_size": 7,
    "max_barriers": 14,
    "max_moves": 35,
    "survival_threshold": 35,
    "requests_per_minute": 30,
    "concurrent_requests": 2,
    "retry_backoff_sec": 5,
    "max_retries": 3,
    "queue_depth": 100,
}
NEG_DEFAULTS = {"map_area": "New York"}  # negotiable value default when empty
SUB_GAMES = 6  # counted series length is fixed at 6 (num_games=1 is illustrative per-run)
