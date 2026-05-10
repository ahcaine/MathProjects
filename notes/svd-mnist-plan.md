# SVD Series and MNIST Section Plan

## Summary

Add a new student-focused SVD mini-course to the static site as a small multi-page section. The section should teach the intuition behind singular value decomposition first, then culminate in an MNIST application page showing how SVD can help detect digit shape structure using a training set and a test set.

The tone should stay instructional and visual, matching the current site style: simple static pages, side-by-side code/media layouts, and easy-to-follow explanations.

## Key Changes

- Add a new SVD section to the homepage so it sits alongside the existing Manim examples.
- Create an SVD landing page that acts as the hub for the series.
- Create a small set of lesson pages for the mini-course:
  - geometric intuition
  - matrices as transformations
  - rank, approximation, and compression
  - images, dominant features, and low-rank structure
  - MNIST application
- Treat the MNIST page as the capstone page, not the first page users land on.
- Keep the site static: each lesson is a normal HTML page using the existing shared styling and code-display pattern.

### Planned page/interface structure

Use a structure like this:

- `index.html`
  - add a new card or section linking to the SVD mini-course
- `svd/index.html`
  - overview page for the series
  - short explanation of what SVD is
  - playlist embed area or YouTube links
  - links to all lesson pages
- `svd/geometry.html`
- `svd/transformations.html`
- `svd/approximation.html`
- `svd/images.html`
- `svd/mnist.html`

### Planned content behavior

- Each lesson page should include:
  - a short plain-language overview
  - a code panel when useful
  - a visual/demo area
  - links to previous/next lessons
- The landing page should include:
  - a short series introduction
  - embedded playlist or links to videos
  - a clear reading/watching order
- The MNIST page should include:
  - a plain-language explanation of the dataset
  - a training-set / test-set explanation
  - a code example showing the SVD-based workflow
  - example digit images and/or reconstructed digits
  - an explanation that SVD captures dominant shape information
  - simple results such as accuracy, example classifications, or a confusion-style summary

## Implementation Details

- Reuse the current site’s static approach and styling rather than introducing any framework.
- Reuse the existing “code from file” pattern for Python examples where possible.
- Add a new directory for the SVD section rather than mixing those pages into a shared pages folder.
- Keep video support flexible:
  - short local MP4s for brief demonstrations
  - YouTube embeds or links for lecture/playlist material
- Store future SVD/MNIST code, data, and figures together inside a dedicated project folder.

### Public-facing additions

- New homepage navigation or section for “SVD Series”
- New SVD landing page
- New lesson pages
- New MNIST capstone page
- Optional playlist embed area on the SVD landing page

## Test Plan

- Verify the homepage links correctly to the SVD landing page.
- Verify each SVD lesson page loads with the shared site styling.
- Verify previous/next lesson navigation works.
- Verify code panels load the intended Python files.
- Verify any local MP4s and YouTube embeds display correctly.
- Verify the MNIST page explains the training/test split clearly and presents at least one concrete result or visual example.
- Verify the whole section remains readable on both desktop and mobile.

## Assumptions and Defaults

- Audience: students first.
- Site structure: mini-course, not a single page.
- Delivery format: static HTML pages, no build system.
- Teaching order: intuition first, application second.
- The MNIST page will emphasize explanation and visualization over research-grade benchmarking.
- Playlist/video support should be included in the plan, but the exact YouTube URLs can be added later.
- This plan is for a future site addition and should eventually be recorded in repo context documents such as `AGENTS.md` or a future note when implementation resumes.
