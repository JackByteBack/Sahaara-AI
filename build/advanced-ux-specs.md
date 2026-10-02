// React Component Logic
import { useState, useEffect } from 'react';

const TraumaInformedInterface = ({ questions, isTraumaMode, transcript }) => {
const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
const [userSpeaking, setUserSpeaking] = useState(false);

// Calculate if user has paused (Logic for auto-advance)
useEffect(() => {
if (isTraumaMode && !userSpeaking && transcript.length > 0) {
// Timeout to allow "silence" (processing time) before showing next question
const timer = setTimeout(() => {
setCurrentQuestionIndex((prev) => (prev < questions.length ? prev + 1 : prev));
}, 3000); // 3 second pause
return () => clearTimeout(timer);
}
}, [userSpeaking, transcript, isTraumaMode]);

const getCurrentQuestion = () => {
const q = questions[currentQuestionIndex];

    // Feature 2.13: Trauma-informed filtering
    // Block questions starting with "Why" to avoid victim-blaming
    if (isTraumaMode && q.text.toLowerCase().startsWith('why')) {
      return getNextTraumaSafeQuestion(currentQuestionIndex);
    }

    return q;

};

return (
<div className="interface-container">
<div className="transcript-area">
{transcript.map((segment, i) => (
<div key={i} className={segment.is_user ? "user-msg" : "system-msg"}>
{segment.text}
</div>
))}
</div>

      <div className="question-area">
        <button
          onClick={() => setUserSpeaking(true)}
          disabled={userSpeaking}
          className="trauma-urgent-btn"
        >
          {isTraumaMode ? "Reassure Victim" : "Next Question"}
        </button>
        <p>{getCurrentQuestion().text}</p>
      </div>
    </div>

);
};

// Helper to swap "Why" questions with "What happened" questions
function getNextTraumaSafeQuestion(currentIdx) {
const traumaSafeMap = {
"Why did you go there?": "What was the situation like?",
"Why did he hit you?": "What was the interaction like?",
"Why are you crying?": "It sounds like you are going through a lot."
};
return traumaSafeMap[questions[currentIdx].text] || questions[currentIdx];
}
