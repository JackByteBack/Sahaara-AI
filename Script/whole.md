1. Original Requirements
   This section contains only the capabilities originally specified and implemented for Sahaara AI, without adding the later NHAA-
   specific research enhancements.
   1.1 AI-Assisted Distress Assessment
   Sahaara should provide an AI-assisted system for identifying observable distress indicators during helpline conversations.
   The system should support:
   real-time assessment of conversations
   identification of observable distress indicators
   evidence-based AI flags
   confidence associated with detected indicators
   limitations associated with AI assessment
   The system is intended as a decision-support tool, not a diagnostic system.
   1.2 Voice and Text-Based Interaction
   The system should support:
   live voice conversations
   speech-to-text processing
   typed/text-based sessions
   demonstration/simulated conversations
   The voice pipeline should allow audio to be captured, transcribed and analyzed.
   1.3 Multilingual Support
   The original Sahaara implementation supports:
   English
   Hindi
   Marathi
   It should provide:
   language detection
   language confidence
   original-language transcript
   optional English interpretation/gloss
   operator language override
   1.4 AI-Assisted Review Priority
   Sahaara should calculate an AI-assisted Review Priority Score to help trained personnel determine which cases require attention.
   The original implementation uses weighted components such as:
   linguistic indicators
   contextual indicators
   conversation indicators
   speech indicators
   The score is explicitly positioned as a review-priority mechanism rather than a medical or psychological diagnosis.
   1.5 Explainable AI Indicators
   For every detected indicator, Sahaara should provide:
   the indicator
   supporting evidence
   relevant transcript excerpt
   timestamp where applicable
   confidence
   model/source responsible for the indication
   This allows the human reviewer to understand why the AI flagged the conversation.
   1.6 Human-in-the-Loop Review
   A trained human must remain responsible for the final decision.
   The reviewer should be able to:
   confirm an AI finding
   modify it
   escalate it
   dismiss it
   add notes
   initiate appropriate support/referral actions
   The original design specifically places AI analysis alongside human review rather than allowing AI to make autonomous decisions.
   1.7 Case Management
   Sahaara should provide case-management functionality including:
   case creation
   case identification
   case status
   consent information
   timeline
   notes
   follow-ups
   review history
   referral information
   case closure
   anonymization
   1.8 Support and Referral
   The original system should allow human reviewers to route cases toward appropriate support services.
   AI may suggest a referral, but the human reviewer confirms the action.
   1.9 AI-Generated Summaries
   The system should generate structured summaries of conversations.
   The summary should distinguish between:
   What the person said
   and
   What the AI inferred from the conversation.
   A deterministic/extractive fallback should remain available when generative AI is unavailable.
   1.10 Privacy and Security
   The original Sahaara system includes:
   consent-first processing
   data minimization
   encryption
   role-based access
   audit logs
   retention controls
   anonymization
   privacy mode
   controlled access to sensitive case information
   Raw audio is not intended to be retained in the default privacy-oriented workflow.
   1.11 User Roles
   The original system supports different operational roles, including:
   Administrator
   Counsellor/Reviewer
   Operator
   Supervisor
   Each role receives appropriate access to system functions.
   1.12 Analytics and Monitoring
   The original Sahaara system provides operational analytics such as:
   number of cases
   cases by day
   language distribution
   priority distribution
   escalation trends
   duration categories
   AI versus human decisions
   demonstration-data usage
   1.13 Auditability
   The system should maintain audit records for important actions such as:
   login
   case access
   transcript access
   AI analysis
   modifications
   escalation
   referral
   export
   deletion
   administrative changes
   1.14 Graceful AI Failure
   If the AI services are unavailable, the core human workflow should remain usable.
   The system should support a Human Assessment Mode rather than becoming unusable when an AI provider fails.
   1.15 Demonstration and Evaluation Foundation
   The original Sahaara implementation includes:
   scripted demonstration cases
   different priority levels
   multilingual demonstrations
   a real analysis pipeline
   human-review workflow
   analytics
   The existing prototype also clearly identifies its current limitations: the rule-based engine is not a validated clinical model, speech
   features are observable proxies, and the priority score is an explainable heuristic rather than a validated psychometric instrument.
2. Additional Features
   This section contains the new capabilities derived from the research, NHAA problem statement, identified research gaps, and
   proposed improvements. These should be treated as enhancements to Sahaara rather than part of the original requirements.
   2.1 NHAA-Specific Victim Vulnerability Assessment
   The original Sahaara focuses primarily on distress and review prioritization.
   The enhancement is to extend this into a broader assessment of:
   psychological distress
   trauma indicators
   self-harm/suicide concern
   immediate physical danger
   intimidation
   possible coercion
   social vulnerability
   medical vulnerability
   legal/service vulnerability
   This addresses the research finding that psychological distress does not fully represent victim vulnerability.
   2.2 Victim Safety & Wellbeing Profile
   Instead of relying only on one Review Priority Score, the enhanced system should produce a multidimensional profile.
   For example:
   Psychological distress HIGH
   Trauma indicators HIGH
   Immediate danger HIGH
   Self-harm concern UNKNOWN
   Intimidation/coercion POSSIBLE
   Social vulnerability MODERATE
   Medical vulnerability LOW
   Legal/service vulnerability HIGH
   This is an additional analytical layer and does not replace the original Review Priority Score.
   2.3 Separate Review Priority From Victim Risk
   The original Review Priority Score should remain.
   The enhancement is to clearly distinguish:
   Victim Safety & Wellbeing Profile
   from
   AI-Assisted Review Priority
   The first describes the potential needs and vulnerabilities of the victim.
   The second determines how urgently a human should review the case.
   This prevents an operational queue score from being incorrectly interpreted as a clinical or psychological measurement.
   2.4 Immediate Safety Assessment
   Add a dedicated assessment for situations such as:
   perpetrator nearby
   ongoing violence
   immediate threats
   unsafe accommodation
   threats against family members
   retaliation
   inability to remain safe
   This is different from general emotional distress.
   A person could have relatively moderate emotional indicators but still require immediate protection.
   2.5 Safety Override Engine
   Introduce explicit safety rules that can override an average AI score.
   For example:
   Overall distress = MODERATE
   Immediate physical threat = YES
   → Safety Override
   → High/Critical human review
   The purpose is to ensure that a critical safety signal is not hidden by a lower overall score.
   2.6 Self-Harm and Suicide-Risk Screening
   Add a dedicated safety pathway for possible:
   suicidal ideation
   self-harm
   inability to remain safe
   other high-risk crisis indicators
   The enhancement should combine structured/validated screening with human review rather than claiming that voice emotion alone
   can diagnose suicide risk.
   2.7 Trauma-Specific Assessment
   Add explicit trauma-related indicators to the existing distress analysis.
   This can include narrative indicators related to:
   traumatic experiences
   fear
   avoidance
   intrusive experiences
   hypervigilance-related descriptions
   severe emotional reactions
   The system should continue to avoid claiming that these indicators constitute a clinical PTSD diagnosis.
   2.8 Indian Multilingual and Dialect Expansion
   The original Sahaara implementation supports English, Hindi and Marathi.
   The enhancement is to investigate and support additional Indian languages and relevant dialects.
   Potential expansion includes:
   Bengali
   Telugu
   Tamil
   Kannada
   Gujarati
   Odia
   Punjabi
   Assamese
   other languages required by NHAA
   This is motivated by the research gap concerning insufficient multilingual and culturally representative mental-health datasets.
   2.9 Code-Switching Detection
   The enhanced system should handle conversations such as:
   “Mala khup bhiti vatate... they are threatening me.”
   rather than assuming that a conversation remains in one language.
   The system should retain:
   original wording
   language identification
   code-switching information
   ASR confidence
   downstream assessment confidence
   2.10 Uncertainty-Aware Assessment
   The original system provides confidence for individual indicators.
   The enhancement is to make uncertainty a formal part of the overall assessment.
   Sahaara should be able to produce:
   Assessment confidence: 0.64
   Evidence quality: Moderate
   Missing information: Immediate safety not established
   Recommended action: Human assessment required
   The system should be able to abstain rather than produce an unreliable classification.
   2.11 Context-Aware Interpretation of Speech
   The original system uses speech timing and observable speech features.
   The enhancement is to prevent simplistic interpretations such as:
   Long pause = trauma.
   Instead, the system should consider alternative explanations such as:
   network delay
   translation
   word retrieval
   hearing difficulty
   fear
   interruption
   communication environment
   Thus speech becomes supporting evidence rather than a standalone diagnosis.
   2.12 Possible Coercion/Interference Indicator
   Add an indicator for situations where the conversation may suggest that the person cannot speak freely.
   Potential signals could include:
   sudden change in speaking behaviour
   whispering
   abrupt termination
   repeated avoidance
   inconsistent answers
   someone potentially entering the environment
   However, the output should always be:
   Possible coercion/interference
   rather than a definitive claim.
   Human review is required.
   2.13 Trauma-Informed Conversation Mode
   Add a specialized interaction mode based on trauma-informed principles.
   It should support:
   minimum necessary questioning
   progressive disclosure
   victim choice
   control over disclosure
   non-judgmental language
   reassurance
   short safety-focused questioning during crisis situations
   This reduces unnecessary traumatic disclosure.
   2.14 Trauma Narrative Continuity
   Add a mechanism whereby, with appropriate consent, the victim's account can be converted into a structured case representation.
   This can support authorized:
   counsellors
   legal-aid personnel
   medical personnel
   protection services
   welfare/rehabilitation authorities
   The objective is to reduce repeated retelling of traumatic events.
   2.15 Role-Based Narrative Sharing
   The narrative continuity feature should be accompanied by need-to-know information sharing.
   For example:
   Counsellor
   → psychological information
   Medical professional
   → relevant medical information
   Legal service
   → relevant legal/case information
   Protection authority
   → relevant immediate safety information
   No stakeholder should automatically receive the complete sensitive record.
   2.16 Expanded Intervention Orchestration
   The original referral system should be expanded into structured pathways for:
   counselling
   mental-health services
   medical assistance
   legal aid
   protection
   emergency support
   shelter
   rehabilitation
   welfare assistance
   AI can recommend possible pathways, but authorized humans confirm consequential actions.
   2.17 Longitudinal Monitoring
   Add the ability to reassess a case over time.
   The system could track:
   Initial assessment
   ↓
   Intervention
   ↓
   Follow-up
   ↓
   Reassessment
   ↓
   Risk trajectory
   This addresses the research gap around one-time assessment versus changing victim circumstances.
   2.18 NHAA-Specific Dataset
   The original prototype uses synthetic demonstration data and leaves real-world validation as future work.
   The enhancement is to develop an ethically collected, consented and appropriately anonymized NHAA Trauma-Safety Dataset
   containing relevant:
   languages
   dialects
   spontaneous speech
   atrocity contexts
   trauma indicators
   safety indicators
   vulnerability factors
   expert annotations
   2.19 NHAA Multimodal Benchmark
   Create a formal research benchmark comparing:
3. questionnaire only
4. text only
5. voice only
6. text + voice
7. text + voice + context
8. full multimodal + validated screening
   The goal is to determine whether each additional information source actually improves performance.
   2.20 Expanded Evaluation
   The original system does not yet have a validated evaluation dataset or displayed validation metrics.
   The enhancement should introduce evaluation using:
   Model performance
   sensitivity
   specificity
   precision
   recall
   F1
   AUROC
   AUPRC
   calibration
   Safety
   false-negative rate
   false-positive rate
   inappropriate escalation
   missed high-risk cases
   Fairness
   Performance across:
   languages
   dialects
   gender
   age
   region
   trauma type
   Operational outcomes
   time to intervention
   referral appropriateness
   referral completion
   follow-up completion
   case outcomes
   2.21 Human-AI Performance Evaluation
   The enhanced research should also measure:
   reviewer agreement
   reviewer overrides
   AI-human disagreement
   inappropriate AI recommendations
   explanation usefulness
   reviewer workload
   time saved
   quality of final decisions
   This evaluates whether AI actually improves the human workflow rather than merely achieving a model-level accuracy score.
   2.22 Outcome-Based Learning
   Instead of measuring only whether Sahaara correctly classified a conversation, the enhanced system should eventually examine:
   Did the AI-assisted assessment lead to an appropriate intervention and useful outcome?
   This connects AI performance with real service delivery.
   2.23 Safety and Privacy for Potentially Unsafe Devices
   The original privacy model should be extended for situations where the victim's device may be accessible to another person.
   Additional considerations include:
   discreet interfaces
   minimal sensitive notifications
   privacy-aware screen states
   safe exit
   limited local history
   careful notification handling
   This addresses the fact that the victim's communication environment itself can present a safety risk.
   2.24 Dedicated Research Monitoring
   The enhanced Sahaara should continuously monitor:
   language-specific performance
   false negatives
   false positives
   calibration
   reviewer overrides
   model drift
   referral outcomes
   subgroup disparities
   unexpected failure patterns
   This creates a mechanism for detecting when the AI is performing differently across populations.
   Final Separation
   The distinction can therefore be summarized as:
   Original Requirements
   Build Sahaara as an AI-assisted, multilingual, real-time distress-assessment and support-routing platform for trained
   human operators, with voice/text intake, explainable AI indicators, review prioritization, human review, case
   management, referral, summaries, privacy, security, auditability and operational analytics.
   Additional Features
   Extend Sahaara into an NHAA-specific victim trauma, safety and vulnerability assessment platform by adding
   multidimensional vulnerability assessment, immediate safety detection, trauma and self-harm assessment, coercion
   indicators, Indian multilingual/dialect and code-switching capability, uncertainty and abstention, trauma-informed
   interaction, narrative continuity, expanded intervention orchestration, longitudinal monitoring, dedicated NHAA
   datasets and benchmarks, fairness/safety evaluation, and outcome-based validation.
   Original Requirements Additional Features
   AI-assisted distress assessment, not diagnosis Voice and text interaction NHAA-specific victim vulnerability assessment
   Victim Safety & Wellbeing Profile covering psychologic
   and legal vulnerability
   Multilingual support: English, Hindi, Marathi Expanded Indian languages, dialects and code-switch
   AI-assisted Review Priority Score with explainable weighted components Separate victim risk/vulnerability from operational revie
   Explainable AI indicators with evidence, timestamps, confidence and
   Safety Override Engine for explicit high-consequence s
   model
   Human-in-the-loop review: Confirm, Modify, Escalate, Dismiss Dedicated self-harm/suicide-risk screening pathway
   Trauma-specific assessment and uncertainty-aware ou
   Case management: IDs, status, consent, timeline, notes, follow-ups,
   closure, anonymization
   Human-confirmed support/referral routing Trauma-informed conversation mode with minimum ne
   Trauma Narrative Continuity to reduce repeated retellin
   AI-generated summaries separating person's statements vs AI
   inferences
   Privacy/security: consent, minimization, encryption, RBAC, audit logs,
   retention, anonymization
   Role-based access: Admin, Counsellor/Reviewer, Operator, Supervisor Possible coercion/interference detection as a non-con
   Operational analytics and case monitoring Full auditability of AI and human decisions Expanded intervention orchestration: legal, medical, pro
   counselling, welfare, etc.
   Longitudinal monitoring and reassessment
   Dedicated NHAA Trauma-Safety Dataset
   Graceful AI failure / Human Assessment Mode NHAA Multimodal Trauma-Safety Benchmark
   Scripted multilingual demo and evaluation foundation Expanded evaluation: sensitivity, specificity, F1, AURO
   positives/negatives
   — Fairness evaluation across language, dialect, gender, a
   — Human-AI performance evaluation: reviewer agreeme
   explanation usefulness
   — Outcome-based learning using intervention, referral an
   — Device-safety protections for potentially unsafe environ
   — Continuous safety, fairness, model-drift and performa
