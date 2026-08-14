import pandas as pd

def gujarati_char_ratio(text):
    """Return the fraction of characters in a string that are Gujarati script."""
    if not isinstance(text, str) or len(text) == 0:
        return 0.0
    
    gujarati_count = sum(1 for ch in text if '\u0A80' <= ch <= '\u0AFF')
    total_letters = sum(1 for ch in text if ch.isalpha())  # count only letter characters, ignore punctuation/emoji/numbers
    
    if total_letters == 0:
        return 0.0
    return gujarati_count / total_letters


def classify_comment(text, threshold=0.85):
    """Classify a comment as 'pure_gujarati', 'candidate', or 'empty'."""
    ratio = gujarati_char_ratio(text)
    if ratio >= threshold:
        return "pure_gujarati"
    elif len(str(text).strip()) == 0:
        return "empty"
    else:
        return "candidate"  # keep for labeling: could be Gujlish or English


if __name__ == "__main__":
    df = pd.read_csv("data/raw/comments_raw.csv")
    df["category"] = df["text"].apply(classify_comment)

    print(df["category"].value_counts())

    df_candidates = df[df["category"] == "candidate"]
    df_candidates.to_csv("data/processed/candidates_for_labeling.csv", index=False)
    print(f"\nSaved {len(df_candidates)} candidate comments to data/processed/candidates_for_labeling.csv")