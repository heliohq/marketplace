# Automation evaluation loop

Read this reference for structured or strict evaluation, and whenever a
failure prompts a change to an existing automation. The loop mirrors skill
creation: define realistic cases, preserve a baseline, run the candidate,
grade the evidence, analyze the results, show the user, revise, and repeat.

## 1. Capture the evaluation contract

Start from the approved example and define success before running anything.
Begin with two or three cases; expand only when results or production failures
reveal a real gap.

Keep each case small and observable:

```markdown
### <case name>
Purpose:
Input or fixture:
Expected behavior:
Observable checks:
Repetitions and rationale:
Safety controls:
```

Useful starting cases are:

- one representative success;
- one important boundary or deliberate no-op;
- one dependency, authentication, or malformed-input failure.

For side effects, include authorization, destination, delivery count, and
idempotency. For monitored systems, cover every relevant terminal state. Do
not turn taste into a numeric score: let the user judge subjective quality and
reserve assertions for facts that can be observed.

Store stable cases under `## Evaluation contract` in the procedure so future
maintainers can replay them. Keep the contract in the procedure, not only in a
local file.

## 2. Preserve the baseline

For a new automation, the approved direct execution is the quality baseline;
the disabled automation run tests whether a fresh executor and trigger path
reproduce it.

For an existing automation:

1. read the automation, procedure, recent runs, and failing transcript;
2. retain the exact current procedure in the evaluation evidence before the
   edit;
3. when safe, run the representative or failing case against the current
   version;
4. label those execution IDs `baseline`;
5. edit the bound procedure or trigger in place, preserving automation and
   trigger identities.

The observed production failure can serve as the baseline when replaying the
old version would repeat a harmful side effect. Never recreate a production
automation merely to obtain a baseline.

## 3. Run cases at the chosen depth

Create new automations disabled. Disable an existing automation before a
meaningful behavioral change when leaving it live could send duplicate or
unsafe output.

- For schedule or one-shot work, use **Run now** while the automation remains
  disabled. Manual runs are allowed for rehearsal; automatic firing stays off.
- For event triggers, exercise handler fixtures locally first, then use a
  manual disabled run to verify the executor and procedure separately. A
  deployed event fire is real; there is no trigger dry-run flag.
- Intercept or sandbox email, writes, money movement, and broad-audience
  delivery during evaluation.
- Keep inputs equivalent between baseline and candidate configurations.

AI output varies, so one good result may be luck. When inconsistency would
matter, run each representative candidate three times by default and report
the spread. Use one run for deterministic, unsafe, or expensive cases, and say
why repetition would add little confidence or too much risk.

For every run, retain the execution ID and inspect the transcript:

```bash
heliox automation run <id> --json
heliox automation run show <execution_id> --transcript --json
```

`run show` exposes the fire record and transcript, not token or duration totals.
Record only metrics Helio actually returns; never invent missing telemetry.

## 4. Grade after execution

Separate producing the output from judging it. After each run, grade every
observable check as pass or fail and cite the exact output or transcript
evidence. Use a fresh judging pass or another evaluator when available;
otherwise make the separation explicit in your own work.

For each run, record:

```markdown
Execution: <id>
Configuration: baseline | candidate
Case: <name>
Checks:
- PASS | FAIL — <check>: <specific evidence>
Claims needing review:
Unexpected behavior:
```

Programmatic checks are preferable for counts, schema, freshness, signatures,
idempotency, and delivery totals. Human review remains the authority for tone,
usefulness, and other subjective qualities.

## 5. Aggregate and analyze

Summarize results across cases and repeated runs before drawing a conclusion:

```markdown
| Case | Configuration | Passed runs | Total runs | Consistency | Evidence |
| --- | --- | ---: | ---: | --- | --- |
```

Then perform the analyst pass that a raw pass rate cannot provide:

- Which checks pass for both broken and working behavior and therefore do not
  discriminate?
- Which cases vary between repeated runs?
- Did a fallback hide a broken dependency?
- Did delivery count, audience, authorization, or side effects drift?
- Did the candidate add unnecessary tool calls or complexity?
- Do failures cluster around one missing instruction or one upstream system?

For maintenance, compare baseline and candidate directly. For a new automation,
compare the approved direct example with the candidate runs and report the
remaining end-to-end proof gap.

## 6. Put results in front of the user

Before enablement, show the user representative outputs, the pass/fail summary,
variance, and important transcript findings. Use a concise chat message for a
lightweight evaluation. When structured or strict work produces substantial
evidence, create a Helio document with the cases, execution IDs, grades,
analysis, and feedback, then share it.

Ask for feedback at the user's altitude. Empty feedback means the result is
acceptable; specific feedback becomes the next revision target.

## 7. Revise and repeat

When a case fails:

1. fix the smallest general procedure or trigger defect;
2. replay the failing case;
3. replay a prior representative case to catch regressions;
4. repeat the aggregate and analyst pass;
5. show the changed output and evidence to the user.

Avoid tuning only to the exact fixture. Add a new stable regression case when a
real failure teaches something the existing contract did not cover.

Stop iterating when the user is satisfied and all required checks pass with
acceptable consistency. If further runs stop changing a failed conclusion,
report the blocker and keep the automation disabled. Offer enablement only
after the required checks pass and the user approves. Retain the stable cases
and latest verified execution IDs in the procedure; leave bulky transcripts
in run history.
