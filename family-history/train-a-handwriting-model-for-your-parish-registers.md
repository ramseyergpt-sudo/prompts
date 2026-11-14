# Train a handwriting model for your parish registers

> **Work in progress.** The Bern study this comes from is still running: the larger test set, the human check and publishing are not done yet. This prompt will change as the study does. Each change to the process is made here too, so it always describes the current method. Last updated 2026-11-14.

A prompt for teaching a free, local handwriting model to read one archive's old registers, with AI models making and checking the training data and a person approving every step that leaves the computer. It is written up from the study behind `trocr-kurrent-bern-parish-registers` (the Reformed parish registers of canton Bern, 1555–1875, in German Kurrent). It works for any script, language and archive.

**Why bother.** The best AI models can read old handwriting well, but reading tens of thousands of pages with them costs a lot. A small fine-tuned model runs free on your own computer, and can read a whole archive overnight to make it searchable. The large models are then used where they matter most: making the training data, and checking the hard lines.

**What to expect, from the Bern study.**
- Out of the box, the published Bern model read our registers at about 40–50 % character error rate (CER).
- After fine-tuning on about 1,200 checked lines, it read them at about 14–20 %, level with a mid-sized general AI model.
- The best AI reader stayed at about 4–5 %.
- The gains flattened after about 1,200 lines, and from then on, better measurement mattered more than more data.

**Working scripts** for every step (rendering, line cutting, reading sheets, consensus, training data, fine-tuning and scoring), with one settings file, are at [github.com/ramseyergpt-sudo/prompts › handwriting-tools](https://github.com/ramseyergpt-sudo/prompts/tree/main/family-history/handwriting-tools). Tell the AI to start from them.

*Give everything below "The prompt" to an AI agent that can work with files and run programs on your computer.*

## The prompt

You are helping me build an open handwriting-recognition model for one set of historical registers. We will make the training data with AI readers, check it carefully, fine-tune an existing open model, measure it honestly, and publish it only when I approve. Work in phases, in order, and keep a written record of every decision and result. A wrong line in the training data teaches the model a mistake, so leave out anything you're unsure of rather than guess.

### Phase 0: Ask me first

Before doing anything, ask me:
- **Which records:** archive, series, places, record types (baptisms, marriages, burials, indexes) and years.
- **Script and language:** for example German Kurrent, Secretary hand, Dutch, Latin formulas, or a mix.
- **Access:** are the scans online, and what do the archive's terms allow: downloading, research use, publishing images?
- **My computer:** operating system, memory, and GPU (an Apple-silicon Mac or an NVIDIA card is enough). Training runs for hours, so can it run overnight?
- **AI budget:** which AI models and usage limits do I have? Making training data uses the large models heavily.
- **The goal:** searching my family's records, or a public model for other researchers too, or both.

Then write a short plan with phases and decisions, and keep it up to date as a `PLAN.md` file.

### Phase 1: Groundwork

1. **Study folder.** Make one folder for the project, with:
   - `README.md` (what this is);
   - `PLAN.md` (phases and decisions);
   - `METHOD.md` (exactly how each step is done);
   - `RESULTS.md` (numbers, dated, never overwritten);
   - `BACKGROUND.md` (models, papers, prior work, with links);
   - `GUIDELINES.md` (transcription rules).
   
   Large files (scans, line images, model checkpoints) go in a data folder beside it, not in Git.
2. **Find what exists.** Search for open models already trained on this script (Hugging Face, Transkribus public models, university digital-humanities groups), their training data, their licences and their reported error rates. Record who made them and when. **Fine-tune the closest open model; don't start from nothing.**
3. **Download gently.** Fetch scans one at a time, with pauses between requests, and keep a manifest (catalogue ID, title, source URL, date). Resume after errors; never hammer a small archive's server.

### Phase 2: A test set and a fair comparison

1. **Choose about 12–15 test pages** spread across the period, the record types and the difficulty (easy, ordinary and hard hands). They are **never** used for training: note their volumes and keep them out of every later round.
2. **Cut each page into line images.** Render each page to a large grayscale image, find the text lines with a layout tool (kraken's default segmentation works well), number the lines, and drop specks and fragments. Make sheets of about 12 numbered lines for reading.
3. **Blind readings.** Have two strong AI models each read every test page independently. Run them as separate helpers that see **only** that page's line sheets: no reference, no other readings, no hints beyond place, record type, period and script. Each returns `line, text, confidence`, transcribed **diplomatically**: spelling, abbreviations and punctuation exactly as written, nothing expanded or modernised, `word[?]` for a doubtful word, `[?]` for an unreadable one, `[noise]` for a line with no text.
4. **Run the existing open models** on the same line images.
5. **Consensus.** Compare the two AI readings line by line after loose normalisation (case, letter variants and punctuation ignored). Mark each line *agreed*, *close* (one word differs) or *disputed*.
6. **Verified reference.** On at least two pages, settle every close and disputed line on an enlarged image, using:
   - the two readings;
   - the calendar (weekday and date must agree; mind Julian and Gregorian);
   - page context (twins, repeated formulas);
   - local surnames and place names;
   - records already known.
   
   Mark lines *verified* or leave them out. **Never guess.**
7. **Score every reader** by character error rate on the verified lines only, both strict (exact text) and loose (normalised). Write the results to `RESULTS.md` with the date. Say plainly that an AI-made reference partly measures the adjudicating model's agreement with itself.

### Phase 3: Transcription guidelines

Write `GUIDELINES.md` before making training data, and apply it in code so every line follows it. For each rule, record who decided it and which published guidelines agree or differ. Examples are the OCR-D ground-truth guidelines, an archive's own HTR guidelines, CATMuS for medieval hands, or the base model's own output. Cover:
- letter forms (long s, ß, y with dots, u/v and i/j, umlauts and an e written above a vowel, capitals that look like small letters);
- marks above letters (the stroke that doubles n or m);
- abbreviations, kept as written and never expanded by a line model;
- numbers, dates, fractions and symbols (for example planet signs for weekdays);
- punctuation, line-end hyphens, and what to leave out (archive stamps, later labels).

**Prefer the rules of guidelines written for HTR training data** over those for printed editions: training data must show what the scribe wrote, not a modern reading text. Ask me to review the guidelines, and suggest a palaeographer's review before publishing.

### Phase 4: Training rounds

Each round is about 10 pages, sized to fit one AI usage window.
- **Choose pages** from volumes not in the test set and not used before, one or two per volume, spread across scribes, decades and record types. Aim for a mix by period and record type, and include some faded and heavy pages.
- **Same pipeline:** render, segment, two blind AI readings, consensus.
- **Settle close lines** on enlarged images. Keep only lines where every character is confirmed. Drop lines with `[?]`. Leave out unresolved names rather than guess them.
- **Save** each page's verified lines (`line, text, status`) and the round's training file. Record the count and page list in `RESULTS.md`.

### Phase 5: Fine-tune

- **Fine-tune the closest open model** on all verified lines so far. Run it in the background on my GPU.
- **Hold out whole validation pages**, not random lines, so the score reflects unseen hands.
- **Mix in about 25 % of the base model's own training data,** if it is published, so the model doesn't forget what it already knew.
- **Train for several epochs,** and keep the checkpoint with the lowest validation CER.
- **Read the test pages** with the new model, score them against the verified reference and the consensus pages, and compare with the base model and the AI readers.
- **After each round, add a point to a learning curve:** CER against the number of training lines. When the curve flattens, stop adding the same kind of data. Target the gaps instead (name indexes, the earliest hands, the latest period, the hardest scribes), or improve the measurement.
- **Settings to try** if the model repeats itself at the end of a line: a no-repeat setting during reading (`no_repeat_ngram_size=3`).

### Phase 6: Make the measurement trustworthy

A model is only as credible as its test. Before publishing:
- **A larger verified test set:** about six fully verified pages, covering every period and including at least one name index and one of the earliest hands. Report a score per page with an uncertainty range.
- **A human check:** build me a simple review page with about 100 sampled reference lines, each with its image and text, and buttons for *correct*, *wrong* and *unsure*. My marks, or a palaeographer's, give the error rate of the AI-made reference itself.
- **An outside baseline:** if I'm willing, I run the same test pages through a public model in my own Transkribus account and give you the export to score.

### Phase 7: Publish (each step only with my approval)

- **Name** the model clearly: architecture, script, source and version (for example `trocr-kurrent-<archive>-<record-type>-v1`).
- **Model card:**
  - what it reads and what it doesn't;
  - training data and test scores before and after;
  - the method and its limits (names, microfilm quality, the AI-made reference);
  - credits and licences for the base model and any data mixed in. Match the base model's licence.
- **Dataset:** the transcriptions and line references (volume, image, line position), and a script that fetches the images from the archive. **Don't publish scan images** unless the archive has agreed.
- **Upload:** I sign in to the hosting site myself (for example `huggingface-cli login`). You never see or handle my token.
- **Write-up:** a short article built from `RESULTS.md` and `BACKGROUND.md`: what worked, what didn't, and the numbers.

### Phase 8: Outreach (you draft, I send)

Draft short messages, for me to review and send, to:
- the group that made the base model: offer the verified lines and test set, ask for an expert check, and ask about their guidelines;
- the archive: about publishing line images in a research dataset, and a note about the gentle bulk download;
- local historians or societies who could use the searchable registers.

### Phase 9: Use it

Once the error rate is known, read whole registers overnight (a **register sweep**). Write each reading to a file that keeps its volume, page and line. Then:
- **search** the readings for surnames, with spelling variants;
- **check every hit by eye** on the image before it enters the family tree;
- rebuilding whole families from the readings is the next step (a prompt for it is in preparation).

### Rules throughout

1. **Leave a line out rather than guess.** Training data must be correct to the character.
2. **Keep the test set out of training,** by volume, not just by page.
3. **Record every result with its date,** including the disappointing ones. Never overwrite earlier numbers.
4. **Be gentle with archive servers:** one download at a time, with pauses.
5. **Nothing leaves my computer without my approval:** no uploads, no messages, no publishing.
6. **Never handle my passwords or tokens.**
7. **Don't publish archive images** without the archive's permission. Transcriptions and line references are fine.
8. **Credit everyone whose work you build on:** model makers, dataset makers, guideline authors.
