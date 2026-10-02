"""Multilingual indicator lexicons (Features 1.1, 2.4, 2.6, 2.7, 2.12).

Every entry maps to an observable *indicator*, never a diagnosis (rules.md §General 2).
Lexicons cover the core release languages (en/hi/mr — Feature 1.3) plus romanized
variants common in Indian helpline texting (Feature 2.8/2.9 groundwork).
"""

# category -> severity weight (used by priority + profile layers)
CATEGORIES = {
    "distress": "distress",
    "self_harm": "safety",
    "immediate_danger": "safety",
    "coercion": "safety",
    "trauma": "distress",
    "vulnerability": "context",
}

# term -> (category, severity, confidence)
# severity: low | medium | high | critical
EN = {
    "i am scared": ("distress", "medium", 0.75),
    "scared": ("distress", "medium", 0.7),
    "afraid": ("distress", "medium", 0.7),
    "terrified": ("distress", "high", 0.8),
    "hopeless": ("distress", "high", 0.8),
    "worthless": ("distress", "high", 0.82),
    "lonely": ("distress", "medium", 0.65),
    "crying": ("distress", "medium", 0.65),
    "sad": ("distress", "low", 0.6),
    "depressed": ("distress", "medium", 0.7),
    "anxious": ("distress", "medium", 0.7),
    "can't take it": ("distress", "high", 0.78),
    "cannot take it": ("distress", "high", 0.78),
    "hurting myself": ("self_harm", "critical", 0.9),
    "hurt myself": ("self_harm", "critical", 0.9),
    "kill myself": ("self_harm", "critical", 0.95),
    "end my life": ("self_harm", "critical", 0.95),
    "suicide": ("self_harm", "critical", 0.95),
    "want to die": ("self_harm", "critical", 0.92),
    "no reason to live": ("self_harm", "critical", 0.9),
    "cutting myself": ("self_harm", "critical", 0.92),
    "kill you": ("immediate_danger", "critical", 0.9),
    "he is here": ("coercion", "high", 0.8),
    "they are listening": ("coercion", "high", 0.85),
    "he is listening": ("coercion", "high", 0.85),
    "i can't talk": ("coercion", "medium", 0.75),
    "i cannot talk": ("coercion", "medium", 0.75),
    "don't tell anyone": ("coercion", "high", 0.8),
    "he will hurt me": ("immediate_danger", "critical", 0.9),
    "threatening me": ("immediate_danger", "high", 0.85),
    "gun": ("immediate_danger", "critical", 0.9),
    "knife": ("immediate_danger", "critical", 0.88),
    "beat me": ("immediate_danger", "high", 0.85),
    "beating me": ("immediate_danger", "high", 0.88),
    "hitting me": ("immediate_danger", "high", 0.88),
    "i am in danger": ("immediate_danger", "critical", 0.9),
    "unsafe": ("immediate_danger", "high", 0.8),
    "no place to stay": ("vulnerability", "medium", 0.7),
    "no money": ("vulnerability", "medium", 0.65),
    "no one to help": ("vulnerability", "medium", 0.7),
    "alone with": ("vulnerability", "medium", 0.6),
    "he beats me": ("trauma", "high", 0.8),
    "i froze": ("trauma", "medium", 0.7),
    "nightmares": ("trauma", "medium", 0.72),
    "i keep thinking about": ("trauma", "medium", 0.68),
    "i was raped": ("trauma", "critical", 0.9),
    "rape": ("trauma", "critical", 0.9),
    "burning": ("immediate_danger", "high", 0.8),
    "i want to hurt him": ("distress", "medium", 0.6),
    "everyone would be better off": ("self_harm", "high", 0.8),
    "yelling": ("distress", "medium", 0.6),
    "screaming": ("distress", "medium", 0.6),
    "shouting": ("distress", "medium", 0.6),
    "drinking again": ("vulnerability", "medium", 0.6),
}

# Hindi (Devanagari)
HI = {
    "मुझे डर लग रहा है": ("distress", "medium", 0.75),
    "डर": ("distress", "medium", 0.65),
    "घबराहट": ("distress", "medium", 0.7),
    "उदास": ("distress", "medium", 0.7),
    "रो रही हूँ": ("distress", "medium", 0.7),
    "अकेली": ("distress", "medium", 0.65),
    "मदद": ("vulnerability", "low", 0.5),
    "जान से मारना": ("immediate_danger", "critical", 0.9),
    "मार दूंगा": ("immediate_danger", "critical", 0.88),
    "चाकू": ("immediate_danger", "critical", 0.85),
    "पीट रहा है": ("immediate_danger", "high", 0.85),
    "मारपीट": ("immediate_danger", "high", 0.8),
    "खुद को मार": ("self_harm", "critical", 0.9),
    "आत्महत्या": ("self_harm", "critical", 0.92),
    "जीने का मन नहीं": ("self_harm", "high", 0.85),
    "वह यहीं है": ("coercion", "high", 0.8),
    "सुन रहा है": ("coercion", "high", 0.82),
    "किसी को मत बताना": ("coercion", "high", 0.8),
    "धमकी": ("immediate_danger", "high", 0.8),
    "छत": ("vulnerability", "low", 0.4),
    "भूखा": ("vulnerability", "medium", 0.65),
    "कोई नहीं है": ("vulnerability", "medium", 0.68),
    "बार-बार याद आता है": ("trauma", "medium", 0.72),
    "सपने में आता है": ("trauma", "medium", 0.72),
}

# Marathi (Devanagari) — Feature 1.3 core language
MR = {
    "मला भीती वाटते": ("distress", "medium", 0.78),
    "भीती": ("distress", "medium", 0.68),
    "घाबरतो": ("distress", "medium", 0.68),
    "रडतो": ("distress", "medium", 0.68),
    "उद्विग्न": ("distress", "medium", 0.7),
    "एकटा": ("distress", "medium", 0.6),
    "मदत": ("vulnerability", "low", 0.5),
    "जगायची इच्छा नाही": ("self_harm", "critical", 0.9),
    "आत्महत्या": ("self_harm", "critical", 0.92),
    "स्वतःला मार": ("self_harm", "critical", 0.9),
    "तो इथे आहे": ("coercion", "high", 0.82),
    "ऐकत आहे": ("coercion", "high", 0.84),
    "कोणाला सांगू नका": ("coercion", "high", 0.8),
    "धमकी": ("immediate_danger", "high", 0.8),
    "वाढवतो": ("immediate_danger", "high", 0.78),
    "मारतो": ("immediate_danger", "high", 0.85),
    "खुणतो": ("immediate_danger", "critical", 0.85),
    "तलवार": ("immediate_danger", "critical", 0.85),
    "जागेशिवाय": ("vulnerability", "medium", 0.65),
    "पैसे नाहीत": ("vulnerability", "medium", 0.68),
    "कोणीच नाही": ("vulnerability", "medium", 0.68),
    "पुन्हा पुन्हा": ("trauma", "medium", 0.7),
    "स्वप्नात येते": ("trauma", "medium", 0.72),
    "हिंसा": ("trauma", "high", 0.8),
}

# Romanized (Hinglish/Marathi in text messages) — Feature 2.8/2.9 groundwork
ROMANIZED = {
    "dar lag raha hai": ("distress", "medium", 0.7),
    "bahut dar": ("distress", "medium", 0.7),
    "mujhe koi nahi samajhta": ("distress", "medium", 0.68),
    "mujhe maar dega": ("immediate_danger", "critical", 0.88),
    "jaan se maar dunga": ("immediate_danger", "critical", 0.9),
    "koi madad nahi": ("vulnerability", "medium", 0.65),
    "khudkushi": ("self_harm", "critical", 0.9),
    "mar jaana chahta": ("self_harm", "critical", 0.9),
    "yahan koi hai": ("coercion", "high", 0.75),
    "wo sun raha hai": ("coercion", "high", 0.8),
    "mala bhiti vatate": ("distress", "medium", 0.75),   # Marathi, romanized
    "mala madat havi aahe": ("vulnerability", "medium", 0.7),
    "to ithe aahe": ("coercion", "high", 0.8),
    "marun takel": ("immediate_danger", "high", 0.8),
    "they are threatening me": ("immediate_danger", "high", 0.85),
}

LEXICONS = {"en": EN, "hi": HI, "mr": MR, "ro": ROMANIZED}
# Cross-language search: always check core languages regardless of detected language,
# because code-switching (Feature 2.9) means any language may appear mid-conversation.
ALL_TERMS = {**EN, **HI, **MR, **ROMANIZED}

# Immediate-danger keywords driving the Safety Override Engine (Feature 2.5)
DANGER_KEYWORDS = [
    "gun", "knife", "kill", "threaten", "dead", "hurt me", "beating", "hitting",
    "immediate danger", "end my life", "suicide", "rape",
    "मार", "चाकू", "धमकी", "आत्महत्या",
    "मारतो", "खुणतो", "धमकी", "आत्महत्या",
    "jaan se maar", "khudkushi", "marun takel",
]

# Coercion signals (Feature 2.12) — always non-definitive, requires human review
COERCION_TERMS = [
    "he is here", "they are listening", "i can't talk", "don't tell anyone",
    "someone came in", "i should go", "he is nearby", "can't speak freely",
    "वह यहीं है", "सुन रहा है", "किसी को मत बताना",
    "तो इथे आहे", "ऐकत आहे", "कोणाला सांगू नका",
    "yahan koi hai", "wo sun raha hai",
]

# Alternative explanations for pauses/silence (Feature 2.11 — avoid "long pause = trauma")
PAUSE_ALTERNATIVES = [
    "network delay",
    "translation / interpretation in progress",
    "word retrieval",
    "hearing difficulty",
    "fear or caution before speaking",
    "interruption in the environment",
    "communication environment (background noise)",
]
