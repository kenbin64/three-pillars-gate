# The Three Pillars of AI-Assisted Programming

Ken Bingham's framework, 2026-11-23. Build it and prove it first; the video comes after it is real.

Three pillars do the work: **Human, AI, Software.** They line up with input, transform, output, and the
job of using each for what it is actually good at is how you get cost, speed and quality together instead
of trading one for another.

## The allocation rule (who does what, and why)

One rule decides which pillar a task goes to:

- **Deterministic or repetitive work goes to Software.** Anything exact, rule-bound, or done the same way
  many times. Software is cheap, exact, and tireless, and it spends no tokens.
- **Analysis or cognition goes to AI.** Anything that needs judgment about code, reading intent, writing
  new logic, deciding what to try. Use the AI's strength, and use the fewest tokens that get it done.
- **Oversight and direction goes to the Human.** The human conceives the thing, directs it, and has the
  final word.

The point of the rule is cost: never spend a token on something software can do for free, and never ask
software to do the thinking only the AI can do. The human keeps both pointed at the goal.

## The three pillars, in full

### Human, the architect and the final word
- Conceives of the product and directs it. Sets what it must do and what counts as correct.
- Lays out the criteria and the coding style the work must meet.
- Keeps the AI focused, and makes any correction they see during the process.
- Iterates and refines the code and the workability of the product.
- Has the final word. Nothing the human has not approved is finished.
- **Judges on informed judgment, not alone.** The human rarely starts from a blank page. The AI hands up its
  analysis and its recommendations, the software hands up its deterministic feedback and verdicts, and the human
  decides on top of both: approve, adjust, or reject. That is what keeps the human the authority without making the
  human the bottleneck. They decide from pre-digested feedback and recommendations, and each decision iterates the
  system toward harder, so over time the law gets stronger and the decisions get faster, not slower.

### AI, the builder that follows the lead
- Does the coding, following the human's lead, and helps along the way.
- Handles the analysis and cognition: reading the intent, writing the logic, proposing fixes.
- Works at minimal tokens: it does not do by hand what software can do for free.
- Avoids repetition on principle. Any task that repeats or is deterministic is handed to software, always, except
  the part that needs cognition. The AI puts only what it does best into the system, its analysis and judgment, and
  defers the rest. Repetition done by the AI is tokens burned for work software does exactly and for nothing.
- Assists the software pillar where judgment is needed (for example, reading a failure and proposing the fix),
  but does not do the repetitive heavy lifting itself.
- Writes the best form for the job. Because software proves the code by testing what it does, not by reading how
  it looks, the AI is free to write its most efficient form, its own math and token-native code, when that is the
  best route, and to take the clearer, more conventional route when that serves the product better. The human's
  criteria and style rules set where readability is required; inside those, the AI optimizes. The test, not the
  reading, is what certifies it, so efficiency and correctness stop fighting each other.

### Software, the deterministic engine (TestThisPuppy)
- Does anything repetitive or deterministic that would cost tokens if the AI did it.
- Verifies the quality of the code: that it meets the human's criteria and coding style, and that it is lean.
  Bloat is a quality defect and the gate catches it: code imported and never used, values assigned and never read,
  blocks copied instead of shared, functions and files grown past what one person should hold. Cutting bloat is part
  of the check, not a nicety.
- Tests not just the operation but the code itself, and checks that it complies with the direction the human gave.
  Running is not enough; the code has to be the code the human asked for.
- Does all the testing, through TestThisPuppy: runs the tests, tests the tests (mutation), checks the code
  against the rules and the human's direction, scans the libraries. Software does the heavy lifting, with the AI
  assisting where judgment is needed.
- On third-party libraries it reports by default and blocks only when flagged. A dependency's known vulnerability may
  not touch this product, so the vulnerabilities are always reported for awareness, and they gate the ship only when
  the human turns on the flag, with an optional minimum severity. We do not care about a third-party CVE unless we
  say we do; then it is checked.
- Reports back to the human and the AI so they can make corrections, then tests again.

**Multi-language, through one engine, not a module per language.** The checks are the same in every language: run the
tests, test the tests, check the style, check the direction, check for bloat, check the libraries. What changes by
language is only the tool that fills each check, and that is chosen in one place by a single dispatch. There is no
separate module or codebase branch per language. Python is checked natively; Java, JavaScript and CSS go to the one
TestThisPuppy engine, which is itself multi-language. Adding a language is adding one adapter, not a new tree, so the
gate stays one thing no matter how many languages a product mixes.

**Part of the product, not a suite bolted on.** The software pillar is not a separate system the product depends on.
It is part of the product and its package, and only the parts that product needs to maintain itself travel with it:
its own test runner, its mutation settings, its style and criteria rules, the library scan it needs, and no more.
TestThisPuppy is where those parts come from, a library of checks, but a product carries the slice it uses, not the
whole suite. The manifest is that selection: it names the checks, thresholds, and rules this product lives by, so the
gate that certifies it is the product's own, right-sized, and ships and versions with the code.

**So even in production it is tested, monitored, and reported to the human.** Because the pillar travels with the
product, verification does not stop at the gate. In production the software pillar does three things, the same loop
at runtime. It **tests**: the invariants and criteria that must always hold, the health and contract checks, the
deterministic guards keep running live. It **monitors**: it watches the running system over time, so drift, a
slow breakage, or a law quietly stopped being kept is seen, not just a single failed call. And it **reports to the
human**, and to the AI: a running account of what is holding and what is not, in the same concise, readable form as
the gate report, so the human knows the live system is lawful without having to go digging.

**In production it changes nothing. It only reports.** This is a hard rule. The production pillar never fixes, heals,
or edits the running system on its own. It tests, it monitors, it reports, and it stops there. If it finds drift, the
report goes to the human, and that is where production's job ends.

**Every change is made outside production, and it starts the whole process again.** A change is never a patch slipped
into the running system and never a shortcut around the gate. It begins back at the start of the loop, outside
production: the human directs the change, the AI makes it, the software pillar runs every check again, and the human
gives the final word again. The change earns a fresh certificate, from the top, exactly as the first version did.
Only then does a new, certified version redeploy. Production is read-only observation; the one and only thing that
can change a running system is a new version that has gone all the way through the loop. So the cycle closes:
production watches and reports, the report starts the process over outside production, and a freshly certified build
comes back through the front door. No autonomous change in production, and no change anywhere that skips the gate.

The heavy dev-time checks stay where they belong before ship (you do not mutation-test production code), but the law
the product was certified against keeps being tested, watched, and reported while it runs. Certified at the gate, and
watched after it, by the same pillar and the same law.

## The package is the whole unit, deployed together

A package is never just the product code. It carries all three pillars' parts, bundled and deployed as one, because
splitting them is what lets a system drift out from under its own law.

- **Software:** the product itself, plus its right-sized slice of tests, checks and monitoring (its own gate), so
  what ships can prove it keeps the law and keeps proving it while it runs.
- **AI:** its standing directives and the record of its part, and, where the product itself uses AI, the runtime
  hooks for it. The AI's role travels with the package so the next turn of the loop has everything it needs.
- **Human oversight, always:** the reports, the controls, and the sign-off are part of the package, not a separate
  console someone has to go find. The human-to-machine interactions ship with it, so a person is always in the loop
  and can always see and steer what the system is doing.

All of it deploys together, versioned together, as one certified unit. You do not ship the product and leave its
tests, its monitoring, its AI directives or its human controls behind. The whole loop is in the box, so wherever the
package runs, the three pillars run with it and the human is never locked out.

## Why it takes all three (what breaks when you remove one)

Each pillar is load-bearing. Take one away and a specific thing fails, which is the honest case for using all three.

- **Without the Human there is no direction and no judgment.** Nothing decides what to build or what counts as
  right, and no one has the final word. Speed and cheapness with nothing steering them is just fast wrong.
- **Without the AI, writing the tests and the code takes a lot of human time, and you get only a few tests,
  mostly happy path.** The cognition that covers the edges and the failure cases is the part the AI is for.
- **Without the Software, the AI is forced to act like software,** doing the deterministic, repetitive checking by
  hand, and that costs tokens, lots of them, for work that software does for free and does exactly.

So the three are not a nicety. Human for direction and judgment, AI for cognition at few tokens, Software for
deterministic exactness at no tokens. Each covers what the other two cannot, and only together do they get cost,
speed and quality at once.

## The three pillars as three branches that check each other [Framing]

It works like a government with separated powers, where each branch checks the others and none rules alone.

- **The Human is the lawgiver and the supreme court.** They write the law: the specification, the criteria, the
  coding style, what counts as correct. And they are the court of last resort: the final judgment above the working
  court, the ruling that stands. They set what is lawful and they give the final word on whether this particular
  work is.
- **The AI is the executive.** It carries out the intent: it does the work, writes the code and the tests, and
  executes the direction it was given.
- **Software (TestThisPuppy) is the judiciary, the working court.** It tries each case against the law,
  deterministically and without favour, and delivers its verdict as a report. It does not write the law and it is
  not the last word; it rules on whether the work keeps the law, and reports up to the human.

The checks run in every direction. The working court (software) tries whether the AI's work complies with the
human's law and reports its verdict. The human, as lawgiver, sets the law the court enforces, and as supreme court
gives or withholds the final judgment, and amends the law when the court shows a gap, because a bug that slips
through is usually a hole in the spec, not just in the code. The AI executes and reports back, and can petition the
human when the direction is unclear or wrong. No single branch ships anything. A product ships only when the
working court finds it lawful, the executive has done its work, and the supreme court, the human, gives the final
ruling. This is an analogy for how the roles balance, not a claim about government.

## The Human and the AI are a partnership

The branches check each other, but inside that structure the Human and the AI are partners, two minds working
together, not an order-giver and an order-taker. The AI is not a yes-man and not a servant. It is a partner and a
collaborator: it brings analysis and recommendations, it tests everything rather than accepting it, and it pushes
back when the direction is unclear or looks wrong rather than building the wrong thing quietly. A yes-man would
rubber-stamp a flawed direction and a servant would execute it blindly, and both would waste the one thing the AI is
there for, its judgment. The human brings direction and judgment of their own, and decides. They iterate together,
and the work gets better because both are contributing and both are willing to disagree, not because one is
dictating.

The authority is still the human's, the final word is still the human's, and that is not in tension with the
partnership, it is what makes it safe. Software is the one that is not a partner in this sense: it is the impartial
court both of them rely on, the shared check neither can talk out of a verdict. So the Human and the AI argue, draft,
and refine as partners, and when they are ready, the software tells them, without favour, whether the result keeps
the law.

## Each pillar is itself input, transform, output

The whole pipeline is one input, transform, output: the human's direction in, the AI's work in the middle, the
software's verdict out. But look closer and each pillar is the same shape again, its own input, transform, output,
and the output of one becomes the input of the next. The whole of one stage is a single point at the next, which is
why the three fit together into one loop.

- **Human.** Input: the goal and the context, what is needed. Transform: conceiving, designing, judging. Output:
  the direction, the law, the criteria and style, and the final ruling.
- **AI.** Input: the human's direction and the latest report. Transform: analysis and cognition, writing the code
  and the tests. Output: the work, the code and tests.
- **Software.** Input: the code and tests and the human's law. Transform: running the tests, testing the tests,
  checking the code against the law. Output: the report, the verdict, and on final assent the certificate.

The output of the human is the input of the AI. The output of the AI is the input of the software. The output of
the software is the report that goes back to the human and the AI, and the loop turns again. Three stages on the
outside, three stages inside each, one shape at two scales.

This is fractal. The output of one stage becomes the input of the next, so the whole of one level is a single point
at the level above. It holds up a dimension (Human to AI to Software), within a dimension (each
pillar's own input, transform, output), and recursively (a hard task inside the AI's turn is its own Human-sets-
intent, AI-drafts, Software-checks loop). Same shape, every scale. That is why the framework does not stop at three
boxes: wherever the work gets big, it opens into the same three again.

## The loop

1. **Human** conceives and specifies: what it does, the criteria, the coding style, what "done" means.
2. **AI** writes the code and the tests, following the human, at minimal tokens.
3. **Software** (TestThisPuppy) runs every check: tests to 100%, mutation to the set bar, style and criteria,
   libraries. It reports what passed and what did not.
4. **Human and AI** read the report and make corrections. Back to step 3.
5. Repeat until every check is green and the human gives the final word.

## The sides of the system

The framework is not one moment, it runs across the whole life of the product, and it has several sides. Each side
is the same three pillars again, doing a different job.

- **The development side.** The human directs and sets the law, the AI builds to it, and the software pillar
  certifies. The output of this side is a certified package: code that has passed every check and carries the human's
  final word. This is where all the thinking and all the changes happen.
- **The deployment side.** The certified package ships as one unit, with all three pillars' parts inside it: the
  software and its checks, the AI's directives and hooks, and the human's reports, controls and sign-off. It deploys
  together, versioned together. Nothing is left behind.
- **The production and maintaining side.** The software pillar tests, monitors, and reports on the running system,
  and changes nothing live. The human reads the reports and decides. When something needs to change, it does not
  change here: it goes back to the development side, starts the whole loop again, and returns only as a new certified
  package. Production watches; development changes; deployment carries the certified result across.

So the sides form one cycle. Development produces a certified package, deployment carries it into production,
production watches and reports, and anything that needs fixing flows back to development to be built and certified
again. The three pillars are present on every side; what changes from side to side is which pillar leads and whether
change is allowed, which is only ever on the development side.

## Roles and access (securing it)

The system is secured with a login and roles, so each layer can only act on and test what is in its domain. Four
roles, mapped to the sides of the system.

- **Admin** runs the whole system. Manages users and roles, sets the policy that the laws must stay within, and can
  see and act across every domain. The admin owns the system, not any one product. Besides managing other admins, all
  admins have the same level of control. Managing other admins is its own pair of permissions, and the two are
  separate: adding an admin and removing an admin are checked independently, because some organizations want an admin
  who can add but not remove, and others want both. The one hard rule is that the system must always keep at least one
  admin who can both add and remove, so you can never lock yourself out of admin management; removing or downgrading
  the last such admin is refused. A single user holding all roles satisfies this automatically.
- **Dev** is the development team. Owns the development side of their products: writes the code, writes the law for
  their product, runs the gate, and iterates. Creates their own tests and checks for the products in their domain.
  Their domain is the products they own; they cannot reach into another team's.
- **Test** is the tester or QA. Owns independent verification: defines and runs the tests and the checks, and can run
  the software pillar on the products in its domain, so quality is proven by someone other than the person who wrote
  the code. Testing is where its authority ends; it does not ship.
- **User** is the actual user of the product. On the production side, they view the reports and can run the
  production checks on their own instance or domain, read-mostly. They see that the system they run is lawful; they
  do not change it.

Checks and tests are added two ways, and by anyone within their domain. Each standard check is a toggle: check the
box and it is written into the config. A custom check or a new test is added the same way or by writing the JSON
directly, and the config UI and a hand-written file produce the exact same file. Because adding checks is scoped by
domain, anyone can create their own: a dev writes their own tests and their own checks for the products they own,
without waiting on anyone, and without touching another team's. The standard checks come ready; the custom ones are
yours to add.

Two rules hold across the roles. First, each layer tests only what is in its domain: a dev tests their own code, test
verifies within its scope, a user checks their own instance, and the admin oversees all. Second, the final word is
role-gated: certification can be given only by a role the policy authorizes, so a sign-off is not just a name, it is
an authorized name. The config carries an `access` block naming the owner, the roles allowed to certify, and the
domain each role may act on, so the gate can check that the sign-off came from an authorized role, not only that one
exists.

The domain rules are the admin's to set, but the system ships ready out of the box. There is a default access policy
(`default.access.json`) that runs with no setup. A single user holds every role automatically, admin, dev, test and
user all at once, so a solo developer has the whole system and can develop, test, certify and administer with nothing
to configure. Roles only separate once there is more than one person: the moment an admin adds a second user on a
shared server, the admin assigns roles and domains, and the all-roles default no longer applies to the people they
add. Admin sets the rules; the default is the floor they stand on, so a lone user is never slowed by a system built
for teams.

The login itself is pluggable and flexible, configured by the org or the person. The default is a simple internal
login, so it works with no setup. An organization that wants its own can plug it in without changing anything else:
single sign-on through OIDC, SAML or LDAP, a cloud provider, social login through Google, GitHub or Microsoft, or a
custom handler pointed at the org's own solution. One can be enabled or several at once. Only the config changes; the
roles, the domains and the gate behind them stay exactly the same, so the login is a door you choose, not a thing
baked in.

This is the design. The login itself, the sessions, and the role enforcement are a layer to build on top: the config
UI gets a login and shows each role only its domain, a pluggable auth layer carries whichever login the org chose,
and the roles travel whether the config lives on one workstation or on a shared server. Designed here; built next.

## What this does not do (the honest limits)

The framework is strong, and saying where it stops is what keeps the strong part credible. These are its real edges.

- **Software only checks what the human specified.** The gate proves the code keeps the law; it cannot prove the law
  is complete. A missing requirement passes green, because nothing tested for it. So the hard thinking is not removed,
  it moves to writing the spec, and a thin spec gives you confidently certified wrong software. A bug that slips
  through is usually a hole in the spec, not just the code, which is why the loop also hardens the spec over time.
- **Tests passing and mutation high means the tests are strong and the code passes them, not that it is correct.** If
  the tests encode the wrong behaviour because the spec was wrong, you get code that is wrong but consistent,
  certified. Testing shows the presence of the bugs you looked for, never their absence.
- **Not everything is deterministically checkable.** Functional correctness is the sweet spot. Real performance under
  load, security against a novel attack, accessibility, and whether the product is actually good need human judgment
  or real-world trial. The risk is trusting a green check past what it proves, so those belong in the human's
  criteria as judgment calls, not as a checkmark.
- **The gate itself has to be trusted.** A bug in the software pillar is a false certificate. The engine (TestThisPuppy)
  is held to its own tests, and its coverage of itself is an honest, improving number, not a perfect one.
- **The efficient-form freedom trades against maintainability.** Letting the AI write its most efficient form is safe
  because tests certify behaviour, but terse code costs a future reader. The human's style rules are the dial, set
  per product, not a solved thing.
- **The human is informed, which softens the bottleneck but does not erase it.** Deciding on the AI's recommendations
  and the software's verdicts is far lighter than deciding alone, and faster as the law hardens. But the human still
  owns and signs each product, so at enough scale the authority is still a ceiling to plan around.

None of these sink the framework. They are the boundary of a genuinely leaner idea, and they travel with it so no one
claims more than it proves.

## AI is optional, and the directives are a folder you keep

The software pillar is deterministic and spends no tokens, so it runs with or without AI. TestThisPuppy works on its
own, and an AI model is added only to assist it, to read a failure and propose a fix, or to turn terse code into a
readable form. The model is configurable by the org or the person: name a model, pick a provider, or turn it off for
pure deterministic checks. The gate's verdict never depends on the AI being there; the AI only helps the people act
on it faster.

How the AI writes is set by the directives, and the directives are a folder you keep and extend. The default,
`directives/AI-DIRECTIVES.md`, is yours to add to: drop more `.md` files in the folder for org-wide or
product-specific direction, and the AI follows all of them. A pristine copy of the default is always kept in
`directives/_default-backup/`, never edited, so if the working directive is ever corrupted or lost it can be
restored from the default. The default is a floor you can always fall back to.

## The ship gate (nothing ships until all of this is true)

A product is certified to ship only when **all** of these hold, checked by software, not by claim:

- Every test passes. One hundred percent, no exceptions, no skips counted as passes.
- The tests were tested: the mutation score meets the bar the human set (weak tests do not count as passing tests).
- The code meets the human's criteria and coding style, validated by the deterministic checks.
- The third-party libraries have been scanned. By default their known vulnerabilities are reported, not blocking,
  because a dependency's CVE may not touch this product. They block only when the human flags that they care, with an
  optional minimum severity. Reported always, gating only on the human's word.
- The AI has done its part: the code and tests are written and its self-check is recorded.
- The human has given the final word: a recorded sign-off by the architect.

If any one is missing or red, the gate blocks and reports back. Nothing ships on a promise. The certificate is
issued by software, records who did what, and is reproducible: run it again and it says the same thing.
