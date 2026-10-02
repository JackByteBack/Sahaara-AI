Requirement 2.9: Code-Switching Detection Algorithm

Technical implementation to split transcripts by language segment.

# Python Implementation

from langdetect import detect, LangDetectException
import math
def detect_code_switching(transcript_segments):
"""
transcript_segments: List of strings extracted from ASR.

    Returns:
        {
            "is_code_switched": boolean,
            "segments": [
                {"text": "...", "language": "hi"},
                {"text": "...", "language": "en"}
            ]
        }
    """
    is_switched = False
    processed_segments = []

    # Iterate through segments. If adjacent segments differ, flag switch.
    for i, segment in enumerate(transcript_segments):
        try:
            lang = detect(segment)
            processed_segments.append({
                "text": segment,
                "language": lang,
                "confidence": 0.9 # Placeholder for ASR confidence
            })

            # Check for switch with next segment
            if i < len(transcript_segments) - 1:
                next_seg = transcript_segments[i+1]
                next_lang = detect(next_seg)

                if lang != next_lang:
                    is_switched = True
                    # Add metadata about the switch point
                    processed_segments[i]["switch_point"] = True

        except LangDetectException:
            # If detection fails, default to English (or current setting)
            processed_segments.append({
                "text": segment,
                "language": "en",
                "confidence": 0.0
            })

    return {"is_code_switched": is_switched, "segments": processed_segments}

3. Requirement 2.5: Safety Override Engine

The strict logic rules that decide when to force high priority.

def calculate_final_priority(ai_score, audio_features, transcript_text):
"""
Implements Feature 2.5: Safety Override.
"""
safety_override_triggered = False

    # --- RULE SET 1: Immediate Physical Danger ---
    danger_keywords = ["gun", "knife", "threaten", "come at me", "dead", "kill"]
    if any(word in transcript_text.lower() for word in danger_keywords):
        return 1.0, True # Return Max Score + Override Flag

    # --- RULE SET 2: Volume Spike (Context-Aware) ---
    # If volume is SHOUTING AND distress keywords exist
    if audio_features['volume'] > 90 and audio_features['pitch_variance'] > 150:
        # Additional check to ensure it's not just network noise
        # If the user is screaming, it's an override.
        return 0.9, True
    # --- RULE SET 3: Whispering (Possible Coercion) ---
    # If user is whispering suddenly (Feature 2.12)
    if audio_features['volume'] < 20 and audio_features['volume'] > 5:
        # Check if transcript is about someone else being present
        if "he is here" in transcript_text.lower() or "they are listening" in transcript_text.lower():
            return 0.8, True
    # --- RULE SET 4: Fail-Safe for High Distress Score ---
    if ai_score > 0.8:
        return ai_score, False

    # Default calculation
    return ai_score, False
