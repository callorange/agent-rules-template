# Web Frontend Architecture Rules (웹 프론트엔드 특화 규칙)

웹 프론트엔드(React, Next.js, Vue, Vite, Svelte 등) 프로젝트에 적용되는 아키텍처 및 개발 규칙입니다.

---

## 🎨 1. UI/UX 디자인 및 디벨롭먼트 표준

- **시각적 우수성 (Rich Aesthetics)**: 단순한 최소 기능 구현에 그치지 않고 현대적이고 감각적인 UI 스타일링(조화로운 컬러 팔레트, 현대적 서체, Glassmorphism, 부드러운 트랜지션 및 Hover 효과)을 적용하십시오.
- **모던 CSS/Styling**: 픽셀 하드코딩 대신 HSL tailored 색상 모듈 및 Vanilla CSS/TailwindCSS 디자인 토큰을 활용하고, 브라우저 기본 폰트 대신 Google Fonts 등 현대적 폰트를 활용하십시오.
- **인터랙티브 마이크로 애니메이션**: 사용자 인터랙션 요소(버튼, 카드, 모달 등)에는 부드러운 상태 변화 애니메이션을 적용하여 사용성을 높이십시오.
- **플레이스홀더 이미지 자제**: 이미지가 필요한 경우 실제 동작 가능한 미디어 및 생성형 에셋을 활용하십시오.

---

## 🛠️ 2. 프론트엔드 아키텍처 및 상태 관리

- **컴포넌트 단일 책임**: 컴포넌트는 단일 기능에 집중하고, UI 렌더링과 비즈니스 로직(API 호출, 상태 처리)을 가급적 커스텀 훅(Custom Hooks) 등으로 분리하십시오.
- **지역 상태 우선 (Local State First)**: 전역 상태(Redux, Zustand 등)는 앱 전체에서 공유해야 하는 최소한의 데이터에만 사용하고, 컴포넌트 내부 렌더링 상태는 React State 등 지역 상태로 격리하십시오.
- **Form 및 유효성 검사**: 폼 입력 요소에는 적절한 validation 지침 및 ARIA 접근성 속성을 명시하십시오.

---

## ♿ 3. 접근성 (A11y) 및 SEO 표준

- **시맨틱 HTML5**: `<div>` 남용을 지양하고 `<header>`, `<main>`, `<nav>`, `<article>`, `<section>`, `<footer>` 등 적절한 시맨틱 태그를 활용하십시오.
- **접근성 (Accessibility)**: 이미지에는 `alt` 속성, 버튼에는 `aria-label`을 명시하고 키보드 포커스 링(Focus state)을 유지하십시오.
- **SEO 기본 적용**: 페이지별 Title 태그, Meta Description, OpenGraph 태그 및 단일 `<h1>` 구조를 준수하십시오.
