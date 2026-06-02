# Visual Companion Guide

Browser-based visual brainstorming companion for showing mockups, diagrams, and options.

## When to Use

Decide per-question, not per-session. The test: **would the user understand this better by seeing it than reading it?**

**Use the browser** when the content itself is visual:
- **UI mockups** — wireframes, layouts, navigation structures, component designs
- **Architecture diagrams** — system components, data flow, relationship maps
- **Side-by-side visual comparisons** — comparing two layouts, two color schemes
- **Design polish** — when the question is about look and feel, spacing, visual hierarchy
- **Spatial relationships** — state machines, flowcharts, entity relationships as diagrams

**Use the terminal** when the content is text or tabular:
- **Requirements and scope questions**
- **Conceptual A/B/C choices** — picking between approaches described in words
- **Tradeoff lists** — pros/cons, comparison tables
- **Technical decisions** — API design, data modeling, architectural approach
- **Clarifying questions** — anything where the answer is words, not visuals

## How It Works

The server watches a directory for HTML files and serves the newest one to the browser. You write HTML content to `screen_dir`, the user sees it in their browser and can click to select options.

**Content fragments vs full documents:** If your HTML file starts with `<!DOCTYPE` or `<html`, the server serves it as-is. Otherwise, the server automatically wraps your content in the frame template.

## Starting a Session

```bash
# Start server with persistence
scripts/start-server.sh --project-dir /path/to/project

# Returns: JSON with port, url, screen_dir, state_dir
```

**Windows/Git Bash note:** Use `--foreground` flag as Windows auto-detects and uses foreground mode.

**Tell user to open the URL.** Server info is also written to `$STATE_DIR/server-info`.

## The Loop

1. **Check server is alive**, then **write HTML** to a new file in `screen_dir`:
   - Use semantic filenames: `platform.html`, `visual-style.html`, `layout.html`
   - **Never reuse filenames** — each screen gets a fresh file
   - Server automatically serves the newest file

2. **Tell user what to expect and end your turn:**
   - Remind them of the URL
   - Give a brief text summary of what's on screen

3. **On your next turn** — after the user responds:
   - Read `$STATE_DIR/events` if it exists — contains user's browser interactions

4. **Iterate or advance** — write new file for changes

5. **Unload when returning to terminal** — push a waiting screen

6. Repeat until done.

## Writing Content Fragments

Write just the content that goes inside the page. The server wraps it in the frame template.

**Minimal example:**

```html
<h2>Which layout works better?</h2>
<p class="subtitle">Consider readability and visual hierarchy</p>

<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content">
      <h3>Single Column</h3>
      <p>Clean, focused reading experience</p>
    </div>
  </div>
  <div class="option" data-choice="b" onclick="toggleSelect(this)">
    <div class="letter">B</div>
    <div class="content">
      <h3>Two Column</h3>
      <p>Sidebar navigation with main content</p>
    </div>
  </div>
</div>
```

## CSS Classes Available

### Options (A/B/C choices)
```html
<div class="options">
  <div class="option" data-choice="a" onclick="toggleSelect(this)">
    <div class="letter">A</div>
    <div class="content"><h3>Title</h3><p>Description</p></div>
  </div>
</div>
```

**Multi-select:** Add `data-multiselect` to the container.

### Cards (visual designs)
```html
<div class="cards">
  <div class="card" data-choice="design1" onclick="toggleSelect(this)">
    <div class="card-image"><!-- mockup --></div>
    <div class="card-body"><h3>Name</h3><p>Description</p></div>
  </div>
</div>
```

### Mockup container
```html
<div class="mockup">
  <div class="mockup-header">Preview: Dashboard Layout</div>
  <div class="mockup-body"><!-- your mockup --></div>
</div>
```

### Split view, Pros/Cons, Mock elements
See `scripts/frame-template.html` for all available CSS classes.

## Cleaning Up

```bash
scripts/stop-server.sh $SESSION_DIR
```

## Reference

- Frame template (CSS reference): `scripts/frame-template.html`
- Helper script (client-side): `scripts/helper.js`
- Server: `scripts/server.cjs`
