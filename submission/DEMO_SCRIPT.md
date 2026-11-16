# Optional 3 to 5 minute demonstration

Run the main MMLU reproduction and then `python code/quick_demo.py`.

**0:00-0:40.** Ask the central question: can an evaluator choose a different system when every answer is fixed? Explain that this is a controlled copy audit and not a claim about naturally occurring errors. Define a root, its declared mass and one shared copy schedule.

**0:40-1:30.** Show Figure 1 and the quick-demo output. Gemini has 532/588 correct, GPT 530/588 and Claude 525/588. Copy the three supplied roots for all ten configurations. GPT becomes uniquely first with 533/591. Two copies could only tie the two-answer deficit, so three is minimal.

**1:30-2:10.** Show the different eight-copy schedule for Claude. Explain why separately possible pairwise reversals cannot simply be combined; the same schedule must beat all rivals. Show the seven exact integer blocking certificates and the complete three-member possible-winner set.

**2:10-2:50.** Show Figure 2. At the 10% floor budget, 24 pooled orders reverse, one can tie only and twenty stay strictly robust. Calibration has four targeted reversals among eighteen comparisons but none in its declared random controls. Explain the difference between finite worst cases, specified randomization and natural prevalence.

**2:50-3:40.** Demonstrate the mass-conserving closure and declare its assumption: copies preserve the full evaluated input and trusted root lineage. Explain that literal deduplication is simpler for literal copies and that unknown lineage remains unverified.

**3:40-4:20.** Show the reproduction status and source manifest. Finish with the practical proposal: publish copy budgets, attained bounds, possible winners and root-mass policies alongside point scores.
