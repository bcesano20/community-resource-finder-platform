# CLAUDE.md — Frontend

This file defines the code conventions for the project's frontend. It goes inside `frontend/CLAUDE.md`. Any code generated or modified in this folder must follow these rules.

## Stack

React + TypeScript, Vite as the bundler, Tailwind CSS, **pnpm** as the package manager. Mobile-only design. No external state management library (Redux, Zustand, etc.) — the app's state is small enough to be handled with `useState`/`useReducer` and React Context. Don't introduce a global state dependency without a concrete reason for it.

## Folder structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── ChatBubble/
│   │   │   ├── ChatBubble.tsx
│   │   ├── PlanCard/
│   │   │   ├── PlanCard.tsx
│   │   └── index.ts          # barrel file: re-exports all components
│   ├── pages/
│   │   ├── UnlockScreen.tsx
│   │   └── ChatScreen.tsx
│   ├── hooks/
│   │   ├── useAudioRecorder.ts
│   │   ├── useSession.ts
│   │   └── useFollowUpLimit.ts
│   ├── apiCalls/
│   │   ├── client.ts          # base fetch/axios instance, handles the session token
│   │   ├── session.ts         # POST /api/session/
│   │   ├── queries.ts         # POST /api/queries/
│   │   └── messages.ts        # POST /api/messages/
│   ├── types/
│   │   └── index.ts           # Resource, Plan, ChatMessage, ApiError, etc. Named with Interface at the end for each one
│   ├── helpers/
│   │   ├── constants.ts       # API routes, limits (e.g. MAX_FOLLOW_UP_QUESTIONS = 2), error messages
│   │   └── formatters.ts      # pure utils (time formatting, validation, etc.)
│   ├── assets/
│   ├── App.tsx
│   ├── Layout.tsx
│   ├── main.tsx
│   └── index.css              # Tailwind entrypoint
├── .env.example
├── .eslintrc.cjs
├── .prettierrc
├── tailwind.config.ts
├── tsconfig.json
├── vite.config.ts
└── package.json
```

### Organization rules

- **`components/`**: one component per folder, with its `.tsx` file. The root `index.ts` in `components/` re-exports everything, so the rest of the app always imports from `@/components`, never from a deep path.
- **`pages/`**: the screens in the flow (for now, unlock and chat). A page composes components and hooks — it holds no business logic and makes no direct `fetch` calls of its own.
- **`hooks/`**: all logic reused across components or pages. Always prefixed with `use`. A hook should not render JSX.
- **`apiCalls/`**: every HTTP call to the backend lives here, not inside components or hooks directly. Hooks consume the functions in `apiCalls/`, never the other way around.
- **`helpers/`**: constants and pure utilities. **No loose magic strings or numbers inside a component** — every API route, numeric limit, `sessionStorage` key, or error message goes as a named constant in `helpers/constants.ts` and gets imported where needed.
- **`types/`**: shared interfaces and types. If the backend ends up exposing an OpenAPI schema via `drf-spectacular`, this is the place for the generated types, or for hand-written equivalents in the meantime. All the interfaces should be named with the "Interface" at the end for example "ResourceInterface".

## Code conventions

- Functional components only, no class components.
- One component per file. File name and component name in `PascalCase`.
- Hooks, helpers, and API files in `camelCase`.
- Props always typed with an `interface` (`interface ChatBubbleProps { ... }`), never `any`.
- Named exports for components (not `export default`), so the `components/index.ts` barrel file works consistently.
- No business logic or network calls inside a presentational component — that lives in `hooks/` or `apiCalls/`.
- Accessibility: every icon-only button (record, send, cancel) needs an `aria-label`. Since the app relies on a single large audio button as its main interaction, pay special attention to focus states and touch target sizes.
- Centralized error handling: the error messages shown to the user should be mapped from `helpers/constants.ts`, not written inline in the component that displays them.

## TypeScript

- `strict: true` in `tsconfig.json`, no exceptions.
- Path aliases configured in both `tsconfig.json` and `vite.config.ts`: `@/components`, `@/pages`, `@/hooks`, `@/api`, `@/types`, `@/helpers`. No long relative imports like `../../../components`.

## ESLint and Prettier

- ESLint with `@typescript-eslint/recommended`, `eslint-plugin-react-hooks` (hooks rules), and `eslint-plugin-jsx-a11y` (accessibility).
- Prettier for formatting, integrated with `eslint-config-prettier` so the two tools' style rules don't clash.
- Suggested base config for `.prettierrc`: single quotes, semicolons, `trailingComma: "all"`, `printWidth: 100`.
- Optional but recommended for this project: `husky` + `lint-staged`, running `eslint --fix` and `prettier --write` on staged files at pre-commit.

## package.json — expected configuration

```json
{
  "name": "community-resources-frontend",
  "private": true,
  "type": "module",
  "packageManager": "pnpm@9",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx",
    "lint:fix": "eslint . --ext ts,tsx --fix",
    "format": "prettier --write .",
    "type-check": "tsc --noEmit"
  }
}
```

Main dependencies: `react`, `react-dom`.
Main dev dependencies: `typescript`, `vite`, `@vitejs/plugin-react`, `tailwindcss`, `postcss`, `autoprefixer`, `eslint` plus the plugins listed above, `prettier`, `eslint-config-prettier`.

## Environment variables

- Any variable exposed to the frontend must be prefixed with `VITE_` (Vite's requirement to expose it to the client).
- `.env` is never committed. Keep `.env.example` up to date with the required keys (e.g. `VITE_API_BASE_URL`) without real values.
- Never put an OpenAI or Anthropic API key in a frontend environment variable — those calls live exclusively in the backend.

## Testing

Vitest + React Testing Library, focused on the hooks (`useAudioRecorder`, `useFollowUpLimit`).
