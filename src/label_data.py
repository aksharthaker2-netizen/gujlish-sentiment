import msvcrt
import pandas as pd
import os

CANDIDATES_PATH = "data/processed/candidates_for_labeling.csv"
LABELED_PATH = "data/labeled/labeled_data.csv"

LABEL_KEYS = {
    "p": "positive",
    "n": "negative",
    "u": "neutral",
    "s": "not_gujlish",   # skip: pure English/Gujarati or spam
}

def load_progress():
    """Load already-labeled comment IDs so we don't re-label them."""
    if os.path.exists(LABELED_PATH):
        df_labeled = pd.read_csv(LABELED_PATH)
        return df_labeled, set(df_labeled["comment_id"])
    else:
        return pd.DataFrame(columns=["comment_id", "video_id", "text", "label"]), set()

def label_session():
    df_candidates = pd.read_csv(CANDIDATES_PATH)
    df_labeled, labeled_ids = load_progress()

    remaining = df_candidates[~df_candidates["comment_id"].isin(labeled_ids)]
    print(f"Already labeled: {len(labeled_ids)} | Remaining: {len(remaining)}\n")
    print("Keys: [p]ositive  [n]egative  [u]neutral  [s]kip (not gujlish)  [q]uit\n")

    new_labels = []

    for idx, row in remaining.iterrows():
        print("-" * 60)
        print(row["text"])
        print("-" * 60)

        while True:
            key = msvcrt.getch().decode("utf-8").lower()

            if key == "q":
                save_progress(df_labeled, new_labels)
                print(f"\nSaved. Labeled {len(new_labels)} this session.")
                return

            if key in LABEL_KEYS:
                new_labels.append({
                    "comment_id": row["comment_id"],
                    "video_id": row["video_id"],
                    "text": row["text"],
                    "label": LABEL_KEYS[key]
                })
                print(f"-> {LABEL_KEYS[key]}\n")
                break
            else:
                print("Invalid key. Use p/n/u/s/q.")

        # Save every 20 labels, in case of crash/power loss
        if len(new_labels) % 20 == 0:
            save_progress(df_labeled, new_labels)

    save_progress(df_labeled, new_labels)
    print(f"\nAll done! Labeled {len(new_labels)} this session.")

def save_progress(df_labeled, new_labels):
    if not new_labels:
        return
    df_new = pd.DataFrame(new_labels)
    df_combined = pd.concat([df_labeled, df_new], ignore_index=True)
    os.makedirs("data/labeled", exist_ok=True)
    df_combined.to_csv(LABELED_PATH, index=False)

if __name__ == "__main__":
    label_session()