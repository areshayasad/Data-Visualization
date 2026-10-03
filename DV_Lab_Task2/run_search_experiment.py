"""
Task 1, Step 2 - run this yourself, in a real terminal, with a real person.

    python3 run_search_experiment.py

Needs a display (it opens a matplotlib window per trial) and someone willing to
answer 18 quick yes/no questions. Takes about 3-5 minutes.
"""
import time
import random
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DATA = Path("data")
SEED = 42  # do not change - keeps the 18-trial selection identical for everyone

SHAPE_MARKER = {"circle": "o", "square": "s"}


def draw_trial(trial_id, ax, df):
    rows = df[df["trial"] == trial_id]
    for (colour, shape), g in rows.groupby(["colour", "shape"]):
        ax.scatter(g["x"], g["y"], c=colour, marker=SHAPE_MARKER[shape], s=180,
                   edgecolor="none", zorder=3)
    ax.set_xlim(-0.5, rows["x"].max() + 0.5)
    ax.set_ylim(-0.5, rows["y"].max() + 0.5)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def pick_trials(df, rng):
    """2 trials per (condition, set_size) cell: one target-present, one target-absent."""
    chosen = []
    for condition in ("colour", "shape", "conjunction"):
        for set_size in (9, 16, 25, 36, 49):
            for present in ("yes", "no"):
                cell = df[(df.condition == condition) & (df.set_size == set_size)
                          & (df.target_present == present)]
                trial_id = rng.choice(cell["trial"].unique().tolist())
                chosen.append(trial_id)
    return chosen


def main():
    df = pd.read_csv(DATA / "stimuli_search.csv")
    rng = random.Random(SEED)
    trials = pick_trials(df, rng)
    rng.shuffle(trials)  # presentation order is shuffled; selection above is not

    print("18 trials. For each: look, then answer y (target present) or n (target absent).")
    name = input("Tester's name (first name or 'a classmate' is fine): ").strip()

    results = []
    current_condition = None
    for trial_id in trials:
        row = df[df.trial == trial_id].iloc[0]
        if row.condition != current_condition:
            current_condition = row.condition
            target_desc = {"colour": "a RED circle", "shape": "a BLUE square",
                            "conjunction": "a RED circle (not a red square, not a blue circle)"}[current_condition]
            input(f"\nNew block: {current_condition}. Target to look for: {target_desc}. Press Enter when ready.")

        fig, ax = plt.subplots(figsize=(6, 6))
        draw_trial(trial_id, ax, df)
        plt.show(block=False)
        plt.pause(0.05)

        t0 = time.perf_counter()
        answer = input("  Target present? (y/n): ").strip().lower()
        rt_ms = (time.perf_counter() - t0) * 1000
        plt.close(fig)

        truth = "yes" if row.target_present == "yes" else "no"
        given = "yes" if answer.startswith("y") else "no"
        results.append({
            "tester": name, "trial": trial_id, "condition": row.condition,
            "set_size": row.set_size, "target_present": row.target_present,
            "response": given, "correct": given == truth, "rt_ms": round(rt_ms, 1),
        })

    out = pd.DataFrame(results)
    out.to_csv(DATA / "search_results.csv", index=False)
    print(f"\nSaved {len(out)} rows to data/search_results.csv")
    print(f"Accuracy: {out['correct'].mean():.0%}")


if __name__ == "__main__":
    main()
