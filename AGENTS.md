# AGENTS.md

## Project Summary

This repository is a static website for hosting short mathematical and Manim-based animations, alongside the Python code used to generate them.

The immediate goal is to publish the site on GitHub Pages and use it as a lightweight teaching portfolio for simulations, visual explanations, and small MP4 demonstrations.

## Current Site Structure

- `index.html`: homepage for the site
- `styles.css`: shared visual styling
- `scripts/site.js`: loads Python source files into syntax-highlighted code blocks
- `projects/parabola-average/`: hosted example project using a real Manim animation
- `projects/lorenz-attractor/`: reusable template/example project
- `projects/`: preferred home for each project page, code, and project-specific media
- `media/images/`: shared site imagery such as the homepage slideshow

## User Context

- The site owner is a math professor.
- The site is intended to present mathematical simulations clearly for students or interested viewers.
- Short MP4 files under a few megabytes should be hosted directly in the repo when practical.
- Python code should be visible with syntax highlighting, ideally next to the demonstration it produces.
- Some pages may eventually include YouTube links or embeds for longer explanations.
- The user is currently creating Manim animations and wants real examples hosted rather than placeholder content.

## Design Direction

- Keep the site simple and static.
- Favor readable academic presentation over heavy frameworks.
- Use side-by-side layouts for code and demonstration media.
- Make it easy to duplicate a simulation page and swap in a new Python file and MP4.
- Preserve a polished but approachable look suitable for mathematical teaching content.

## Current Hosted Example

The main real example at the moment is:

- `projects/parabola-average/`

This page uses:

- `projects/parabola-average/FluidAverageValue.py`
- `projects/parabola-average/parabola_avg.mp4`

The animation shows a parabola, a particle-based fill of the region, and a horizontal line corresponding to the average value.

## Local Preview

The site can be previewed locally with:

```bash
python3 -m http.server 8000
```

Then open:

- `http://localhost:8000`

## GitHub Pages Plan

This repository is already connected to:

- `git@github.com:anthonyholliscaine-creator/github.io.git`

The intended publishing path is:

1. Push this repository to GitHub on the `main` branch.
2. Open GitHub repository settings.
3. Go to `Pages`.
4. Set deployment to `Deploy from a branch`.
5. Choose `main` and `/ (root)`.
6. Visit the published Pages URL once deployment finishes.

If this repository is the special user site repo for the account, the final URL may be the account root domain. If it is a normal project repo, GitHub Pages will typically publish it under a project subpath.

## Content Workflow

When adding a new animation:

1. Copy an existing project folder in `projects/`.
2. Keep that project's HTML, source code, notebook/data files, and short media together.
3. Update the page title, summary text, code source path, and video/image paths.
4. Add a homepage link from `index.html`.

## Near-Term Priorities

- Add more real Manim examples.
- Personalize the homepage with the professor's name, course framing, and mathematical themes.
- Decide whether to embed YouTube videos directly on some pages.
- Publish the current version on GitHub Pages.

## Notes For Future Agents

- Keep the site build-free unless there is a strong reason to introduce tooling.
- Prefer editing the existing static structure over replacing it with a heavy framework.
- Avoid removing user content or imported examples unless explicitly requested.
- Prefer direct branch-based GitHub Pages deployment unless the user explicitly wants more automation later.
