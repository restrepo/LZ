"""Triage student answers to a physics question with TypeSafe System One.

One request asks three independent questions about the same answer:
  - Choice: which misconception (if any) the answer shows
  - Noul:   does the answer reach the correct conclusion?
  - Score:  how well is the reasoning justified (0-3)?
Code, not the model, decides what to do with the results.

Run:  pip install typesafe-sdk && export TYPESAFE_API_KEY=... && python typesafe_example.py
"""

from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

PROBLEM = (
    "A ball is thrown straight up. At the highest point of its path, "
    "what are its velocity and its acceleration? Explain."
)

STUDENT_ANSWERS = [
    "At the top the velocity is zero and the acceleration is also zero, because it stops moving.",
    "Velocity is 0 for an instant, but acceleration is still g = 9.8 m/s^2 downward, "
    "since gravity keeps acting; that is why the ball starts coming back down.",
    "The velocity is zero and the acceleration is 9.8.",
]

QUESTIONS = {
    "misconception": Choice(
        instructions="Which misconception, if any, does `student_answer` show about `problem`?",
        criteria={
            "none": "The answer shows no misconception about velocity or acceleration.",
            "zero_acceleration": "Thinks acceleration is zero where velocity is zero.",
            "force_of_throw": "Thinks a force from the throw still acts on the ball after release.",
            "other": "Shows a different misconception about the motion.",
        },
    ),
    "correct": Noul(
        instructions="Does `student_answer` state that velocity is zero AND acceleration is g downward at the top?",
    ),
    "justification": Score(
        instructions="How well does `student_answer` justify its claims about acceleration at the top?",
        criteria=[
            "No justification is given.",
            "Gives a number or claim but no physical reason.",
            "Gives a physical reason, but incomplete (e.g. no direction or no link to gravity).",
            "Explains that gravity still acts, gives magnitude and downward direction.",
        ],
    ),
}


def triage(client: TypeSafeClient, answer: str) -> str:
    response = client.system_one(
        state={"problem": PROBLEM, "student_answer": answer},
        questions=QUESTIONS,
    )
    misconception = response.choices["misconception"]
    correct = response.nouls["correct"].noul
    justification = response.scores["justification"]

    print(f"\nAnswer: {answer}")
    print(f"  misconception: {misconception.choice} (confidence {misconception.confidence:.2f})")
    print(f"  P(correct):    {correct:.2f}")
    print(f"  justification: {justification.score:.1f} / 3")

    # Policy lives in code: thresholds are examples to tune on real class data.
    if misconception.confidence < 0.6 or 0.3 < correct < 0.7:
        return "send to teacher (uncertain)"
    if correct >= 0.7 and justification.score >= 2.5:
        return "full credit"
    if correct >= 0.7:
        return "partial credit: ask for justification"
    return f"feedback on misconception: {misconception.choice}"


if __name__ == "__main__":
    with TypeSafeClient() as client:
        for answer in STUDENT_ANSWERS:
            print("  ->", triage(client, answer))
