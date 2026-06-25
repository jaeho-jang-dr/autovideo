# Gemini Code Directive: Hangeul Curriculum Deploy & Bilingual Toggle Enforcement

The Producer (User) has requested that **all pages must have a clear Korean/English language toggle button**. Since the "Sori Hangeul" (groove) page currently hides the header/footer (`hideHeaderFooter={true}`), it lacks the GNB language toggle. 

Perform the routing swap (defaulting to English) and enforce bilingual toggle visibility across all screens before final production deployment:

---

## 1. Routing Swap & Re-architecture

Move the pages so that root templates render English (`en`), and the `/ko/` directory contains the Korean versions.

### A. Swap Index Page (Home)
- **Root Home (`web/src/pages/index.astro`)**:
  - Render English (`lang = 'en'`). Set `altUrl="/ko/"`.
- **Korean Home (`web/src/pages/ko/index.astro`)**:
  - Render Korean (`lang = 'ko'`). Set `altUrl="/"`.

### B. Swap Curriculum Page
- **Root Curriculum (`web/src/pages/curriculum.astro`)**:
  - Render English (`lang = 'en'`). Set `altUrl="/ko/curriculum/"`.
- **Korean Curriculum (`web/src/pages/ko/curriculum.astro`)**:
  - Render Korean (`lang = 'ko'`). Set `altUrl="/curriculum/"`.

### C. Swap Groove Page
- **Root Groove (`web/src/pages/groove.astro`)**:
  - Render English (`lang = 'en'`). Set `altUrl="/ko/groove/"`.
- **Korean Groove (`web/src/pages/ko/groove.astro`)**:
  - Render Korean (`lang = 'ko'`). Set `altUrl="/groove/"`.

### D. Swap Lesson Page
- **Root Lesson (`web/src/pages/lesson/[code].astro`)**:
  - Render English (`lang = 'en'`). Set `altUrl={`/ko/lesson/${episode.code}/`}`.
- **Korean Lesson (`web/src/pages/ko/lesson/[code].astro`)**:
  - Create directory `web/src/pages/ko/lesson/` if it doesn't exist.
  - Render Korean (`lang = 'ko'`). Set `altUrl={`/lesson/${episode.code}/`}`.

### E. Swap Category Page
- **Root Category (`web/src/pages/category/[category].astro`)**:
  - Render English (`lang = 'en'`). Set `altUrl={`/ko/category/${category}/`}`.
- **Korean Category (`web/src/pages/ko/category/[category].astro`)**:
  - Create directory `web/src/pages/ko/category/` if it doesn't exist.
  - Render Korean (`lang = 'ko'`). Set `altUrl={`/category/${category}/`}`.

- **Delete old `web/src/pages/en/` directory completely** to prevent route conflicts.

---

## 2. Bilingual Toggle Visibility Enforcement

Ensure that **every page** has a visible language switcher.

1.  **GNB Lang Switcher Enhancement**:
    - Brush up the `.lang-switch` styles in `web/src/layouts/BaseLayout.astro` to be more prominent, modern, and beautiful (e.g. glassmorphism capsule/pill design with a subtle border and glowing hover indicator).
2.  **Sori Hangeul (Groove) App Language Toggle**:
    - Since `web/src/pages/groove.astro` and `web/src/pages/ko/groove.astro` hide GNB header/footer (`hideHeaderFooter={true}`), we must add a floating language switcher inside the `GrooveBoard.astro` cockpit UI (e.g. top-right corner next to the control panel).
    - Render a stylish pill-shaped button: `KO | EN` switching between `/groove/` (English default) and `/ko/groove/` (Korean). Make sure it matches the neon 3D mechanical arcade theme.

---

## 3. Commit & Verification
- Commit the modified files to `feat/hangeul-curriculum`.
- Verify the encoding of modified/new files:
  ```bash
  python .harness/verify/check_encoding.py
  ```
- Checkout `main`, merge `feat/hangeul-curriculum` into `main`.

---

## 4. Production Build & Deployment
1.  Navigate to `web/` and build the static artifacts:
    ```bash
    npm run build
    ```
2.  **Vercel Deploy**:
    Run `vercel deploy --prod` in the `web/` folder.
3.  **Cloudflare Pages Deploy**:
    Run `npx wrangler pages deploy dist` in the `web/` folder.

---

## 5. Report Results
Verify that the production URLs (e.g. `https://drjayed.com/` -> EN default, `https://drjayed.com/ko/` -> KO fallback, `/curriculum/` -> EN default, `/ko/curriculum/` -> KO, `/groove/` -> EN, `/ko/groove/` -> KO) all resolve correctly and feature the new language toggles. Write a summary to `scratch/gemini_report.md`.

Begin task execution now.
