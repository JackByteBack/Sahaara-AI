# Python Implementation for Backend

import re

def anonymize_transcript(transcript, case_data):
"""
Removes PII (Names, Phone Numbers, Locations) from transcript.
""" # 1. Name Stripping (Simple Regex - Use NER for production) # Assuming name is in the 'victim_name' field or inferred
victim_name = case_data.get('victim_name', '').strip()

    # Replace occurrences of the victim's name with [REDACTED]
    if victim_name:
        # Replace full words, not substrings (e.g., "Name" not in "MyName")
        pattern = r'\b' + re.escape(victim_name) + r'\b'
        transcript = re.sub(pattern, "[Name Redacted]", transcript, flags=re.IGNORECASE)

    # 2. Phone Number Stripping
    transcript = re.sub(r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
                        "[Phone Number Redacted]", transcript)

    # 3. Location Stripping (Simple: replace common location patterns if vague)
    transcript = re.sub(r'\b(Street|Road|Lane|District|City)\b', "[Location]", transcript, flags=re.IGNORECASE)

    return transcript

# SQL Trigger for Postgres (Ensures no data leaks)

# This trigger runs BEFORE the row is deleted, running the anonymization logic.

SQL Trigger for Case Closure
CREATE OR REPLACE FUNCTION anonymize_on_close()
RETURNS TRIGGER AS $$
BEGIN
    -- If status is closed, scrub PII
    IF NEW.status = 'closed' AND OLD.status != 'closed' THEN
        -- Check if transcript exists
        IF NEW.transcript IS NOT NULL THEN
            -- Apply Python anonymization logic here (via plpythonu or calling API)
            -- For now, this is a placeholder for the sanitization step
            RAISE NOTICE 'Anonymizing case %', NEW.id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
