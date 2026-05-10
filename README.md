# Math Simulation Site Starter

This repository is a small static website starter for sharing math simulations, short MP4 demonstrations, Python code, and optional YouTube videos.

Project context, goals, and deployment notes are also stored in `AGENTS.md`.

## Structure

- `index.html` is the homepage.
- `projects/parabola-average/` is a hosted Manim example project.
- `projects/lorenz-attractor/` is a sample simulation project.
- `styles.css` contains the layout and visual styling.
- `scripts/site.js` adds small interactions and auto-loads example code.
- `projects/` holds self-contained project folders with each page, its code, and its project-specific media together.
- `media/images/` is reserved for shared site images such as the homepage slideshow.

## Local Preview

You can open `index.html` directly in a browser, but the code loader works best if you serve the folder locally.

For example:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Publishing

This site is designed to work well with GitHub Pages because it does not require a build step.

To publish it the simple way:

1. Push the repository to GitHub.
2. Open the repository on GitHub.
3. Go to `Settings` -> `Pages`.
4. Under `Build and deployment`, choose `Deploy from a branch`.
5. Set the branch to `main` and the folder to `/ (root)`.
6. Save.

GitHub will then host the files directly from this repository.

## Adding a New Simulation

1. Copy `projects/lorenz-attractor/` to a new project folder.
2. Rename the copied `index.html` and code file references as needed.
3. Place your MP4, notebook, figures, or Python source inside that project folder.
4. Update the page title, summary, and local file paths.
5. Add a link to the new project from `index.html`.

## Notes

- Syntax highlighting is provided with Prism from a CDN.
- The sample page includes a local MP4 slot and a YouTube embed slot.
- If you prefer, the local video and YouTube embed can be used independently.
