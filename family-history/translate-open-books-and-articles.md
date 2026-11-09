# How to translate open books and articles

An instruction set for making **side-by-side translations** of books and articles that are free to translate, with an AI doing the work and a person setting the rules. It grew out of the family-history work behind [Build your own family history with AI](build-your-own-family-history-with-ai.md), where old German books, sermons and histories needed English versions. It works for any language pair.

*To use it, give everything below "The instructions" to an AI agent along with the text to translate.*

## The instructions

You are translating a book or article for me. Make a faithful, readable translation, set **side by side with the original**, that keeps the original's structure exactly. Then a reader can check any sentence against the source, and others can reuse and correct the work. Work through the steps in order.

### 1. Check that the text is free to translate

Before translating anything, establish its status and write it in the file header:

- **Public domain:** the author died long enough ago (70 years in most of Europe, the UK and many other countries), or the work was published before the cut-off in the United States (currently works published before 1931). Check both the author's death and the publication date.
- **Open licence:** the text carries a licence that allows adaptations.
  - **CC BY** or **CC0**: translation is allowed.
  - **CC BY-SA**: allowed, and the translation must carry the same licence.
  - **CC BY-NC**: allowed for non-commercial use only.
  - **CC BY-ND** (no derivatives): translation is **not** allowed without permission.
- **A modern edition of an old text** may add copyrighted material: an editor's introduction, notes or modernised spelling. Translate the old text itself, not the modern additions.
- **If it isn't free,** stop and tell me. A private reading translation for my own use may be possible, but it must be marked "private: not for publication" and never shared, published or committed to a public repository.

### 2. Choose and cite the source text

- Use the **best available original**: the first edition, the author's last revised edition, or a scholarly edition of the original text. Say which, and why.
- Prefer a **proofread transcription** (Wikisource, Project Gutenberg, a scholarly edition) over raw OCR. If only scans exist, transcribe from the page images and proofread against them.
- **Record** the author, title, edition, place, publisher, year, page range, the URL of the copy used, and the date you accessed it.
- **Check for an existing translation first.** If an open translation already exists, tell me before starting: improving or annotating it may be more useful than making a new one.

### 3. Keep the original's structure

The translation must follow the original **unit for unit**, so the two can always be lined up:

- the same **title, parts, chapters and headings**, in the same order and with the same numbering;
- the same **paragraphs**: never merge or split them, even when an original paragraph is very long;
- **verse** line by line and stanza by stanza; **lists, tables and question-and-answer** pairs item by item;
- **page breaks** of the source edition, marked in both columns as `[p. 12]` at the point where the page turns;
- the author's **footnotes** with their original numbers or symbols, kept separate from your notes;
- **section breaks you add** for readability, marked differently (for example `✦`) and explained in the header. Never present them as the author's.

Nothing is left out. If a passage is illegible, damaged or untranslatable, keep its row and say so: `[illegible, about two lines]`.

### 4. The side-by-side format

Write one Markdown file per work, or one per chapter for a long book. Each file starts with a header, then the text as a table: one row per paragraph, heading, verse stanza or list item.

```markdown
# Useful and Edifying Address to the Young (1804)

| | |
|---|---|
| **Original** | Christian Burkholder, *Nützliche und erbauliche Anrede an die Jugend* (Ephrata, 1804), pp. 1–35. Copy used: … (URL, accessed 2026-11-09) |
| **Status** | Public domain (published 1804) |
| **Translation** | English, by Claude (Anthropic), 2026-11-09, for … Draft, not yet reviewed by a person |
| **Licence of this translation** | CC BY 4.0 (or the original's licence, if it requires one) |
| **Conventions** | page breaks as [p. n]; translator's notes as TN1, TN2…; ✦ = break added by the translator |

| ¶ | Original | Translation |
|---|---|---|
| 0.1 | **Nützliche und Erbauliche Anrede an die Jugend** | **Useful and Edifying Address to the Young** |
| 0.2 | Psalm 119, 9. Wie wird ein Jüngling seinen Weg unsträfflich gehen? Wenn er sich hält nach deinen Worten. | Psalm 119:9. Wherewithal shall a young man cleanse his way? by taking heed thereto according to thy word. (KJV) |
| 0.3 | Gedruckt im Jahr MDCCCIV. | Printed in the year 1804. |
| 1.1 | [p. 3] Die Haupt-Bewegungs-Ursach zu diesem Büchlein … | [p. 3] The chief reason for this little book … |

## Translator's notes

- **TN1** (¶ 1.1) *Bewegungs-Ursach*: literally "moving cause"; rendered "reason".
```

- **Number the rows** by chapter and paragraph (`3.14` = chapter 3, paragraph 14), so anyone can cite a passage in either language.
- **Keep the original's formatting** in both columns: bold, italics, small capitals rendered as bold, quotations and indented verse.
- **Long texts:** if a table becomes unwieldy, use one file per chapter, with the same numbering.
- **Optionally,** produce a translation-only reading copy from the table afterwards. The side-by-side file remains the master.

### 5. Translate faithfully and readably

- **Meaning first.** Translate what the text means, in natural modern prose, not word for word. Don't paraphrase, summarise, abridge or improve the argument.
- **Keep the voice and period.** Don't modernise the author's beliefs, soften harsh passages or add political correctness. Don't make old prose sound like today's either: plain, dignified English suits most older texts.
- **Scripture and quotations:** when the author quotes a well-known text, use an established translation of the same period and tradition (for example the King James Version for a German Protestant text of 1800), and name it in the header.
- **Names and places:** keep personal names as written. Use the usual modern form of place names, with the original in a note the first time.
- **Terms of art** (church, legal, farming, coins, measures, offices): keep the original word in italics with a gloss in square brackets the first time, e.g. *Täufer* [Anabaptists], *Batzen* [a small coin], then use the English. Record each one in the glossary (step 6).
- **Dialect and old spelling:** read through them to the standard language, and note in a TN where a dialect word carries a meaning the standard word would lose.
- **Dates, money and measures:** keep them as the author gave them (Old Style dates, local currency, local units). Explain them in a TN if needed; don't convert silently.
- **Uncertainty:** where you aren't sure of a reading or a meaning, translate your best reading, mark it `[?]`, and explain the alternatives in a TN. Never hide a doubt.

### 6. Notes and glossary

- **Translator's notes** (TN1, TN2…) go in a list after the table, each pointing to its row. Keep them short: what is uncertain or unusual, and why you chose your rendering. Keep them separate from the author's own notes.
- **A glossary** at the end (or a shared glossary file for a series) lists each term of art with its gloss and the row where it first appears. Use the same English for the same term throughout.
- **Historical context** belongs in the notes only where a reader would otherwise misunderstand the text. Longer context goes in a separate essay, labelled as interpretation.

### 7. Check the work

Before calling a translation done:

1. **Alignment:** every row has both columns filled, row numbers run without gaps, and the number of rows matches the number of paragraphs in the original.
2. **Completeness:** compare each translated row with its original for omissions, especially lists, negations, numbers and names.
3. **Consistency:** every glossary term is rendered the same way throughout.
4. **Second reading:** where possible, have a second model or a person who reads the language check a sample of rows, and record who checked what.
5. **Status:** set the header to *Draft*, *Checked by AI* or *Reviewed by [person], [date]*. Never label an unreviewed AI translation as reviewed.

### 8. Share it constructively

- **Credit the original** prominently: author, edition and a link to the copy used.
- **Be honest about how it was made:** name the AI, the date, and the review status, and invite corrections.
- **Licence it openly** so others can reuse and improve it: CC BY 4.0, or the licence the original requires (CC BY-SA if the source is CC BY-SA).
- **Give back.** Report transcription errors you find to the source (Wikisource, Project Gutenberg, the Internet Archive or the archive's catalogue), and link the translation from wherever readers of the original will look.
- **Ask before publishing.** Nothing is posted, uploaded or pushed until I have looked at it.

### 9. Articles

The same steps apply to articles. In addition:

- **Check the licence** on the article page itself. Open-access articles are often CC BY, but not always: some journals add NC or ND.
- **Keep the scholarly apparatus as it is:** the citations, reference list, figure numbers, table numbers and DOI stay in the original form. Translate figure captions, table headings and the abstract.
- **Keep technical terms** consistent with the field's standard translations, and gloss any that have none.
