document.addEventListener("click", (event) => {
  const button = event.target.closest(".quiz-check");
  if (!button) return;

  const quiz = button.closest(".quiz");
  const expected = quiz?.dataset.answer;
  const selected = quiz?.querySelector("input[type='radio']:checked");
  const feedback = quiz?.querySelector(".quiz-feedback");

  if (!quiz || !expected || !feedback) return;

  if (!selected) {
    feedback.textContent = "Pick an answer first.";
    feedback.dataset.state = "neutral";
    return;
  }

  const correct = selected.value === expected;
  feedback.textContent = correct
    ? "Correct. Keep the answer structure compact and applied."
    : "Not quite. Re-read the linked concept and try to explain the mechanism.";
  feedback.dataset.state = correct ? "correct" : "wrong";
});
